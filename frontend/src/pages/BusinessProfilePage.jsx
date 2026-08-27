// Business Profile (Company Settings) — optional company details for a
// workspace: registered address, RCCM number, tax ID and fiscal year start
// month. Reachable from the workspace home; NEVER required at creation time
// (Session 4's flow stays simple and not every user is a registered business).
//
// Fiscal-year note: fiscal_year_start_month is real period math, not display —
// it shifts the trial balance's opening/movement split (see
// trial_balance_service._fiscal_year_start). Default January = calendar year.
import { useEffect, useState } from 'react'
import { fetchOrganization, updateOrganization } from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'

const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1)

export default function BusinessProfilePage({ org, onBack, onSaved }) {
  const { t } = useLanguage()
  const [form, setForm] = useState({
    registered_address: org.registered_address || '',
    rccm_number: org.rccm_number || '',
    tax_id: org.tax_id || '',
    fiscal_year_start_month: org.fiscal_year_start_month || 1,
  })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState(null)

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
          fiscal_year_start_month: fresh.fiscal_year_start_month || 1,
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
    setForm((f) => ({ ...f, [key]: value }))
  }

  async function onSave(e) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    setSaved(false)
    try {
      // PATCH always sends every key: empty strings clear a field back to NULL
      // on the backend (a business that de-registers can blank its RCCM).
      const updated = await updateOrganization(org.id, {
        registered_address: form.registered_address,
        rccm_number: form.rccm_number,
        tax_id: form.tax_id,
        fiscal_year_start_month: Number(form.fiscal_year_start_month),
      })
      onSaved?.(updated)
      setSaved(true)
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
      <button
        type="button"
        onClick={onBack}
        className="text-sm font-medium text-slate-600 hover:text-slate-900"
      >
        ← {t('tx.backToOrg')}
      </button>

      <h2 className="mt-4 text-2xl font-bold text-slate-900">{t('bp.title')}</h2>
      <p className="mt-1 text-sm text-slate-600">{t('bp.subtitle')}</p>

      <form onSubmit={onSave} className="mt-6 space-y-4">
        <div>
          <label htmlFor="bp-address" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.address')}
          </label>
          <textarea
            id="bp-address"
            rows={2}
            value={form.registered_address}
            onChange={(e) => setField('registered_address', e.target.value)}
            placeholder={t('bp.addressPlaceholder')}
            className={inputCls}
          />
        </div>

        <div>
          <label htmlFor="bp-rccm" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.rccm')}
          </label>
          <input
            id="bp-rccm"
            type="text"
            value={form.rccm_number}
            onChange={(e) => setField('rccm_number', e.target.value)}
            className={inputCls}
          />
        </div>

        <div>
          <label htmlFor="bp-taxid" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.taxId')}
          </label>
          <input
            id="bp-taxid"
            type="text"
            value={form.tax_id}
            onChange={(e) => setField('tax_id', e.target.value)}
            className={inputCls}
          />
        </div>

        <div>
          <label htmlFor="bp-fysm" className="mb-1 block text-sm font-medium text-slate-700">
            {t('bp.fiscalYearStart')}
          </label>
          <select
            id="bp-fysm"
            value={form.fiscal_year_start_month}
            onChange={(e) => setField('fiscal_year_start_month', e.target.value)}
            className={inputCls}
          >
            {MONTHS.map((m) => (
              <option key={m} value={m}>
                {m} — {t(`bp.month.${m}`)}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-slate-500">{t('bp.fiscalYearHint')}</p>
        </div>

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