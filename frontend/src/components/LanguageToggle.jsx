// Header language toggle: EN <-> FR with an instant switch (no page reload).
// When a user is signed in, the preference is persisted per-user via PATCH /me.
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../i18n/index.jsx'

export default function LanguageToggle() {
  const { lang, setLang } = useLanguage()
  const { user, setUserLanguage } = useAuth()

  function handleToggle() {
    const next = lang === 'en' ? 'fr' : 'en'
    setLang(next)
    if (user) setUserLanguage(next)
  }

  return (
    <button
      type="button"
      onClick={handleToggle}
      aria-label="Toggle language"
      className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-semibold text-slate-700 hover:bg-slate-100"
    >
      {lang === 'en' ? 'FR' : 'EN'}
    </button>
  )
}
