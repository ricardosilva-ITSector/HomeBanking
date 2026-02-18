import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { createTransfer } from '@/services/api'
import type { Account, TransferRequest } from '@/types/api'

interface TransferFormProps {
  accounts: Account[]
  onTransferSuccess: () => void
}

interface FormErrors {
  fromAccountId?: string
  toAccountId?: string
  amount?: string
  general?: string
}

/**
 * Masks an account number showing only the last 4 digits.
 * @param accountNumber - Full account number
 * @returns Masked account number (e.g., "****1234")
 */
function maskAccountNumber(accountNumber: string): string {
  const lastFour = accountNumber.slice(-4)
  return `****${lastFour}`
}

/**
 * Validates the amount to ensure it has at most 2 decimal places.
 * @param amount - Amount string to validate
 * @returns True if valid, false otherwise
 */
function validateDecimalPlaces(amount: string): boolean {
  const parts = amount.split('.')
  if (parts.length === 1) return true // No decimal point
  return parts[1].length <= 2
}

export function TransferForm({ accounts, onTransferSuccess }: TransferFormProps) {
  const [fromAccountId, setFromAccountId] = useState<string>('')
  const [toAccountId, setToAccountId] = useState<string>('')
  const [amount, setAmount] = useState<string>('')
  const [description, setDescription] = useState<string>('')
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [successMessage, setSuccessMessage] = useState<string>('')

  /**
   * Validates the form fields before submission.
   * @returns True if form is valid, false otherwise
   */
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    // Required field validations
    if (!fromAccountId) {
      newErrors.fromAccountId = 'Please select a source account'
    }

    if (!toAccountId) {
      newErrors.toAccountId = 'Please select a destination account'
    }

    if (!amount) {
      newErrors.amount = 'Please enter an amount'
    } else {
      const amountNum = parseFloat(amount)

      // Amount range validation
      if (isNaN(amountNum)) {
        newErrors.amount = 'Please enter a valid amount'
      } else if (amountNum < 0.01) {
        newErrors.amount = 'Amount must be at least $0.01'
      } else if (amountNum > 10000) {
        newErrors.amount = 'Amount cannot exceed $10,000'
      }

      // Decimal places validation
      if (!validateDecimalPlaces(amount)) {
        newErrors.amount = 'Amount can have at most 2 decimal places'
      }
    }

    // Self-transfer prevention
    if (fromAccountId && toAccountId && fromAccountId === toAccountId) {
      newErrors.toAccountId = 'Cannot transfer to the same account'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  /**
   * Handles form submission and transfer creation.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSuccessMessage('')
    setErrors({})

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      const transferRequest: TransferRequest = {
        fromAccountId,
        toAccountId,
        amount: parseFloat(amount),
        description: description.trim() || undefined,
      }

      await createTransfer(transferRequest)

      // Show success message
      setSuccessMessage('Transfer completed successfully!')

      // Reset form
      setFromAccountId('')
      setToAccountId('')
      setAmount('')
      setDescription('')
      setErrors({})

      // Call success callback to refresh accounts
      onTransferSuccess()

      // Clear success message after 5 seconds
      setTimeout(() => setSuccessMessage(''), 5000)
    } catch (error) {
      // Handle API errors
      const errorMessage =
        error instanceof Error ? error.message : 'Transfer failed. Please try again.'
      setErrors({ general: errorMessage })
    } finally {
      setIsSubmitting(false)
    }
  }

  /**
   * Handles amount input changes with validation.
   */
  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    // Allow empty string, numbers, and decimal point
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      setAmount(value)
      // Clear amount error when user starts typing
      if (errors.amount) {
        setErrors((prev) => ({ ...prev, amount: undefined }))
      }
    }
  }

  return (
    <Card className="border-0 bg-transparent shadow-none">
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Success Message */}
          {successMessage && (
            <div
              className="bg-green-50 border border-green-200 rounded-lg p-4"
              role="alert"
              aria-live="polite"
            >
              <p className="text-green-700">{successMessage}</p>
            </div>
          )}

          {/* General Error Message */}
          {errors.general && (
            <div
              className="bg-red-50 border border-red-200 rounded-lg p-4"
              role="alert"
              aria-live="assertive"
            >
              <p className="text-red-700">{errors.general}</p>
            </div>
          )}

          {/* From Account */}
          <div className="space-y-2">
            <Label htmlFor="fromAccount" className="text-slate-700">
              From Account
            </Label>
            <Select
              value={fromAccountId}
              onValueChange={(value) => {
                setFromAccountId(value)
                if (errors.fromAccountId) {
                  setErrors((prev) => ({ ...prev, fromAccountId: undefined }))
                }
              }}
            >
              <SelectTrigger
                id="fromAccount"
                className="border-slate-300 bg-white text-slate-900"
                aria-invalid={!!errors.fromAccountId}
                aria-describedby={errors.fromAccountId ? 'fromAccount-error' : undefined}
              >
                <SelectValue placeholder="Select source account" />
              </SelectTrigger>
              <SelectContent className="border-slate-200 bg-white">
                {accounts.map((account) => (
                  <SelectItem
                    key={account.id}
                    value={account.id}
                    className="text-slate-900 focus:bg-slate-100 focus:text-slate-900"
                  >
                    {account.accountName} - {maskAccountNumber(account.accountNumber)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.fromAccountId && (
              <p id="fromAccount-error" className="text-sm text-red-400" role="alert">
                {errors.fromAccountId}
              </p>
            )}
          </div>

          {/* To Account */}
          <div className="space-y-2">
            <Label htmlFor="toAccount" className="text-slate-700">
              To Account
            </Label>
            <Select
              value={toAccountId}
              onValueChange={(value) => {
                setToAccountId(value)
                if (errors.toAccountId) {
                  setErrors((prev) => ({ ...prev, toAccountId: undefined }))
                }
              }}
            >
              <SelectTrigger
                id="toAccount"
                className="border-slate-300 bg-white text-slate-900"
                aria-invalid={!!errors.toAccountId}
                aria-describedby={errors.toAccountId ? 'toAccount-error' : undefined}
              >
                <SelectValue placeholder="Select destination account" />
              </SelectTrigger>
              <SelectContent className="border-slate-200 bg-white">
                {accounts.map((account) => (
                  <SelectItem
                    key={account.id}
                    value={account.id}
                    disabled={account.id === fromAccountId}
                    className="text-slate-900 focus:bg-slate-100 focus:text-slate-900 disabled:opacity-50"
                  >
                    {account.accountName} - {maskAccountNumber(account.accountNumber)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.toAccountId && (
              <p id="toAccount-error" className="text-sm text-red-400" role="alert">
                {errors.toAccountId}
              </p>
            )}
          </div>

          {/* Amount */}
          <div className="space-y-2">
            <Label htmlFor="amount" className="text-slate-700">
              Amount
            </Label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">
                $
              </span>
              <Input
                id="amount"
                type="text"
                inputMode="decimal"
                value={amount}
                onChange={handleAmountChange}
                placeholder="0.00"
                className="border-slate-300 bg-white pl-7 text-slate-900"
                aria-invalid={!!errors.amount}
                aria-describedby={errors.amount ? 'amount-error' : undefined}
              />
            </div>
            {errors.amount && (
              <p id="amount-error" className="text-sm text-red-400" role="alert">
                {errors.amount}
              </p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-slate-700">
              Description <span className="text-slate-400">(Optional)</span>
            </Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter transfer description"
              className="resize-none border-slate-300 bg-white text-slate-900"
              rows={3}
              maxLength={500}
            />
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-red-600 text-white hover:bg-red-700 disabled:bg-slate-300 disabled:text-slate-500"
          >
            {isSubmitting ? 'Processing...' : 'Transfer'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
