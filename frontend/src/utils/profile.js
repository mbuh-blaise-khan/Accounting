// Business-Profile gating rules — PURE functions (no React, no DOM) so the
// mandatory-step rules are provable in plain node (`npm run test:profile`).
//
// Two deliberate tiers:
// - BLOCKING fields (registered_address, fiscal_year_start_month): every
//   workspace has SOME location and SOME fiscal year, even an informal
//   learner's. Missing these hard-blocks the mandatory creation step.
// - REGISTRATION fields (rccm_number, tax_id): only real registered
//   businesses have them. Missing these NEVER hard-blocks (the learner
//   exemption) — it triggers a dismissible completion banner instead.
//
// The hard gate is the SERVER-SIDE `profile_completed` flag (migration 0011),
// not an in-memory session marker: a session flag would reset on page reload
// and let a brand-new workspace dodge the mandate. New orgs start at False;
// every pre-mandate org is backfilled to True (never hard-blocked, banner
// instead); saving the profile sets it True server-side when the blocking
// fields exist. All profile columns stay nullable — the learner exemption has
// to remain expressible in the data.

export function missingProfileFields(org) {
  const missing = []
  if (!org || !String(org.registered_address || '').trim()) {
    missing.push('registered_address')
  }
  if (!org || !org.fiscal_year_start_month) {
    missing.push('fiscal_year_start_month')
  }
  return missing
}

export function missingRegistrationFields(org) {
  const missing = []
  if (!org || !String(org.rccm_number || '').trim()) missing.push('rccm_number')
  if (!org || !String(org.tax_id || '').trim()) missing.push('tax_id')
  return missing
}

/** Hard gate condition: the workspace cannot be used until these are filled. */
export function profileBlocking(org) {
  return missingProfileFields(org).length > 0
}

/** Soft attention: show the completion banner (never hard-blocks). */
export function profileNeedsAttention(org) {
  return profileBlocking(org) || missingRegistrationFields(org).length > 0
}

/**
 * Whether the UI must be replaced by the mandatory profile step. Driven by the
 * persistent SERVER-SIDE `profile_completed` flag (migration 0011):
 * - False -> hard gate (new workspace that has not completed the step yet —
 *   survives page reloads, so the step genuinely cannot be skipped);
 * - True -> never gated (pre-mandate orgs are backfilled True; saving the
 *   profile sets it True);
 * - undefined (stale/older payload) fails SAFE to "not gated" so a legacy
 *   user can never be locked out by a caching glitch.
 */
export function profileGateActive(org) {
  return org?.profile_completed === false
}