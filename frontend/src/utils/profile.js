// Business-Profile gating rules — PURE functions (no React, no DOM) so the
// mandatory-step rules are provable in plain node (`npm run test:profile`).
//
// Three deliberate tiers:
// - BLOCKING fields (registered_address, fiscal_year_start_month): every
//   workspace has SOME location and SOME fiscal year, even an informal
//   learner's. Missing these hard-blocks the mandatory creation step.
// - IDENTITY fields (country for everyone; legal_form for the two business
//   identities): required by Business Profile Part 2's identity rules. They
//   do NOT hard-block (pre-mandate orgs must keep access) but DO drive the
//   completion banner.
// - REGISTRATION fields (rccm_number, tax_id): ONLY a fully
//   registered_business requires them. Learners and unregistered businesses
//   never raise a banner for missing registration numbers — that is exactly
//   what the old "learner exemption" checkbox became: the identity_type
//   choice REPLACED it (one mechanism, not two overlapping ones).
//
// The hard gate is the SERVER-SIDE `profile_completed` flag (migration 0011),
// not an in-memory session marker: a session flag would reset on page reload
// and let a brand-new workspace dodge the mandate. New orgs start at False;
// every pre-mandate org is backfilled to True (never hard-blocked, banner
// instead); saving the profile sets it True server-side. All profile columns
// stay nullable — these rules have to remain expressible in the data.

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

/**
 * Identity-driven requirements (Business Profile Part 2, mirrored in the
 * backend's update_business_profile validation):
 * - country: required for EVERY identity type (even a learner has a country).
 * - legal_form: required for unregistered_business and registered_business;
 *   a learner may use the explicit NOT_APPLICABLE skip value (which counts
 *   as filled) or leave it unset without any banner.
 */
export function missingIdentityFields(org) {
  const missing = []
  if (!org || !String(org.country || '').trim()) missing.push('country')
  const identity = org?.identity_type
  if (
    (identity === 'unregistered_business' || identity === 'registered_business') &&
    !(org && String(org.legal_form || '').trim())
  ) {
    missing.push('legal_form')
  }
  return missing
}

/** Registration numbers are required ONLY for a fully registered business. */
export function missingRegistrationFields(org) {
  if (!org || org.identity_type !== 'registered_business') return []
  const missing = []
  if (!String(org.rccm_number || '').trim()) missing.push('rccm_number')
  if (!String(org.tax_id || '').trim()) missing.push('tax_id')
  return missing
}

/** Hard gate condition: the workspace cannot be used until these are filled. */
export function profileBlocking(org) {
  return missingProfileFields(org).length > 0
}

/** Soft attention: show the completion banner (never hard-blocks). */
export function profileNeedsAttention(org) {
  return (
    profileBlocking(org) ||
    missingIdentityFields(org).length > 0 ||
    missingRegistrationFields(org).length > 0
  )
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