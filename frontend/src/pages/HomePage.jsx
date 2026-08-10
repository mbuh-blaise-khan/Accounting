// Public landing page: shows backend/database status and CTAs to log in/register.
import { useEffect, useState } from 'react'
import { fetchHealth } from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'

export default function HomePage({ onCreateAccount, onLogin }) {
  const { t } = useLanguage()
  const [health, setHealth] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchHealth()
      .then((data) => !cancelled && setHealth(data))
      .catch((err) => !cancelled && setError(err.message))
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4 py-10">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-slate-200 p-8 text-center">
        <h1 className="text-2xl font-bold text-slate-900">{t('app.title')}</h1>
        <p className="mt-1 text-slate-600">{t('app.subtitle')}</p>
        <p className="mt-4 text-slate-700">{t('landing.tagline')}</p>

        <div className="mt-6 flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3 text-left mb-3">
          <span className="text-sm font-medium text-slate-700">{t('status.api')}</span>
          <span className={`text-sm font-semibold ${error ? 'text-red-600' : health ? 'text-green-600' : 'text-slate-400'}`}>
            {error ? t('status.unreachable') : health ? t('status.connected') : t('common.loading')}
          </span>
        </div>
        <div className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3 text-left mb-6">
          <span className="text-sm font-medium text-slate-700">{t('status.database')}</span>
          <span className={`text-sm font-semibold ${health ? (health.db ? 'text-green-600' : 'text-red-600') : 'text-slate-400'}`}>
            {health ? (health.db ? t('status.connected') : t('status.down')) : '—'}
          </span>
        </div>

        <div className="space-y-3">
          <button
            type="button"
            onClick={onLogin}
            className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            {t('landing.ctaLogin')}
          </button>
          <button
            type="button"
            onClick={onCreateAccount}
            className="w-full rounded-lg border border-blue-600 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50"
          >
            {t('landing.ctaRegister')}
          </button>
        </div>
      </div>
    </div>
  )
}
