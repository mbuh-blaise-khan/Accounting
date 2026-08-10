// Authentication state for the whole app.
// The JWT lives in an httpOnly cookie set by the backend; there is no token
// stored in JavaScript. On mount we call GET /me to learn whether we are
// authenticated, then keep the user in memory.
import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import {
  fetchMe,
  loginUser,
  logoutUser,
  registerUser,
  updateMe,
} from '../services/api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  // status: 'loading' | 'authed' | 'guest'
  const [status, setStatus] = useState('loading')
  const [user, setUser] = useState(null)
  const [authError, setAuthError] = useState(null)

  const reloadUser = useCallback(async () => {
    setStatus('loading')
    try {
      const me = await fetchMe()
      setUser(me)
      setStatus('authed')
    } catch {
      setUser(null)
      setStatus('guest')
    }
  }, [])

  useEffect(() => {
    reloadUser()
  }, [reloadUser])

  const login = useCallback(async (email, password) => {
    setAuthError(null)
    try {
      const me = await loginUser(email, password)
      setUser(me)
      setStatus('authed')
    } catch (err) {
      setAuthError(err.message)
      throw err
    }
  }, [])

  const register = useCallback(async (data) => {
    setAuthError(null)
    try {
      const me = await registerUser(data)
      setUser(me)
      setStatus('authed')
    } catch (err) {
      setAuthError(err.message)
      throw err
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await logoutUser()
    } catch {
      /* best effort */
    }
    setUser(null)
    setStatus('guest')
  }, [])

  const setUserLanguage = useCallback(async (languagePreference) => {
    // Optimistic local update, then persist via PATCH /me.
    setUser((prev) =>
      prev ? { ...prev, language_preference: languagePreference } : prev
    )
    try {
      const updated = await updateMe({ language_preference: languagePreference })
      setUser(updated)
      setStatus('authed')
    } catch {
      /* keep optimistic value; backend will correct on next reload */
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{ status, user, authError, login, register, logout, reloadUser, setUserLanguage }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
