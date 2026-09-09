import { useState } from 'react';
import { useLanguage } from '../i18n';
import Callout from '../components/Callout';
import { createOrganization } from '../services/api';

export default function OnboardingChoicePage({ onChoice, onShowMeAround }) {
  const { t } = useLanguage();
  const [selected, setSelected] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const choices = [
    {
      id: 'learn',
      icon: '📚',
      title: t('choice.learn'),
      description: t('choice.learnDesc'),
      bullets: [
        t('choice.learnBullet1'),
        t('choice.learnBullet2'),
        t('choice.learnBullet3')
      ],
      cta: t('choice.learnCta'),
      color: 'border-blue-200 bg-blue-50 hover:border-blue-400 hover:shadow-blue-100',
      accent: 'text-blue-600',
      bg: 'bg-blue-50'
    },
    {
      id: 'practice',
      icon: '💼',
      title: t('choice.practice'),
      description: t('choice.practiceDesc'),
      bullets: [
        t('choice.practiceBullet1'),
        t('choice.practiceBullet2'),
        t('choice.practiceBullet3')
      ],
      cta: t('choice.practiceCta'),
      color: 'border-green-200 bg-green-50 hover:border-green-400 hover:shadow-green-100',
      accent: 'text-green-600',
      bg: 'bg-green-50'
    },
    {
      id: 'both',
      icon: '🔄',
      title: t('choice.both'),
      description: t('choice.bothDesc'),
      bullets: [
        t('choice.bothBullet1'),
        t('choice.bothBullet2'),
        t('choice.bothBullet3')
      ],
      cta: t('choice.bothCta'),
      color: 'border-purple-200 bg-purple-50 hover:border-purple-400 hover:shadow-purple-100',
      accent: 'text-purple-600',
      bg: 'bg-purple-50'
    }
  ];

  const handleChoice = async (choiceId) => {
    setSelected(choiceId);
    setIsLoading(true);
    
    if (choiceId === 'both') {
      try {
        // Auto-create demo workspace
        const org = await createOrganization({
          name: `${t('demo.workspaceName')} - ${new Date().toLocaleDateString()}`,
          framework: 'OHADA',
          currency: 'XAF',
          is_demo: true
        });
        onChoice(choiceId, { workspace: org, demo: true });
      } catch (error) {
        console.error('Failed to create demo workspace:', error);
        onChoice(choiceId, { demo: false });
      }
    } else {
      onChoice(choiceId);
    }
    setIsLoading(false);
  };

  const handleShowMeAround = () => {
    // Auto-create demo workspace with sample data
    onShowMeAround();
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white px-4 py-16 md:py-24">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-800 mb-4">
            {t('choice.title')}
          </h1>
          <p className="text-lg text-slate-500 max-w-2xl mx-auto">
            {t('choice.subtitle')}
          </p>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {choices.map((choice) => (
            <div
              key={choice.id}
              className={`relative rounded-2xl border-2 p-6 transition-all duration-300 cursor-pointer ${choice.color} ${
                selected === choice.id ? 'ring-2 ring-offset-2 ' + choice.accent : ''
              } hover:shadow-xl hover:-translate-y-1`}
              onClick={() => !isLoading && handleChoice(choice.id)}
            >
              {isLoading && selected === choice.id && (
                <div className="absolute top-4 right-4">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-slate-600"></div>
                </div>
              )}
              <div className="text-5xl mb-4">{choice.icon}</div>
              <h3 className={`text-xl font-bold ${choice.accent} mb-2`}>
                {choice.title}
              </h3>
              <p className="text-slate-600 text-sm mb-4">
                {choice.description}
              </p>
              <ul className="space-y-2 mb-6">
                {choice.bullets.map((bullet, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-slate-600">
                    <span className="text-slate-300 mt-1">•</span>
                    <span>{bullet}</span>
                  </li>
                ))}
              </ul>
              <button
                className={`w-full py-2.5 rounded-lg font-medium transition-all ${choice.bg} ${choice.accent} hover:opacity-80`}
                onClick={() => !isLoading && handleChoice(choice.id)}
                disabled={isLoading}
              >
                {choice.cta} →
              </button>
            </div>
          ))}
        </div>

        {/* Callout Section */}
        <div className="max-w-2xl mx-auto">
          <Callout variant="info" title={t('choice.calloutTitle')}>
            {t('choice.calloutText')}
          </Callout>
        </div>

        {/* Show Me Around Button */}
        <div className="text-center mt-6">
          <button
            onClick={handleShowMeAround}
            className="text-sm text-slate-500 hover:text-slate-700 underline-offset-2 hover:underline transition-colors"
          >
            {t('choice.showMeAround')} 🚀
          </button>
        </div>
      </div>
    </div>
  );
}