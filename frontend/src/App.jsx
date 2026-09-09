import { useState } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import { LanguageProvider, useLanguage } from './i18n/index.jsx'
import LanguageToggle from './components/LanguageToggle.jsx'
import Logo from './components/Logo.jsx'
import HomePage from './pages/HomePage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import OnboardingChoicePage from './pages/OnboardingChoicePage.jsx'
import LearnPage from './pages/LearnPage.jsx'
import { fetchOrganizations, createOrganization } from './services/api.js'

// Lightweight client-side view switch for the MVP (no router dependency yet).
function AppShell() {
  const { t } = useLanguage()
  const { status } = useAuth()
  const [view, setView] = useState('home') // 'home' | 'login' | 'register'
  const [onboardingState, setOnboardingState] = useState({
    orgs: null,        // null = loading, [] = no orgs, [...] = has orgs
    choice: null,      // null = not chosen, 'learn' | 'practice' | 'both'
    learnLessonId: null,
  })

  const goHome = () => setView('home')
  const goLogin = () => setView('login')
  const goRegister = () => setView('register')

  // After authentication, check if the user has any workspaces.
  // If not, show the 3-Tier Choice Screen.
  const checkWorkspaces = async () => {
    setOnboardingState((s) => ({ ...s, orgs: null }))
    try {
      const orgs = await fetchOrganizations()
      setOnboardingState((s) => ({ ...s, orgs }))
    } catch {
      setOnboardingState((s) => ({ ...s, orgs: [] }))
    }
  }

  // Handle the user's choice from the onboarding screen
  const handleChoice = async (choiceId, meta = {}) => {
    if (choiceId === 'learn') {
      // Learn mode — no workspace needed, go straight to lessons
      setOnboardingState((s) => ({ ...s, choice: choiceId }))
    } else if (choiceId === 'practice') {
      // Practice mode — let the user create/select a workspace via DashboardPage
      setOnboardingState((s) => ({ ...s, choice: choiceId }))
    } else if (choiceId === 'both') {
      // Both mode — auto-created a demo workspace, now show dashboard
      if (meta.workspace) {
        setOnboardingState((s) => ({ ...s, choice: choiceId, orgs: [meta.workspace] }))
      } else {
        setOnboardingState((s) => ({ ...s, choice: choiceId }))
      }
    }
  }

  // "Show me around" — auto-create a demo workspace with sample data
  const handleShowMeAround = async () => {
    try {
      const org = await createOrganization({
        name: `${t('demo.workspaceName')} - ${new Date().toLocaleDateString()}`,
        framework: 'OHADA',
        currency: 'XAF',
        is_demo: true,
      })
      setOnboardingState((s) => ({ ...s, choice: 'both', orgs: [org] }))
    } catch {
      // Fallback: just show the dashboard
      setOnboardingState((s) => ({ ...s, choice: 'both', orgs: [] }))
    }
  }

  // Protected: the Dashboard only renders when authenticated.
  if (status === 'authed') {
    // First, check if we need to show the onboarding choice screen
    if (onboardingState.orgs === null) {
      // Trigger workspace check on first render
      checkWorkspaces()
      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center">
          <p className="text-slate-500">{t('common.loading')}</p>
        </div>
      )
    }

    // If user has no workspaces and hasn't made a choice yet, show the choice screen
    if (onboardingState.orgs.length === 0 && !onboardingState.choice) {
      return (
        <OnboardingChoicePage
          onChoice={handleChoice}
          onShowMeAround={handleShowMeAround}
        />
      )
    }

    // If user chose "learn" (no workspace), show the Learn page
    if (onboardingState.choice === 'learn' && onboardingState.orgs.length === 0) {
      return (
        <div>
          <Header />
          <div className="max-w-3xl mx-auto px-4 py-4">
            <button
              type="button"
              onClick={() => setOnboardingState({ orgs: null, choice: null, learnLessonId: null })}
              className="text-sm text-slate-500 hover:text-slate-700 mb-4"
            >
              ← {t('choice.title')}
            </button>
          </div>
          <LearnPage
            onOpenLesson={(id) =>
              setOnboardingState((s) => ({ ...s, learnLessonId: id }))
            }
          />
        </div>
      )
    }

    // Otherwise, show the Dashboard (user has workspaces or chose practice/both)
    return (
      <div>
        <Header />
        <DashboardPage
          forceOnboardingChoice={onboardingState.choice}
          onOnboardingHandled={() =>
            setOnboardingState((s) => ({ ...s, choice: null }))
          }
        />
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
          className="flex items-center gap-2"
        >
          <Logo wordmark={t('app.title')} />
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

