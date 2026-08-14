// Protected Dashboard. Only rendered when the app is authenticated (see App.jsx).
// Loads the user's workspaces; shows the "create your first workspace" flow when
// there are none, otherwise lists their workspaces.
import { useEffect, useState } from 'react'
import { fetchFrameworks, fetchOrganizations } from '../services/api.js'
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../i18n/index.jsx'
import CreateWorkspace from '../components/CreateWorkspace.jsx'
import ChartOfAccountsPage from './ChartOfAccountsPage.jsx'

export default function DashboardPage() {
  const { t } = useLanguage()
  const { user, logout } = useAuth()
  const [orgs, setOrgs] = useState(null) // null = loading
  const [frameworks, setFrameworks] = useState([])
  const [error, setError] = useState(null)
  const [activeOrg, setActiveOrg] = useState(null) // set -> showing chart of accounts

  async function load() {
    setError(null)
    try {
      const [orgList, fwList] = await Promise.all([
        fetchOrganizations(),
        fetchFrameworks(),
      ])
      setOrgs(orgList)
      setFrameworks(fwList)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    load()
  }, [])

  if (activeOrg) {
    return <ChartOfAccountsPage org={activeOrg} onBack={() => setActiveOrg(null)} />
  }

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto w-full max-w-2xl">
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

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}

        {orgs === null ? (
          <p className="mt-10 text-center text-slate-500">{t('common.loading')}</p>
        ) : orgs.length === 0 ? (
          <div className="mt-8">
            <CreateWorkspace frameworks={frameworks} onCreated={load} />
          </div>
        ) : (
          <div className="mt-8">
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
              {t('dashboard.workspaces')}
            </h3>
            <ul className="space-y-3">
              {orgs.map((org) => (
                <li
                  key={org.id}
                  className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-900">{org.name}</span>
                    {org.is_demo && (
                      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                        Demo
                      </span>
                    )}
                  </div>
                  <dl className="mt-2 grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <dt className="text-slate-500">{t('dashboard.framework')}</dt>
                      <dd className="font-medium text-slate-800">{org.framework}</dd>
                    </div>
                    <div>
                      <dt className="text-slate-500">{t('dashboard.currency')}</dt>
                      <dd className="font-medium text-slate-800">{org.currency}</dd>
                    </div>
                  </dl>
                  <button
                    type="button"
                    onClick={() => setActiveOrg(org)}
                    className="mt-3 w-full rounded-lg border border-blue-600 px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50"
                  >
                    {t('dashboard.openChart')}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
