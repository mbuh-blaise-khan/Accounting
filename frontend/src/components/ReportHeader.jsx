import { formatReportDateTime, reportPeriodLabel } from '../utils/reportPresentation.js'

export default function ReportHeader({ org, title, from, to, asOf, generatedAt, t }) {
  return (
    <div className="report-header mt-3 border-b border-slate-200 pb-3">
      <p className="text-2xl font-bold text-slate-900">{org.name}</p>
      <p className="text-lg font-semibold text-slate-800">{title} ({org.framework})</p>
      <p className="text-sm text-slate-600">{reportPeriodLabel({ from, to, asOf, t })}</p>
      <p className="text-xs text-slate-500">{t('report.generated')}: {formatReportDateTime(generatedAt)}</p>
    </div>
  )
}
