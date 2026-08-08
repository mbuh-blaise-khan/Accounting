import { useState } from 'react'

// Landing / placeholder page for Session 1.
// The Dashboard that talks to the backend arrives in Session 2.
function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-6">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-sm border border-slate-200 p-8 text-center">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">
          Universal Accounting Platform
        </h1>
        <p className="text-slate-600 mb-6">
          React + Vite + Tailwind are working. Backend hookup comes in Session 2.
        </p>

        <button
          type="button"
          onClick={() => setCount((c) => c + 1)}
          className="rounded-lg bg-blue-600 px-4 py-2 text-white font-medium hover:bg-blue-700"
        >
          Tailwind button — click {count} time{count === 1 ? '' : 's'}
        </button>

        <p className="mt-6 text-xs text-slate-400">
          Session 1 · Local development environment
        </p>
      </div>
    </div>
  )
}

export default App
