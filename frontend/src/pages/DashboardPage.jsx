// Protected Dashboard. Only rendered when the app is authenticated (see App.jsx).
// Workspaces/framework selection arrive in Session 4.
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../i18n/index.jsx'

export default function DashboardPage() {
  const { t } = useLanguage()
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-10">
      <div className="mx-auto w-full max-w-2xl bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-900">
            {t('dashboard.welcome')}, {user?.display_name}
          </h2>
          <button
            type="button"
            onClick={logout}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
          >
            {t('nav.logout')}
          </button>
        </div>

        <p className="mt-4 text-sm text-slate-600">{t('dashboard.subtitle')}</p>

        <dl className="mt-6 grid grid-cols-1 gap-3 text-sm">
          <div className="flex justify-between rounded-lg border border-slate-200 px-4 py-3">
            <dt className="font-medium text-slate-700">{t('register.email')}</dt>
            <dd className="text-slate-600">{user?.email}</dd>
          </div>
          <div className="flex justify-between rounded-lg border border-slate-200 px-4 py-3">
            <dt className="font-medium text-slate-700">{t('dashboard.language')}</dt>
            <dd className="text-slate-600 uppercase">{user?.language_preference}</dd>
          </div>
        </dl>
      </div>
    </div>
  )
}
