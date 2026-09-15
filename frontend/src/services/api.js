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


/**
 * GET /reports/income-statement?organization_id=&from=&as_of=
 * Compte de résultat (OHADA) / Statement of Profit or Loss (IFRS). The
 * framework-correct statement names come back IN the payload — the UI never
 * hardcodes them (Session 10 Part B requirement).
 */
export function fetchIncomeStatement(organizationId, params = {}) {
  const qs = new URLSearchParams({ organization_id: organizationId })
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v)
  }
  return request(`/reports/income-statement?${qs.toString()}`)
}

/**
 * GET /reports/financial-position?organization_id=&as_of=
 * Bilan (OHADA) / Statement of Financial Position (IFRS).
 */
export function fetchFinancialPosition(organizationId, params = {}) {
  const qs = new URLSearchParams({ organization_id: organizationId })
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v)
  }
  return request(`/reports/financial-position?${qs.toString()}`)
}

/**
 * GET a report PDF as a Blob (Session 12). Same params as the JSON fetch;
 * returns the response body as application/pdf bytes so the UI can trigger a
 * download. Auth/errors handled exactly like `request` (cookie + parseError).
 */
async function fetchPdfBlob(path) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'GET',
    credentials: 'include',
  })
  if (!res.ok) {
    const text = await res.text()
    throw parseError(res, text)
  }
  return res.blob()
}

function pdfParams(organizationId, params = {}) {
  const qs = new URLSearchParams({ organization_id: organizationId })
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v)
  }
  return qs.toString()
}

/** GET /reports/pdf/journal?organization_id=&from=&to=&lang= -> Blob */
export function fetchJournalPdf(organizationId, params = {}) {
  return fetchPdfBlob(`/reports/pdf/journal?${pdfParams(organizationId, params)}`)
}

/** GET /reports/pdf/cashbook?organization_id=&from=&to=&type=&lang= -> Blob */
export function fetchCashBookPdf(organizationId, params = {}) {
  return fetchPdfBlob(`/reports/pdf/cashbook?${pdfParams(organizationId, params)}`)
}

/** GET /reports/pdf/ledger/{accountId}?organization_id=&from=&to=&lang= -> Blob */
export function fetchLedgerPdf(organizationId, accountId, params = {}) {
  return fetchPdfBlob(
    `/reports/pdf/ledger/${accountId}?${pdfParams(organizationId, params)}`
  )
}

/** GET /reports/pdf/trial-balance?organization_id=&as_of=&from=&columns=&lang= -> Blob */
export function fetchTrialBalancePdf(organizationId, params = {}) {
  return fetchPdfBlob(`/reports/pdf/trial-balance?${pdfParams(organizationId, params)}`)
}

/** GET /reports/pdf/income-statement?organization_id=&from=&as_of=&lang= -> Blob */
export function fetchIncomeStatementPdf(organizationId, params = {}) {
  return fetchPdfBlob(
    `/reports/pdf/income-statement?${pdfParams(organizationId, params)}`
  )
}

/** GET /reports/pdf/financial-position?organization_id=&as_of=&lang= -> Blob */
export function fetchFinancialPositionPdf(organizationId, params = {}) {
  return fetchPdfBlob(
    `/reports/pdf/financial-position?${pdfParams(organizationId, params)}`
  )
}

export default { fetchHealth }


// ---------- Learning (Session 11 Part A) ----------
export async function fetchLessons() {
  return request('/learning/lessons');
}

export async function fetchLesson(id) {
  return request(`/learning/lessons/${id}`);
}

// Session 11 Part C1: `lang` selects the language of the post-answer feedback
// the server returns. It is optional and additive — existing callers that omit
// it keep working, and the server then falls back to the user's stored
// language preference.
export async function submitAttempt(questionId, payload, lang) {
  const query = lang ? `?lang=${encodeURIComponent(lang)}` : '';
  return request(`/learning/attempts${query}`, {
    method: 'POST',
    body: JSON.stringify({ question_id: questionId, ...payload }),
  });
}

// ---------- Course completion + certificate (Session 11 Part B2) ----------
// The backend owns the course identity — exactly one curriculum today, fixed
// server-side as COURSE_SLUG = "accounting-basics" in certificate_service.py.
// These endpoints take no slug parameter; never invent a second course
// identifier here.

/** GET /learning/completion -> authoritative completion summary + certificate. */
export async function fetchCourseCompletion() {
  return request('/learning/completion');
}

/** POST /learning/certificate -> CertificateOut (idempotent; 403 when not eligible). */
export async function issueCertificate() {
  return request('/learning/certificate', { method: 'POST' });
}

// ---------- Public certificate verification (Session 11 Part B3) ----------
// Public by design: NO auth, NO credentials:include, NO private data sent.
// The response (PublicCertificateOut) carries only credential metadata + the
// recipient display-name snapshot — never internal ids, emails, or
// workspace/transaction/answer data.

/** Build a shareable verification URL (frontend origin + hash deep link). */
export function certificateVerificationUrl(credentialId) {
  const origin = typeof window !== 'undefined' && window.location && window.location.origin
    ? window.location.origin
    : '';
  return `${origin}/#/verify/${encodeURIComponent(credentialId)}`;
}

/**
 * GET /learning/certificates/verify/{credential_id} -> PublicCertificateOut.
 * Throws on 404 ("Certificate not found") and other failures; callers map
 * those to the not-found / error states.
 */
export async function fetchPublicCertificate(credentialId) {
  if (!credentialId || typeof credentialId !== 'string') {
    throw new Error('Invalid credential ID');
  }
  const id = credentialId.trim();
  if (!id) throw new Error('Invalid credential ID');
  const res = await fetch(`${API_BASE}/learning/certificates/verify/${encodeURIComponent(id)}`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) {
    const text = await res.text();
    throw parseError(res, text);
  }
  return res.json();
}
