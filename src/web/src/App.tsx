import { useState, useEffect } from 'react'
import { Header } from '@/components/Header'
import { AccountCard } from '@/components/AccountCard'
import { TransactionList } from '@/components/TransactionList'
import { TransferForm } from '@/components/TransferForm'
import { ChatWidget } from '@/components/ChatWidget'
import { getAccounts } from '@/services/api'
import type { Account } from '@/types/api'
import { ArrowRightLeft, Landmark, Wallet } from 'lucide-react'
import './App.css'

function App() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAccounts = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getAccounts()
      setAccounts(data)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to load accounts'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAccounts()
  }, [])

  const totalBalance = accounts.reduce((sum, account) => sum + account.balance, 0)

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Header />
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">Total Accounts</p>
              <Landmark className="h-5 w-5 text-red-500" />
            </div>
            <p className="mt-3 text-3xl font-semibold text-slate-900">{accounts.length}</p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">Available Balance</p>
              <Wallet className="h-5 w-5 text-red-500" />
            </div>
            <p className="mt-3 text-3xl font-semibold text-slate-900">
              {formatCurrency(totalBalance)}
            </p>
          </div>

          <div className="rounded-xl border border-red-200 bg-red-50 p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-red-700">Today’s Actions</p>
              <ArrowRightLeft className="h-5 w-5 text-red-600" />
            </div>
            <p className="mt-3 text-sm text-red-800">
              Review recent transactions and manage transfers securely.
            </p>
          </div>
        </section>

        <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold text-slate-900">My Accounts</h2>

              {loading && (
                <div className="py-12 text-center">
                  <p className="text-slate-500">Loading accounts...</p>
                </div>
              )}

              {error && (
                <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4">
                  <p className="text-red-700">Error: {error}</p>
                </div>
              )}

              {!loading && !error && accounts.length === 0 && (
                <div className="py-12 text-center">
                  <p className="text-slate-500">No accounts found.</p>
                </div>
              )}

              {!loading && !error && accounts.length > 0 && (
                <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
                  {accounts.map((account) => (
                    <AccountCard key={account.id} account={account} />
                  ))}
                </div>
              )}
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold text-slate-900">Recent Transactions</h2>
              <div className="mt-6">
                <TransactionList />
              </div>
            </div>
          </div>

          <div className="lg:sticky lg:top-24 lg:self-start">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold text-slate-900">Transfer</h2>
              <p className="mt-1 text-sm text-slate-500">
                Move money between your accounts instantly.
              </p>
              <div className="mt-5">
                <TransferForm accounts={accounts} onTransferSuccess={fetchAccounts} />
              </div>
            </div>
          </div>
        </section>
      </main>

      <ChatWidget />
    </div>
  )
}

export default App
