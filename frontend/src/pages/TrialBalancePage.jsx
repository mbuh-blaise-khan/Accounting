// Trial Balance page (Session 9; Session 10 report polish). ONE fetch supplies
// opening balance, period movement and closing balance for every account; the
// 2/4/6-column selector is purely a VIEW of that payload (no refetch).
// Beginners default to the simple 2-column closing view; the fuller views show
// activity + result.
//
// Grouped two-row table headers (Session 10, research-based): the top row spans
// "Opening balance / Movement / Closing balance" groups (colspan=2), the row
// below carries the Debit/Credit sub-headers — the layout real accounting
// software uses instead of flat concatenated labels.
// MOBILE DECISION: like every other wide table in this app (Journal, Ledger)
// the trial balance scrolls horizontally on phone-width screens rather than
// collapsing to cards, because a grouped header must stay attached to its
// columns to remain readable. The 2-column beginner view fits without
// scrolling; the 4/6-column views scroll inside the same overflow-x-auto
// container.
import { Fragment, useEffect, useState } from 'react'
import { fetchTrialBalance } from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'
import { downloadCsv } from '../utils/csvExport.js'
import ReportHeader from '../components/ReportHeader.jsx'
import {
  formatReportDate,
  formatReportNumber,
  reportAccountColumns,
  reportCsvHeader,
} from '../utils/reportPresentation.js'

const VIEWS = [2, 4, 6]

// One group definition per balance family. Each group owns exactly two amount
// columns (Debit/Credit) — the grouped two-row header is built from this.
const GROUP_DEFS = (t) => [
  { key: 'opening', label: t('tb.opening'), cols: [{ key: 'opening_debit' }, { key: 'opening_credit' }] },
  { key: 'movement', label: t('tb.movement'), cols: [{ key: 'movement_debit' }, { key: 'movement_credit' }] },
  { key: 'closing', label: t('tb.closing'), cols: [{ key: 'closing_debit' }, { key: 'closing_credit' }] },
]

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

  const nameOf = (r) => (lang === 'fr' ? r.name_fr : r.name_en)

  // The groups shown in the current 2/4/6-column view, and their flattened
  // amount columns — the single source for the table, totals and CSV.
  const allGroups = GROUP_DEFS(t)
  const visibleGroups = view === 6 ? allGroups : view === 4 ? allGroups.slice(1) : allGroups.slice(2)
  const amountCols = visibleGroups.flatMap((g) => g.cols)
  const accountCols = reportAccountColumns(isOhada, t)
  const totalColumnCount = accountCols.length + 1 + amountCols.length + 1 // account cols + name + amounts + ledger action

  function exportCsv() {
    if (!tb) return
    // Two header rows mirror the on-screen grouped header: group names above,
    // Debit/Credit below; OHADA carries N° compte, IFRS omits it.
    const groupHeaderRow = [
      ...accountCols.map(() => ''),
      '',
      ...visibleGroups.flatMap((g) => [g.label, g.label]),
    ]
    const subHeaderRow = [
      ...accountCols,
      t('journal.accountName'),
      ...visibleGroups.flatMap(() => [t('journal.debit'), t('journal.credit')]),
    ]
    const rows = tb.rows.map((r) => [
      ...(isOhada ? [r.code || ''] : []),
      nameOf(r),
      ...amountCols.map((c) => Number(r[c.key]) || 0),
    ])
    const totalsRow = [
      ...(isOhada ? [''] : []),
      t('tb.total'),
      ...amountCols.map((c) => Number(tb.totals[c.key]) || 0),
    ]
    const period = asOf ? `${t('report.asAt')} ${formatReportDate(asOf)}` : ''
    downloadCsv(
      `trial-balance-${asOf}`,
      [groupHeaderRow, subHeaderRow],
      [...rows, totalsRow],
      reportCsvHeader({ organization: org, title: t('tb.title'), framework: org.framework, period, generatedAt, t })
    )
  }

  const inputCls =
    'rounded-lg border border-slate-300 px-2 py-1.5 text-sm focus:border-blue-500 focus:outline-none'

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
          <h2 className="text-xl font-bold text-slate-900">{t('tb.title')}</h2>
        </div>
        <ReportHeader org={org} title={t('tb.title')} from={from} asOf={asOf} generatedAt={generatedAt} t={t} />

        {/* Period + view controls (never printed) */}
        <div className="no-print mt-4 flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
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

        {/* LOUD pass/fail indicator at the CLOSING level (never printed) */}
        {tb && (
          <div
            className={`no-print mt-4 rounded-xl border p-4 shadow-sm ${
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
          <div className="no-print mt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => window.print()}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
            >
              🖨 {t('common.print')}
            </button>
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
          <div className="report-table mt-2 overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full min-w-[520px] text-left text-sm">
              <thead>
                {/* Group row: one spanning cell per balance family present in
                    the selected 2/4/6-column view. Account cols (N° compte for
                    OHADA) and the GL-action column span both header rows. */}
                <tr className="border-b border-slate-300 bg-slate-100 text-xs font-semibold uppercase text-slate-600">
                  {accountCols.map((label, i) => (
                    <th key={i} rowSpan={2} className="whitespace-nowrap px-3 py-2">
                      {label}
                    </th>
                  ))}
                  <th rowSpan={2} className="px-3 py-2">
                    {t('journal.accountName')}
                  </th>
                  {visibleGroups.map((g) => (
                    <th
                      key={g.key}
                      colSpan={2}
                      className="border-x border-slate-200 bg-slate-200/70 px-3 py-2 text-center"
                    >
                      {g.label}
                    </th>
                  ))}
                  <th rowSpan={2} className="px-3 py-2 text-right">
                    {t('ledger.title')}
                  </th>
                </tr>
                {/* Sub-header row: Debit / Credit under every group */}
                <tr className="border-b border-slate-300 bg-slate-50 text-xs font-semibold uppercase text-slate-500">
                  {visibleGroups.map((g) => (
                    <Fragment key={g.key}>
                      <th className="whitespace-nowrap px-3 py-2 text-right">{t('journal.debit')}</th>
                      <th className="whitespace-nowrap px-3 py-2 text-right">{t('journal.credit')}</th>
                    </Fragment>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tb.rows.length === 0 && (
                  <tr>
                    <td colSpan={totalColumnCount} className="px-3 py-8 text-center text-slate-500">
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
                    {amountCols.map((c) => {
                      const v = Number(r[c.key]) || 0
                      return (
                        <td
                          key={c.key}
                          className={`whitespace-nowrap px-3 py-2 text-right ${
                            v > 0 ? 'font-medium text-slate-900' : 'text-slate-400'
                          }`}
                        >
                          {v > 0 ? formatReportNumber(v) : ''}
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
                    {amountCols.map((c) => (
                      <td key={c.key} className="whitespace-nowrap px-3 py-2 text-right">
                        {formatReportNumber(tb.totals[c.key])}
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

