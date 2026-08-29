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

/** GET /organizations/identity-options?framework=OHADA|IFRS -> country +
 * legal-form dropdown data (single source of truth: OHADA = 17 member states
 * + AUSCGIE forms; IFRS = full ISO list + international forms). */
export function fetchIdentityOptions(framework) {
  return request(`/organizations/identity-options?framework=${encodeURIComponent(framework)}`)
}

/**
 * PATCH /organizations/{id} -> update the optional Business Profile
 * (registered address, RCCM number, tax ID, fiscal year start month).
 * PATCH semantics: only provided keys change; empty strings clear a value.
 */
export function updateOrganization(orgId, data) {
  return request(`/organizations/${orgId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

/** GET /frameworks -> available accounting frameworks with plain-language descriptions */
export function fetchFrameworks() {
  return request('/frameworks')
}

/** GET /accounts?organization_id={id} -> the org's chart of accounts */
export function fetchAccounts(organizationId) {
  return request(`/accounts?organization_id=${organizationId}`)
}

/** POST /accounts -> create a user-defined custom account */
export function createAccount(data) {
  return request('/accounts', { method: 'POST', body: JSON.stringify(data) })
}

/** PATCH /accounts/{id}?organization_id={id} -> edit name / toggle active */
export function updateAccount(accountId, organizationId, data) {
  return request(`/accounts/${accountId}?organization_id=${organizationId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

/** POST /transactions -> create a draft transaction */
export function createTransaction(data) {
  return request('/transactions', { method: 'POST', body: JSON.stringify(data) })
}

/** GET /transactions?organization_id={id} -> list the org's transactions */
export function fetchTransactions(organizationId) {
  return request(`/transactions?organization_id=${organizationId}`)
}

/** POST /transactions/{id}/post?organization_id={id} -> post a draft (immutable) */
export function postTransaction(organizationId, transactionId) {
  return request(`/transactions/${transactionId}/post?organization_id=${organizationId}`, {
    method: 'POST',
  })
}

/** GET /journal-entries?organization_id=&from=&to=&account_id=&reference= (Session 7) */
export function fetchJournalEntries(organizationId, params = {}) {
  const qs = new URLSearchParams({ organization_id: organizationId })
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v)
  }
  return request(`/journal-entries?${qs.toString()}`)
}

/** GET /cashbook?organization_id=&from=&to=&account_id=&reference=&type=single|double (Session 10) */
export function fetchCashBook(organizationId, params = {}) {
  const qs = new URLSearchParams({ organization_id: organizationId })
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v)
  }
  return request(`/cashbook?${qs.toString()}`)
}

/** GET /ledger/{accountId}?organization_id=&from=&to= (Session 8) */
export function fetchLedger(organizationId, accountId, params = {}) {
  const qs = new URLSearchParams({ organization_id: organizationId })
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v)
  }
  return request(`/ledger/${accountId}?${qs.toString()}`)
}

/**
 * GET /accounts/suggested?organization_id={id}
 * Smart-ordered account list for pickers: accounts the current user created
 * first, then most recently used (by real posted activity), then code/name.
 */
export function fetchSuggestedAccounts(organizationId) {
  return request(`/accounts/suggested?organization_id=${organizationId}`)
}

/**
 * POST /transactions/{id}/reverse?organization_id={id}
 * Posted entries are immutable: correction happens via a NEW mirrored entry
 * with debit/credit sides swapped, linked back to the original. Returns the
 * NEW posted mirror transaction.
 */
export function reverseTransaction(organizationId, transactionId) {
  return request(`/transactions/${transactionId}/reverse?organization_id=${organizationId}`, {
    method: 'POST',
  })
}

/**
 * GET /trial-balance?organization_id=&as_of=&from=&columns=2|4|6
 * ONE computation carrying opening/movement/closing for every account, so the
 * UI can switch between the 2/4/6-column views without refetching.
 */
export function fetchTrialBalance(organizationId, params = {}) {
  const qs = new URLSearchParams({ organization_id: organizationId })
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v)
  }
  return request(`/trial-balance?${qs.toString()}`)
}


export default { fetchHealth }
