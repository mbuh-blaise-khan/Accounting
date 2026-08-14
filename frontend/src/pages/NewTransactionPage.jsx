// Beginner-friendly "New Transaction" flow:
// 1. Describe what happened in plain language.
// 2. Pick accounts + amounts (debit or credit per line).
// 3. Review the resulting debit/credit lines.
// 4. Confirm posting, then read a plain-language "what it means" explanation.
import { useEffect, useState } from 'react'
import {
  createTransaction,
  fetchAccounts,
  postTransaction,
} from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'

let lineSeq = 0
const INPUT_CLS =
  'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none'
const LABEL_CLS = 'block text-sm font-medium text-slate-700'

function newLine() {
  lineSeq += 1
  return { id: lineSeq, account_id: '', side: 'debit', amount: '' }
}

export default function NewTransactionPage({ org, onBack }) {
  const { t, lang } = useLanguage()
  const [accounts, setAccounts] = useState([])
  const [description, setDescription] = useState('')
  const [lines, setLines] = useState([newLine(), newLine()])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [posted, setPosted] = useState(null)

  useEffect(() => {
    let active = true
    fetchAccounts(org.id)
      .then((list) => active && setAccounts(list))
      .catch((err) => active && setError(err.message))
    return () => {
      active = false
    }
  }, [org.id])

  function nameOf(a) {
    return lang === 'fr' ? a.name_fr : a.name_en
  }

  function updateLine(id, patch) {
    setLines((prev) => prev.map((l) => (l.id === id ? { ...l, ...patch } : l)))
  }

  function addLine() {
    setLines((prev) => [...prev, newLine()])
  }

  function removeLine(id) {
    if (lines.length <= 2) return
    setLines((prev) => prev.filter((l) => l.id !== id))
  }

  const totalDebit = lines.reduce(
    (sum, l) => (l.side === 'debit' ? sum + (Number(l.amount) || 0) : sum),
    0
  )
  const totalCredit = lines.reduce(
    (sum, l) => (l.side === 'credit' ? sum + (Number(l.amount) || 0) : sum),
    0
  )
  const balanced = totalDebit === totalCredit && lines.length >= 2

  function canPost() {
    if (!description.trim()) return false
    if (lines.length < 2) return false
    if (!lines.every((l) => l.account_id && Number(l.amount) > 0)) return false
    return balanced
  }

  async function handlePost() {
    setError(null)
    setBusy(true)
    try {
      const payload = {
        organization_id: org.id,
        description: description.trim(),
        lines: lines.map((l) => ({
          account_id: l.account_id,
          debit: l.side === 'debit' ? Number(l.amount) : 0,
          credit: l.side === 'credit' ? Number(l.amount) : 0,
        })),
      }
      const draft = await createTransaction(payload)
      const result = await postTransaction(org.id, draft.id)
      setPosted(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  function reset() {
    setDescription('')
    setLines([newLine(), newLine()])
    setPosted(null)
    setError(null)
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
      <div className="mx-auto w-full max-w-2xl">
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

        <div className="mt-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <label className="block">
            <span className={LABEL_CLS}>{t('tx.description')}</span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              placeholder={t('tx.descriptionPlaceholder')}
              className={INPUT_CLS}
            />
          </label>
        </div>

        <div className="mt-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
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

          <div className="mt-3 space-y-3">
            {lines.map((line) => (
              <LineRow
                key={line.id}
                line={line}
                accounts={accounts}
                nameOf={nameOf}
                onChange={updateLine}
                onRemove={removeLine}
                canRemove={lines.length > 2}
                t={t}
              />
            ))}
          </div>

          <div className="mt-4 rounded-lg bg-slate-50 border border-slate-200 p-3 text-sm">
            <p className="font-semibold text-slate-700">{t('tx.totals')}</p>
            <p className="mt-1 text-slate-600">
              {t('tx.totalDebit')}:{' '}
              <span className="font-medium">{totalDebit.toLocaleString()} {org.currency}</span> ·{' '}
              {t('tx.totalCredit')}:{' '}
              <span className="font-medium">{totalCredit.toLocaleString()} {org.currency}</span>
            </p>
            <p className={balanced ? 'mt-1 font-medium text-green-700' : 'mt-1 font-medium text-amber-700'}>
              {balanced ? t('tx.balanced') : t('tx.unbalanced')}
            </p>
          </div>
        </div>

        <div className="mt-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-slate-900">{t('tx.review')}</h3>
          <ul className="mt-2 space-y-1 text-sm">
            {lines.map((l) => {
              const acct = accounts.find((a) => a.id === l.account_id)
              return (
                <li key={l.id} className="flex justify-between">
                  <span className="text-slate-700">{acct ? `${acct.code} ${nameOf(acct)}` : '—'}</span>
                  <span className={l.side === 'debit' ? 'font-medium text-red-700' : 'font-medium text-green-700'}>
                    {t(l.side === 'debit' ? 'tx.debit' : 'tx.credit')} {Number(l.amount) || 0}
                  </span>
                </li>
              )
            })}
          </ul>
        </div>

        <button
          type="button"
          disabled={!canPost() || busy}
          onClick={handlePost}
          className="mt-5 w-full rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {busy ? t('tx.posting') : t('tx.post')}
        </button>
        {!canPost() && !busy && (
          <p className="mt-2 text-center text-xs text-slate-500">{t('tx.postHint')}</p>
        )}
      </div>
    </div>
  )
}
function LineRow({ line, accounts, nameOf, onChange, onRemove, canRemove, t }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="block">
          <span className={LABEL_CLS}>{t('tx.account')}</span>
          <select
            value={line.account_id}
            onChange={(e) => onChange(line.id, { account_id: e.target.value })}
            className={INPUT_CLS}
          >
            <option value="">{t('tx.chooseAccount')}</option>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.code} — {nameOf(a)}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className={LABEL_CLS}>{t('tx.amount')}</span>
          <input
            type="number"
            min="0"
            step="1"
            value={line.amount}
            onChange={(e) => onChange(line.id, { amount: e.target.value })}
            className={INPUT_CLS}
            placeholder="0"
          />
        </label>
      </div>
      <div className="mt-3 flex items-center justify-between">
        <div className="flex gap-4">
          <label className="flex items-center text-sm text-slate-700">
            <input
              type="radio"
              name={`side-${line.id}`}
              checked={line.side === 'debit'}
              onChange={() => onChange(line.id, { side: 'debit' })}
              className="mr-1"
            />
            {t('tx.debit')}
          </label>
          <label className="flex items-center text-sm text-slate-700">
            <input
              type="radio"
              name={`side-${line.id}`}
              checked={line.side === 'credit'}
              onChange={() => onChange(line.id, { side: 'credit' })}
              className="mr-1"
            />
            {t('tx.credit')}
          </label>
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
    const amount = Number(side === 'debit' ? line.debit_amount : line.credit_amount)
    return {
      label: `${acct.code} ${nameOf(acct)}`,
      side,
      amount,
      effect: increasing ? t('tx.increased') : t('tx.decreased'),
    }
  }

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
          <h2 className="text-lg font-bold text-green-900">✓ {t('tx.posted')}</h2>
          <p className="mt-1 text-sm text-green-800">
            {t('tx.balanceVerified')} — {org.currency}
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
                  <span className="font-medium">{e.label}</span> — {t(`tx.${e.side}`)}{' '}
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