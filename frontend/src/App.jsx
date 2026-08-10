import { useState } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import { LanguageProvider, useLanguage } from './i18n/index.jsx'
import LanguageToggle from './components/LanguageToggle.jsx'
import HomePage from './pages/HomePage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'

// Lightweight client-side view switch for the MVP (no router dependency yet).
function AppShell() {
  const { t } = useLanguage()
  const { status } = useAuth()
  const [view, setView] = useState('home') // 'home' | 'login' | 'register'

  const goHome = () => setView('home')
  const goLogin = () => setView('login')
  const goRegister = () => setView('register')

  // Protected: the Dashboard only renders when authenticated.
  if (status === 'authed') {
    return (
      <div>
        <Header />
        <DashboardPage />
      </div>
    )
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <p className="text-slate-500">{t('common.loading')}</p>
      </div>
    )
  }

  // Guest
  return (
    <div>
      <Header onHome={goHome} onLogin={goLogin} onRegister={goRegister} />
      {view === 'login' && <LoginPage onSwitchToRegister={goRegister} />}
      {view === 'register' && <RegisterPage onSwitchToLogin={goLogin} />}
      {view === 'home' && (
        <HomePage onCreateAccount={goRegister} onLogin={goLogin} />
      )}
    </div>
  )
}

function Header({ onHome, onLogin, onRegister }) {
  const { t } = useLanguage()
  const { status, logout } = useAuth()
  const authed = status === 'authed'

  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <button
          type="button"
          onClick={onHome}
          className="text-base font-bold text-slate-900"
        >
          {t('app.title')}
        </button>

        <div className="flex items-center gap-2">
          {authed ? (
            <button
              type="button"
              onClick={logout}
              className="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
            >
              {t('nav.logout')}
            </button>
          ) : (
            <>
              <button
                type="button"
                onClick={onHome}
                className="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
              >
                {t('nav.home')}
              </button>
              <button
                type="button"
                onClick={onLogin}
                className="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
              >
                {t('nav.login')}
              </button>
              <button
                type="button"
                onClick={onRegister}
                className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
              >
                {t('nav.register')}
              </button>
            </>
          )}
          <LanguageToggle />
        </div>
      </div>
    </header>
  )
}

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <AppShell />
      </AuthProvider>
    </LanguageProvider>
  )
}

export default App

