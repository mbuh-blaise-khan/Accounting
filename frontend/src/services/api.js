// Centralized API client for the frontend.
// The FastAPI backend runs on port 8000; the Vite dev server on 5173.
// Override via VITE_API_BASE in frontend/.env if you deploy elsewhere.
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`Request to ${path} failed (${res.status}): ${body}`)
  }
  return res.json()
}

/** GET /health -> { status, db } */
export function fetchHealth() {
  return request('/health')
}

export default { fetchHealth }
