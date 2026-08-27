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
  return [
    [t('report.business'), organization.name],
    [t('report.title'), `${title} (${framework})`],
    [t('report.period'), period],
    [t('report.generated'), formatReportDateTime(generatedAt)],
    [],
  ]
}
