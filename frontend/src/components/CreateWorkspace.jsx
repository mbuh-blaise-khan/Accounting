// "Create your first workspace" flow: name, framework (with a one-line
// plain-language description per language), currency (default XAF), plus a
// "use a sample demo business" option that creates an is_demo workspace
// (its account seed data arrives in Session 5).
import { useState } from 'react'
import { createOrganization } from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'

export default function CreateWorkspace({ frameworks, onCreated }) {
  const { t, lang } = useLanguage()
  const [name, setName] = useState('')
  const [framework, setFramework] = useState(frameworks[0]?.code || 'OHADA')
  const [currency, setCurrency] = useState('XAF')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  function description(fw) {
    return lang === 'fr' ? fw.description_fr : fw.description_en
  }

  async function create(payload) {
    setError(null)
    setBusy(true)
    try {
      // Hand the created org back so the dashboard can send NEW workspaces
      // straight into the mandatory Business Profile step.
      const created = await createOrganization(payload)
      onCreated(created)
    } catch {
      setError(t('workspace.error'))
    } finally {
      setBusy(false)
    }
  }

  function handleSubmit(e) {
    e.preventDefault()
    create({ name, framework, currency })
  }

  function handleDemo() {
    create({
      name: 'Sample Demo Business',
      framework,
      currency,
      is_demo: true,
    })
  }

  const inputCls =
    'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none'

  return (
    <div className="mx-auto w-full max-w-lg bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-bold text-slate-900">{t('workspace.title')}</h3>
      <p className="mt-1 text-sm text-slate-600">{t('workspace.subtitle')}</p>

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
          {error}
        </p>
      )}

      <form onSubmit={handleSubmit} className="mt-5 space-y-4">
        <label className="block">
          <span className="text-sm font-medium text-slate-700">{t('workspace.name')}</span>
          <input
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t('workspace.namePlaceholder')}
            className={inputCls}
          />
        </label>

        <div>
          <span className="text-sm font-medium text-slate-700">{t('workspace.framework')}</span>
          <div className="mt-2 space-y-2">
            {frameworks.map((fw) => (
              <label
                key={fw.code}
                className={`block cursor-pointer rounded-lg border px-4 py-3 ${
                  framework === fw.code
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-slate-300'
                }`}
              >
                <span className="flex items-center">
                  <input
                    type="radio"
                    name="framework"
                    value={fw.code}
                    checked={framework === fw.code}
                    onChange={() => setFramework(fw.code)}
                    className="mr-2"
                  />
                  <span className="font-semibold text-slate-800">{fw.name}</span>
                </span>
                <span className="mt-1 block text-sm text-slate-600">{description(fw)}</span>
              </label>
            ))}
          </div>
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">{t('workspace.currency')}</span>
          <input
            type="text"
            required
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            className={inputCls}
            placeholder="XAF"
          />
        </label>

        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {t('workspace.create')}
        </button>
      </form>

      <div className="mt-4 border-t border-slate-200 pt-4">
        <button
          type="button"
          onClick={handleDemo}
          disabled={busy}
          className="w-full rounded-lg border border-blue-600 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 disabled:opacity-60"
        >
          {t('workspace.demo')}
        </button>
        <p className="mt-2 text-center text-xs text-slate-500">{t('workspace.demoHint')}</p>
      </div>
    </div>
  )
}