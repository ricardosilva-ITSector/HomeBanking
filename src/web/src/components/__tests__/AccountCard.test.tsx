import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AccountCard } from '../AccountCard'
import type { Account } from '@/types/api'

describe('AccountCard', () => {
  const mockAccount: Account = {
    id: '1',
    accountNumber: '1234567890',
    accountName: 'Primary Checking',
    type: 'Checking',
    balance: 1234.56,
    currency: 'USD',
    createdAt: '2024-01-01T00:00:00Z',
  }

  it('renders account name correctly', () => {
    render(<AccountCard account={mockAccount} />)
    expect(screen.getByText('Primary Checking')).toBeInTheDocument()
  })

  it('displays masked account number with last 4 digits', () => {
    render(<AccountCard account={mockAccount} />)
    expect(screen.getByText('****7890')).toBeInTheDocument()
  })

  it('formats balance with currency symbol', () => {
    render(<AccountCard account={mockAccount} />)
    expect(screen.getByText('$1,234.56')).toBeInTheDocument()
  })

  it('displays account type badge for Checking account', () => {
    render(<AccountCard account={mockAccount} />)
    expect(screen.getByText('Checking')).toBeInTheDocument()
  })

  it('displays account type badge for Savings account', () => {
    const savingsAccount: Account = {
      ...mockAccount,
      type: 'Savings',
      accountName: 'Savings Account',
    }
    render(<AccountCard account={savingsAccount} />)
    expect(screen.getByText('Savings')).toBeInTheDocument()
  })

  it('handles different currency formats', () => {
    const euroAccount: Account = {
      ...mockAccount,
      balance: 5000.0,
      currency: 'EUR',
    }
    render(<AccountCard account={euroAccount} />)
    expect(screen.getByText('€5,000.00')).toBeInTheDocument()
  })

  it('handles large balances with proper formatting', () => {
    const largeBalanceAccount: Account = {
      ...mockAccount,
      balance: 1234567.89,
    }
    render(<AccountCard account={largeBalanceAccount} />)
    expect(screen.getByText('$1,234,567.89')).toBeInTheDocument()
  })

  it('handles negative balances', () => {
    const negativeBalanceAccount: Account = {
      ...mockAccount,
      balance: -500.0,
    }
    render(<AccountCard account={negativeBalanceAccount} />)
    expect(screen.getByText('-$500.00')).toBeInTheDocument()
  })
})
