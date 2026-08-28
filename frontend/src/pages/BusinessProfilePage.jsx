// Business Profile (Company Settings) — registered address, RCCM number, tax
// ID and fiscal year start month for a workspace.
//
// REVERSAL of the previous "purely optional" decision: the Business Profile is
// now a MANDATORY step immediately after workspace creation. A NEW workspace
// is redirected straight into this form and cannot reach the Chart of Accounts
// or any transaction page until it is completed — with a LEARNER EXEMPTION: a
// clearly-labeled checkbox for genuine beginners without a registered business
// makes the RCCM/tax ID fields optional, while registered_address and
// fiscal_year_start_month stay required for everyone (every workspace has SOME
// location and SOME fiscal year, even an informal one). Existing pre-change
// organizations (fields were optional before) are NOT hard-blocked — they see
// a dismissible completion banner instead (WorkSpace in DashboardPage). The
// database columns remain nullable on purpose: the mandate is a frontend flow
// rule, tested in utils/profile.js (`npm run test:profile`).
//
// Fiscal-year note: fiscal_year_start_month is real period math, not display —
// it shifts the trial balance's opening/movement split (see
// trial_balance_service._fiscal_year_start). January = calendar year.
import { useEffect, useState } from 'react'
import { fetchOrganization, updateOrganization } from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'

const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1)

export default function BusinessProfilePage({ org, onBack, onSaved, onDone, mandatory = false }) {
  const { t } = useLanguage()
  const [form, setForm] = useState({
    registered_address: org.registered_address || '',
    rccm_number: org.rccm_number || '',
    tax_id: org.tax_id || '',
    // Mandatory step: NO silent January default — the month must be picked
    // explicitly (even when January really is the answer). The settings-page
    // mode keeps the sensible default for quick edits.
    fiscal_year_start_month: mandatory ? '' : (org.fiscal_year_start_month || 1),
  })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState(null)
  // Learner exemption: checked -> RCCM/tax ID become optional (inputs disabled,
  // values cleared); address + fiscal year stay required either way.
  const [learner, setLearner] = useState(false)
  // Localized labels of unfilled required fields (mandatory step validation).
  const [missing, setMissing] = useState(null)

  // Reload so the form reflects the saved state even if the dashboard's copy
  // of the org is stale.
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchOrganization(org.id)
      .then((fresh) => {
        if (cancelled) return
        setForm({
          registered_address: fresh.registered_address || '',
          rccm_number: fresh.rccm_number || '',
          tax_id: fresh.tax_id || '',
          fiscal_year_start_month: mandatory ? '' : (fresh.fiscal_year_start_month || 1),
        })
      })
      .catch(() => {}) // keep the props-based values on failure
      .finally(() => !cancelled && setLoading(false))
    return () => {
      cancelled = true
    }
  }, [org.id])

  function setField(key, value) {
    setSaved(false)
    setMissing(null)
    setForm((f) => ({ ...f, [key]: value }))
  }

  async function onSave(e) {
    e.preventDefault()
    setSaved(false)
    setError(null)

    // Mandatory step: enforce the required fields client-side BEFORE the API
    // call. Address + fiscal month are required for EVERYONE; RCCM/tax ID are
    // required UNLESS the learner exemption is checked.
    if (mandatory) {
      const notFilled = []
      if (!String(form.registered_address).trim()) notFilled.push(t('bp.address'))
      if (!form.fiscal_year_start_month) notFilled.push(t('bp.fiscalYearStart'))
      if (!learner) {
        if (!String(form.rccm_number).trim()) notFilled.push(t('bp.rccm'))
        if (!String(form.tax_id).trim()) notFilled.push(t('bp.taxId'))
      }
      if (notFilled.length > 0) {
        setMissing(notFilled)
        return
      }
    }

    setSaving(true)
    try {
      // PATCH always sends every key: empty strings clear a field back to NULL
      // on the backend (a business that de-registers can blank its RCCM). With
      // the learner exemption the registration fields are sent empty.
      const updated = await updateOrganization(org.id, {
        registered_address: form.registered_address,
        rccm_number: learner ? '' : form.rccm_number,
        tax_id: learner ? '' : form.tax_id,
        fiscal_year_start_month: Number(form.fiscal_year_start_month),
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

        {/* Learner exemption: no registered business yet -> RCCM/tax ID optional */}
        <label
          htmlFor="bp-learner"
          className="flex items-start gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2"
        >
          <input
            id="bp-learner"
            type="checkbox"
            checked={learner}
            onChange={(e) => {
              setLearner(e.target.checked)
              setSaved(false)
              setMissing(null)
            }}
            className="mt-0.5"
          />
          <span className="text-sm text-slate-700">{t('bp.learner')}</span>
        </label>

        <div>
          <label htmlFor="bp-rccm" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.rccm')} {!learner && <span className="text-red-500">*</span>}
          </label>
          <input
            id="bp-rccm"
            type="text"
            value={form.rccm_number}
            onChange={(e) => setField('rccm_number', e.target.value)}
            placeholder={t('bp.rccmPlaceholder')}
            disabled={learner}
            className={`${inputCls}${learner ? ' bg-slate-100 text-slate-400' : ''}`}
          />
        </div>

        <div>
          <label htmlFor="bp-taxid" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.taxId')} {!learner && <span className="text-red-500">*</span>}
          </label>
          <input
            id="bp-taxid"
            type="text"
            value={form.tax_id}
            onChange={(e) => setField('tax_id', e.target.value)}
            placeholder={t('bp.taxIdPlaceholder')}
            disabled={learner}
            className={`${inputCls}${learner ? ' bg-slate-100 text-slate-400' : ''}`}
          />
          {learner && <p className="mt-1 text-xs text-slate-500">{t('bp.learnerNote')}</p>}
        </div>

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