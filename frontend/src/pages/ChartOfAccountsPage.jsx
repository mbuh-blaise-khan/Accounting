// Chart of Accounts page (Session 6b).
// Hierarchical tree view grouped by parent_account_id (indented by depth),
// with OHADA class badges + real class numbers for OHADA workspaces, an
// AccountLookup (code <-> name, within-org) in the create flow, and a
// framework-aware demo notice. OHADA rows are the real SYSCOHADA 2017 révisé
// structure; IFRS rows are an editable starting template. Plain-language
// labels keep it readable for a non-accountant.
import { useEffect, useMemo, useState } from 'react'
import {
  createAccount,
  fetchAccounts,
  updateAccount,
} from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'
import AccountLookup from '../components/AccountLookup.jsx'

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
  const [editing, setEditing] = useState(null) // account object

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

  // Client-side search over the (org-scoped) chart — matches code or names.
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

  // Legacy Session-5 flat chart check: OHADA workspaces whose seed accounts
  // lack ohada_class_number are the old illustrative set.
  const isLegacy =
    org.framework === 'OHADA' &&
    !!accounts &&
    accounts.some((a) => a.is_system_default && a.ohada_class_number == null)

  function demoNoticeKey() {
    if (isLegacy) return 'coa.demoNoticeLegacy'
    if (org.framework === 'OHADA') return 'coa.demoNoticeOhada'
    return 'coa.demoNoticeIfrs'
  }

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

  const count = accounts
    ? `${accounts.length} ${t('coa.accounts')}`
    : t('common.loading')

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

        <p className="mt-3 text-xs text-slate-500">{t(demoNoticeKey())}</p>
        <p className="mt-1 text-sm text-slate-500">{count}</p>

        <div className="mt-3">
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('coa.searchPlaceholder')}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </div>

        {showCreate && (
          <CreateAccountForm
            org={org}
            allAccounts={accounts}
            onSave={handleSave}
            onCancel={() => setShowCreate(false)}
          />
        )}

        {editing && (
          <EditAccountForm
            account={editing}
            onSave={handleUpdate}
            onCancel={() => setEditing(null)}
          />
        )}

        {accounts === null ? (
          <p className="mt-10 text-center text-slate-500">{t('common.loading')}</p>
        ) : (
          <div className="mt-4 space-y-1">
            <AccountTree
              accounts={filtered}
              lang={lang}
              onEdit={(a) => setEditing(a)}
              onToggleActive={(a) =>
                handleUpdate(a.id, { active: !a.active })
              }
            />
            {filtered.length === 0 && (
              <p className="mt-8 text-center text-slate-500">
                {t('coa.noResults')}
              </p>
            )}
          </div>
        )}

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}
      </div>
    </div>
  )
}

// Hierarchical tree: render roots (no parent) then descendants, indented by
// depth. OHADA sub-accounts (101, 1011, ...) nest under their 2-digit parent.
function AccountTree({ accounts, lang, onEdit, onToggleActive }) {
  const children = new Map()
  const roots = []
  for (const a of accounts) {
    if (a.parent_account_id == null) roots.push(a)
    else {
      const list = children.get(a.parent_account_id) || []
      list.push(a)
      children.set(a.parent_account_id, list)
    }
  }
  const sort = (a, b) =>
    a.code.localeCompare(b.code, undefined, { numeric: true })
  roots.sort(sort)
  for (const list of children.values()) list.sort(sort)

  function render(node, depth) {
    const kids = children.get(node.id)
    return [
      <TreeNode
        key={node.id}
        account={node}
        depth={depth}
        lang={lang}
        onEdit={() => onEdit(node)}
        onToggleActive={onToggleActive}
      />,
      ...(kids ? kids.flatMap((k) => render(k, depth + 1)) : []),
    ]
  }

  if (roots.length === 0) return null
  return <>{roots.flatMap((r) => render(r, 0))}</>
}

function TreeNode({ account, depth, onEdit, onToggleActive, lang }) {
  const { t } = useLanguage()
  const name = lang === 'fr' ? account.name_fr : account.name_en

  return (
    <div
      className="border-l-2 border-slate-100 py-1"
      style={{ paddingLeft: `${depth * 1.25 + 0.5}rem` }}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-xs font-semibold text-slate-700">
              {account.code}
            </span>
            {account.ohada_class_number != null && (
              <span
                className="rounded bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-800"
                title={`${t('coa.ohadaClass')} ${account.ohada_class_number}`}
              >
                {t('coa.ohadaClass')} {account.ohada_class_number}
              </span>
            )}
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
            {!account.is_system_default && (
              <span className="rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-700">
                Custom
              </span>
            )}
          </div>
          <p className="mt-0.5 text-xs text-slate-500">
            {t(`coa.balance.${account.normal_balance}`)} ·{' '}
            {account.description || t('coa.noDescription')}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => onEdit(account)}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
          >
            {t('coa.edit')}
          </button>
          <button
            type="button"
            onClick={() => onToggleActive(account)}
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
    </div>
  )
}

// Create form wires AccountLookup so the user can search by code OR name and
// auto-fill the parent + names (bidirectional code <-> name, within-org only).
function CreateAccountForm({ org, allAccounts, onSave, onCancel }) {
  const { t } = useLanguage()
  const [form, setForm] = useState({
    code: '',
    name_en: '',
    name_fr: '',
    account_class: 'asset',
    normal_balance: 'debit',
    parent_account_id: null,
    ohada_class_number: org.framework === 'OHADA' ? 1 : null,
    description: '',
  })

  function set(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function onClassChange(value) {
    set('account_class', value)
    set(
      'normal_balance',
      value === 'asset' || value === 'expense' ? 'debit' : 'credit'
    )
  }

  function onParentSelect(parent) {
    set('parent_account_id', parent.id)
    // Pre-fill names from the picked account so the user can copy / adapt.
    set('name_en', parent.name_en)
    set('name_fr', parent.name_fr)
    set(
      'ohada_class_number',
      parent.ohada_class_number ??
        (org.framework === 'OHADA' ? 1 : null)
    )
  }

  function handleSubmit(e) {
    e.preventDefault()
    onSave({
      ...form,
      organization_id: org.id,
      framework: org.framework,
    })
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
          <input
            required
            value={form.code}
            onChange={(e) => set('code', e.target.value)}
            className={INPUT_CLS}
            placeholder={org.framework === 'OHADA' ? '1011' : '1300'}
          />
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.chooseParent')}</span>
          <AccountLookup
            accounts={allAccounts || []}
            value={
              form.parent_account_id
                ? allAccounts?.find((a) => a.id === form.parent_account_id)
                : null
            }
            onChange={onParentSelect}
            placeholder={t('coa.chooseParent')}
          />
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.nameEn')}</span>
          <input
            required
            value={form.name_en}
            onChange={(e) => set('name_en', e.target.value)}
            className={INPUT_CLS}
          />
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.nameFr')}</span>
          <input
            required
            value={form.name_fr}
            onChange={(e) => set('name_fr', e.target.value)}
            className={INPUT_CLS}
          />
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.class')}</span>
          <select
            value={form.account_class}
            onChange={(e) => onClassChange(e.target.value)}
            className={INPUT_CLS}
          >
            {CLASS_ORDER.map((c) => (
              <option key={c} value={c}>
                {t(`coa.class.${c}`)}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('coa.balanceLabel')}</span>
          <select
            value={form.normal_balance}
            onChange={(e) => set('normal_balance', e.target.value)}
            className={INPUT_CLS}
          >
            <option value="debit">{t('coa.balance.debit')}</option>
            <option value="credit">{t('coa.balance.credit')}</option>
          </select>
        </label>
        {org.framework === 'OHADA' && (
          <label className="block">
            <span className={LABEL_CLS}>{t('coa.ohadaClass')}</span>
            <select
              value={form.ohada_class_number}
              onChange={(e) =>
                set(
                  'ohada_class_number',
                  e.target.value ? Number(e.target.value) : null
                )
              }
              className={INPUT_CLS}
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => (
                <option key={n} value={n}>
                  {n} — {t(`coa.ohadaClass${n}`)}
                </option>
              ))}
            </select>
          </label>
        )}
        <label className="block sm:col-span-2">
          <span className={LABEL_CLS}>{t('coa.description')}</span>
          <input
            value={form.description}
            onChange={(e) => set('description', e.target.value)}
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
          {t('coa.create')}
        </button>
      </div>
    </form>
  )
}

// Edit form: only plain-language names (structural fields are locked per the
// API/schema — AccountUpdate only allows name_en/name_fr/active).
function EditAccountForm({ account, onSave, onCancel }) {
  const { t } = useLanguage()
  const [form, setForm] = useState({
    name_en: account.name_en,
    name_fr: account.name_fr,
    active: account.active,
  })

  function handleSubmit(e) {
    e.preventDefault()
    onSave(account.id, form)
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 space-y-3">
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h4 className="mb-3 font-semibold text-slate-900">{t('coa.edit')}</h4>
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
          <label className="block sm:col-span-2 flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.active}
              onChange={(e) =>
                setForm((p) => ({ ...p, active: e.target.checked }))
              }
              className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
            />
            <span className={LABEL_CLS}>
              {form.active ? t('coa.active') : t('coa.inactive')}
            </span>
          </label>
        </div>
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
