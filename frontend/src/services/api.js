// Centralized API client for the frontend.
// The FastAPI backend runs on port 8000; the Vite dev server on 5173.
// Override via VITE_API_BASE in frontend/.env if you deploy elsewhere.
//
// credentials: 'include' is required so the httpOnly auth cookie set by the
// backend is sent on every cross-origin request.
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function parseError(res, body) {
  try {
    const data = JSON.parse(body)
    if (data && data.detail) {
      return new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))
    }
  } catch {
    /* not JSON */
  }
  return new Error(`Request to ${res.url} failed (${res.status})`)
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: options.method || 'GET',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    credentials: 'include',
    body: options.body,
  })
  if (!res.ok) {
    const text = await res.text()
    throw parseError(res, text)
  }
  if (res.status === 204) return null
  return res.json()
}

/** GET /health -> { status, db } */
export function fetchHealth() {
  return request('/health')
}

/** POST /auth/register -> user (sets httpOnly cookie) */
export function registerUser(data) {
  return request('/auth/register', { method: 'POST', body: JSON.stringify(data) })
}

/** POST /auth/login -> user (sets httpOnly cookie) */
export function loginUser(email, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

/** POST /auth/logout -> clears the cookie */
export function logoutUser() {
  return request('/auth/logout', { method: 'POST' })
}

/** GET /me -> current user (401 if not authenticated) */
export function fetchMe() {
  return request('/me')
}

/** PATCH /me -> updated user (persist language_preference / display_name) */
export function updateMe(data) {
  return request('/me', { method: 'PATCH', body: JSON.stringify(data) })
}

/** GET /organizations -> organizations the current user is a member of */
export function fetchOrganizations() {
  return request('/organizations')
}

/** GET /organizations/{id} -> single organization (member-only) */
export function fetchOrganization(id) {
  return request(`/organizations/${id}`)
}

/** POST /organizations -> create a workspace (creator becomes owner) */
export function createOrganization(data) {
  return request('/organizations', { method: 'POST', body: JSON.stringify(data) })
}

/** GET /frameworks -> available accounting frameworks with plain-language descriptions */
export function fetchFrameworks() {
  return request('/frameworks')
}

export default { fetchHealth }
