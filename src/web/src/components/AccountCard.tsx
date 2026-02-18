import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { Account } from '@/types/api'

interface AccountCardProps {
  account: Account
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
 * Formats a currency amount using Intl.NumberFormat.
 * @param amount - The amount to format
 * @param currency - Currency code (e.g., "USD")
 * @returns Formatted currency string (e.g., "$1,234.56")
 */
function formatCurrency(amount: number, currency: string): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount)
}

/**
 * Get badge variant based on account type.
 * @param type - Account type (Checking or Savings)
 * @returns Badge variant
 */
function getAccountTypeBadgeVariant(type: string): 'default' | 'secondary' {
  return type === 'Checking' ? 'default' : 'secondary'
}

export function AccountCard({ account }: AccountCardProps) {
  return (
    <Card className="border-slate-200 bg-white transition-colors hover:border-red-300">
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-xl text-slate-900">
            {account.accountName}
          </CardTitle>
          <Badge
            variant={getAccountTypeBadgeVariant(account.type)}
            className={`ml-2 ${
              account.type === 'Checking'
                ? 'bg-red-100 text-red-700 hover:bg-red-200'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            {account.type}
          </Badge>
        </div>
        <p className="mt-2 text-sm text-slate-500">
          {maskAccountNumber(account.accountNumber)}
        </p>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold text-slate-900">
          {formatCurrency(account.balance, account.currency)}
        </div>
      </CardContent>
    </Card>
  )
}
