import { Building2 } from 'lucide-react'

export function Header() {
  return (
    <header className="bg-slate-900/50 border-b border-slate-800 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3 h-16">
          <Building2 className="h-8 w-8 text-blue-500" />
          <h1 className="text-2xl font-bold text-slate-50">HomeBanking</h1>
        </div>
      </div>
    </header>
  )
}
