// WelcomeTour — Part 5 orientation: a lightweight 3-step modal/stepper shown
// from the choice hub's "Show me around" action. Pure presentation over the
// existing UI patterns (modal + buttons); no new framework, no AI chat-bot
// (the AI help-bot is deliberately deferred to a future session).
//
// onFinish('demo') asks the parent to create the sample demo business and
// enter the practice space; onFinish('close') just dismisses the tour.
import { useState } from 'react'
import { useLanguage } from '../i18n/index.jsx'

export default function WelcomeTour({ onFinish }) {
  const { t } = useLanguage()
  const [step, setStep] = useState(0)
  const [creating, setCreating] = useState(false)

  const steps = [
    {
      icon: '👋',
      title: t('tour.welcomeTitle'),
      text: t('tour.welcomeText'),
    },
    {
      icon: '📚',
      title: t('tour.learnTitle'),
      text: t('tour.learnText'),
    },
    {
      icon: '💼',
      title: t('tour.practiceTitle'),
      text: t('tour.practiceText'),
    },
  ]
  const last = step === steps.length - 1
  const current = steps[step]

  async function handleDemo() {
    if (creating) return
    setCreating(true)
    try {
      await onFinish('demo')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            {step + 1} / {steps.length}
          </span>
          <button
            type="button"
            onClick={() => onFinish('close')}
            className="rounded-lg px-2 py-1 text-sm text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            {t('tour.skip')} ✕
          </button>
        </div>

        <div className="mt-3 text-5xl" aria-hidden="true">
          {current.icon}
        </div>
        <h3 className="mt-3 text-xl font-bold text-slate-900">{current.title}</h3>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">{current.text}</p>

        <div className="mt-5 flex items-center justify-between">
          <div className="flex gap-1.5" aria-hidden="true">
            {steps.map((_, i) => (
              <span
                key={i}
                className={`h-2 w-2 rounded-full ${i === step ? 'bg-blue-600' : 'bg-slate-200'}`}
              />
            ))}
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              disabled={step === 0}
              className="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-40"
            >
              ← {t('tour.back')}
            </button>
            {!last && (
              <button
                type="button"
                onClick={() => setStep(step + 1)}
                className="rounded-lg bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
              >
                {t('tour.next')} →
              </button>
            )}
          </div>
        </div>

        {last && (
          <button
            type="button"
            onClick={handleDemo}
            disabled={creating}
            className="mt-4 w-full rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
          >
            {creating ? '…' : t('tour.ctaDemo')}
          </button>
        )}
      </div>
    </div>
  )
}
