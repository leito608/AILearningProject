// Story: user-stories/playwright-docs-getting-started.md
// Plan: specs/playwright-getting-started.plan.md
import { test, expect } from '@playwright/test';

test.describe('Playwright Documentation — Getting Started', () => {
  test('AC-1 — Home page identifies Playwright', async ({ page }) => {
    // 1. In a fresh browser context, open https://playwright.dev/.
    await page.goto('https://playwright.dev/');

    // 2. Verify the page loads at https://playwright.dev/.
    await expect(page).toHaveURL('https://playwright.dev/');

    // 3. Verify the title contains “Playwright” and the documentation home page is displayed.
    await expect(page).toHaveTitle(/Playwright/);
    await expect(
      page.getByRole('heading', {
        name: 'Playwright enables reliable web automation for testing, scripting, and AI agents.',
      }),
    ).toBeVisible();
  });
});
