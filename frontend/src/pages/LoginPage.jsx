// Login page: mobile-responsive Tailwind form that authenticates via the
// backend and stores the JWT in an httpOnly cookie (no token in JS).
import { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../i18n/index.jsx'

export default function LoginPage({ onSwitchToRegister }) {
  const { t } = useLanguage()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [localError, setLocalError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setLocalError(null)
    setSubmitting(true)
    try {
      await login(email, password)
      // On success the auth state flips to 'authed' and App shows the Dashboard.
    } catch {
      setLocalError(t('login.error'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-900 mb-6">{t('login.title')}</h2>

        {localError && (
          <p className="mb-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {localError}
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">{t('login.email')}</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">{t('login.password')}</span>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
          </label>

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {t('login.submit')}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-600">
          <button
            type="button"
            onClick={onSwitchToRegister}
            className="font-medium text-blue-600 hover:underline"
          >
            {t('landing.ctaRegister')}
          </button>
        </p>
      </div>
    </div>
  )
}
