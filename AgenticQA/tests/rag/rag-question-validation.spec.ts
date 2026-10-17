// Story: ../../../RAG/specs/spec.md (REQ-009)
// Plan: ../../specs/rag-pdf-assistant.plan.md (RAG-05)
import { expect, test } from '@playwright/test';

test.describe('RAG-05 — Empty question validation', () => {
  test('does not submit empty or whitespace-only questions', async ({ page }) => {
    // 1. Open the RAG UI and locate the question form controls.
    await page.goto(process.env.RAG_BASE_URL ?? 'http://127.0.0.1:8501/');
    const question = page.getByRole('textbox', { name: 'Your question' });
    const ask = page.getByRole('button', { name: 'Ask' });

    // 2. Submit the form empty and verify it produces no result or error.
    await ask.click();
    await expect(page.getByRole('heading', { name: 'Answer' })).toHaveCount(0);
    await expect(page.getByRole('alert')).toHaveCount(0);

    // 3. Submit whitespace-only input and verify it also produces no result or error.
    await question.fill('   ');
    await ask.click();
    await expect(page.getByRole('heading', { name: 'Answer' })).toHaveCount(0);
    await expect(page.getByRole('alert')).toHaveCount(0);
  });
});
