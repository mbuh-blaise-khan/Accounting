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
// Fixed sector codes the Business Profile stores in `business_activity`
// (free text is stored when the user picks "Other" — see
// BusinessProfilePage). Used to translate a known code back into a localized
// label; unknown (free-text) values display as-is.
const ACTIVITY_CODES = [
  'retail',
  'agriculture',
  'manufacturing',
  'services',
  'technology',
  'construction',
  'transport',
  'education',
  'healthcare',
  'hospitality',
  'finance',
]

export default function ReportHeader({ org, title, from, to, asOf, generatedAt, t }) {
  const hasRegistration = Boolean(org.rccm_number || org.tax_id)
  return (
    <div className="report-header mt-3 border-b border-slate-200 pb-3">
      <p className="text-2xl font-bold text-slate-900">{org.name}</p>
      <p className="text-lg font-semibold text-slate-800">{title} ({org.framework})</p>
      {org.registered_address && (
        <p className="text-sm text-slate-600">{org.registered_address}</p>
      )}
      {/* Descriptive info sits near the business name (it describes the
          organization, unlike the legal identifiers which stay in the
          footer-style line below). Each line renders only when set. */}
      {org.company_description && (
        <p className="max-w-2xl text-sm italic text-slate-600">{org.company_description}</p>
      )}
      {(org.org_purpose || org.business_activity) && (
        <p className="text-sm text-slate-600">
          {org.org_purpose && (
            <span className="mr-3">{t(`bp.purpose.${org.org_purpose}`)}</span>
          )}
          {org.business_activity && (
            <span>
              {t('bp.activity')}:{' '}
              {ACTIVITY_CODES.includes(org.business_activity)
                ? t(`bp.activity.${org.business_activity}`)
                : org.business_activity}
            </span>
          )}
        </p>
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
