// OHADA journal-entry grid form (Session 6c).
//
// Matches the standard journal layout:
//   Date | N° compte | Intitulé du compte | Libellé | Débit | Crédit
// Debit lines come first, then credit lines, and total debits must equal total
// credits before posting (enforced at the service layer too, unchanged from
// Session 6).
//
// Bug fixed: the Session 6 form used a plain <select> that was never upgraded
// to the Session 6b AccountLookup autocomplete. After the 6b account-model
// changes (real OHADA hierarchy with ohada_class_number), that plain select
// showed accounts without search or hierarchy support and degraded to an
// effectively empty/unusable dropdown for non-trivial charts. This form now
// reuses AccountLookup (compact mode) everywhere.
//
// Note: the backend Transaction model has no user-editable date column (it
// uses created_at). The date field here is a UI-only field for journal
// presentation; adding a transaction_date column is deferred to a future
// session (schema change is out of scope per the task brief).
import { useEffect, useMemo, useState } from 'react'
import {
  createTransaction,
  fetchAccounts,
  postTransaction,
} from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'
import AccountLookup from '../components/AccountLookup.jsx'
import {
  canPost,
  isBalanced,
  sumLines,
  toPayload,
  validatePost,
} from '../utils/txnCalculations.js'

const INPUT_CLS =
  'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none'
const LABEL_CLS = 'block text-sm font-medium text-slate-700'

let lineSeq = 0
function newLine() {
  lineSeq += 1
  return {
    id: lineSeq,
    account_id: '',
    account: null, // full account object, for display
    libelle: '', // per-line narration (French accounting term for the description column)
    debit: '',
    credit: '',
  }
}

function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export default function NewTransactionPage({ org, onBack }) {
  const { t, lang } = useLanguage()
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [date, setDate] = useState(todayISO())
  const [description, setDescription] = useState('')
  const [lines, setLines] = useState([newLine(), newLine()])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [errors, setErrors] = useState(null) // { ok, descriptionError, lineErrors, balanceError }
  const [posted, setPosted] = useState(null)

  useEffect(() => {
    let active = true
    setLoading(true)
    fetchAccounts(org.id)
      .then((list) => {
        if (active) {
          setAccounts(list)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (active) {
          setError(err.message)
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [org.id])

  // Only active accounts are selectable for new lines — the backend rejects
  // inactive accounts at draft-creation time.
  const activeAccounts = useMemo(
    () => accounts.filter((a) => a.active),
    [accounts]
  )

  function nameOf(a) {
    return lang === 'fr' ? a.name_fr : a.name_en
  }

  function updateLine(id, patch) {
    setLines((prev) =>
      prev.map((l) => (l.id === id ? { ...l, ...patch } : l))
    )
  }

  function addLine() {
    setLines((prev) => [...prev, newLine()])
  }

  function removeLine(id) {
    if (lines.length <= 2) return
    setLines((prev) => prev.filter((l) => l.id !== id))
  }

  const { totalDebit, totalCredit } = sumLines(lines)
  const balanced = isBalanced(lines)
  const ready = canPost(description, lines)

  async function handlePost() {
    setError(null)
    setBusy(true)
    try {
      const payload = toPayload(description, lines, org.id)
      const draft = await createTransaction(payload)
      const result = await postTransaction(org.id, draft.id)
      setPosted(result)
      setErrors(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  // Post gate (Part F): validate required fields FIRST and surface WHICH ones
  // are missing inline. A line with no account or no amount blocks the post
  // even if what remains happens to balance — this is about explicit field
  // completion, not balance (balance is still checked separately after).
  function attemptPost() {
    const result = validatePost(description, lines)
    setErrors(result)
    if (result.ok) handlePost()
  }

  function reset() {
    setDescription('')
    setLines([newLine(), newLine()])
    setDate(todayISO())
    setPosted(null)
    setError(null)
    setErrors(null)
  }

  if (posted) {
    return (
      <PostedExplanation
        org={org}
        result={posted}
        accounts={accounts}
        nameOf={nameOf}
        onBack={onBack}
        onNewEntry={reset}
        t={t}
      />
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto w-full max-w-4xl">
        <button
          type="button"
          onClick={onBack}
          className="mb-2 text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          ← {t('tx.backToOrg')}
        </button>
        <h2 className="text-xl font-bold text-slate-900">{t('tx.title')}</h2>
        <p className="mt-1 text-sm text-slate-600">
          {org.name} · {org.currency}
        </p>

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}

        {/* Step 1: What happened? (plain language) — Part C: modernized
            description field with clearer hierarchy and spacing. */}
        <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <label className="block">
            <span className="block text-base font-semibold text-slate-900">
              {t('tx.description')}
            </span>
            <span className="mt-1 block text-sm text-slate-500">
              {t('tx.descriptionHint')}
            </span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder={t('tx.descriptionPlaceholder')}
              className="mt-3 w-full resize-y rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-base text-slate-900 placeholder-slate-400 transition focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <p className="mt-2 text-right text-xs text-slate-400">
            {description.trim().length} {t('tx.characters')}
          </p>
          {errors?.descriptionError && (
            <p className="mt-2 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
              {t('tx.errDescription')}
            </p>
          )}
        </div>

        {/* Step 2: Date (journal entry date; UI-only for now) */}
        <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:max-w-xs">
          <label className="block">
            <span className={LABEL_CLS}>{t('tx.date')}</span>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className={INPUT_CLS}
            />
          </label>
        </div>

        {/* Step 3: Journal grid (Date | Account | Name | Libellé | Débit | Crédit) */}
        <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">{t('tx.lines')}</h3>
            <button
              type="button"
              onClick={addLine}
              className="rounded-lg border border-blue-600 px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50"
            >
              + {t('tx.addLine')}
            </button>
          </div>

          {/* Desktop column header — always rendered so rows added via the
              "+ Add a line" button are immediately visible (Part A bug 3: the
              grid used to be hidden behind the loading/no-accounts branch,
              making the button look dead). */}
          <div
            className={`mt-3 hidden border-b border-slate-200 pb-2 text-xs font-semibold uppercase text-slate-500 sm:grid sm:gap-2 ${
              org.framework === 'OHADA'
                ? 'sm:grid-cols-12'
                : 'sm:grid-cols-9'
            }`}
          >
            {org.framework === 'OHADA' && (
              <div className="col-span-4">{t('tx.account')}</div>
            )}
            <div className={org.framework === 'OHADA' ? 'col-span-3' : 'col-span-4'}>
              {t('tx.accountName')}
            </div>
            <div className={org.framework === 'OHADA' ? 'col-span-3' : 'col-span-3'}>
              {t('tx.libelle')}
            </div>
            <div className="col-span-1">{t('tx.debitCol')}</div>
            <div className="col-span-1">{t('tx.creditCol')}</div>
          </div>

          <div className="mt-2 space-y-3">
            {lines.map((line) => (
              <LineRow
                key={line.id}
                line={line}
                accounts={activeAccounts}
                framework={org.framework}
                nameOf={nameOf}
                onChange={updateLine}
                onRemove={removeLine}
                canRemove={lines.length > 2}
                t={t}
                errorKey={errors?.lineErrors?.[line.id]}
              />
            ))}
          </div>

          {/* Inline notice: rows are still editable/visible while the account
              list loads, or if the chart is empty (create accounts first). */}
          {loading && (
            <p className="mt-3 text-sm text-slate-500">{t('common.loading')}</p>
          )}
          {!loading && activeAccounts.length === 0 && (
            <p className="mt-3 text-sm text-slate-500">{t('tx.noAccounts')}</p>
          )}

          {/* Running totals + balance indicator */}
          <div className="mt-4 rounded-lg bg-slate-50 border border-slate-200 p-3 text-sm">
            <p className="font-semibold text-slate-700">{t('tx.totals')}</p>
            <p className="mt-1 text-slate-600">
              {t('tx.totalDebit')}:{' '}
              <span className="font-medium">
                {totalDebit.toLocaleString()} {org.currency}
              </span>
              {' · '}
              {t('tx.totalCredit')}:{' '}
              <span className="font-medium">
                {totalCredit.toLocaleString()} {org.currency}
              </span>
            </p>
            <p
              className={`mt-1 font-medium ${
                balanced ? 'text-green-700' : 'text-amber-700'
              }`}
            >
              {balanced ? t('tx.balanced') : t('tx.unbalanced')}
            </p>
          </div>
        </div>

        {/* Post button — click runs attemptPost which validates required fields
            FIRST and surfaces WHICH are missing inline (Part F), then posts. */}
        <button
          type="button"
          disabled={!ready || busy}
          onClick={attemptPost}
          className="mt-5 w-full rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {busy ? t('tx.posting') : t('tx.post')}
        </button>
        {!ready && !busy && (
          <p className="mt-2 text-center text-xs text-slate-500">
            {t('tx.postHint')}
          </p>
        )}
      </div>
    </div>
  )
}

// A single journal-entry grid row. Desktop uses a 12-col (OHADA) or 9-col
// (IFRS) grid aligned with the header; mobile stacks the fields into a card.
//
// Part B: IFRS workspaces have no account codes, so the row is
//   Account (name lookup) | Libellé | Débit | Crédit
// while OHADA keeps the classic journal layout
//   Account (code lookup) | Account name | Libellé | Débit | Crédit.
function LineRow({ line, accounts, framework = 'OHADA', nameOf, onChange, onRemove, canRemove, t, errorKey }) {
  const selected = line.account
  const inputCls = INPUT_CLS // reuse shared input styling
  const isOhada = framework === 'OHADA'

  // Part F: inline validation message for THIS line, keyed by errorKey from
  // validatePost ('account' | 'amount' | 'bothSides' | undefined).
  function errorMsg() {
    if (errorKey === 'account') return t('tx.errAccount')
    if (errorKey === 'amount') return t('tx.errAmount')
    if (errorKey === 'bothSides') return t('tx.errBothSides')
    return null
  }
  const msg = errorMsg()

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
      {msg && (
        <p className="mb-2 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
          {msg}
        </p>
      )}
      {/* Desktop grid */}
      <div
        className={`hidden sm:grid sm:gap-2 sm:items-end ${
          isOhada ? 'sm:grid-cols-12' : 'sm:grid-cols-9'
        }`}
      >
        {/* Account (autocomplete) */}
        <div className={isOhada ? 'col-span-4' : 'col-span-4'}>
          <AccountLookup
            accounts={accounts}
            framework={framework}
            value={selected}
            onChange={(acct) =>
              onChange(line.id, { account_id: acct.id, account: acct })
            }
            placeholder={t('tx.chooseAccount')}
            compact
          />
        </div>
        {/* Account name (read-only, OHADA only — IFRS lookup already shows the
            plain name and there is no code column). */}
        {isOhada && (
          <div className="col-span-3">
            <input
              type="text"
              readOnly
              value={selected ? nameOf(selected) : ''}
              placeholder={t('tx.chooseAccount')}
              className="w-full rounded-md border border-slate-200 bg-slate-100 px-2 py-1 text-xs text-slate-500"
            />
          </div>
        )}
        {/* Libellé (per-line narration) */}
        <div className={isOhada ? 'col-span-3' : 'col-span-3'}>
          <input
            type="text"
            value={line.libelle || ''}
            onChange={(e) => onChange(line.id, { libelle: e.target.value })}
            placeholder={t('tx.libellePlaceholder')}
            className={inputCls}
          />
        </div>
        {/* Debit */}
        <div className="col-span-1">
          <input
            type="number"
            min="0"
            step="1"
            value={line.debit}
            onChange={(e) => onChange(line.id, { debit: e.target.value })}
            placeholder="0"
            className={inputCls}
          />
        </div>
        {/* Credit */}
        <div className="col-span-1">
          <input
            type="number"
            min="0"
            step="1"
            value={line.credit}
            onChange={(e) => onChange(line.id, { credit: e.target.value })}
            placeholder="0"
            className={inputCls}
          />
        </div>
        {/* Remove */}
        {canRemove && (
          <div className="col-span-12 sm:col-span-1">
            <button
              type="button"
              onClick={() => onRemove(line.id)}
              className="text-sm text-red-600 hover:text-red-700"
            >
              {t('tx.remove')}
            </button>
          </div>
        )}
      </div>

      {/* Mobile: stacked fields per line */}
      <div className="space-y-3 sm:hidden">
        {msg && (
          <p className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {msg}
          </p>
        )}
        <div>
          <span className="text-xs text-slate-500">
            {framework === 'OHADA' ? t('tx.account') : t('tx.accountName')}
          </span>
          <AccountLookup
            accounts={accounts}
            framework={framework}
            value={selected}
            onChange={(acct) =>
              onChange(line.id, { account_id: acct.id, account: acct })
            }
            placeholder={t('tx.chooseAccount')}
            compact
          />
        </div>
        <div>
          <span className="text-xs text-slate-500">{t('tx.libelle')}</span>
          <input
            type="text"
            value={line.libelle || ''}
            onChange={(e) => onChange(line.id, { libelle: e.target.value })}
            placeholder={t('tx.libellePlaceholder')}
            className={inputCls}
          />
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <span className="text-xs text-slate-500">{t('tx.debitCol')}</span>
            <input
              type="number"
              min="0"
              step="1"
              value={line.debit}
              onChange={(e) => onChange(line.id, { debit: e.target.value })}
              placeholder="0"
              className={inputCls}
            />
          </div>
          <div>
            <span className="text-xs text-slate-500">{t('tx.creditCol')}</span>
            <input
              type="number"
              min="0"
              step="1"
              value={line.credit}
              onChange={(e) => onChange(line.id, { credit: e.target.value })}
              placeholder="0"
              className={inputCls}
            />
          </div>
        </div>
        {canRemove && (
          <button
            type="button"
            onClick={() => onRemove(line.id)}
            className="text-sm text-red-600 hover:text-red-700"
          >
            {t('tx.remove')}
          </button>
        )}
      </div>
    </div>
  )
}

// After posting, show a plain-language "what happened / what this means"
// explanation using the backend response (lines come back with debit_amount /
// credit_amount and account display fields).
function PostedExplanation({ org, result, accounts, nameOf, onBack, onNewEntry, t }) {
  function sideOf(line) {
    return Number(line.debit_amount) > 0 ? 'debit' : 'credit'
  }
  function explanation(line) {
    const acct = accounts.find((a) => a.id === line.account_id)
    if (!acct) return null
    const side = sideOf(line)
    const increasing =
      (side === 'debit' && acct.normal_balance === 'debit') ||
      (side === 'credit' && acct.normal_balance === 'credit')
    const amount = Number(
      side === 'debit' ? line.debit_amount : line.credit_amount
    )
    // Part B: IFRS accounts have no code — show the plain name only.
    const codePrefix =
      org.framework === 'OHADA' && acct.code ? `${acct.code} ` : ''
    return {
      label: `${codePrefix}${nameOf(acct)}`,
      side,
      amount,
      effect: increasing ? t('tx.increased') : t('tx.decreased'),
    }
  }

  // Part C: the real posting timestamp (backend sets posted_at on posting) is
  // the FIRST date shown whenever a posted transaction is presented.
  const postedDate = result.posted_at
    ? new Date(result.posted_at).toLocaleString()
    : '—'

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto w-full max-w-2xl">
        <button
          type="button"
          onClick={onBack}
          className="mb-2 text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          ← {t('tx.backToOrg')}
        </button>

        <div className="rounded-xl border border-green-200 bg-green-50 p-5 shadow-sm">
          <h2 className="text-lg font-bold text-green-900">
            ✓ {t('tx.posted')}
          </h2>
          <p className="mt-1 text-sm text-green-800">
            {t('tx.balanceVerified')} — {org.currency}
          </p>
          <p className="mt-1 text-sm text-green-800">
            {t('journal.postedAt')}: <span className="font-medium">{postedDate}</span>
          </p>
        </div>

        <div className="mt-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-slate-900">{t('tx.whatHappened')}</h3>
          <p className="mt-1 text-sm text-slate-700">{result.description}</p>
        </div>

        <div className="mt-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-slate-900">{t('tx.whatItMeans')}</h3>
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {result.lines.map((l) => {
              const e = explanation(l)
              if (!e) return null
              return (
                <li key={l.id}>
                  <span className="font-medium">{e.label}</span> —{' '}
                  {t(`tx.${e.side}`)}{' '}
                  {e.amount.toLocaleString()} {org.currency} → {e.effect}
                </li>
              )
            })}
          </ul>
        </div>

        <div className="mt-5 flex flex-col gap-2 sm:flex-row">
          <button
            type="button"
            onClick={onNewEntry}
            className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
          >
            {t('tx.newEntry')}
          </button>
          <button
            type="button"
            onClick={onBack}
            className="flex-1 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
          >
            {t('tx.backToOrg')}
          </button>
        </div>
      </div>
    </div>
  )
}
