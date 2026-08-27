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
import AccountFilterSelect from '../components/AccountFilterSelect.jsx'
import TxnStatusBlock from '../components/TxnStatusBlock.jsx'
import { downloadCsv } from '../utils/csvExport.js'
import ReportHeader from '../components/ReportHeader.jsx'
import { formatReportDate, formatReportNumber, reportCsvHeader, reportPeriodLabel } from '../utils/reportPresentation.js'

export default function JournalPage({ org, onBack, cashbook = false }) {
  const { t, lang } = useLanguage()
  const [rows, setRows] = useState(null) // null = loading
  const [error, setError] = useState(null)
  const [accounts, setAccounts] = useState([])
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [accountId, setAccountId] = useState('')
  const [reference, setReference] = useState('')
  const [cashbookType, setCashbookType] = useState('double')
  const [generatedAt, setGeneratedAt] = useState(() => new Date())
  const [detail, setDetail] = useState(null) // drill-down transaction detail
  const [detailError, setDetailError] = useState(null)

  const nameOf = (a) => (lang === 'fr' ? a.name_fr : a.name_en)
  const isOhada = org.framework === 'OHADA'

  async function load() {
    setError(null)
    try {
      const params = {
        from,
        to,
        account_id: accountId,
        reference,
        ...(cashbook ? { type: cashbookType } : {}),
      }
      const data = cashbook
        ? await fetchCashBook(org.id, params)
        : await fetchJournalEntries(org.id, params)
      setRows(data)
      setGeneratedAt(new Date())
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    setRows(null)
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [org.id, cashbook, cashbookType])

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
    <div className="report-page min-h-screen bg-slate-50 px-4 py-8">
      <div className="report-content mx-auto w-full max-w-6xl">
        <div className="no-print">
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
        </div>
        <ReportHeader
          org={org}
          title={cashbook ? t('cashbook.title') : t('journal.title')}
          from={from}
          to={to}
          generatedAt={generatedAt}
          t={t}
        />

        {/* Part 3: export exactly what the current filters display */}
        <div className="no-print mt-2 flex justify-end">
          <button
            type="button"
            disabled={!rows || rows.length === 0}
            onClick={() => {
              const amountColumns = cashbook && cashbookType === 'double'
                ? [
                    { key: 'cashDebit', label: t('cashbook.cashDebit') },
                    { key: 'bankDebit', label: t('cashbook.bankDebit') },
                    { key: 'cashCredit', label: t('cashbook.cashCredit') },
                    { key: 'bankCredit', label: t('cashbook.bankCredit') },
                  ]
                : [
                    { key: 'debit', label: t('cashbook.debit') },
                    { key: 'credit', label: t('cashbook.credit') },
                  ]
              const amount = (r, key) => {
                if (key === 'debit' || key === 'credit') return Number(r[key]) || 0
                if (key === 'cashDebit') return r.cashbook_type === 'cash' ? Number(r.debit) || 0 : 0
                if (key === 'bankDebit') return r.cashbook_type === 'bank' ? Number(r.debit) || 0 : 0
                if (key === 'cashCredit') return r.cashbook_type === 'cash' ? Number(r.credit) || 0 : 0
                return r.cashbook_type === 'bank' ? Number(r.credit) || 0 : 0
              }
              downloadCsv(
                `${cashbook ? 'cash-book' : 'journal'}-${new Date().toISOString().slice(0, 10)}`,
                [
                  t('journal.date'),
                  t('journal.reference'),
                  t('journal.description'),
                  ...(isOhada ? [t('journal.accountNo')] : []),
                  t('journal.accountName'),
                  t('journal.narration'),
                  ...amountColumns.map((column) => column.label),
                  ...(!cashbook ? [t('journal.source'), t('journal.status')] : []),
                ],
                (rows || []).map((r) => [
                  r.date ? new Date(r.date).toLocaleString() : '',
                  r.reference,
                  r.description,
                  ...(isOhada ? [r.account_code || ''] : []),
                  nameOf({ name_en: r.account_name_en, name_fr: r.account_name_fr }),
                  r.narration || '',
                  ...amountColumns.map((column) => amount(r, column.key)),
                  ...(!cashbook ? [r.source, r.status] : []),
                ])
              )
            }}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
          >
            ⬇ {t('common.downloadCsv')}
          </button>
        </div>
        <p className="mt-1 text-sm text-slate-500">
          {cashbook ? t('cashbook.subtitle') : t('journal.subtitle')}
        </p>
        {cashbook && (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-slate-700">{t('cashbook.type')}</span>
            {[['single', t('cashbook.single')], ['double', t('cashbook.double')]].map(([value, label]) => (
              <button
                key={value}
                type="button"
                onClick={() => setCashbookType(value)}
                className={`rounded-lg border px-3 py-1.5 text-sm font-medium ${cashbookType === value ? 'border-blue-600 bg-blue-600 text-white' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-100'}`}
              >
                {label}
              </button>
            ))}
          </div>
        )}

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}

        {/* Filters */}
        <div className="no-print mt-5 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
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
            <label className="block col-span-2 sm:col-span-2 lg:col-span-2">
              <span className={labelCls}>{t('journal.account')}</span>
              <AccountFilterSelect
                accounts={accounts}
                framework={org.framework}
                value={accounts.find((a) => a.id === Number(accountId)) || null}
                onChange={(id) => setAccountId(id)}
                t={t}
                nameOf={nameOf}
              />
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
        <div className="report-table mt-4">
          {rows === null ? (
            <p className="text-center text-slate-500">{t('common.loading')}</p>
          ) : rows.length === 0 ? (
            <p className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-500">
              {t('journal.empty')}
              {reference && reference.trim() && (
                <>
                  {' '}
                  — <span className="font-medium">{t('journal.searchedReference')}</span>{' '}
                  <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs text-slate-700">
                    {reference.trim()}
                  </code>
                  <span className="mt-1 block text-xs text-slate-400">
                    {t('journal.referenceHint')}
                  </span>
                </>
              )}
            </p>
          ) : (
            cashbook ? (
              <CashBookTable
                rows={rows}
                org={org}
                type={cashbookType}
                nameOf={(r) => lang === 'fr' ? r.account_name_fr : r.account_name_en}
                t={t}
                onViewTxn={openDetail}
              />
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
            )
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
          <p className="no-print mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {detailError}
          </p>
        )}

        {detail && (
          <div className="no-print">
          <TransactionDetail
            txn={detail}
            org={org}
            onClose={() => setDetail(null)}
            onReversed={async () => {
              // Refresh the table AND re-read the (now reversed) original so
              // the drill-down shows its updated status immediately.
              await load()
              await openDetail(detail.id)
            }}
          />
          </div>
        )}
      </div>
    </div>
  )
}

// Full detail of the originating transaction (all lines, not just the rows
// shown in the current filtered view) — the drill-down target of every row.
function TransactionDetail({ txn, org, onClose, onReversed }) {
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
          <dd className="font-medium text-slate-800">
            {t(`journal.status_${txn.status}`)}
          </dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="text-xs text-slate-500">{t('tx.description')}</dt>
          <dd className="text-slate-800">{txn.description}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="text-xs text-slate-500">{t('journal.createdAt')}</dt>
          <dd className="font-medium text-slate-600">{createdDate}</dd>
        </div>
      </dl>

      {/* Status badge + reversal action (Part 4) */}
      <TxnStatusBlock txn={txn} org={org} onReversed={onReversed} />

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

function CashBookTable({ rows, org, type, nameOf, t, onViewTxn }) {
  const isOhada = org.framework === 'OHADA'
  const amountColumns = type === 'single'
    ? [
        { key: 'debit', label: t('cashbook.debit') },
        { key: 'credit', label: t('cashbook.credit') },
      ]
    : [
        { key: 'cashDebit', label: t('cashbook.cashDebit') },
        { key: 'bankDebit', label: t('cashbook.bankDebit') },
        { key: 'cashCredit', label: t('cashbook.cashCredit') },
        { key: 'bankCredit', label: t('cashbook.bankCredit') },
      ]
  const value = (row, key) => {
    if (key === 'debit' || key === 'credit') return Number(row[key]) || 0
    if (key === 'cashDebit') return row.cashbook_type === 'cash' ? Number(row.debit) || 0 : 0
    if (key === 'bankDebit') return row.cashbook_type === 'bank' ? Number(row.debit) || 0 : 0
    if (key === 'cashCredit') return row.cashbook_type === 'cash' ? Number(row.credit) || 0 : 0
    return row.cashbook_type === 'bank' ? Number(row.credit) || 0 : 0
  }
  const totals = Object.fromEntries(amountColumns.map((c) => [c.key, rows.reduce((s, r) => s + value(r, c.key), 0)]))
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full min-w-[620px] text-left text-sm">
        <thead><tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase text-slate-500">
          <th className="px-3 py-2">{t('journal.date')}</th>
          <th className="px-3 py-2">{t('journal.reference')}</th>
          {isOhada && <th className="px-3 py-2">{t('journal.accountNo')}</th>}
          <th className="px-3 py-2">{t('journal.accountName')}</th>
          <th className="px-3 py-2">{t('journal.narration')}</th>
          {amountColumns.map((c) => <th key={c.key} className="whitespace-nowrap px-3 py-2 text-right">{c.label}</th>)}
          <th className="px-3 py-2"></th>
        </tr></thead>
        <tbody>{rows.map((r) => <tr key={r.id} className="border-b border-slate-100 hover:bg-slate-50">
          <td className="whitespace-nowrap px-3 py-2">{r.date ? new Date(r.date).toLocaleDateString() : '—'}</td>
          <td className="px-3 py-2 font-mono text-xs">{r.reference}</td>
          {isOhada && <td className="px-3 py-2 font-mono text-xs">{r.account_code || ''}</td>}
          <td className="px-3 py-2">{nameOf(r)}</td>
          <td className="max-w-[180px] truncate px-3 py-2 text-slate-600">{r.narration || '—'}</td>
          {amountColumns.map((c) => <td key={c.key} className="whitespace-nowrap px-3 py-2 text-right">{value(r, c.key) ? value(r, c.key).toLocaleString() : ''}</td>)}
          <td className="px-3 py-2 text-right"><button type="button" onClick={() => onViewTxn(r.transaction_id)} className="text-sm font-medium text-blue-600 hover:text-blue-700">{t('journal.view')} →</button></td>
        </tr>)}</tbody>
        <tfoot><tr className="border-t border-slate-300 bg-slate-100 font-bold">
          <td className="px-3 py-2" colSpan={(isOhada ? 5 : 4)}>{t('journal.totals')}</td>
          {amountColumns.map((c) => <td key={c.key} className="px-3 py-2 text-right">{totals[c.key].toLocaleString()}</td>)}
          <td />
        </tr></tfoot>
      </table>
    </div>
  )
}