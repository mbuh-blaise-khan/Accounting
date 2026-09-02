// Pure presentation helpers for the financial statements (Session 10, Part B).
// The page imports these so the on-screen table, the plain-language summary
// and the CSV export can never disagree; financial.test.mjs (npm run
// test:financial) unit-tests them without a browser.
import { formatReportNumber } from './reportPresentation.js'

// Fill "{placeholder}" tokens in an i18n template. split/join instead of
// replaceAll so it also runs on older Node for the util tests.
function fill(template, values) {
  let out = template
  for (const [k, v] of Object.entries(values)) {
    out = out.split(`{${k}}`).join(v)
  }
  return out
}

/**
 * Plain-language summary above the INCOME statement, built from the SAME
 * payload the detailed table renders (totals can never disagree with it).
 * OHADA & IFRS wording is identical by design — beginners first, jargon below.
 */
export function plainSummaryIncome(income, t, fmt = formatReportNumber) {
  if (!income) return ''
  const template =
    Number(income.net_result) >= 0 ? t('fs.summaryIncomeProfit') : t('fs.summaryIncomeLoss')
  return fill(template, {
    revenue: fmt(income.revenue_total),
    expenses: fmt(income.expense_total),
    result: fmt(Math.abs(Number(income.net_result))),
  })
}

/** Plain-language summary above the Bilan / Statement of Financial Position. */
export function plainSummaryPosition(position, t, fmt = formatReportNumber) {
  if (!position) return ''
  return fill(t('fs.summaryPosition'), {
    assets: fmt(position.assets),
    liabilities: fmt(position.liabilities),
    equity: fmt(position.equity),
  })
}

/**
 * How the Bilan balances, given that OHADA/IFRS statements carry NO closing
 * entries: revenue and expense accounts hold the period result, so with any
 * P&L activity assets = liabilities + equity + net_result (the result is not
 * yet booked to equity). 'exact' means the classic identity already holds
 * (no P&L activity); 'withResult' means it holds once the period result is
 * included; 'none' means genuinely unbalanced (report an issue).
 */
export function positionBalanceKind(position, netResult = 0) {
  if (!position) return 'none'
  const a = Number(position.assets)
  const l = Number(position.liabilities)
  const e = Number(position.equity)
  const r = Number(netResult) || 0
  if (a === l + e) return 'exact'
  if (a === l + e + r) return 'withResult'
  return 'none'
}

/**
 * Localized section label. The backend's section `key` is stable
 * (revenue/expenses/extraordinary/assets/liabilities/equity); the i18n files
 * own the wording, with the backend's English label as the fallback.
 */
export function sectionLabel(section, t, lang = 'en') {
  const key = `fs.section.${section.key}`
  const localized = t(key)
  if (localized !== key) return localized
  return lang === 'fr' ? section.label_fr : section.label_en
}

/**
 * CSV rows for the INCOME statement, mirroring the on-screen structure:
 * one section-header row per section, its line rows, the ordinary result,
 * the HAO result (OHADA only, signed) and the final NET RESULT. Framework
 * column rule is the shared one: OHADA carries N° compte, IFRS omits it.
 * Returns { headerRows: [header], rows } for csvExport.downloadCsv().
 */
export function incomeCsvParts(income, { t, isOhada, lang = 'en' }) {
  if (!income) return { headerRows: [], rows: [] }
  const headerRows = [
    [
      ...(isOhada ? [t('journal.accountNo')] : []),
      t('journal.accountName'),
      t('fs.amount'),
    ],
  ]
  const code = (line) => (isOhada ? [line.code || ''] : [])
  const rows = []
  for (const section of income.sections) {
    rows.push([sectionLabel(section, t, lang), ''])
    for (const line of section.lines) {
      rows.push([...code(line), lang === 'fr' ? line.name_fr : line.name_en, Number(line.amount) || 0])
    }
    rows.push([`${t('fs.total')} — ${sectionLabel(section, t, lang)}`, Number(section.total) || 0])
  }
  rows.push([t('fs.ordinaryResult'), Number(income.ordinary_result) || 0])
  if (isOhada) {
    const hao = Number(income.net_result) - Number(income.ordinary_result)
    rows.push([t('fs.extraordinaryResult'), hao])
  }
  rows.push([t('fs.netResult'), Number(income.net_result) || 0])
  return { headerRows, rows }
}

/**
 * CSV rows for the Bilan / Statement of Financial Position: section headers,
 * line rows and section totals, then (when there is P&L activity) the period
 * result and total equity including it. Returns { headerRows, rows }.
 */
export function positionCsvParts(position, { t, isOhada, lang = 'en', netResult = 0 }) {
  if (!position) return { headerRows: [], rows: [] }
  const headerRows = [
    [
      ...(isOhada ? [t('journal.accountNo')] : []),
      t('journal.accountName'),
      t('fs.amount'),
    ],
  ]
  const code = (line) => (isOhada ? [line.code || ''] : [])
  const rows = []
  for (const section of position.sections) {
    rows.push([sectionLabel(section, t, lang), ''])
    for (const line of section.lines) {
      rows.push([...code(line), lang === 'fr' ? line.name_fr : line.name_en, Number(line.amount) || 0])
    }
    rows.push([`${t('fs.total')} — ${sectionLabel(section, t, lang)}`, Number(section.total) || 0])
  }
  const result = Number(netResult) || 0
  if (result !== 0) {
    rows.push([t('fs.resultOfPeriod'), result])
    rows.push([t('fs.totalEquityAndResult'), Number(position.equity) + result])
  }
  return { headerRows, rows }
}