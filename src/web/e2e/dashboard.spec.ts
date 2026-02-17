import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should load dashboard with accounts and transactions', async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/');

    // Wait for accounts cards to appear
    await page.waitForSelector('[data-testid="account-card"], .account-card, [class*="AccountCard"]', {
      timeout: 10000,
    });

    // Verify at least 1 account is visible
    const accountCards = page.locator('[data-testid="account-card"], .account-card, [class*="AccountCard"]');
    await expect(accountCards.first()).toBeVisible();

    // Verify transactions table is visible
    const transactionsTable = page.locator('[data-testid="transactions-table"], table, [class*="TransactionList"]');
    await expect(transactionsTable.first()).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'test-results/dashboard.png', fullPage: true });
  });
});
