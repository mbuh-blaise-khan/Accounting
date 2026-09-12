// Lightweight client-side view switch for the MVP (no router dependency yet).
//
// Session 13 — Learn/Practice choice hub as a persistent landing:
// - EVERY login (new or existing user) lands on the choice hub ("How do you
//   want to get started?"); it is NOT gated on the user's workspaces anymore.
//   The old "Both" card was removed — two paths remain (Learn, Practice).
// - Both authenticated flows stay MOUNTED but hidden (CSS `hidden`) once the
//   user has entered them, so switching Learn <-> Practice <-> hub never
//   resets local state and returning resumes exactly where the user left off
//   (Learn progress is additionally stored server-side).
// - Persistent hub access: the header's logo / "← Back to start" action
//   returns here from anywhere in Learn or Practice (no data loss).
//
// Session 13 — register-no-auto-login: registration redirects to Login with
// an "Account created — please log in" notice; no session is established.
import { useState, useEffect, useCallback } from 'react'
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
import LessonDetailPage from './pages/LessonDetailPage.jsx'
import CertificateVerificationPage from './pages/CertificateVerificationPage.jsx'
import { fetchOrganizations, createOrganization } from './services/api.js'

// Session 11 Part B3 — public certificate verification deep link.
// The SPA uses a view-switch (no router dep): a #/verify/<credential_id> hash
// renders the public verification page for unauthenticated visitors. The
// credential id is read safely from the path; a malformed id yields a safe
// not-found state inside the page (no network call, no data leakage).
function parseVerifyHash(hash) {
  if (!hash) return null
  const match = hash.match(/^#\/verify\/([A-Za-z0-9_-]+)$/)
  return match ? match[1] : null
}

function AppShell() {
  const { t } = useLanguage()
  const { status, logout } = useAuth()
  const [view, setView] = useState('home') // guest views: 'home' | 'login' | 'register'
  const [loginNotice, setLoginNotice] = useState(false)
  // Session 11 Part B3 — public verification deep link (#/verify/<credential_id>).
  // null = not a verification URL; string = the credential id to verify.
  const [verifyCredentialId, setVerifyCredentialId] = useState(() =>
    parseVerifyHash(typeof window !== 'undefined' ? window.location.hash : '')
  )

  // Keep the verify state in sync with hash changes (back/forward, manual edit).
  useEffect(() => {
    function onHashChange() {
      setVerifyCredentialId(parseVerifyHash(window.location.hash))
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  // mode: null = at the choice hub; 'learn' | 'practice' = inside a mode.
  // `entered*` flags keep flows mounted (hidden) once visited, so nothing
  // resets when the user switches modes or returns to the hub.
  const [mode, setMode] = useState(null)
  const [enteredLearn, setEnteredLearn] = useState(false)
  const [enteredPractice, setEnteredPractice] = useState(false)
  const [learnLessonId, setLearnLessonId] = useState(null)
  const [orgs, setOrgs] = useState(null) // null = loading; [] = new user; [...] = returning
  const [practiceIntent, setPracticeIntent] = useState(null) // 'create' | 'list'
  const [pendingPracticeClick, setPendingPracticeClick] = useState(false)
  const [autoSelectOrgId, setAutoSelectOrgId] = useState(null)

  const goHome = () => {
    setLoginNotice(false)
    setView('home')
  }
  const goLogin = () => setView('login')
  const goRegister = () => {
    setLoginNotice(false)
    setView('register')
  }

  // Part 1 (register-no-auto-login): after successful registration, redirect
  // to the Login page with a clear "Account created — please log in" notice.
  const handleAccountCreated = useCallback(() => {
    setLoginNotice(true)
    setView('login')
  }, [])

  // Fetch organizations once when the auth status transitions to 'authed'.
  const loadOrgs = useCallback(async () => {
    setOrgs(null)
    try {
      const data = await fetchOrganizations()
      setOrgs(data || [])
    } catch {
      setOrgs([])
    }
  }, [])

  // Trigger org loading ONLY on the auth-status transition, not every render.
  const [prevStatus, setPrevStatus] = useState(status)
  useEffect(() => {
    if (status === 'authed' && prevStatus !== 'authed') {
      // Every login lands on the choice hub (Part 2).
      setMode(null)
      setEnteredLearn(false)
      setEnteredPractice(false)
      setLearnLessonId(null)
      setPracticeIntent(null)
      setAutoSelectOrgId(null)
      loadOrgs()
    }
    if (status !== 'authed') {
      // Logging out resets all view state (data itself is server-side).
      setMode(null)
      setEnteredLearn(false)
      setEnteredPractice(false)
      setLearnLessonId(null)
      setOrgs(null)
      setPracticeIntent(null)
      setAutoSelectOrgId(null)
      setLoginNotice(false)
    }
    setPrevStatus(status)
  }, [status, prevStatus, loadOrgs])

  // --- Entering the modes ------------------------------------------------
  const goHub = useCallback(() => {
    // Back to the choice hub WITHOUT unmounting anything: the flows stay
    // mounted (hidden) so progress/workspaces resume exactly as left.
    setMode(null)
  }, [])

  const enterLearn = useCallback(() => {
    setEnteredLearn(true)
    setMode('learn')
  }, [])

  const enterPractice = useCallback((intent) => {
    setPracticeIntent(intent)
    setEnteredPractice(true)
    setMode('practice')
  }, [])

  const handleChoice = useCallback(
    (choiceId) => {
      if (choiceId === 'learn') {
        enterLearn()
      } else if (choiceId === 'practice') {
        if (orgs === null) {
          // Workspaces still loading (only possible right after login):
          // enter as soon as they arrive, via the effect below.
          setPendingPracticeClick(true)
        } else {
          // NEW-vs-RETURNING decision (Part 4): zero workspaces -> the
          // "create your first workspace" flow; one or more -> the
          // "Your Workspaces" list.
          enterPractice(orgs.length === 0 ? 'create' : 'list')
        }
      }
    },
    [orgs, enterLearn, enterPractice]
  )

  useEffect(() => {
    if (!pendingPracticeClick || orgs === null) return
    setPendingPracticeClick(false)
    enterPractice(orgs.length === 0 ? 'create' : 'list')
  }, [pendingPracticeClick, orgs, enterPractice])

  // "Show me around" (after the WelcomeTour): create the sample demo business
  // and enter its practice space (the mandatory Business Profile step applies
  // to it like to every new workspace — server-side enforced).
  const handleShowMeAround = useCallback(async () => {
    try {
      const org = await createOrganization({
        name: `${t('demo.workspaceName')} - ${new Date().toLocaleDateString()}`,
        framework: 'OHADA',
        currency: 'XAF',
        is_demo: true,
      })
      setOrgs((prev) => (prev ? [...prev, org] : [org]))
      setAutoSelectOrgId(org.id)
      enterPractice('list')
    } catch {
      // Fall back to the plain practice entry instead of stranding the user.
      enterPractice(orgs && orgs.length > 0 ? 'list' : 'create')
    }
  }, [t, orgs, enterPractice])

  // Session 11 Part B3 — public certificate verification page.
  // Renders for BOTH authenticated and unauthenticated visitors: a public
  // verification URL must never redirect to login. It takes precedence over
  // the normal view because the hash deep link is the user's explicit intent.
  // `onHome` clears the hash (returning to the normal home/hub) so the verify
  // page unmounts cleanly.
  const handleVerifyHome = useCallback(() => {
    window.location.hash = ''
    setVerifyCredentialId(null)
  }, [])

  if (verifyCredentialId) {
    return (
      <LanguageProvider>
        <CertificateVerificationPage
          credentialId={verifyCredentialId}
          onHome={handleVerifyHome}
        />
      </LanguageProvider>
    )
  }

  // Protected: the hub + the two authenticated flows render only when authed.
  if (status === 'authed') {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header
          onBackToStart={mode ? goHub : undefined}
          onHome={undefined}
          onLogin={undefined}
          onRegister={undefined}
        />
        {/* Learn flow — stays mounted (hidden) once entered. FIXED (Part 3):
            the lesson detail page now actually renders when a lesson card is
            clicked (learnLessonId is consumed here; previously it was stored
            but no branch ever displayed it). */}
        <div className={mode === 'learn' ? '' : 'hidden'}>
          {enteredLearn && (
            <LearnFlow
              lessonId={learnLessonId}
              onOpenLesson={setLearnLessonId}
              onBackToStart={goHub}
            />
          )}
        </div>
        {/* Practice flow — stays mounted (hidden) once entered. FIXED (Part 4):
            entering Practice no longer bounces back to the hub — the App drives
            the new-vs-returning intent instead of DashboardPage's own
            onboarding effect that immediately cleared the choice. */}
        <div className={mode === 'practice' ? '' : 'hidden'}>
          {enteredPractice && (
            <DashboardPage
              practiceIntent={practiceIntent}
              autoSelectOrgId={autoSelectOrgId}
              onAutoSelectHandled={() => setAutoSelectOrgId(null)}
              onBackToHub={goHub}
            />
          )}
        </div>
        {/* The choice hub overlays the hidden flows — every login lands here. */}
        {mode === null && (
          <OnboardingChoicePage
            onChoice={handleChoice}
            onShowMeAround={handleShowMeAround}
            practiceReady={orgs !== null}
          />
        )}
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
      {view === 'login' && (
        <LoginPage notice={loginNotice} onSwitchToRegister={goRegister} />
      )}
      {view === 'register' && (
        <RegisterPage
          onSwitchToLogin={goLogin}
          onAccountCreated={handleAccountCreated}
        />
      )}
      {view === 'home' && (
        <HomePage onCreateAccount={goRegister} onLogin={goLogin} />
      )}
    </div>
  )
}

// Standalone Learn flow (entered from the hub, outside any workspace).
// No org is passed, so lesson 4's practice connector simply does not post
// (the lesson itself still works; posting happens from a workspace).
function LearnFlow({ lessonId, onOpenLesson, onBackToStart }) {
  const { t } = useLanguage()
  return (
    <div>
      <div className="mx-auto max-w-3xl px-4 pt-4">
        {/* The FIXED back arrow (Part 3): it only flips the mode — orgs and
            all other state stay untouched, so it responds instantly instead
            of forcing a refetch that previously left a permanent spinner. */}
        <button
          type="button"
          onClick={onBackToStart}
          className="text-sm text-slate-500 hover:text-slate-700"
        >
          ← {t('choice.backToStart')}
        </button>
      </div>
      {lessonId != null ? (
        <LessonDetailPage
          lessonId={lessonId}
          orgId={null}
          onBack={() => onOpenLesson(null)}
        />
      ) : (
        <LearnPage onOpenLesson={onOpenLesson} />
      )}
    </div>
  )
}

function Header({ onBackToStart, onHome, onLogin, onRegister }) {
  const { t } = useLanguage()
  const { status, logout } = useAuth()
  const authed = status === 'authed'

  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        {/* Authenticated: logo click = persistent way back to the choice hub
            (Part 2). Guest: logo click = home. */}
        <button
          type="button"
          onClick={authed && onBackToStart ? onBackToStart : onHome}
          className="flex items-center gap-2"
          title={authed && onBackToStart ? t('choice.backToStart') : undefined}
        >
          <Logo wordmark={t('app.title')} />
          {authed && onBackToStart && (
            <span className="text-sm text-slate-400">← {t('choice.backToStart')}</span>
          )}
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
