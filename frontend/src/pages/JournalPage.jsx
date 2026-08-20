// Journal page (Session 7): a read-only view over POSTED transactions.
// One row per transaction line: date (posted_at, FIRST — Part C), reference,
// description, account number (OHADA only), account name, debit, credit,
// narration, source, posting status, created-by/timestamp. Framework-aware:
// OHADA shows N° compte; IFRS omits the account-number column (Part B).
// Each row drills down to the originating transaction's full detail.
import { useEffect, useMemo, useState } from 'react'
import {
  fetchAccounts,
  fetchCashBook,
  fetchJournalEntries,
  fetchTransactions,
} from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'
import JournalTable from '../components/JournalTable.jsx'

export default function JournalPage({ org, onBack, cashbook = false }) {
  const { t, lang } = useLanguage()
  const [rows, setRows] = useState(null) // null = loading
  const [error, setError] = useState(null)
  const [accounts, setAccounts] = useState([])
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [accountId, setAccountId] = useState('')
  const [reference, setReference] = useState('')
  const [detail, setDetail] = useState(null) // drill-down transaction detail
  const [detailError, setDetailError] = useState(null)

  const nameOf = (a) => (lang === 'fr' ? a.name_fr : a.name_en)

  async function load() {
    setError(null)
    try {
      const params = { from, to, account_id: accountId, reference }
      const data = cashbook
        ? await fetchCashBook(org.id, params)
        : await fetchJournalEntries(org.id, params)
      setRows(data)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    setRows(null)
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [org.id, cashbook])

  useEffect(() => {
    fetchAccounts(org.id)
      .then(setAccounts)
      .catch(() => {})
  }, [org.id])

  async function openDetail(transactionId) {
    setDetailError(null)
    try {
      const txns = await fetchTransactions(org.id)
      const txn = txns.find((x) => x.id === transactionId)
      if (!txn) {
        setDetailError(t('journal.txnNotFound'))
        return
      }
      setDetail(txn)
    } catch (err) {
      setDetailError(err.message)
    }
  }

  const totalDebit = useMemo(
    () => (rows || []).reduce((s, r) => s + (Number(r.debit) || 0), 0),
    [rows]
  )
  const totalCredit = useMemo(
    () => (rows || []).reduce((s, r) => s + (Number(r.credit) || 0), 0),
    [rows]
  )

  const inputCls =
    'rounded-lg border border-slate-300 px-2 py-1.5 text-sm focus:border-blue-500 focus:outline-none'
  const labelCls = 'block text-xs font-medium text-slate-500'

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto w-full max-w-6xl">
        <button
          type="button"
          onClick={onBack}
          className="mb-2 text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          ← {t('tx.backToOrg')}
        </button>
        <h2 className="text-xl font-bold text-slate-900">
          {cashbook ? t('cashbook.title') : t('journal.title')}
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          {org.name} · {t('dashboard.framework')} {org.framework} · {org.currency}
        </p>
        <p className="mt-1 text-sm text-slate-500">
          {cashbook ? t('cashbook.subtitle') : t('journal.subtitle')}
        </p>

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}

        {/* Filters */}
        <div className="mt-5 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6">
            <label className="block">
              <span className={labelCls}>{t('journal.from')}</span>
              <input
                type="date"
                value={from}
                onChange={(e) => setFrom(e.target.value)}
                className={`mt-1 w-full ${inputCls}`}
              />
            </label>
            <label className="block">
              <span className={labelCls}>{t('journal.to')}</span>
              <input
                type="date"
                value={to}
                onChange={(e) => setTo(e.target.value)}
                className={`mt-1 w-full ${inputCls}`}
              />
            </label>
            <label className="block col-span-2 sm:col-span-1">
              <span className={labelCls}>{t('journal.account')}</span>
              <select
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                className={`mt-1 w-full ${inputCls}`}
              >
                <option value="">{t('journal.allAccounts')}</option>
                {accounts.map((a) => (
                  <option key={a.id} value={a.id}>
                    {org.framework === 'OHADA' && a.code ? `${a.code} — ` : ''}
                    {nameOf(a)}
                  </option>
                ))}
              </select>
            </label>
            <label className="block col-span-2 sm:col-span-1">
              <span className={labelCls}>{t('journal.reference')}</span>
              <input
                type="text"
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                placeholder={t('journal.referencePlaceholder')}
                className={`mt-1 w-full ${inputCls}`}
              />
            </label>
            <div className="flex items-end">
              <button
                type="button"
                onClick={load}
                className="w-full rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
              >
                {t('journal.apply')}
              </button>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="mt-4">
          {rows === null ? (
            <p className="text-center text-slate-500">{t('common.loading')}</p>
          ) : rows.length === 0 ? (
            <p className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-500">
              {t('journal.empty')}
            </p>
          ) : (
            <JournalTable
              rows={rows}
              org={org}
              nameOf={(r) =>
                lang === 'fr' ? r.account_name_fr : r.account_name_en
              }
              t={t}
              onViewTxn={openDetail}
            />
          )}
          {rows && rows.length > 0 && (
            <p className="mt-2 text-sm text-slate-500">
              {t('journal.totals')}: {t('journal.totalDebit')}{' '}
              <span className="font-medium">
                {totalDebit.toLocaleString()} {org.currency}
              </span>{' '}
              · {t('journal.totalCredit')}{' '}
              <span className="font-medium">
                {totalCredit.toLocaleString()} {org.currency}
              </span>
            </p>
          )}
        </div>

        {/* Drill-down: originating transaction detail */}
        {detailError && (
          <p className="mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {detailError}
          </p>
        )}

        {detail && (
          <TransactionDetail
            txn={detail}
            org={org}
            onClose={() => setDetail(null)}
          />
        )}
      </div>
    </div>
  )
}

// Full detail of the originating transaction (all lines, not just the rows
// shown in the current filtered view) — the drill-down target of every row.
function TransactionDetail({ txn, org, onClose }) {
  const { t, lang } = useLanguage()
  const postedDate = txn.posted_at ? new Date(txn.posted_at).toLocaleString() : '—'
  const createdDate = new Date(txn.created_at).toLocaleString()
  const isOhada = org.framework === 'OHADA'

  return (
    <div className="mt-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-slate-900">
          {t('journal.txnDetail')} · {t('journal.reference')} TX-
          {String(txn.id).padStart(4, '0')}
        </h3>
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg border border-slate-300 px-2 py-1 text-sm text-slate-600 hover:bg-slate-100"
        >
          ✕
        </button>
      </div>
      <dl className="mt-3 grid grid-cols-1 gap-2 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-xs text-slate-500">{t('journal.postedAt')}</dt>
          <dd className="font-medium text-slate-800">{postedDate}</dd>
        </div>
        <div>
          <dt className="text-xs text-slate-500">{t('journal.status')}</dt>
          <dd className="font-medium text-slate-800">{txn.status}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="text-xs text-slate-500">{t('tx.description')}</dt>
          <dd className="text-slate-800">{txn.description}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="text-xs text-slate-500">{t('journal.createdAt')}</dt>
          <dd className="text-slate-600">{createdDate}</dd>
        </div>
      </dl>
      <div className="mt-3 overflow-x-auto">
        <table className="w-full min-w-[480px] text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-xs font-semibold uppercase text-slate-500">
              {isOhada && (
                <th className="px-2 py-1">{t('journal.accountNo')}</th>
              )}
              <th className="px-2 py-1">{t('journal.accountName')}</th>
              <th className="px-2 py-1">{t('journal.narration')}</th>
              <th className="px-2 py-1 text-right">{t('journal.debit')}</th>
              <th className="px-2 py-1 text-right">{t('journal.credit')}</th>
            </tr>
          </thead>
          <tbody>
            {txn.lines.map((l) => (
              <tr key={l.id} className="border-b border-slate-100 last:border-0">
                {isOhada && (
                  <td className="px-2 py-1 font-mono text-xs text-slate-600">
                    {l.account_code || ''}
                  </td>
                )}
                <td className="px-2 py-1 text-slate-800">
                  {lang === 'fr' ? l.account_name_fr : l.account_name_en}
                </td>
                <td className="px-2 py-1 text-slate-600">{l.narration || '—'}</td>
                <td className="px-2 py-1 text-right text-slate-800">
                  {Number(l.debit_amount) > 0
                    ? Number(l.debit_amount).toLocaleString()
                    : ''}
                </td>
                <td className="px-2 py-1 text-right text-slate-800">
                  {Number(l.credit_amount) > 0
                    ? Number(l.credit_amount).toLocaleString()
                    : ''}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}