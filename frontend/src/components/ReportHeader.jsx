import { formatReportDateTime, reportPeriodLabel } from '../utils/reportPresentation.js'

// Report header block (identical on screen and in print).
//
// Top of the block = business identity (name, report title + framework,
// registered address when set). The OHADA-convention registration identifiers
// (RCCM / tax ID) sit in a footer-style line at the BOTTOM of the block,
// visually separated from the branding above.
//
// Every Business Profile field is OPTIONAL: each line renders only when the
// data actually exists — no blank placeholder text when unset.
export default function ReportHeader({ org, title, from, to, asOf, generatedAt, t }) {
  const hasRegistration = Boolean(org.rccm_number || org.tax_id)
  return (
    <div className="report-header mt-3 border-b border-slate-200 pb-3">
      <p className="text-2xl font-bold text-slate-900">{org.name}</p>
      <p className="text-lg font-semibold text-slate-800">{title} ({org.framework})</p>
      {org.registered_address && (
        <p className="text-sm text-slate-600">{org.registered_address}</p>
      )}
      <p className="text-sm text-slate-600">{reportPeriodLabel({ from, to, asOf, t })}</p>
      <p className="text-xs text-slate-500">{t('report.generated')}: {formatReportDateTime(generatedAt)}</p>
      {hasRegistration && (
        <p className="report-header-registration mt-1 border-t border-slate-100 pt-1 text-xs text-slate-500">
          {org.rccm_number && (
            <span className="mr-3">{t('report.rccm')} {org.rccm_number}</span>
          )}
          {org.tax_id && (
            <span>{t('report.taxId')} {org.tax_id}</span>
          )}
        </p>
      )}
    </div>
  )
}
