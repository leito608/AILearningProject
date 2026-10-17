// Story: ../../../RAG/specs/spec.md
// Plan: ../../specs/rag-pdf-assistant.plan.md (RAG-06)
import { expect, test } from '@playwright/test';

test.describe('RAG-06 — Retrieval count controls', () => {
  test('shows the default count and supported range', async ({ page }) => {
    // 1. Open the RAG UI.
    await page.goto(process.env.RAG_BASE_URL ?? 'http://127.0.0.1:8501/');

    // 2. Verify the question form is visible and the default count is 5.
    await expect(page.getByRole('heading', { name: 'Ask a question about your PDFs' })).toBeVisible();
    const count = page.getByRole('spinbutton', { name: 'How many chunks to retrieve' });
    await expect(count).toHaveValue('5');

    // 3. Verify both supported boundaries and select each boundary value.
    await expect(count).toHaveAttribute('min', '1');
    await expect(count).toHaveAttribute('max', '20');

    await count.fill('1');
    await expect(count).toHaveValue('1');
    await count.fill('20');
    await expect(count).toHaveValue('20');
  });
});
