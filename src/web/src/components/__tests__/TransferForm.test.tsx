import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TransferForm } from '../TransferForm'
import * as api from '@/services/api'
import type { Account, TransferResponse } from '@/types/api'

// Mock the API module
vi.mock('@/services/api', () => ({
  createTransfer: vi.fn(),
}))

describe('TransferForm', () => {
  const mockAccounts: Account[] = [
    {
      id: '1',
      accountNumber: '1234567890',
      accountName: 'Checking Account',
      type: 'Checking',
      balance: 5000,
      currency: 'USD',
      createdAt: '2024-01-01T00:00:00Z',
    },
    {
      id: '2',
      accountNumber: '0987654321',
      accountName: 'Savings Account',
      type: 'Savings',
      balance: 10000,
      currency: 'USD',
      createdAt: '2024-01-01T00:00:00Z',
    },
  ]

  const mockOnTransferSuccess = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Form Rendering', () => {
    it('should render all form fields', () => {
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      expect(screen.getByLabelText(/from account/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/to account/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/^amount$/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /transfer/i })).toBeInTheDocument()
    })

    it('should display account options in dropdowns', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Click on "From Account" dropdown
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)

      // Check if account options are displayed
      await waitFor(() => {
        expect(screen.getAllByText(/Checking Account - \*\*\*\*7890/).length).toBeGreaterThan(0)
        expect(screen.getAllByText(/Savings Account - \*\*\*\*4321/).length).toBeGreaterThan(0)
      })
    })

    it('should show $ prefix for amount input', () => {
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      expect(screen.getByText('$')).toBeInTheDocument()
    })
  })

  describe('Validation - Required Fields', () => {
    it('should show error when from account is not selected', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      expect(
        await screen.findByText(/please select a source account/i)
      ).toBeInTheDocument()
    })

    it('should show error when to account is not selected', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      expect(
        await screen.findByText(/please select a destination account/i)
      ).toBeInTheDocument()
    })

    it('should show error when amount is not entered', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      expect(await screen.findByText(/please enter an amount/i)).toBeInTheDocument()
    })
  })

  describe('Validation - Amount Range', () => {
    it('should show error when amount is less than $0.01', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '0.00')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      expect(
        await screen.findByText(/amount must be at least \$0\.01/i)
      ).toBeInTheDocument()
    })

    it('should show error when amount exceeds $10,000', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '10000.01')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      expect(
        await screen.findByText(/amount cannot exceed \$10,000/i)
      ).toBeInTheDocument()
    })

    it('should accept valid amount within range', async () => {
      const user = userEvent.setup()
      vi.mocked(api.createTransfer).mockResolvedValue({
        debitTransactionId: 'txn1',
        creditTransactionId: 'txn2',
        timestamp: '2024-01-01T00:00:00Z',
      })

      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Select from account
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ })
      await user.click(checkingOption)

      // Select to account
      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)
      const savingsOption = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ })
      await user.click(savingsOption)

      // Enter valid amount
      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100.00')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(api.createTransfer).toHaveBeenCalledWith({
          fromAccountId: '1',
          toAccountId: '2',
          amount: 100,
          description: undefined,
        })
      })
    })
  })

  describe('Validation - Amount Decimals', () => {
    it('should show error when amount has more than 2 decimal places', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100.123')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      expect(
        await screen.findByText(/amount can have at most 2 decimal places/i)
      ).toBeInTheDocument()
    })

    it('should accept amount with 0 decimal places', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      // Should not show decimal error
      expect(
        screen.queryByText(/amount can have at most 2 decimal places/i)
      ).not.toBeInTheDocument()
    })

    it('should accept amount with 1 decimal place', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100.5')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      // Should not show decimal error
      expect(
        screen.queryByText(/amount can have at most 2 decimal places/i)
      ).not.toBeInTheDocument()
    })

    it('should accept amount with 2 decimal places', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100.50')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      // Should not show decimal error
      expect(
        screen.queryByText(/amount can have at most 2 decimal places/i)
      ).not.toBeInTheDocument()
    })
  })

  describe('Validation - Self-Transfer Prevention', () => {
    it('should show error when same account is selected for from and to', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Select from account
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ }); await user.click(checkingOption)

      // Wait for dropdown to close
      await waitFor(() => {
        expect(fromAccountTrigger).toHaveAttribute('aria-expanded', 'false')
      })

      // Select to account (same as from account)
      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)
      const checkingOption2 = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ }); await user.click(checkingOption2)

      // Wait for dropdown to close
      await waitFor(() => {
        expect(toAccountTrigger).toHaveAttribute('aria-expanded', 'false')
      })

      // Now change from account to match to account
      await user.click(fromAccountTrigger)
      const savingsOption = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ }); await user.click(savingsOption)

      // Wait for dropdown to close
      await waitFor(() => {
        expect(fromAccountTrigger).toHaveAttribute('aria-expanded', 'false')
      })

      // Enter amount
      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      expect(
        await screen.findByText(/cannot transfer to the same account/i)
      ).toBeInTheDocument()
    })

    it('should disable from account in to account dropdown', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Select from account
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ }); await user.click(checkingOption)

      // Open to account dropdown
      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)

      // The from account option should be disabled in the to account dropdown
      await waitFor(() => {
        const disabledOption = screen.getByRole('option', { name: /Checking Account - \*\*\*\*7890/ })
        expect(disabledOption).toHaveAttribute('data-disabled')
      })
    })
  })

  describe('Form Submission - Success', () => {
    it('should call createTransfer with correct data on successful submission', async () => {
      const user = userEvent.setup()
      vi.mocked(api.createTransfer).mockResolvedValue({
        debitTransactionId: 'txn1',
        creditTransactionId: 'txn2',
        timestamp: '2024-01-01T00:00:00Z',
      })

      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Fill out the form
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ }); await user.click(checkingOption)

      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)
      const savingsOption = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ }); await user.click(savingsOption)

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '250.75')

      const descriptionInput = screen.getByLabelText(/description/i)
      await user.type(descriptionInput, 'Monthly savings')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(api.createTransfer).toHaveBeenCalledWith({
          fromAccountId: '1',
          toAccountId: '2',
          amount: 250.75,
          description: 'Monthly savings',
        })
      })
    })

    it('should show success message after successful transfer', async () => {
      const user = userEvent.setup()
      vi.mocked(api.createTransfer).mockResolvedValue({
        debitTransactionId: 'txn1',
        creditTransactionId: 'txn2',
        timestamp: '2024-01-01T00:00:00Z',
      })

      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Fill and submit form
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ }); await user.click(checkingOption)

      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)
      const savingsOption = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ }); await user.click(savingsOption)

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      expect(
        await screen.findByText(/transfer completed successfully/i)
      ).toBeInTheDocument()
    })

    it('should call onTransferSuccess callback after successful transfer', async () => {
      const user = userEvent.setup()
      vi.mocked(api.createTransfer).mockResolvedValue({
        debitTransactionId: 'txn1',
        creditTransactionId: 'txn2',
        timestamp: '2024-01-01T00:00:00Z',
      })

      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Fill and submit form
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ })
      await user.click(checkingOption)

      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)
      const savingsOption = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ })
      await user.click(savingsOption)

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnTransferSuccess).toHaveBeenCalledTimes(1)
      })
    })

    it('should reset form after successful transfer', async () => {
      const user = userEvent.setup()
      vi.mocked(api.createTransfer).mockResolvedValue({
        debitTransactionId: 'txn1',
        creditTransactionId: 'txn2',
        timestamp: '2024-01-01T00:00:00Z',
      })

      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Fill and submit form
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ })
      await user.click(checkingOption)

      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)
      const savingsOption = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ })
      await user.click(savingsOption)

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100')

      const descriptionInput = screen.getByLabelText(/description/i)
      await user.type(descriptionInput, 'Test transfer')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      // Wait for form to reset
      await waitFor(() => {
        expect(amountInput).toHaveValue('')
        expect(descriptionInput).toHaveValue('')
      })
    })

    it('should show loading state during submission', async () => {
      const user = userEvent.setup()
      let resolveTransfer: (value: TransferResponse) => void
      const transferPromise = new Promise<TransferResponse>((resolve) => {
        resolveTransfer = resolve
      })
      vi.mocked(api.createTransfer).mockReturnValue(transferPromise)

      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Fill and submit form
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ })
      await user.click(checkingOption)

      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)
      const savingsOption = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ })
      await user.click(savingsOption)

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      // Check loading state
      expect(
        await screen.findByRole('button', { name: /processing/i })
      ).toBeDisabled()

      // Resolve the transfer
      resolveTransfer!({
        debitTransactionId: 'txn1',
        creditTransactionId: 'txn2',
        timestamp: '2024-01-01T00:00:00Z',
      })

      // Wait for button to return to normal state
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /transfer/i })).not.toBeDisabled()
      })
    })
  })

  describe('Form Submission - Error Handling', () => {
    it('should display error message on API failure', async () => {
      const user = userEvent.setup()
      vi.mocked(api.createTransfer).mockRejectedValue(
        new Error('Insufficient funds')
      )

      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Fill and submit form
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ })
      await user.click(checkingOption)

      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)
      const savingsOption = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ })
      await user.click(savingsOption)

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      expect(await screen.findByText(/insufficient funds/i)).toBeInTheDocument()
    })

    it('should not call onTransferSuccess callback on error', async () => {
      const user = userEvent.setup()
      vi.mocked(api.createTransfer).mockRejectedValue(new Error('API Error'))

      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Fill and submit form
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ })
      await user.click(checkingOption)

      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)
      const savingsOption = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ })
      await user.click(savingsOption)

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/api error/i)).toBeInTheDocument()
      })

      expect(mockOnTransferSuccess).not.toHaveBeenCalled()
    })

    it('should not reset form on error', async () => {
      const user = userEvent.setup()
      vi.mocked(api.createTransfer).mockRejectedValue(new Error('API Error'))

      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      // Fill and submit form
      const fromAccountTrigger = screen.getByRole('combobox', { name: /from account/i })
      await user.click(fromAccountTrigger)
      const checkingOption = await screen.findByRole('option', { name: /Checking Account - \*\*\*\*7890/ })
      await user.click(checkingOption)

      const toAccountTrigger = screen.getByRole('combobox', { name: /to account/i })
      await user.click(toAccountTrigger)
      const savingsOption = await screen.findByRole('option', { name: /Savings Account - \*\*\*\*4321/ })
      await user.click(savingsOption)

      const amountInput = screen.getByLabelText(/^amount$/i)
      await user.type(amountInput, '100')

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/api error/i)).toBeInTheDocument()
      })

      // Form should still have the values
      expect(amountInput).toHaveValue('100')
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      expect(screen.getByLabelText(/from account/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/to account/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/^amount$/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
    })

    it('should mark invalid fields with aria-invalid', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      await waitFor(() => {
        const fromAccount = screen.getByRole('combobox', { name: /from account/i })
        const toAccount = screen.getByRole('combobox', { name: /to account/i })
        const amount = screen.getByLabelText(/^amount$/i)

        expect(fromAccount).toHaveAttribute('aria-invalid', 'true')
        expect(toAccount).toHaveAttribute('aria-invalid', 'true')
        expect(amount).toHaveAttribute('aria-invalid', 'true')
      })
    })

    it('should associate error messages with fields using aria-describedby', async () => {
      const user = userEvent.setup()
      render(
        <TransferForm
          accounts={mockAccounts}
          onTransferSuccess={mockOnTransferSuccess}
        />
      )

      const submitButton = screen.getByRole('button', { name: /transfer/i })
      await user.click(submitButton)

      await waitFor(() => {
        const fromAccount = screen.getByRole('combobox', { name: /from account/i })
        expect(fromAccount).toHaveAttribute('aria-describedby', 'fromAccount-error')
      })
    })
  })
})







