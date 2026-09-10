// Choice hub — "How do you want to get started?" (Session 13 redesign).
//
// EVERY user, new or existing, lands here immediately after logging in (it is
// NOT gated on whether they already have workspaces). Two paths only — the old
// "Both" option was removed — plus "Show me around", which now opens a short
// WelcomeTour (orientation) whose final step creates the sample demo business
// and enters the practice space.
//
// A back arrow is intentionally NOT needed here: the hub is the top of the
// authenticated flow (the persistent way back is the "← Back to start"
// header action available inside Learn and Practice).
import { useState } from 'react'
import { useLanguage } from '../i18n/index.jsx'
import Callout from '../components/Callout.jsx'
import WelcomeTour from '../components/WelcomeTour.jsx'

export default function OnboardingChoicePage({ onChoice, onShowMeAround, practiceReady = true }) {
  const { t } = useLanguage()
  const [selected, setSelected] = useState(null)
  const [showTour, setShowTour] = useState(false)

  const choices = [
    {
      id: 'learn',
      icon: '📚',
      title: t('choice.learn'),
      description: t('choice.learnDesc'),
      bullets: [
        t('choice.learnBullet1'),
        t('choice.learnBullet2'),
        t('choice.learnBullet3'),
      ],
      cta: t('choice.learnCta'),
      ready: true,
      color: 'border-blue-200 bg-blue-50 hover:border-blue-400 hover:shadow-blue-100',
      accent: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      id: 'practice',
      icon: '💼',
      title: t('choice.practice'),
      description: t('choice.practiceDesc'),
      bullets: [
        t('choice.practiceBullet1'),
        t('choice.practiceBullet2'),
        t('choice.practiceBullet3'),
      ],
      cta: t('choice.practiceCta'),
      ready: practiceReady,
      color: 'border-green-200 bg-green-50 hover:border-green-400 hover:shadow-green-100',
      accent: 'text-green-600',
      bg: 'bg-green-50',
    },
  ]

  const handleChoice = (choiceId) => {
    setSelected(choiceId)
    onChoice(choiceId)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white px-4 py-16 md:py-24">
      <div className="mx-auto max-w-4xl">
        <div className="mb-12 text-center">
          <h1 className="mb-4 text-4xl font-bold text-slate-800 md:text-5xl">
            {t('choice.title')}
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-slate-500">
            {t('choice.subtitle')}
          </p>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
          {choices.map((choice) => (
            <div
              key={choice.id}
              className={`relative cursor-pointer rounded-2xl border-2 p-6 transition-all duration-300 ${choice.color} ${
                selected === choice.id ? 'ring-2 ring-offset-2 ' + choice.accent : ''
              } hover:-translate-y-1 hover:shadow-xl`}
              onClick={() => handleChoice(choice.id)}
            >
              {!choice.ready && (
                <div className="absolute right-4 top-4">
                  <div className="h-5 w-5 animate-spin rounded-full border-b-2 border-slate-600"></div>
                </div>
              )}
              <div className="mb-4 text-5xl">{choice.icon}</div>
              <h3 className={`mb-2 text-xl font-bold ${choice.accent}`}>{choice.title}</h3>
              <p className="mb-4 text-sm text-slate-600">{choice.description}</p>
              <ul className="mb-6 space-y-2">
                {choice.bullets.map((bullet, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-slate-600">
                    <span className="mt-1 text-slate-300">•</span>
                    <span>{bullet}</span>
                  </li>
                ))}
              </ul>
              <button
                type="button"
                className={`w-full rounded-lg py-2.5 font-medium transition-all ${choice.bg} ${choice.accent} hover:opacity-80`}
                onClick={() => handleChoice(choice.id)}
              >
                {choice.cta} →
              </button>
            </div>
          ))}
        </div>

        <div className="mx-auto max-w-2xl">
          <Callout variant="info" title={t('choice.calloutTitle')}>
            {t('choice.calloutText')}
          </Callout>
        </div>

        <div className="mt-6 text-center">
          <button
            type="button"
            onClick={() => setShowTour(true)}
            className="text-sm text-slate-500 underline-offset-2 transition-colors hover:text-slate-700 hover:underline"
          >
            {t('choice.showMeAround')} 🚀
          </button>
        </div>
      </div>

      {showTour && (
        <WelcomeTour
          onFinish={async (action) => {
            setShowTour(false)
            if (action === 'demo') await onShowMeAround()
          }}
        />
      )}
    </div>
  )
}
