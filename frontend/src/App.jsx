import { useEffect, useState } from 'react'
import { fetchHealth } from './services/api.js'

// Landing page. On load it calls the backend /health endpoint and shows
// whether the API is up and the PostgreSQL database is reachable.
function App() {
  const [health, setHealth] = useState(null) // { status, db }
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchHealth()
      .then((data) => {
        if (!cancelled) setHealth(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const backendUp = health !== null && health.status === 'ok'
  const dbUp = health?.db === true

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-6">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-sm border border-slate-200 p-8 text-center">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">
          Universal Accounting Platform
        </h1>
        <p className="text-slate-600 mb-6">
          Frontend ↔ Backend ↔ Database connectivity check
        </p>

        {/* Backend status */}
        <div className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3 mb-3 text-left">
          <span className="text-sm font-medium text-slate-700">API (FastAPI)</span>
          <span
            className={`text-sm font-semibold ${
              error ? 'text-red-600' : backendUp ? 'text-green-600' : 'text-slate-400'
            }`}
          >
            {error ? 'Unreachable' : health ? 'Connected ✓' : 'Loading…'}
          </span>
        </div>

        {/* Database status */}
        <div className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3 mb-6 text-left">
          <span className="text-sm font-medium text-slate-700">Database (PostgreSQL)</span>
          <span
            className={`text-sm font-semibold ${
              health ? (dbUp ? 'text-green-600' : 'text-red-600') : 'text-slate-400'
            }`}
          >
            {health ? (dbUp ? 'Connected ✓' : 'Down ✗') : '—'}
          </span>
        </div>

        {error && (
          <p className="text-xs text-red-500 mb-4">
            Is the backend running?{' '}
            <code className="bg-slate-100 px-1 rounded">
              cd backend &amp;&amp; uvicorn app.main:app --reload --port 8000
            </code>
          </p>
        )}

        <p className="mt-6 text-xs text-slate-400">
          Session 2 · Project skeleton — frontend, backend &amp; database connected
        </p>
      </div>
    </div>
  )
}

export default App

