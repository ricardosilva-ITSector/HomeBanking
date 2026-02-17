import { test, expect } from '@playwright/test';

test.describe('Transactions', () => {
  test('should display transaction list with categories', async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/');

    // Wait for transactions table to load
    await page.waitForSelector('[data-testid="transactions-table"], table, [class*="TransactionList"]', {
      timeout: 10000,
    });

    // Verify table has the expected columns
    const table = page.locator('[data-testid="transactions-table"], table, [class*="TransactionList"]').first();
    await expect(table).toBeVisible();

    // Check for column headers (Date, Description, Category, Amount, Balance)
    await expect(page.getByText('Date', { exact: false })).toBeVisible();
    await expect(page.getByText('Description', { exact: false })).toBeVisible();
    await expect(page.getByText('Category', { exact: false })).toBeVisible();
    await expect(page.getByText('Amount', { exact: false })).toBeVisible();
    await expect(page.getByText('Balance', { exact: false })).toBeVisible();

    // Verify at least 1 transaction row is visible
    const transactionRows = page.locator('table tbody tr, [data-testid="transaction-row"]');
    await expect(transactionRows.first()).toBeVisible();
    const rowCount = await transactionRows.count();
    expect(rowCount).toBeGreaterThan(0);

    // Verify category badges are visible
    const categoryBadges = page.locator('[data-testid="category-badge"], .badge, [class*="badge"]');
    await expect(categoryBadges.first()).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'test-results/transactions.png', fullPage: true });
  });
});
