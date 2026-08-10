// Register page: creates an account, sets the httpOnly cookie, and lands on
// the (protected) Dashboard.
import { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../i18n/index.jsx'

export default function RegisterPage({ onSwitchToLogin }) {
  const { t } = useLanguage()
  const { register, authError } = useAuth()
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [languagePreference, setLanguagePreference] = useState('en')
  const [submitting, setSubmitting] = useState(false)
  const [localError, setLocalError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setLocalError(null)

    if (password !== confirmPassword) {
      setLocalError(t('register.passwordMismatch'))
      return
    }
    if (password.length < 8) {
      setLocalError('Password must be at least 8 characters.')
      return
    }

    setSubmitting(true)
    try {
      await register({
        email,
        display_name: displayName,
        password,
        language_preference: languagePreference,
      })
      // Success -> auth state flips to 'authed' and App shows the Dashboard.
    } catch {
      setLocalError(t('register.error'))
    } finally {
      setSubmitting(false)
    }
  }

  const inputCls =
    'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none'

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-900 mb-6">{t('register.title')}</h2>

        {localError && (
          <p className="mb-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {localError}
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">{t('register.displayName')}</span>
            <input
              type="text"
              required
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className={inputCls}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">{t('register.email')}</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={inputCls}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">{t('register.password')}</span>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={inputCls}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">{t('register.confirmPassword')}</span>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className={inputCls}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">{t('register.language')}</span>
            <select
              value={languagePreference}
              onChange={(e) => setLanguagePreference(e.target.value)}
              className={inputCls}
            >
              <option value="en">English</option>
              <option value="fr">Français</option>
            </select>
          </label>

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {t('register.submit')}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-600">
          <button
            type="button"
            onClick={onSwitchToLogin}
            className="font-medium text-blue-600 hover:underline"
          >
            {t('landing.ctaLogin')}
          </button>
        </p>
      </div>
    </div>
  )
}
