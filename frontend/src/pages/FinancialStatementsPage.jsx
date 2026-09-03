// Financial Statements page (Session 10, Part B). Two views driven by ONE
// payload pair: the Income Statement (Compte de résultat / Statement of Profit
// or Loss) and the Bilan / Statement of Financial Position, both derived from
// the ledger by the Part A backend (never manually entered).
//
// Framework-correct titles (requirement): page titles come from the BACKEND
// response (statement_name_en / statement_name_fr) — an OHADA workspace shows
// the real legal document names "Compte de résultat" / "Bilan", an IFRS
// workspace the IAS 1 names. Nothing is hardcoded per framework.
//
// OHADA income statement structure (requirement 4): the ordinary result
// (classes 6-7) and the HAO / extraordinary result (class 8) are rendered as
// TWO DISTINCT sections leading to one combined NET RESULT — never merged
// into a flat list, because that would misrepresent OHADA's actual structure.
//
// Position balance check: OHADA/IFRS statements here have NO closing entries,
// so with any P&L activity assets = liabilities + equity + period result (the
// result is not yet booked to equity). The UI states this honestly
// (fs.balanceCheckWithResult) instead of showing a scary false "unbalanced".
//
// MOBILE DECISION (requirement 7): like Journal/Ledger/Trial Balance, the
// statement tables scroll horizontally on phone widths (overflow-x-auto)
// because section headers must stay attached to their columns. Everything
// else — the plain-language summary, controls and balance strip — stacks
// naturally at any width.
//
// CSV + print reuse the shared report pattern (csvExport.js, ReportHeader,
// @media print classes) exactly like Journal/Cash Book/Ledger/Trial Balance.
import { Fragment, useEffect, useState } from 'react'
import { fetchFinancialPosition, fetchIncomeStatement } from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'
import { downloadCsv } from '../utils/csvExport.js'
import ReportHeader from '../components/ReportHeader.jsx'
import {
  formatReportDate,
  formatReportNumber,
  reportCsvHeader,
} from '../utils/reportPresentation.js'
import {
  incomeCsvParts,
  plainSummaryIncome,
  plainSummaryPosition,
  positionBalanceKind,
  positionCsvParts,
  sectionLabel,
} from '../utils/financialPresentation.js'

const fmt = formatReportNumber

export default function FinancialStatementsPage({ org, onBack, onOpenLedger }) {
  const { t, lang } = useLanguage()
  const isOhada = org.framework === 'OHADA'
  const [view, setView] = useState('income') // 'income' | 'position'
  const [asOf, setAsOf] = useState(new Date().toISOString().slice(0, 10))
  const [from, setFrom] = useState('')
  const [generatedAt, setGeneratedAt] = useState(new Date())
  const [income, setIncome] = useState(null)
  const [position, setPosition] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      // ONE Apply refreshes BOTH statements — they describe the same books,
      // and the position needs the income payload's net_result for the honest
      // "including the period result" balance check.
      const [inc, pos] = await Promise.all([
        fetchIncomeStatement(org.id, { from, as_of: asOf }),
        fetchFinancialPosition(org.id, { as_of: asOf }),
      ])
      setIncome(inc)
      setPosition(pos)
      setGeneratedAt(new Date())
    } catch (err) {
      setError(err.message)
      setIncome(null)
      setPosition(null)
    } finally {
      setLoading(false)
    }
  }

  // Load once per workspace; the view toggle below NEVER refetches.
  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [org.id])

  const nameOf = (line) => (lang === 'fr' ? line.name_fr : line.name_en)

  // Requirement 2: the statement NAMES come from the backend payload — the
  // OHADA LEGAL document names ("Compte de résultat (OHADA)" / "Bilan (OHADA)")
  // or the IAS 1 names — selected per active language. For OHADA the backend
  // returns the SAME string for both languages (the legal names are never
  // translated, like "SARL"). Generic i18n labels are only the fallback shown
  // for the instant before the fetch resolves (also framework-aware below).
  const incomeTitle = income
    ? lang === 'fr' ? income.statement_name_fr : income.statement_name_en
    : isOhada ? t('fs.tabIncomeOhada') : t('fs.tabIncome')
  const positionTitle = position
    ? lang === 'fr' ? position.statement_name_fr : position.statement_name_en
    : isOhada ? t('fs.tabPositionOhada') : t('fs.tabPosition')
  const currentTitle = view === 'income' ? incomeTitle : positionTitle
  function exportCsv() {
    if (!income || !position) return
    const period =
      view === 'income' && from
        ? `${t('report.period')}: ${formatReportDate(from) || '—'} – ${formatReportDate(asOf) || '—'}`
        : `${t('report.asAt')} ${formatReportDate(asOf)}`
    const meta = reportCsvHeader({
      organization: org,
      title: currentTitle,
      framework: org.framework,
      period,
      generatedAt,
      t,
    })
    if (view === 'income') {
      const { headerRows, rows } = incomeCsvParts(income, { t, isOhada, lang })
      downloadCsv(`income-statement-${asOf}`, headerRows, rows, meta)
    } else {
      const { headerRows, rows } = positionCsvParts(position, {
        t, isOhada, lang, netResult: income.net_result,
      })
      downloadCsv(`financial-position-${asOf}`, headerRows, rows, meta)
    }
  }

  const inputCls =
    'rounded-lg border border-slate-300 px-2 py-1.5 text-sm focus:border-blue-500 focus:outline-none'

  return (
    <div className="report-page min-h-screen bg-slate-50 px-4 py-8">
      <div className="report-content mx-auto w-full max-w-5xl">
        <div className="no-print">
          <button
            type="button"
            onClick={onBack}
            className="mb-2 text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            ← {t('tx.backToOrg')}
          </button>
          <h2 className="text-xl font-bold text-slate-900">{currentTitle}</h2>
        </div>
        <ReportHeader
          org={org}
          title={currentTitle}
          from={view === 'income' ? from : undefined}
          to={view === 'income' ? asOf : undefined}
          asOf={view === 'position' ? asOf : undefined}
          generatedAt={generatedAt}
          t={t}
        />

        {/* Statement toggle + period controls (never printed) */}
        <div className="no-print mt-4 flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-500">{t('fs.title')}:</span>
            <div className="flex overflow-hidden rounded-lg border border-slate-300">
              <button
                type="button"
                onClick={() => setView('income')}
                className={`px-3 py-2 text-sm font-medium ${
                  view === 'income' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                {isOhada ? t('fs.tabIncomeOhada') : t('fs.tabIncome')}
              </button>
              <button
                type="button"
                onClick={() => setView('position')}
                className={`px-3 py-2 text-sm font-medium ${
                  view === 'position' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                {isOhada ? t('fs.tabPositionOhada') : t('fs.tabPosition')}
              </button>
            </div>
          </div>
          {view === 'income' && (
            <label>
              <span className="block text-xs font-medium text-slate-500">{t('fs.from')}</span>
              <input
                type="date"
                value={from}
                onChange={(e) => setFrom(e.target.value)}
                className={`mt-1 block ${inputCls}`}
              />
            </label>
          )}
          <label>
            <span className="block text-xs font-medium text-slate-500">{t('fs.asOf')}</span>
            <input
              type="date"
              value={asOf}
              onChange={(e) => setAsOf(e.target.value)}
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
          <div className="flex gap-2">
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
              disabled={!income || !position}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
            >
              ⬇ {t('common.downloadCsv')}
            </button>
          </div>
        </div>

        {error && (
          <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}

        {/* PLAIN-LANGUAGE SUMMARY (requirement 5) — printed, above the jargon.
            Built from the SAME payload as the table, so the numbers can never
            disagree with the detailed statement below. */}
        {view === 'income' && income && (
          <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-4">
            <p className="text-base font-semibold text-slate-900">
              {plainSummaryIncome(income, t)}
            </p>
            <p className="mt-1 text-xs text-slate-600">{t('fs.summaryNote')}</p>
          </div>
        )}
        {view === 'position' && position && (
          <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-4">
            <p className="text-base font-semibold text-slate-900">
              {plainSummaryPosition(position, t)}
            </p>
            <p className="mt-1 text-xs text-slate-600">{t('fs.summaryNote')}</p>
          </div>
        )}

        {/* ---------------- INCOME STATEMENT ---------------- */}
        {view === 'income' && income && income.sections.length === 0 && (
          <p className="mt-4 rounded-xl border border-slate-200 bg-white p-6 text-center text-slate-500">
            {t('fs.empty')}
          </p>
        )}
        {view === 'income' && income && income.sections.length > 0 && (
          <div className="report-table mt-2 overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full min-w-[480px] text-left text-sm">
              <thead>
                <tr className="border-b border-slate-300 bg-slate-100 text-xs font-semibold uppercase text-slate-600">
                  {isOhada && (
                    <th className="whitespace-nowrap px-3 py-2">{t('journal.accountNo')}</th>
                  )}
                  <th className="px-3 py-2">{t('journal.accountName')}</th>
                  <th className="px-3 py-2 text-right">{t('fs.amount')}</th>
                  <th className="no-print px-3 py-2 text-right">{t('ledger.title')}</th>
                </tr>
              </thead>
              <tbody>
                {/* ORDINARY sections (revenue, expenses) first */}
                {income.sections
                  .filter((s) => s.key !== 'extraordinary')
                  .map((section) => (
                    <Fragment key={section.key}>
                      <tr className="border-b border-slate-200 bg-slate-100">
                        <td
                          colSpan={isOhada ? 4 : 3}
                          className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-700"
                        >
                          {sectionLabel(section, t, lang)}
                        </td>
                      </tr>
                      {section.lines.map((line) => (
                        <tr
                          key={line.account_id}
                          className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                        >
                          {isOhada && (
                            <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-600">
                              {line.code || ''}
                            </td>
                          )}
                          <td className="px-3 py-2 text-slate-800">{nameOf(line)}</td>
                          <td className="whitespace-nowrap px-3 py-2 text-right font-medium text-slate-900">
                            {fmt(line.amount)}
                          </td>
                          <td className="no-print whitespace-nowrap px-3 py-2 text-right">
                            <button
                              type="button"
                              onClick={() => onOpenLedger(line.account_id)}
                              title={t('fs.drillHint')}
                              className="text-sm font-medium text-blue-600 hover:text-blue-700"
                            >
                              {t('journal.view')} →
                            </button>
                          </td>
                        </tr>
                      ))}
                      <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-900">
                        {isOhada && <td className="px-3 py-2" />}
                        <td className="px-3 py-2">
                          {t('fs.total')} — {sectionLabel(section, t, lang)}
                        </td>
                        <td className="whitespace-nowrap px-3 py-2 text-right">
                          {fmt(section.total)}
                        </td>
                        <td className="no-print" />
                      </tr>
                    </Fragment>
                  ))}
                {/* RESULT OF ORDINARY ACTIVITIES — a distinct subtotal; HAO
                    NEVER blends into this figure */}
                <tr className="border-y border-slate-300 bg-blue-50 font-bold text-slate-900">
                  {isOhada && <td className="px-3 py-2" />}
                  <td className="px-3 py-2">{t('fs.ordinaryResult')}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-right">
                    {fmt(income.ordinary_result)}
                  </td>
                  <td className="no-print" />
                </tr>
                {/* HAO (class 8) — SEPARATE extraordinary section, amber
                    accent, only when class-8 activity exists (OHADA) */}
                {income.sections
                  .filter((s) => s.key === 'extraordinary')
                  .map((section) => (
                    <Fragment key={section.key}>
                      <tr className="border-b border-amber-200 bg-amber-100">
                        <td
                          colSpan={isOhada ? 4 : 3}
                          className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-amber-800"
                        >
                          {sectionLabel(section, t, lang)}
                        </td>
                      </tr>
                      {section.lines.map((line) => (
                        <tr
                          key={line.account_id}
                          className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                        >
                          {isOhada && (
                            <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-600">
                              {line.code || ''}
                            </td>
                          )}
                          <td className="px-3 py-2 text-slate-800">{nameOf(line)}</td>
                          <td className="whitespace-nowrap px-3 py-2 text-right font-medium text-slate-900">
                            {fmt(line.amount)}
                          </td>
                          <td className="no-print whitespace-nowrap px-3 py-2 text-right">
                            <button
                              type="button"
                              onClick={() => onOpenLedger(line.account_id)}
                              title={t('fs.drillHint')}
                              className="text-sm font-medium text-blue-600 hover:text-blue-700"
                            >
                              {t('journal.view')} →
                            </button>
                          </td>
                        </tr>
                      ))}
                      <tr className="border-b border-slate-200 bg-amber-50 font-semibold text-slate-900">
                        {isOhada && <td className="px-3 py-2" />}
                        <td className="px-3 py-2">{t('fs.extraordinaryResult')}</td>
                        <td className="whitespace-nowrap px-3 py-2 text-right">
                          {fmt(Number(income.net_result) - Number(income.ordinary_result))}
                        </td>
                        <td className="no-print" />
                      </tr>
                    </Fragment>
                  ))}
                {/* FINAL COMBINED NET RESULT (ordinary + extraordinary) */}
                <tr className="bg-slate-800 font-bold text-white">
                  {isOhada && <td className="px-3 py-2" />}
                  <td className="px-3 py-2">{t('fs.netResult')}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-right">
                    {fmt(income.net_result)}
                  </td>
                  <td className="no-print" />
                </tr>
              </tbody>
            </table>
          </div>
        )}

        {/* ---------------- BILAN / STATEMENT OF FINANCIAL POSITION ---------- */}
        {view === 'position' && position && position.sections.length === 0 && (
          <p className="mt-4 rounded-xl border border-slate-200 bg-white p-6 text-center text-slate-500">
            {t('fs.empty')}
          </p>
        )}
        {view === 'position' && position && position.sections.length > 0 && (
          <div className="report-table mt-2 overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="w-full min-w-[480px] text-left text-sm">
              <thead>
                <tr className="border-b border-slate-300 bg-slate-100 text-xs font-semibold uppercase text-slate-600">
                  {isOhada && (
                    <th className="whitespace-nowrap px-3 py-2">{t('journal.accountNo')}</th>
                  )}
                  <th className="px-3 py-2">{t('journal.accountName')}</th>
                  <th className="px-3 py-2 text-right">{t('fs.amount')}</th>
                  <th className="no-print px-3 py-2 text-right">{t('ledger.title')}</th>
                </tr>
              </thead>
              <tbody>
                {position.sections.map((section) => (
                  <Fragment key={section.key}>
                    <tr className="border-b border-slate-200 bg-slate-100">
                      <td
                        colSpan={isOhada ? 4 : 3}
                        className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-700"
                      >
                        {sectionLabel(section, t, lang)}
                      </td>
                    </tr>
                    {section.lines.map((line) => (
                      <tr
                        key={line.account_id}
                        className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                      >
                        {isOhada && (
                          <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-600">
                            {line.code || ''}
                          </td>
                        )}
                        <td className="px-3 py-2 text-slate-800">{nameOf(line)}</td>
                        <td className="whitespace-nowrap px-3 py-2 text-right font-medium text-slate-900">
                          {fmt(line.amount)}
                        </td>
                        <td className="no-print whitespace-nowrap px-3 py-2 text-right">
                          <button
                            type="button"
                            onClick={() => onOpenLedger(line.account_id)}
                            title={t('fs.drillHint')}
                            className="text-sm font-medium text-blue-600 hover:text-blue-700"
                          >
                            {t('journal.view')} →
                          </button>
                        </td>
                      </tr>
                    ))}
                    <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-900">
                      {isOhada && <td className="px-3 py-2" />}
                      <td className="px-3 py-2">
                        {t('fs.total')} — {sectionLabel(section, t, lang)}
                      </td>
                      <td className="whitespace-nowrap px-3 py-2 text-right">
                        {fmt(section.total)}
                      </td>
                      <td className="no-print" />
                    </tr>
                  </Fragment>
                ))}
                {/* The period result is NOT yet booked to equity (no closing
                    entries in this MVP), so with P&L activity it is shown as
                    its own line — that is what makes the balance check below
                    honest instead of falsely "unbalanced". */}
                {income && Number(income.net_result) !== 0 && (
                  <Fragment>
                    <tr className="border-b border-slate-200 bg-blue-50 font-semibold text-slate-900">
                      {isOhada && <td className="px-3 py-2" />}
                      <td className="px-3 py-2">{t('fs.resultOfPeriod')}</td>
                      <td className="whitespace-nowrap px-3 py-2 text-right">
                        {fmt(income.net_result)}
                      </td>
                      <td className="no-print" />
                    </tr>
                    <tr className="border-b border-slate-200 bg-slate-50 font-semibold text-slate-900">
                      {isOhada && <td className="px-3 py-2" />}
                      <td className="px-3 py-2">{t('fs.totalEquityAndResult')}</td>
                      <td className="whitespace-nowrap px-3 py-2 text-right">
                        {fmt(Number(position.equity) + Number(income.net_result))}
                      </td>
                      <td className="no-print" />
                    </tr>
                  </Fragment>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Balance strip (never printed — same treatment as the trial
            balance's balanced indicator): honest about WHERE the identity
            holds, including the not-yet-booked period result. */}
        {view === 'position' && position && (
          <div
            className={`no-print mt-4 rounded-xl border p-4 shadow-sm ${
              positionBalanceKind(position, income ? income.net_result : 0) === 'none'
                ? 'border-red-300 bg-red-100'
                : 'border-green-200 bg-green-50'
            }`}
          >
            {positionBalanceKind(position, income ? income.net_result : 0) === 'exact' && (
              <p className="text-sm font-semibold text-green-800">✓ {t('fs.balanceCheckExact')}</p>
            )}
            {positionBalanceKind(position, income ? income.net_result : 0) === 'withResult' && (
              <p className="text-sm font-semibold text-green-800">✓ {t('fs.balanceCheckWithResult')}</p>
            )}
            {positionBalanceKind(position, income ? income.net_result : 0) === 'none' && (
              <p className="text-sm font-bold text-red-800">⚠ {t('fs.balanceCheckBad')}</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}