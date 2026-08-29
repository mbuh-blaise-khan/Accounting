// Business Profile (Company Settings) — identity, country, legal form,
// registered address, RCCM number, tax ID, fiscal year start month, plus the
// Business Profile "Session 2" descriptive fields: ORGANIZATION PURPOSE,
// BUSINESS ACTIVITY / SECTOR, ACCOUNTING BASIS (informational only) and a
// free-text COMPANY DESCRIPTION.
//
// PART 2 (identity-aware): the form starts with WHO you are — a clearly-labeled
// identity choice (learner / unregistered_business / registered_business) that
// decides what is required next:
//   learner:               country + address + fiscal year; RCCM/tax NOT shown;
//                          legal form skippable via the explicit
//                          "Not applicable" option.
//   unregistered_business: country + address + legal form + fiscal year;
//                          RCCM/tax optional (usable later).
//   registered_business:   everything above PLUS RCCM + tax ID (all required).
// Country is a SEARCHABLE dropdown restricted to the org's framework: OHADA =
// the 17 member states only (see backend/app/accounting/identity_reference.py
// and the GET /organizations/identity-options endpoint); IFRS = the full
// international list. The framework itself is IMMUTABLE after creation.
//
// MANDATORY step reversal: the Business Profile is still a required step right
// after workspace creation (a NEW workspace can't use the app until the
// blocking fields — address + fiscal month — are saved), but the old standalone
// "learner exemption" checkbox is REPLACED by the identity_type radios above:
// one clear mechanism, not two overlapping ones. Existing pre-change
// organizations are NOT hard-blocked (dismissible banner instead; see WorkSpace
// in DashboardPage). The DB columns remain nullable on purpose — the mandate is
// a frontend flow rule mirrored server-side in
// organization_service.update_business_profile, tested in utils/profile.js.
//
// Fiscal-year note: fiscal_year_start_month is real period math (it shifts the
// trial balance's opening/movement split). January = calendar year.
//
// SESSION 2 descriptive fields — ALL optional; they NEVER block saving and
// NEVER change any accounting calculation:
//   - org_purpose: fixed enum values (mirrors backend OrgPurpose), purely
//     informational. NOTE: the backend PATCH treats null as "no change" and
//     has no enum-clear path yet, so a chosen purpose can be CHANGED but not
//     UNSET from here (text fields do clear — blank strings are normalized
//     to NULL server-side).
//   - business_activity: fixed sectors are stored as the CATEGORY CODE
//     (translated back to a localized label at display time — see
//     ReportHeader); choosing "Other" reveals a free-text field and stores
//     that text instead (a bare "OTHER" sentinel is rejected server-side,
//     so it is never sent).
//   - accounting_basis: accrual (default) / cash radio WITH a visible note
//     that it is informational only — the posting engine is accrual-based
//     and this value never affects any calculation in this version.
//   - company_description: free text, max 1000 characters.
import { useEffect, useState } from 'react'
import { fetchIdentityOptions, fetchOrganization, updateOrganization } from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'
import SearchSelect from '../components/SearchSelect.jsx'

const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1)

// Fixed business-activity sectors (mirrors the `bp.activity.*` i18n keys).
// Stored in `business_activity` as the CODE for these; "other" is a UI-only
// sentinel that switches to the free-text field.
const ACTIVITY_SECTORS = [
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
  'other',
]

// Organization purposes (mirrors backend OrgPurpose enum + `bp.purpose.*` keys).
const PURPOSES = ['for_profit', 'non_profit', 'ngo_association', 'government']

// A saved `business_activity` is either a known sector code or free text
// ("Other"). Split it back into (select value, other-text) for the form.
function splitActivityValue(raw) {
  if (!raw) return { code: '', text: '' }
  if (ACTIVITY_SECTORS.includes(raw)) return { code: raw, text: '' }
  return { code: 'other', text: raw }
}

export default function BusinessProfilePage({ org, onBack, onSaved, onDone, mandatory = false }) {
  const { t, lang } = useLanguage()
  // identity_type is REQUIRED for everyone (Part 2). country is required for
  // every identity; legal_form for the two business identities; rccm/tax only
  // for registered_business (hidden entirely for learner). The Session 2
  // descriptive fields are OPTIONAL for every identity.
  const initialActivity = splitActivityValue(org.business_activity)
  const [form, setForm] = useState({
    identity_type: org.identity_type || '',
    country: org.country || '',
    legal_form: org.legal_form || '',
    registered_address: org.registered_address || '',
    rccm_number: org.rccm_number || '',
    tax_id: org.tax_id || '',
    // Mandatory step: NO silent January default — the month must be picked
    // explicitly (even when January really is the answer). The settings-page
    // mode keeps the sensible default for quick edits.
    fiscal_year_start_month: mandatory ? '' : (org.fiscal_year_start_month || 1),
    // Session 2 descriptive fields (all optional; accounting_basis defaults
    // to accrual — the backend default too).
    org_purpose: org.org_purpose || '',
    business_activity: initialActivity.code,
    activity_other_text: initialActivity.text,
    accounting_basis: org.accounting_basis || 'accrual',
    company_description: org.company_description || '',
  })
  const [identityOptions, setIdentityOptions] = useState({ countries: [], legal_forms: [] })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState(null)
  // Localized labels of unfilled required fields (validation message).
  const [missing, setMissing] = useState(null)

  const isLearner = form.identity_type === 'learner'
  const isRegistered = form.identity_type === 'registered_business'
  const isBusiness = form.identity_type === 'unregistered_business' || isRegistered

  // Reload so the form reflects the saved state even if the dashboard's copy
  // of the org is stale.
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchOrganization(org.id)
      .then((fresh) => {
        if (cancelled) return
        const freshActivity = splitActivityValue(fresh.business_activity)
        setForm({
          identity_type: fresh.identity_type || '',
          country: fresh.country || '',
          legal_form: fresh.legal_form || '',
          registered_address: fresh.registered_address || '',
          rccm_number: fresh.rccm_number || '',
          tax_id: fresh.tax_id || '',
          fiscal_year_start_month: mandatory ? '' : (fresh.fiscal_year_start_month || 1),
          org_purpose: fresh.org_purpose || '',
          business_activity: freshActivity.code,
          activity_other_text: freshActivity.text,
          accounting_basis: fresh.accounting_basis || 'accrual',
          company_description: fresh.company_description || '',
        })
      })
      .catch(() => {}) // keep the props-based values on failure
      .finally(() => !cancelled && setLoading(false))
    return () => {
      cancelled = true
    }
  }, [org.id])

  // Fetch the framework-aware dropdown data: country list (OHADA = only the 17
  // member states; IFRS = full international list) + legal-form options with
  // plain-language descriptions. Single source of truth: the backend endpoint
  // (the frontend does not duplicate ~200 country entries).
  useEffect(() => {
    let cancelled = false
    fetchIdentityOptions(org.framework)
      .then((opts) => {
        if (!cancelled) setIdentityOptions(opts)
      })
      .catch(() => {}) // keep empty lists on failure; the form is still usable
    return () => {
      cancelled = true
    }
  }, [org.framework])

  function setField(key, value) {
    setSaved(false)
    setMissing(null)
    setForm((f) => ({ ...f, [key]: value }))
  }

  async function onSave(e) {
    e.preventDefault()
    setSaved(false)
    setError(null)

    // Identity-driven required fields (client mirror of the backend's 422
    // rules + frontend/src/utils/profile.js). country for EVERY identity;
    // legal_form for the two business identities; RCCM + tax ID only for a
    // fully registered business. Enforced in BOTH modes — the API would reject
    // a registered_business save missing those fields anyway.
    // The Session 2 descriptive fields (purpose / activity / basis /
    // description) are deliberately NOT validated as required — they never
    // block saving.
    const notFilled = []
    if (!form.identity_type) notFilled.push(t('bp.identityType'))
    if (!String(form.country || '').trim()) notFilled.push(t('bp.country'))
    if (isBusiness && !String(form.legal_form || '').trim()) notFilled.push(t('bp.legalForm'))
    if (isRegistered) {
      if (!String(form.rccm_number).trim()) notFilled.push(t('bp.rccm'))
      if (!String(form.tax_id).trim()) notFilled.push(t('bp.taxId'))
    }
    // Mandatory step only: the profile-BLOCKING fields (address + fiscal
    // month) are required for everyone to finish onboarding. The settings page
    // lets a pre-change org save partial data (the banner nudges instead).
    if (mandatory) {
      if (!String(form.registered_address).trim()) notFilled.push(t('bp.address'))
      if (!form.fiscal_year_start_month) notFilled.push(t('bp.fiscalYearStart'))
    }
    if (notFilled.length > 0) {
      setMissing(notFilled)
      return
    }

    setSaving(true)
    try {
      // PATCH always sends every key: empty strings clear a registration value
      // back to NULL; null for optional identity fields is skipped. A learner
      // never sends RCCM/tax ID (values cleared).
      //
      // Session 2 mapping:
      //   org_purpose: '' would fail the backend enum validation, so an
      //     unset purpose is sent as null (server-side "no change" — the
      //     backend has no enum-clear path yet, see header note).
      //   business_activity: the sector CODE, or the free-text description
      //     when "Other" is chosen ('' when that text is empty — which
      //     clears). A bare "other"/"OTHER" sentinel is NEVER sent (the
      //     backend rejects it with 422).
      //   accounting_basis: always sent; defaults to accrual.
      //   company_description: '' clears (blank strings normalize to NULL).
      const updated = await updateOrganization(org.id, {
        identity_type: form.identity_type,
        country: form.country || null,
        legal_form: form.legal_form || null,
        registered_address: form.registered_address,
        rccm_number: isLearner ? '' : form.rccm_number,
        tax_id: isLearner ? '' : form.tax_id,
        fiscal_year_start_month: Number(form.fiscal_year_start_month),
        org_purpose: form.org_purpose || null,
        business_activity:
          form.business_activity === 'other'
            ? form.activity_other_text.trim()
            : form.business_activity,
        accounting_basis: form.accounting_basis || 'accrual',
        company_description: form.company_description,
      })
      onSaved?.(updated)
      if (mandatory) {
        onDone?.() // profile complete -> back to workspace home (gate lifts)
      } else {
        setSaved(true)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const inputCls =
    'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none'

  // For a learner the legal-form dropdown is skippable: prepend the explicit
  // "not applicable" option (stored server-side as LEGAL_FORM_NOT_APPLICABLE).
  const legalFormOptions = (() => {
    const base = identityOptions.legal_forms || []
    if (!isLearner) return base
    return [
      {
        code: 'NOT_APPLICABLE',
        label: t('bp.legalFormNa'),
        description_en: t('bp.legalFormNaDesc'),
        description_fr: t('bp.legalFormNaDesc'),
      },
      ...base,
    ]
  })()

  // Business-activity dropdown options (localized labels; SearchSelect filters
  // as you type).
  const activityOptions = ACTIVITY_SECTORS.map((code) => ({
    code,
    label: t(`bp.activity.${code}`),
  }))

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      {!mandatory && (
        <button
          type="button"
          onClick={onBack}
          className="text-sm font-medium text-slate-600 hover:text-slate-900"
        >
          ← {t('tx.backToOrg')}
        </button>
      )}

      <h2 className="mt-4 text-2xl font-bold text-slate-900">
        {mandatory ? t('bp.mandatoryTitle') : t('bp.title')}
      </h2>
      <p className="mt-1 text-sm text-slate-600">
        {mandatory ? t('bp.mandatorySubtitle') : t('bp.subtitle')}
      </p>

      <form onSubmit={onSave} className="mt-6 space-y-4">
        <div>
          <label htmlFor="bp-address" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.address')} <span className="text-red-500">*</span>
          </label>
          <textarea
            id="bp-address"
            rows={2}
            required
            value={form.registered_address}
            onChange={(e) => setField('registered_address', e.target.value)}
            placeholder={t('bp.addressPlaceholder')}
            className={inputCls}
          />
        </div>

        {/* IDENTITY TYPE — decides what is required next */}
        <div role="radiogroup" aria-label={t('bp.identityType')}>
          <span className="mb-2 block text-sm font-medium text-slate-700">
            {t('bp.identityType')} <span className="text-red-500">*</span>
          </span>
          {[
            { value: 'learner', label: t('bp.identityLearner'), desc: t('bp.identityLearnerDesc') },
            { value: 'unregistered_business', label: t('bp.identityUnregistered'), desc: t('bp.identityUnregisteredDesc') },
            { value: 'registered_business', label: t('bp.identityRegistered'), desc: t('bp.identityRegisteredDesc') },
          ].map((opt) => (
            <label
              key={opt.value}
              className="mb-2 flex items-start gap-3 rounded-lg border border-slate-200 px-3 py-2 hover:bg-slate-50"
            >
              <input
                type="radio"
                name="bp-identity"
                value={opt.value}
                checked={form.identity_type === opt.value}
                onChange={() => setField('identity_type', opt.value)}
                className="mt-1"
              />
              <span>
                <span className="block text-sm font-medium text-slate-800">{opt.label}</span>
                <span className="block text-xs text-slate-500">{opt.desc}</span>
              </span>
            </label>
          ))}
        </div>

        {/* COUNTRY — searchable; for OHADA restricted to the 17 member states */}
        <div>
          <label htmlFor="bp-country" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.country')} <span className="text-red-500">*</span>
          </label>
          <SearchSelect
            id="bp-country"
            options={identityOptions.countries}
            value={form.country}
            onChange={(code) => setField('country', code)}
            placeholder={t('bp.countryPlaceholder')}
            getOptionLabel={(o) => (lang === 'fr' ? o.name_fr : o.name_en)}
            inputCls={inputCls}
            disabled={loading}
          />
        </div>

        {/* LEGAL FORM — searchable, framework-aware, with plain-language
            descriptions; learner gets an explicit "Not applicable" skip. */}
        <div>
          <label htmlFor="bp-legalform" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.legalForm')} {isBusiness && <span className="text-red-500">*</span>}
          </label>
          <SearchSelect
            id="bp-legalform"
            options={legalFormOptions}
            value={form.legal_form}
            onChange={(code) => setField('legal_form', code)}
            placeholder={t('bp.legalFormPlaceholder')}
            getOptionLabel={(o) => o.label}
            getOptionSub={(o) => (lang === 'fr' ? o.description_fr : o.description_en)}
            inputCls={inputCls}
            disabled={loading}
          />
          {isLearner && <p className="mt-1 text-xs text-slate-500">{t('bp.legalFormNaHint')}</p>}
        </div>

        {/* RCCM / TAX ID — only for business identities (hidden for learner) */}
        {!isLearner && (
          <>
            <div>
              <label htmlFor="bp-rccm" className="mb-1 block text-sm font-medium text-slate-700">
                {t('bp.rccm')} {isRegistered && <span className="text-red-500">*</span>}
              </label>
              <input
                id="bp-rccm"
                type="text"
                value={form.rccm_number}
                onChange={(e) => setField('rccm_number', e.target.value)}
                placeholder={t('bp.rccmPlaceholder')}
                className={inputCls}
              />
            </div>

            <div>
              <label htmlFor="bp-taxid" className="mb-1 block text-sm font-medium text-slate-700">
                {t('bp.taxId')} {isRegistered && <span className="text-red-500">*</span>}
              </label>
              <input
                id="bp-taxid"
                type="text"
                value={form.tax_id}
                onChange={(e) => setField('tax_id', e.target.value)}
                placeholder={t('bp.taxIdPlaceholder')}
                className={inputCls}
              />
            </div>
          </>
        )}

        <div>
          <label htmlFor="bp-fysm" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.fiscalYearStart')} <span className="text-red-500">*</span>
          </label>
          <select
            id="bp-fysm"
            required
            value={form.fiscal_year_start_month}
            onChange={(e) => setField('fiscal_year_start_month', e.target.value)}
            className={inputCls}
          >
            {/* Mandatory step: forces an EXPLICIT month selection (no silent
                January default). Disabled so it can't be re-picked. */}
            {form.fiscal_year_start_month === '' && (
              <option value="" disabled>
                {t('bp.fiscalPlaceholder')}
              </option>
            )}
            {MONTHS.map((m) => (
              <option key={m} value={m}>
                {m} — {t(`bp.month.${m}`)}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-500">{t('bp.fiscalYearHint')}</p>
        </div>

        {/* ORGANIZATION PURPOSE — optional, informational; 2-col grid on
            wider screens, stacked on a phone. Never blocks saving. */}
        <div role="radiogroup" aria-label={t('bp.purpose')}>
          <span className="mb-2 block text-sm font-medium text-slate-700">{t('bp.purpose')}</span>
          <div className="grid gap-2 sm:grid-cols-2">
            {PURPOSES.map((p) => (
              <label
                key={p}
                className="flex items-start gap-3 rounded-lg border border-slate-200 px-3 py-2 hover:bg-slate-50"
              >
                <input
                  type="radio"
                  name="bp-purpose"
                  value={p}
                  checked={form.org_purpose === p}
                  onChange={() => setField('org_purpose', p)}
                  className="mt-1"
                />
                <span className="text-sm text-slate-800">{t(`bp.purpose.${p}`)}</span>
              </label>
            ))}
          </div>
        </div>

        {/* BUSINESS ACTIVITY / SECTOR — optional, searchable dropdown.
            Fixed sectors store their CODE; "Other" reveals a free-text field
            whose content is stored instead. */}
        <div>
          <label htmlFor="bp-activity" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.activity')}
          </label>
          <SearchSelect
            id="bp-activity"
            options={activityOptions}
            value={form.business_activity}
            onChange={(code) => setField('business_activity', code)}
            placeholder={t('bp.activityPlaceholder')}
            getOptionLabel={(o) => o.label}
            inputCls={inputCls}
            disabled={loading}
          />
          {form.business_activity === 'other' && (
            <div className="mt-2">
              <label
                htmlFor="bp-activity-other"
                className="mb-1 block text-sm font-medium text-slate-700"
              >
                {t('bp.activityOther')}
              </label>
              <input
                id="bp-activity-other"
                type="text"
                maxLength={120}
                value={form.activity_other_text}
                onChange={(e) => setField('activity_other_text', e.target.value)}
                placeholder={t('bp.activityOtherPlaceholder')}
                className={inputCls}
              />
            </div>
          )}
          {form.business_activity && (
            <button
              type="button"
              onClick={() => {
                setField('business_activity', '')
                setField('activity_other_text', '')
              }}
              className="mt-1 text-xs font-medium text-slate-500 hover:text-slate-700"
            >
              ✕ {t('bp.clearSelection')}
            </button>
          )}
        </div>

        {/* ACCOUNTING BASIS — accrual/cash with one-line explanations.
            INFORMATIONAL ONLY (visible note below): it never changes how
            transactions are posted or reported in this version. */}
        <div role="radiogroup" aria-label={t('bp.basis')}>
          <span className="mb-2 block text-sm font-medium text-slate-700">{t('bp.basis')}</span>
          {[
            { value: 'accrual', label: t('bp.basisAccrual'), hint: t('bp.basisAccrualHint') },
            { value: 'cash', label: t('bp.basisCash'), hint: t('bp.basisCashHint') },
          ].map((opt) => (
            <label
              key={opt.value}
              className="mb-2 flex items-start gap-3 rounded-lg border border-slate-200 px-3 py-2 hover:bg-slate-50"
            >
              <input
                type="radio"
                name="bp-basis"
                value={opt.value}
                checked={form.accounting_basis === opt.value}
                onChange={() => setField('accounting_basis', opt.value)}
                className="mt-1"
              />
              <span>
                <span className="block text-sm font-medium text-slate-800">{opt.label}</span>
                <span className="block text-xs text-slate-500">{opt.hint}</span>
              </span>
            </label>
          ))}
          <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
            {t('bp.basisInfoNote')}
          </p>
        </div>
        {/* COMPANY DESCRIPTION — optional free text, max 1000 chars. */}
        <div>
          <label htmlFor="bp-description" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.description')}
          </label>
          <textarea
            id="bp-description"
            rows={3}
            maxLength={1000}
            value={form.company_description}
            onChange={(e) => setField('company_description', e.target.value)}
            placeholder={t('bp.descPlaceholder')}
            className={inputCls}
          />
          <p className="mt-1 text-right text-xs text-slate-400">
            {form.company_description.length}/1000
          </p>
        </div>

        {missing?.length > 0 && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
            {t('bp.requiredFields')} {missing.join(', ')}
          </p>
        )}

        {error && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}
        {saved && (
          <p className="rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-700">
            {t('bp.saved')}
          </p>
        )}

        <button
          type="submit"
          disabled={saving || loading}
          className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50 sm:w-auto"
        >
          {t('bp.save')}
        </button>
      </form>
    </div>
  )
}
