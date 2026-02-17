import { test, expect } from '@playwright/test';

test.describe('Transfer', () => {
  test('should complete transfer flow successfully', async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/');

    // Wait for the transfer form to appear
    await page.waitForSelector('[data-testid="transfer-form"], form, [class*="TransferForm"]', {
      timeout: 10000,
    });

    // Fill "From Account" dropdown
    const fromAccountSelect = page.locator('[data-testid="from-account"], select, [name*="from"]').first();
    await fromAccountSelect.waitFor({ state: 'visible' });
    
    // Get all options and select the first one
    const fromOptions = await fromAccountSelect.locator('option').allTextContents();
    if (fromOptions.length > 1) {
      await fromAccountSelect.selectOption({ index: 1 }); // Select first actual account (skip placeholder if any)
    }

    // Fill "To Account" dropdown (different from From)
    const toAccountSelect = page.locator('[data-testid="to-account"], select, [name*="to"]').first();
    await toAccountSelect.waitFor({ state: 'visible' });
    
    // Get all options and select a different one
    const toOptions = await toAccountSelect.locator('option').allTextContents();
    if (toOptions.length > 2) {
      await toAccountSelect.selectOption({ index: 2 }); // Select second actual account (different from From)
    } else if (toOptions.length > 1) {
      await toAccountSelect.selectOption({ index: 1 });
    }

    // Fill Amount
    const amountInput = page.locator('[data-testid="amount"], input[type="number"], input[name*="amount"]').first();
    await amountInput.waitFor({ state: 'visible' });
    await amountInput.fill('100.00');

    // Fill Description
    const descriptionInput = page.locator('[data-testid="description"], input[type="text"], textarea, input[name*="description"]').first();
    await descriptionInput.waitFor({ state: 'visible' });
    await descriptionInput.fill('E2E Test Transfer');

    // Click Submit button
    const submitButton = page.locator('[data-testid="submit-transfer"], button[type="submit"], button:has-text("Transfer")').first();
    await submitButton.click();

    // Wait for success message
    await page.locator('[data-testid="success-message"]').waitFor({ 
      state: 'visible',
      timeout: 10000 
    });

    // Verify "Transfer successful!" message appears
    await expect(page.getByText(/Transfer successful/i).first()).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'test-results/transfer-success.png', fullPage: true });
  });
});
