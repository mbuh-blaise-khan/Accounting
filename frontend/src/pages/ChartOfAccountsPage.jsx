// Chart of Accounts page: grouped by account class, searchable, with create /
// edit / deactivate for custom accounts. Uses plain-language labels (not just
// codes) so a non-accountant can read it.
import { useEffect, useMemo, useState } from 'react'
import {
  createAccount,
  fetchAccounts,
  updateAccount,
} from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'

const CLASS_ORDER = ['asset', 'liability', 'equity', 'revenue', 'expense']
const INPUT_CLS =
  'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none'
const LABEL_CLS = 'block text-sm font-medium text-slate-700'

export default function ChartOfAccountsPage({ org, onBack }) {
  const { t, lang } = useLanguage()
  const [accounts, setAccounts] = useState(null) // null = loading
  const [search, setSearch] = useState('')
  const [error, setError] = useState(null)
  const [showCreate, setShowCreate] = useState(false)
  const [editing, setEditing] = useState(null)

  async function load() {
    setError(null)
    try {
      setAccounts(await fetchAccounts(org.id))
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [org.id])

  const filtered = useMemo(() => {
    if (!accounts) return []
    const q = search.trim().toLowerCase()
    if (!q) return accounts
    return accounts.filter(
      (a) =>
        a.code.toLowerCase().includes(q) ||
        a.name_en.toLowerCase().includes(q) ||
        a.name_fr.toLowerCase().includes(q)
    )
  }, [accounts, search])

  const grouped = useMemo(() => {
    const map = {}
    for (const c of CLASS_ORDER) map[c] = []
    for (const a of filtered) (map[a.account_class] ||= []).push(a)
    return map
  }, [filtered])

  async function handleSave(payload) {
    setError(null)
    try {
      await createAccount(payload)
      setShowCreate(false)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleUpdate(id, payload) {
    setError(null)
    try {
      await updateAccount(id, org.id, payload)
      setEditing(null)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const count = accounts ? `${accounts.length} ${t('coa.accounts')}` : t('common.loading')

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto w-full max-w-3xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <button
              type="button"
              onClick={onBack}
              className="mb-2 text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              ← {t('coa.back')}
            </button>
            <h2 className="text-xl font-bold text-slate-900">{t('coa.title')}</h2>
            <p className="mt-1 text-sm text-slate-600">
              {org.name} · {t('coa.framework')} {org.framework} · {org.currency}
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            + {t('coa.addAccount')}
          </button>
        </div>

        <p className="mt-4 rounded-lg bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-800">
          {t('coa.demoNotice')}
        </p>

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}

        <div className="mt-4">
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('coa.searchPlaceholder')}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </div>

        {showCreate && (
          <CreateAccountForm org={org} onSave={handleSave} onCancel={() => setShowCreate(false)} />
        )}

        {accounts === null ? (
          <p className="mt-10 text-center text-slate-500">{t('common.loading')}</p>
        ) : (
          <>
            <p className="mt-6 text-sm text-slate-500">{count}</p>
            {CLASS_ORDER.filter((c) => (grouped[c] || []).length > 0).map((cls) => (
              <section key={cls} className="mt-6">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                  {t(`coa.class.${cls}`)}
                </h3>
                <ul className="mt-2 space-y-2">
                  {grouped[cls].map((a) => (
                    <li
                      key={a.id}
                      className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
                    >
                      {editing === a.id ? (
                        <EditAccountForm
                          account={a}
                          onSave={handleUpdate}
                          onCancel={() => setEditing(null)}
                        />
                      ) : (
                        <AccountRow
                          account={a}
                          lang={lang}
                          onEdit={() => setEditing(a.id)}
                          onToggleActive={(active) => handleUpdate(a.id, { active })}
                          t={t}
                        />
                      )}
                    </li>
                  ))}
                </ul>
              </section>
            ))}
            {filtered.length === 0 && (
              <p className="mt-8 text-center text-slate-500">{t('coa.noResults')}</p>
            )}
          </>
        )}
      </div>
    </div>
  )
}

function CreateAccountForm({ org, onSave, onCancel }) {
  const { t } = useLanguage()
  const [form, setForm] = useState({
    code: '',
    name_en: '',
    name_fr: '',
    account_class: 'asset',
    normal_balance: 'debit',
    description: '',
  })

  function set(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  // Keep normal_balance sensible for the chosen class, but let the user change
  // it — the backend still validates it.
  function onClassChange(value) {
    set('account_class', value)
    set('normal_balance', value === 'asset' || value === 'expense' ? 'debit' : 'credit')
  }

  function handleSubmit(e) {
    e.preventDefault()
    onSave({ ...form, organization_id: org.id, framework: org.framework })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mt-6 rounded-xl border border-blue-200 bg-blue-50 p-4 space-y-4"
    >
      <h4 className="font-semibold text-slate-900">{t('coa.createTitle')}</h4>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.code')}</span>
          <input required value={form.code} onChange={(e) => set('code', e.target.value)} className={INPUT_CLS} />
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.class')}</span>
          <select value={form.account_class} onChange={(e) => onClassChange(e.target.value)} className={INPUT_CLS}>
            {CLASS_ORDER.map((c) => (
              <option key={c} value={c}>{t(`coa.class.${c}`)}</option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.nameEn')}</span>
          <input required value={form.name_en} onChange={(e) => set('name_en', e.target.value)} className={INPUT_CLS} />
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.nameFr')}</span>
          <input required value={form.name_fr} onChange={(e) => set('name_fr', e.target.value)} className={INPUT_CLS} />
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.balanceLabel')}</span>
          <select value={form.normal_balance} onChange={(e) => set('normal_balance', e.target.value)} className={INPUT_CLS}>
            <option value="debit">{t('coa.balance.debit')}</option>
            <option value="credit">{t('coa.balance.credit')}</option>
          </select>
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.description')}</span>
          <input value={form.description} onChange={(e) => set('description', e.target.value)} className={INPUT_CLS} />
        </label>
      </div>
      <div className="flex items-center justify-end gap-2">
        <button type="button" onClick={onCancel} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100">
          {t('coa.cancel')}
        </button>
        <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
          {t('coa.create')}
        </button>
      </div>
    </form>
  )
}
function AccountRow({ account, lang, onEdit, onToggleActive, t }) {
  const name = lang === 'fr' ? account.name_fr : account.name_en

  return (
    <div className="flex flex-wrap items-center justify-between gap-2">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-xs font-semibold text-slate-700">
            {account.code}
          </span>
          <span className="font-semibold text-slate-900">{name}</span>
          {!account.active && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
              {t('coa.inactive')}
            </span>
          )}
          {account.is_system_default && (
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500">
              {t('coa.system')}
            </span>
          )}
        </div>
        <p className="mt-1 text-xs text-slate-500">
          {t(`coa.balance.${account.normal_balance}`)} ·{' '}
          {account.description || t('coa.noDescription')}
        </p>
      </div>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onEdit}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
        >
          {t('coa.edit')}
        </button>
        <button
          type="button"
          onClick={() => onToggleActive(!account.active)}
          className={
            account.active
              ? 'rounded-lg border border-red-300 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50'
              : 'rounded-lg border border-green-300 px-3 py-1.5 text-sm font-medium text-green-700 hover:bg-green-50'
          }
        >
          {account.active ? t('coa.deactivate') : t('coa.activate')}
        </button>
      </div>
    </div>
  )
}

function EditAccountForm({ account, onSave, onCancel }) {
  const { t } = useLanguage()
  const [form, setForm] = useState({
    name_en: account.name_en,
    name_fr: account.name_fr,
  })

  function handleSubmit(e) {
    e.preventDefault()
    onSave(account.id, form)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.nameEn')}</span>
          <input
            value={form.name_en}
            onChange={(e) => setForm((p) => ({ ...p, name_en: e.target.value }))}
            className={INPUT_CLS}
          />
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.nameFr')}</span>
          <input
            value={form.name_fr}
            onChange={(e) => setForm((p) => ({ ...p, name_fr: e.target.value }))}
            className={INPUT_CLS}
          />
        </label>
      </div>
      <div className="flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
        >
          {t('coa.cancel')}
        </button>
        <button
          type="submit"
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          {t('coa.save')}
        </button>
      </div>
    </form>
  )
}
