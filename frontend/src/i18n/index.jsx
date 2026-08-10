// Lightweight i18n: language state + a t() function backed by en/fr JSON.
// Strings live outside app logic (per .clinerules) in src/i18n/*.json.
import { createContext, useContext, useEffect, useState } from 'react'
import en from './en.json'
import fr from './fr.json'

const messages = { en, fr }
const STORAGE_KEY = 'uap_lang'

const LanguageContext = createContext(null)

function initialLang() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved === 'en' || saved === 'fr') return saved
  } catch {
    /* storage unavailable */
  }
  return 'en'
}

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(initialLang)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, lang)
    } catch {
      /* ignore */
    }
  }, [lang])

  const t = (key) =>
    (messages[lang] && messages[lang][key]) ||
    (messages.en && messages.en[key]) ||
    key

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage must be used within LanguageProvider')
  return ctx
}
