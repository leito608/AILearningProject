// Story: user-stories/playwright-docs-getting-started.md
// Plan: specs/playwright-getting-started.plan.md
import { test, expect } from '@playwright/test';

test.describe('Playwright Documentation — Getting Started', () => {
  test('AC-2 — Get started opens Installation guide', async ({ page }) => {
    // 1. In a fresh browser context, open https://playwright.dev/.
    await page.goto('https://playwright.dev/');

    // 2. Verify the Playwright home page is displayed.
    await expect(page).toHaveTitle(/Playwright/);

    // 3. Activate the link named “Get started” using its accessible link role and name.
    await page.getByRole('link', { name: 'Get started' }).click();

    // 4. Verify the Getting Started documentation and Installation heading are visible.
    await expect(page).toHaveURL('https://playwright.dev/docs/intro');
    await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
  });
});
