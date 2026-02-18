import { Building2 } from 'lucide-react'
import { useState } from 'react'

export function Header() {
  const logoCandidates = ['/banco-ctt-logo.svg', '/banco-ctt-logo.png']
  const [logoIndex, setLogoIndex] = useState(0)
  const [logoError, setLogoError] = useState(false)

  const handleLogoError = () => {
    if (logoIndex < logoCandidates.length - 1) {
      setLogoIndex((current) => current + 1)
      return
    }

    setLogoError(true)
  }

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-28 items-center justify-center overflow-hidden rounded-lg bg-red-50 px-2 py-1">
              {logoError ? (
                <Building2 className="h-6 w-6 text-red-600" />
              ) : (
                <img
                  src={logoCandidates[logoIndex]}
                  alt="Bank logo"
                  className="max-h-full w-full object-contain"
                  onError={handleLogoError}
                />
              )}
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight text-slate-900">
                HomeBanking
              </h1>
              <p className="text-xs text-slate-500">Client Area</p>
            </div>
          </div>
          <div className="hidden rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-700 sm:block">
            Secure Session
          </div>
        </div>
      </div>
    </header>
  )
}
