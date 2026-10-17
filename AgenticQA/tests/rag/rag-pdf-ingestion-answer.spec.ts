// Story: ../../../RAG/specs/spec.md (REQ-001, REQ-002, REQ-005, REQ-007)
// Plan: ../../specs/rag-pdf-assistant.plan.md (RAG-01, RAG-03, RAG-07)
import { expect, test, type APIRequestContext } from '@playwright/test';
import { existsSync, unlinkSync } from 'node:fs';
import { resolve } from 'node:path';

const appUrl = process.env.RAG_BASE_URL ?? 'http://127.0.0.1:8501/';
const qdrantUrl = process.env.QDRANT_URL ?? 'http://127.0.0.1:6333';

function makePdf(text: string): Buffer {
  const content = `BT /F1 18 Tf 50 700 Td (${text}) Tj ET`;
  const objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    `<< /Length ${Buffer.byteLength(content, 'ascii')} >>\nstream\n${content}\nendstream`,
  ];
  let pdf = '%PDF-1.4\n';
  const offsets = [0];
  for (const [index, object] of objects.entries()) {
    offsets.push(Buffer.byteLength(pdf, 'ascii'));
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  }
  const xrefOffset = Buffer.byteLength(pdf, 'ascii');
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (const offset of offsets.slice(1)) {
    pdf += `${offset.toString().padStart(10, '0')} 00000 n \n`;
  }
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`;
  return Buffer.from(pdf, 'ascii');
}

async function deleteTestPoints(request: APIRequestContext, fileName: string): Promise<void> {
  const response = await request.post(`${qdrantUrl}/collections/docs/points/delete?wait=true`, {
    data: {
      filter: { must: [{ key: 'source', match: { value: fileName } }] },
    },
  });
  expect(response.ok()).toBeTruthy();
}

test.describe('RAG-01/03/07 — PDF ingestion, grounded answer, and source attribution', () => {
  test('uploads a synthetic PDF, retrieves its fact, and displays its source', async ({ page, request }) => {
    test.setTimeout(180_000);
    const fileName = `rag-qa-${crypto.randomUUID()}.pdf`;
    const uniqueFact = `ORANGE-KESTREL-${crypto.randomUUID().slice(0, 8).toUpperCase()}`;
    let uploadAttempted = false;

    try {
      // 1. Open the RAG UI in a fresh browser context.
      await page.goto(appUrl);
      await expect(page.getByRole('heading', { name: 'Upload a PDF to Ingest' })).toBeVisible();

      // 2. Upload a synthetic PDF containing a unique, verifiable fact.
      uploadAttempted = true;
      await page.locator('input[type="file"]').setInputFiles({
        name: fileName,
        mimeType: 'application/pdf',
        buffer: makePdf(`RAG QA test document. The unique validation token is ${uniqueFact}.`),
      });

      // 3. Wait until the uploaded source is persisted in Qdrant.
      await expect(page.getByText(`Triggered ingestion for: ${fileName}`)).toBeVisible({ timeout: 30_000 });
      await expect.poll(async () => {
        const response = await request.post(`${qdrantUrl}/collections/docs/points/scroll`, {
          data: {
            limit: 10,
            with_payload: true,
            with_vector: false,
            filter: { must: [{ key: 'source', match: { value: fileName } }] },
          },
        });
        if (!response.ok()) {
          throw new Error(`Qdrant scroll failed with HTTP ${response.status()}: ${await response.text()}`);
        }
        const body = await response.json();
        return body.result?.points?.length ?? 0;
      }, { timeout: 90_000, intervals: [500, 1_000, 2_000, 5_000] }).toBeGreaterThan(0);

      // 4. Ask about the fact and verify the answer and its source are visible.
      await page.getByRole('textbox', { name: 'Your question' }).fill('What is the unique validation token?');
      await page.getByRole('button', { name: 'Ask' }).click();
      await expect(page.getByRole('heading', { name: 'Answer' })).toBeVisible({ timeout: 150_000 });
      await expect(page.getByText(uniqueFact, { exact: false })).toBeVisible({ timeout: 30_000 });
      await expect(page.getByRole('listitem').filter({ hasText: fileName })).toBeVisible();
    } finally {
      if (uploadAttempted) {
        // 5. Remove only this test's uniquely identified vector and upload.
        await deleteTestPoints(request, fileName);
        const uploadedFile = resolve(process.cwd(), '../uploads', fileName);
        if (existsSync(uploadedFile)) unlinkSync(uploadedFile);
      }
    }
  });
});
