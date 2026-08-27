// General Ledger page (Session 8): pick one account (+ optional period) and see
// its opening balance, every posted movement chronologically with a RUNNING
// balance, and the closing balance. Read-only derivation over POSTED journal
// lines (GET /ledger/{account_id}) — nothing is stored server-side. Each row
// drills down to the originating transaction, same as the Journal.
import { useEffect, useState } from 'react'
import {
  fetchAccounts,
  fetchLedger,
  fetchSuggestedAccounts,
  fetchTransactions,
} from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'
import AccountFilterSelect from '../components/AccountFilterSelect.jsx'
import TxnStatusBlock from '../components/TxnStatusBlock.jsx'
import { downloadCsv } from '../utils/csvExport.js'

export default function GeneralLedgerPage({ org, onBack }) {
  const { t, lang } = useLanguage()
  const [accounts, setAccounts] = useState([])
  const [suggested, setSuggested] = useState([]) // Part 2: smart-ordered list
  const [accountId, setAccountId] = useState('')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [ledger, setLedger] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState(null)
  const [detailError, setDetailError] = useState(null)

  const nameOf = (a) => (lang === 'fr' ? a.name_fr : a.name_en)
  const isOhada = org.framework === 'OHADA'

  async function load() {
    if (!accountId) return
    setLoading(true)
    setError(null)
    try {
      const data = await fetchLedger(org.id, accountId, { from, to })
      setLedger(data)
    } catch (err) {
      setError(err.message)
      setLedger(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAccounts(org.id)
      .then(setAccounts)
      .catch((err) => setError(err.message))
    // Part 2: smart-ordered list for the dropdown (user's own accounts
    // first, then most recently posted-to, then code/name order).
    fetchSuggestedAccounts(org.id)
      .then(setSuggested)
      .catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [org.id])

  function handleSubmit(e) {
    e.preventDefault()
    load()
  }

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

  const inputCls =
    'rounded-lg border border-slate-300 px-2 py-1.5 text-sm focus:border-blue-500 focus:outline-none'

  function fmtAmount(n) {
    return (Number(n) || 0).toLocaleString()
  }

  // A balance point is an unsigned figure sitting on ONE side (Dr or Cr), the
  // way a real ledger shows it. Render the amount with its side label.
  function fmtBalance(bal) {
    if (!bal) return '—'
    if (Number(bal.debit) > 0) return `${fmtAmount(bal.debit)} ${t('ledger.dr')}`
    if (Number(bal.credit) > 0) return `${fmtAmount(bal.credit)} ${t('ledger.cr')}`
    return '—'
  }
  function balanceLabel(bal) {
    if (!bal || bal.side === 'zero') return t('ledger.zeroPosition')
    return bal.side === 'debit'
      ? t('ledger.debitPosition')
      : t('ledger.creditPosition')
  }

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
        <h2 className="text-xl font-bold text-slate-900">{t('ledger.title')}</h2>
        <p className="mt-1 text-sm text-slate-600">
          {org.name} · {t('dashboard.framework')} {org.framework} · {org.currency}
        </p>

        {/* Account + period picker */}
        <form
          onSubmit={handleSubmit}
          className="mt-4 flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
        >
          <label className="min-w-[220px] flex-1">
            <span className="block text-xs font-medium text-slate-500">
              {t('ledger.account')}
            </span>
            {/* Part 2: native dropdown (▾) — smart-ordered; typing in the
                type-ahead below still works. Both drive the same accountId. */}
            <select
              value={accountId}
              onChange={(e) => setAccountId(e.target.value)}
              className={`mt-1 w-full ${inputCls}`}
            >
              <option value="">▾ {t('ledger.pickAccount')}</option>
              {suggested.some((a) => a.is_mine) && (
                <optgroup label={t('ledger.myAccounts')}>
                  {suggested
                    .filter((a) => a.is_mine)
                    .map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.code ? `${a.code} · ` : ''}
                        {nameOf(a)}
                      </option>
                    ))}
                </optgroup>
              )}
              {!suggested.some((a) => a.is_mine) ? (
                suggested.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.code ? `${a.code} · ` : ''}
                    {nameOf(a)}
                  </option>
                ))
              ) : (
                <optgroup label={t('ledger.otherAccounts')}>
                  {suggested
                    .filter((a) => !a.is_mine)
                    .map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.code ? `${a.code} · ` : ''}
                        {nameOf(a)}
                      </option>
                    ))}
                </optgroup>
              )}
            </select>
            <AccountFilterSelect
              accounts={accounts}
              framework={org.framework}
              value={accounts.find((a) => a.id === Number(accountId)) || null}
              onChange={(id) => setAccountId(id)}
              t={t}
              nameOf={nameOf}
            />
          </label>
          <label>
            <span className="block text-xs font-medium text-slate-500">{t('journal.from')}</span>
            <input
              type="date"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
              className={`mt-1 block ${inputCls}`}
            />
          </label>
          <label>
            <span className="block text-xs font-medium text-slate-500">{t('journal.to')}</span>
            <input
              type="date"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              className={`mt-1 block ${inputCls}`}
            />
          </label>
          <button
            type="submit"
            disabled={!accountId || loading}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? t('common.loading') : t('ledger.show')}
          </button>
        </form>

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}
        {!accountId && !error && (
          <p className="mt-6 text-center text-slate-500">{t('ledger.pickFirst')}</p>
        )}

        {/* Part 3: export exactly what the current period/account shows */}
        {ledger && (
          <div className="mt-2 flex justify-end">
            <button
              type="button"
              disabled={!ledger.movements || ledger.movements.length === 0}
              onClick={() =>
                downloadCsv(
                  `ledger-${ledger.account.code || ledger.account.id}-${new Date()
                    .toISOString()
                    .slice(0, 10)}`,
                  [
                    t('journal.date'),
                    t('journal.reference'),
                    t('journal.description'),
                    ...(isOhada ? [t('journal.accountNo')] : []),
                    t('ledger.narrationCol'),
                    t('journal.debit'),
                    t('journal.credit'),
                    t('ledger.runningBalance'),
                  ],
                  (ledger.movements || []).map((m) => [
                    m.date ? new Date(m.date).toLocaleString() : '',
                    m.reference,
                    m.description || '',
                    ...(isOhada ? [ledger.account.code || ''] : []),
                    m.narration || '',
                    Number(m.debit) > 0 ? Number(m.debit) : 0,
                    Number(m.credit) > 0 ? Number(m.credit) : 0,
                    fmtBalance(m.running_balance),
                  ])
                )
              }
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
            >
              ⬇ {t('common.downloadCsv')}
            </button>
          </div>
        )}

        {ledger && (
          <>
            {/* Account header + the four balances */}
            <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-center gap-2">
                {isOhada && ledger.account.code && (
                  <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-xs font-semibold text-slate-700">
                    {ledger.account.code}
                  </span>
                )}
                <h3 className="text-lg font-bold text-slate-900">
                  {nameOf(ledger.account)}
                </h3>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                  {t('coa.balanceLabel')}:{' '}
                  {ledger.account.normal_balance === 'debit'
                    ? t('coa.balance.debit')
                    : t('coa.balance.credit')}
                </span>
              </div>
              <dl className="mt-3 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
                <div className="rounded-lg bg-slate-50 p-3">
                  <dt className="text-xs text-slate-500">
                    {t('ledger.openingBalance')} · {balanceLabel(ledger.opening_balance)}
                  </dt>
                  <dd className="mt-0.5 font-semibold text-slate-800">
                    {fmtBalance(ledger.opening_balance)}
                  </dd>
                </div>
                <div className="rounded-lg bg-blue-50 p-3">
                  <dt className="text-xs text-slate-500">{t('ledger.debitMovements')}</dt>
                  <dd className="mt-0.5 font-semibold text-slate-800">
                    {fmtAmount(ledger.debit_movements)}
                  </dd>
                </div>
                <div className="rounded-lg bg-amber-50 p-3">
                  <dt className="text-xs text-slate-500">{t('ledger.creditMovements')}</dt>
                  <dd className="mt-0.5 font-semibold text-slate-800">
                    {fmtAmount(ledger.credit_movements)}
                  </dd>
                </div>
                <div className="rounded-lg bg-green-50 p-3">
                  <dt className="text-xs text-slate-500">
                    {t('ledger.closingBalance')} · {balanceLabel(ledger.closing_balance)}
                  </dt>
                  <dd className="mt-0.5 font-bold text-slate-900">
                    {fmtBalance(ledger.closing_balance)}
                  </dd>
                </div>
              </dl>
            </div>

            {/* Movements */}
            <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase text-slate-500">
                    <th className="px-3 py-2">{t('journal.date')}</th>
                    <th className="px-3 py-2">{t('journal.reference')}</th>
                    <th className="px-3 py-2">{t('journal.description')}</th>
                    {isOhada && (
                      <th className="px-3 py-2">{t('journal.accountNo')}</th>
                    )}
                    <th className="px-3 py-2">{t('ledger.narrationCol')}</th>
                    <th className="px-3 py-2 text-right">{t('journal.debit')}</th>
                    <th className="px-3 py-2 text-right">{t('journal.credit')}</th>
                    <th className="px-3 py-2 text-right">
                      {t('ledger.runningBalance')}
                    </th>
                    <th className="px-3 py-2"></th>
                  </tr>
                </thead>
                <tbody>
                  {ledger.movements.length === 0 ? (
                    <tr>
                      <td
                        colSpan={isOhada ? 9 : 8}
                        className="px-3 py-6 text-center text-slate-500"
                      >
                        {t('ledger.noActivity')}
                      </td>
                    </tr>
                  ) : (
                    (() => {
                      const rows = []
                      let prevTxnId = null
                      ledger.movements.forEach((m, idx) => {
                        // Thick rule between movements of DIFFERENT transactions
                        // (same visual treatment as the Journal, Part C).
                        if (idx > 0 && m.transaction_id !== prevTxnId) {
                          rows.push(
                            <tr key={`sep-${m.id}`}>
                              <td colSpan={isOhada ? 9 : 8} className="p-0">
                                <div className="border-t-2 border-slate-400" />
                              </td>
                            </tr>
                          )
                        }
                        prevTxnId = m.transaction_id
                        const isCredit = Number(m.credit) > 0
                        rows.push(
                          <tr
                            key={m.id}
                            className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                          >
                          <td className="whitespace-nowrap px-3 py-2 text-slate-700">
                            {m.date ? new Date(m.date).toLocaleString() : '—'}
                          </td>
                          <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-600">
                            {m.reference}
                          </td>
                          <td className="max-w-[220px] truncate px-3 py-2 text-slate-700">
                            {m.description || '—'}
                          </td>
                          {isOhada && (
                            <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-600">
                              {ledger.account.code || ''}
                            </td>
                          )}
                          <td
                            className={`max-w-[180px] truncate px-3 py-2 ${
                              isCredit ? 'pl-8 text-slate-700' : 'text-slate-800'
                            }`}
                          >
                            {isCredit ? '↳ ' : ''}
                            {m.narration || '—'}
                          </td>
                          <td className="whitespace-nowrap px-3 py-2 text-right font-medium text-slate-900">
                            {Number(m.debit) > 0 ? fmtAmount(m.debit) : ''}
                          </td>
                          <td
                            className={`whitespace-nowrap text-right ${
                              isCredit ? 'pl-14 pr-2 text-slate-700' : 'px-3 pr-3 text-slate-300'
                            } py-2`}
                          >
                            {isCredit ? `↳ ${fmtAmount(m.credit)}` : ''}
                          </td>
                          <td className="whitespace-nowrap px-3 py-2 text-right font-semibold text-slate-900">
                            {fmtBalance(m.running_balance)}
                          </td>
                          <td className="px-3 py-2 text-right">
                            <button
                              type="button"
                              onClick={() => openDetail(m.transaction_id)}
                              className="text-sm font-medium text-blue-600 hover:text-blue-700"
                            >
                              {t('journal.view')} →
                            </button>
                          </td>
                        </tr>
                        )
                      })
                      return rows
                    })()
                  )}
                </tbody>
                <tfoot>
                  <tr className="border-t border-slate-200 bg-slate-50 font-semibold text-slate-800">
                    <td className="px-3 py-2" colSpan={isOhada ? 7 : 6}>
                      {t('ledger.closingBalance')}
                    </td>
                    <td className="whitespace-nowrap px-3 py-2 pr-9 text-right">
                      {fmtBalance(ledger.closing_balance)}
                    </td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>

            {detailError && (
              <p className="mt-3 text-sm text-red-600">{detailError}</p>
            )}
            {detail && (
              <TxnDetail
                txn={detail}
                org={org}
                onClose={() => setDetail(null)}
                onReversed={async () => {
                  // Re-run the ledger so the pair (original + reversal) shows
                  // net-zero immediately; re-read the updated transaction.
                  await load()
                  await openDetail(detail.id)
                }}
              />
            )}
          </>
        )}
      </div>
    </div>
  )
}

// Compact drill-down: the originating transaction's lines (same as Journal).
function TxnDetail({ txn, org, onClose, onReversed }) {
  const { t, lang } = useLanguage()
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
      <p className="mt-2 text-sm text-slate-700">{txn.description}</p>

      {/* Status badge + reversal action (Part 4) */}
      <TxnStatusBlock txn={txn} org={org} onReversed={onReversed} />

      <div className="mt-3 overflow-x-auto">
        <table className="w-full min-w-[420px] text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-xs font-semibold uppercase text-slate-500">
              {isOhada && <th className="px-2 py-1">{t('journal.accountNo')}</th>}
              <th className="px-2 py-1">{t('journal.accountName')}</th>
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