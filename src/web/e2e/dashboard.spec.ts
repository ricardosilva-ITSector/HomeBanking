import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should load dashboard with accounts and transactions', async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/');

    // Wait for page to load by checking for main heading
    await expect(page.getByRole('heading', { name: 'My Accounts' })).toBeVisible();

    // Verify at least 1 account card is visible (using more specific selectors)
    const accountCards = page.locator('[class*="grid"] > div').filter({ hasText: /Checking|Savings/ });
    await expect(accountCards.first()).toBeVisible({ timeout: 10000 });

    // Verify transactions table is visible
    const transactionsTable = page.locator('[data-testid="transactions-table"], table, [class*="TransactionList"]');
    await expect(transactionsTable.first()).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'test-results/dashboard.png', fullPage: true });
  });
});
