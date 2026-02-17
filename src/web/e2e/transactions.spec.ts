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

    // Check for column headers (Date, Description, Category, Amount, Balance After)
    await expect(page.getByRole('columnheader', { name: 'Date' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Description' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Category' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Amount' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Balance After' })).toBeVisible();

    // Verify at least 1 transaction row is visible
    const transactionRows = page.locator('table tbody tr, [data-testid="transaction-row"]');
    await expect(transactionRows.first()).toBeVisible();
    const rowCount = await transactionRows.count();
    expect(rowCount).toBeGreaterThan(0);

    // Verify category values are present in the Category column (3rd column in tbody)
    // Categories are rendered as badges with text content
    const firstCategoryCell = page.locator('table tbody tr:first-child td:nth-child(3)');
    await expect(firstCategoryCell).toBeVisible();
    await expect(firstCategoryCell).not.toBeEmpty();

    // Take screenshot
    await page.screenshot({ path: 'test-results/transactions.png', fullPage: true });
  });
});
