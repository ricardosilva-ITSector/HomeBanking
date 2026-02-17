import { useState, useEffect } from 'react'
import { Header } from '@/components/Header'
import { AccountCard } from '@/components/AccountCard'
import { TransactionList } from '@/components/TransactionList'
import { TransferForm } from '@/components/TransferForm'
import { getAccounts } from '@/services/api'
import type { Account } from '@/types/api'
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

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-slate-100">My Accounts</h2>

          {loading && (
            <div className="text-center py-12">
              <p className="text-slate-400">Loading accounts...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-950 border border-red-800 rounded-lg p-4">
              <p className="text-red-300">Error: {error}</p>
            </div>
          )}

          {!loading && !error && accounts.length === 0 && (
            <div className="text-center py-12">
              <p className="text-slate-400">No accounts found.</p>
            </div>
          )}

          {!loading && !error && accounts.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {accounts.map((account) => (
                <AccountCard key={account.id} account={account} />
              ))}
            </div>
          )}
        </div>

        {/* Recent Transactions Section */}
        <div className="mt-12 space-y-6">
          <h2 className="text-2xl font-bold text-slate-100">
            Recent Transactions
          </h2>
          <TransactionList />
        </div>

        {/* Transfer Form Section */}
        <div className="mt-12 space-y-6">
          <h2 className="text-2xl font-bold text-slate-100">Make a Transfer</h2>
          <div className="max-w-2xl">
            <TransferForm accounts={accounts} onTransferSuccess={fetchAccounts} />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
