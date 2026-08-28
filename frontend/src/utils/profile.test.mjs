// Business-Profile gating rules (run: npm run test:profile) — proves the
// mandatory-step contract: a new workspace cannot skip the Business Profile
// step (unless the learner exemption applies to the REGISTRATION fields),
// the learner toggle keeps address + fiscal year required, and an existing
// pre-change org with an incomplete profile is never hard-blocked.
import assert from 'node:assert/strict'

import {
  missingProfileFields,
  missingRegistrationFields,
  profileBlocking,
  profileNeedsAttention,
  profileGateActive,
} from './profile.js'

let passed = 0
function check(name, fn) {
  try {
    fn()
    passed++
    console.log(`ok - ${name}`)
  } catch (err) {
    console.error(`FAIL - ${name}`)
    console.error(err)
    process.exitCode = 1
  }
}

// A brand-new org right after the Session-4 creation flow: DB default month,
// nothing else set, NOT yet profile_completed (server-side gate flag).
const brandNew = { id: 1, name: 'New Co', fiscal_year_start_month: 1, profile_completed: false }

check('a NEW workspace cannot skip the Business Profile step', () => {
  assert.equal(profileBlocking(brandNew), true)
  // The gate is the persistent server-side flag — no session state involved,
  // so reloading the page cannot dodge the mandate.
  assert.equal(profileGateActive(brandNew), true)
  assert.deepEqual(missingProfileFields(brandNew), ['registered_address'])
})

check('the mandatory gate lifts once the profile is completed', () => {
  const complete = {
    ...brandNew,
    registered_address: 'Bonanjo, Douala, Cameroon',
    profile_completed: true, // server sets this on save
  }
  assert.equal(profileGateActive(complete), false)
  assert.equal(profileBlocking(complete), false)
})

check('learner exemption: RCCM/tax ID optional, address + fiscal year still required', () => {
  // What a learner's org looks like after saving with the toggle checked:
  const learnerOrg = {
    id: 2,
    registered_address: 'Nkolbisson, Yaoundé, Cameroon',
    fiscal_year_start_month: 1,
    rccm_number: null,
    tax_id: null,
    profile_completed: true, // learner save still completes the step
  }
  // …NOT blocked — a learner must be able to use the app…
  assert.equal(profileBlocking(learnerOrg), false)
  assert.equal(profileGateActive(learnerOrg), false)
  // …but the missing registration fields still drive the completion banner.
  assert.deepEqual(missingRegistrationFields(learnerOrg), ['rccm_number', 'tax_id'])
  assert.equal(profileNeedsAttention(learnerOrg), true)
  // Address alone is never enough: without a fiscal month the gate stays up.
  assert.deepEqual(
    missingProfileFields({ registered_address: 'somewhere', fiscal_year_start_month: 0 }),
    ['fiscal_year_start_month'],
  )
  assert.equal(profileBlocking({ registered_address: 'somewhere' }), true)
  assert.equal(profileBlocking({ fiscal_year_start_month: 1 }), true)
})

check('a fully registered business raises no banner at all', () => {
  const full = {
    registered_address: 'Bonanjo, Douala, Cameroon',
    rccm_number: 'RC/DLA/2024/B/1234',
    tax_id: 'M012345678901X',
    fiscal_year_start_month: 1,
  }
  assert.deepEqual(missingProfileFields(full), [])
  assert.deepEqual(missingRegistrationFields(full), [])
  assert.equal(profileBlocking(full), false)
  assert.equal(profileNeedsAttention(full), false)
})

check('an EXISTING pre-mandate org with an incomplete profile is NOT hard-blocked', () => {
  // Migration 0011 backfills profile_completed=true for every org that
  // existed before the mandate (the profile fields were optional then).
  const preMandate = { id: 3, name: 'Old Co', fiscal_year_start_month: 1, profile_completed: true }
  assert.equal(profileGateActive(preMandate), false)
  // …and it gets the completion prompt instead:
  assert.equal(profileNeedsAttention(preMandate), true)
})

check('an undefined/missing flag fails SAFE to not-gated (no legacy lockout)', () => {
  assert.equal(profileGateActive({ id: 4 }), false)
  assert.equal(profileGateActive(undefined), false)
})

if (!process.exitCode) {
  console.log(`all profile checks passed (${passed})`)
}