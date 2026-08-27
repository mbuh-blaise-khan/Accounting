// Trial Balance page (Session 9). ONE fetch supplies opening balance, period
// movement and closing balance for every account; the 2/4/6-column selector is
// purely a VIEW of that payload (no refetch). Beginners default to the simple
// 2-column closing view; the fuller views show activity + result.
import { useEffect, useState } from 'react'
import { fetchTrialBalance } from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'
import { downloadCsv } from '../utils/csvExport.js'
import ReportHeader from '../components/ReportHeader.jsx'
import { formatReportNumber, reportCsvHeader, reportPeriodLabel } from '../utils/reportPresentation.js'

const VIEWS = [2, 4, 6]

export default function TrialBalancePage({ org, onBack, onOpenLedger }) {
  const { t, lang } = useLanguage()
  const isOhada = org.framework === 'OHADA'
  const [asOf, setAsOf] = useState(new Date().toISOString().slice(0, 10))
  const [from, setFrom] = useState('')
  const [view, setView] = useState(2)
  const [generatedAt, setGeneratedAt] = useState(new Date())
  const [tb, setTb] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setTb(await fetchTrialBalance(org.id, { as_of: asOf, from, columns: view }))
      setGeneratedAt(new Date())
    } catch (err) {
      setError(err.message)
      setTb(null)
    } finally {
      setLoading(false)
    }
  }

  // Load once per workspace; the view toggle below NEVER refetches.
  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [org.id])

  function fmt(n) {
    return (Number(n) || 0).toLocaleString()
  }
  const nameOf = (r) => (lang === 'fr' ? r.name_fr : r.name_en)

  // Column headers/keys per selected VIEW, all from the same row object.
  const colsByView = {
    2: [
      { key: 'closing_debit', label: `${t('tb.closing')} · ${t('journal.debit')}` },
      { key: 'closing_credit', label: `${t('tb.closing')} · ${t('journal.credit')}` },
    ],
    4: [
      { key: 'movement_debit', label: `${t('tb.movement')} · ${t('journal.debit')}` },
      { key: 'movement_credit', label: `${t('tb.movement')} · ${t('journal.credit')}` },
      { key: 'closing_debit', label: `${t('tb.closing')} · ${t('journal.debit')}` },
      { key: 'closing_credit', label: `${t('tb.closing')} · ${t('journal.credit')}` },
    ],
    6: [
      { key: 'opening_debit', label: `${t('tb.opening')} · ${t('journal.debit')}` },
      { key: 'opening_credit', label: `${t('tb.opening')} · ${t('journal.credit')}` },
      { key: 'movement_debit', label: `${t('tb.movement')} · ${t('journal.debit')}` },
      { key: 'movement_credit', label: `${t('tb.movement')} · ${t('journal.credit')}` },
      { key: 'closing_debit', label: `${t('tb.closing')} · ${t('journal.debit')}` },
      { key: 'closing_credit', label: `${t('tb.closing')} · ${t('journal.credit')}` },
    ],
  }

  function exportCsv() {
    if (!tb) return
    const headers = [
      ...(isOhada ? [t('journal.accountNo')] : []),
      t('journal.accountName'),
      ...colsByView[view].map((c) => c.label),
    ]
    const rows = tb.rows.map((r) => [
      ...(isOhada ? [r.code || ''] : []),
      nameOf(r),
      ...colsByView[view].map((c) => Number(r[c.key]) || 0),
    ])
    const totalsRow = [
      ...(isOhada ? [''] : []),
      t('tb.total'),
      ...colsByView[view].map((c) => Number(tb.totals[c.key]) || 0),
    ]
    downloadCsv(`trial-balance-${asOf}`, headers, [...rows, totalsRow])
  }

  const inputCls =
    'rounded-lg border border-slate-300 px-2 py-1.5 text-sm focus:border-blue-500 focus:outline-none'

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
        <h2 className="text-xl font-bold text-slate-900">{t('tb.title')}</h2>
        <p className="mt-1 text-sm text-slate-600">
          {org.name} · {t('dashboard.framework')} {org.framework} · {org.currency}
        </p>
        <p className="mt-1 text-sm text-slate-500">{t('tb.subtitle')}</p>

        {/* Period + view controls */}
        <div className="mt-4 flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <label>
            <span className="block text-xs font-medium text-slate-500">{t('tb.asOf')}</span>
            <input
              type="date"
              value={asOf}
              onChange={(e) => setAsOf(e.target.value)}
              className={`mt-1 block ${inputCls}`}
            />
          </label>
          <label>
            <span className="block text-xs font-medium text-slate-500">{t('tb.from')}</span>
            <input
              type="date"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
              className={`mt-1 block ${inputCls}`}
            />
          </label>
          <button
            type="button"
            onClick={load}
            disabled={loading}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? t('common.loading') : t('journal.apply')}
          </button>
                    <span className="flex-1" />
          {/* View toggle: re-renders the SAME data, never refetches */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-500">{t('tb.view')}:</span>
            <div className="flex overflow-hidden rounded-lg border border-slate-300">
              {VIEWS.map((v) => (
                <button
                  key={v}
                  type="button"
                  onClick={() => setView(v)}
                  className={`px-3 py-2 text-sm font-medium ${
                    view === v ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  {t(`tb.view${v}`)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* LOUD pass/fail indicator at the CLOSING level */}
        {tb && (
          <div
            className={`mt-4 rounded-xl border p-4 shadow-sm ${
              tb.balanced ? 'border-green-200 bg-green-50' : 'border-red-300 bg-red-100'
            }`}
          >
            {tb.balanced ? (
              <p className="text-sm font-semibold text-green-800">✓ {t('tb.balanced')}</p>
            ) : (
              <>
                <p className="text-sm font-bold text-red-800">⚠ {t('tb.unbalanced')}</p>
                <p className="mt-1 text-xs text-red-700">{t('tb.unbalancedHint')}</p>
              </>
            )}
          </div>
        )}

        {tb && (
          <div className="mt-3 flex justify-end">
            <button
              type="button"
              onClick={exportCsv}
              disabled={tb.rows.length === 0}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
            >
              ⬇ {t('common.downloadCsv')}
            </button>
          </div>
        )}

        {tb && (
          <div className="mt-2 overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full min-w-[520px] text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase text-slate-500">
                  {isOhada && (
                    <th className="whitespace-nowrap px-3 py-2">{t('journal.accountNo')}</th>
                  )}
                  <th className="px-3 py-2">{t('journal.accountName')}</th>
                  {colsByView[view].map((c) => (
                    <th key={c.key} className="whitespace-nowrap px-3 py-2 text-right">
                      {c.label}
                    </th>
                  ))}
                  <th className="px-3 py-2 text-right">{t('ledger.title')}</th>
                </tr>
              </thead>
              <tbody>
                {tb.rows.length === 0 && (
                  <tr>
                    <td
                      colSpan={(isOhada ? 2 : 1) + colsByView[view].length + 1}
                      className="px-3 py-8 text-center text-slate-500"
                    >
                      {t('tb.empty')}
                    </td>
                  </tr>
                )}
                {tb.rows.map((r) => (
                  <tr
                    key={r.account_id}
                    className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                  >
                    {isOhada && (
                      <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-600">
                        {r.code || ''}
                      </td>
                    )}
                    <td className="px-3 py-2 text-slate-800">{nameOf(r)}</td>
                    {colsByView[view].map((c) => {
                      const v = Number(r[c.key]) || 0
                      return (
                        <td
                          key={c.key}
                          className={`whitespace-nowrap px-3 py-2 text-right ${
                            v > 0 ? 'font-medium text-slate-900' : 'text-slate-400'
                          }`}
                        >
                          {v > 0 ? fmt(v) : ''}
                        </td>
                      )
                    })}
                    <td className="whitespace-nowrap px-3 py-2 text-right">
                      <button
                        type="button"
                        onClick={() => onOpenLedger(r.account_id)}
                        className="text-sm font-medium text-blue-600 hover:text-blue-700"
                      >
                        {t('journal.view')} →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
              {tb.rows.length > 0 && (
                <tfoot>
                  <tr className="border-t border-slate-300 bg-slate-100 font-bold text-slate-900">
                    {isOhada && <td className="px-3 py-2" />}
                    <td className="px-3 py-2">{t('tb.total')}</td>
                    {colsByView[view].map((c) => (
                      <td key={c.key} className="whitespace-nowrap px-3 py-2 text-right">
                        {fmt(tb.totals[c.key])}
                      </td>
                    ))}
                    <td />
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

