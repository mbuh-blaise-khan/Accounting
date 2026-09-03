export function formatReportDate(value) {
  if (!value) return ''
  const d = value instanceof Date ? value : new Date(`${value}T00:00:00`)
  if (Number.isNaN(d.getTime())) return String(value)
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`
}

export function formatReportDateTime(value = new Date()) {
  const d = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  return `${formatReportDate(d.toISOString().slice(0, 10))} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

export function formatReportNumber(value) {
  const n = Number(value)
  if (!Number.isFinite(n)) return ''
  return new Intl.NumberFormat('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(n)
}

export function reportPeriodLabel({ from, to, asOf, t }) {
  if (from || to) return `${t('report.period')}: ${formatReportDate(from) || '—'} – ${formatReportDate(to) || '—'}`
  return `${t('report.asAt')} ${formatReportDate(asOf)}`
}

export function reportCsvHeader({ organization, title, framework, period, generatedAt, t }) {
  // The report-info block. Mirrors the on-screen ReportHeader: identity rows
  // first, then the period + generated timestamp, then the OPTIONAL
  // registration identifiers (address / RCCM / tax ID) in the footer-style
  // position — each only when actually set, never as blank placeholders.
  // csvExport.toCsv inserts the blank separator row between these rows and the
  // column headers, so there is no trailing [] here.
  const rows = [
    [t('report.business'), organization.name],
    // Same rule as the on-screen ReportHeader: if the title already carries
    // the framework in its legal name ("Bilan (OHADA)"), don't append it again.
    [
      t('report.title'),
      title && String(title).includes(`(${framework})`)
        ? title
        : `${title} (${framework})`,
    ],
  ]
  if (organization.registered_address) {
    rows.push([t('bp.address'), organization.registered_address])
  }
  rows.push([t('report.period'), period])
  rows.push([t('report.generated'), formatReportDateTime(generatedAt)])
  if (organization.rccm_number) {
    rows.push([t('report.rccm'), organization.rccm_number])
  }
  if (organization.tax_id) {
    rows.push([t('report.taxId'), organization.tax_id])
  }
  return rows
}

/**
 * The account-identity columns for a report. OHADA shows the plan code column
 * ("N° compte") first; IFRS omits it entirely (name-only), so it returns [].
 * Used identically by the UI column header and the CSV export so the two never
 * disagree, and unit-testable without a browser.
 */
export function reportAccountColumns(isOhada, t) {
  return isOhada ? [t('journal.accountNo')] : []
}
