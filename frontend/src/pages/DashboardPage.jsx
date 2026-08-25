// Protected Dashboard. Only rendered when the app is authenticated (see App.jsx).
// Loads the user's workspaces; shows the "create your first workspace" flow when
// there are none, otherwise lists their workspaces.
import { useEffect, useState } from 'react'
import { fetchFrameworks, fetchOrganizations } from '../services/api.js'
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../i18n/index.jsx'
import CreateWorkspace from '../components/CreateWorkspace.jsx'
import ChartOfAccountsPage from './ChartOfAccountsPage.jsx'
import NewTransactionPage from './NewTransactionPage.jsx'
import JournalPage from './JournalPage.jsx'
import CashBookPage from './CashBookPage.jsx'
import GeneralLedgerPage from './GeneralLedgerPage.jsx'

export default function DashboardPage() {
  const { t } = useLanguage()
  const { user, logout } = useAuth()
  const [orgs, setOrgs] = useState(null) // null = loading
  const [frameworks, setFrameworks] = useState([])
  const [error, setError] = useState(null)
  const [activeOrg, setActiveOrg] = useState(null) // set -> inside a workspace
  const [section, setSection] = useState('home') // home | accounts | newTransaction | journal | cashbook | ledger

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
    return (
      <WorkSpace
        org={activeOrg}
        section={section}
        onSectionChange={setSection}
        onExit={() => {
          setActiveOrg(null)
          setSection('home')
        }}
      />
    )
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

function NavBtn({ active, onClick, label }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
        active ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-slate-100'
      }`}
    >
      {label}
    </button>
  )
}

function WorkSpace({ org, section, onSectionChange, onExit }) {
  const { t } = useLanguage()
  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 px-4 py-2 backdrop-blur">
        <div className="mx-auto flex max-w-3xl flex-wrap items-center justify-between gap-2">
          <button
            type="button"
            onClick={onExit}
            className="text-sm font-medium text-slate-600 hover:text-slate-900"
          >
            {org.name} — {t('dashboard.workspaces')}
          </button>
          <div className="flex gap-1">
            <NavBtn active={section === 'home'} onClick={() => onSectionChange('home')} label={t('ws.home')} />
            <NavBtn active={section === 'newTransaction'} onClick={() => onSectionChange('newTransaction')} label={t('ws.newTransaction')} />
            <NavBtn active={section === 'journal'} onClick={() => onSectionChange('journal')} label={t('ws.journal')} />
            <NavBtn active={section === 'cashbook'} onClick={() => onSectionChange('cashbook')} label={t('ws.cashbook')} />
            <NavBtn active={section === 'ledger'} onClick={() => onSectionChange('ledger')} label={t('ws.ledger')} />
            <NavBtn active={section === 'accounts'} onClick={() => onSectionChange('accounts')} label={t('ws.accounts')} />
          </div>
        </div>
      </nav>
      <main>
        {section === 'home' && (
          <OrgHome
            org={org}
            onAccounts={() => onSectionChange('accounts')}
            onNewTransaction={() => onSectionChange('newTransaction')}
            onJournal={() => onSectionChange('journal')}
            onCashBook={() => onSectionChange('cashbook')}
            onLedger={() => onSectionChange('ledger')}
          />
        )}
        {section === 'accounts' && (
          <ChartOfAccountsPage org={org} onBack={() => onSectionChange('home')} />
        )}
        {section === 'newTransaction' && (
          <NewTransactionPage org={org} onBack={() => onSectionChange('home')} />
        )}
        {section === 'journal' && (
          <JournalPage org={org} onBack={() => onSectionChange('home')} />
        )}
        {section === 'cashbook' && (
          <CashBookPage org={org} onBack={() => onSectionChange('home')} />
        )}
        {section === 'ledger' && (
          <GeneralLedgerPage org={org} onBack={() => onSectionChange('home')} />
        )}
      </main>
    </div>
  )
}

function OrgHome({ org, onAccounts, onNewTransaction, onJournal, onCashBook, onLedger }) {
  const { t } = useLanguage()
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h2 className="text-2xl font-bold text-slate-900">{org.name}</h2>
      <p className="mt-1 text-sm text-slate-600">
        {t('dashboard.framework')} {org.framework} · {t('dashboard.currency')} {org.currency}
      </p>
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <BigCard
          title={t('ws.newTransactionTitle')}
          desc={t('ws.newTransactionDesc')}
          action={t('ws.newTransaction')}
          onClick={onNewTransaction}
        />
        <BigCard
          title={t('ws.journalTitle')}
          desc={t('ws.journalDesc')}
          action={t('ws.journal')}
          onClick={onJournal}
        />
        <BigCard
          title={t('ws.cashbookTitle')}
          desc={t('ws.cashbookDesc')}
          action={t('ws.cashbook')}
          onClick={onCashBook}
        />
        <BigCard
          title={t('ws.ledgerTitle')}
          desc={t('ws.ledgerDesc')}
          action={t('ws.ledger')}
          onClick={onLedger}
        />
        <BigCard
          title={t('ws.accountsTitle')}
          desc={t('ws.accountsDesc')}
          action={t('ws.accounts')}
          onClick={onAccounts}
        />
      </div>
    </div>
  )
}

function BigCard({ title, desc, action, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm hover:border-blue-300"
    >
      <h3 className="font-semibold text-slate-900">{title}</h3>
      <p className="mt-1 text-sm text-slate-600">{desc}</p>
      <span className="mt-3 inline-block text-sm font-medium text-blue-600">{action} →</span>
    </button>
  )
}
