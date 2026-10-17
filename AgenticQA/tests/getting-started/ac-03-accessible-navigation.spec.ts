// Story: user-stories/playwright-docs-getting-started.md
// Plan: specs/playwright-getting-started.plan.md
import { test, expect } from '@playwright/test';

test.describe('Playwright Documentation — Getting Started', () => {
  test('AC-3 — Get started link is accessible by role and name', async ({ page }) => {
    // 1. In a fresh browser context, open https://playwright.dev/.
    await page.goto('https://playwright.dev/');

    // 2–3. Locate exactly one visible “Get started” link by its accessible role and name.
    const getStartedLink = page.getByRole('link', { name: 'Get started', exact: true });
    await expect(getStartedLink).toHaveCount(1);
    await expect(getStartedLink).toBeVisible();

    // 4. Activate that role-and-name locator.
    await getStartedLink.click();

    // 5. Verify the Getting Started documentation and Installation heading are visible.
    await expect(page).toHaveURL('https://playwright.dev/docs/intro');
    await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
  });
});
