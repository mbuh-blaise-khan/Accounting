// Business-Profile gating rules (run: npm run test:profile) — proves the
// mandatory-step + identity contracts: a new workspace cannot skip the
// Business Profile step; identity_type drives what else is required
// (learner skips RCCM/tax AND may skip the legal form via NOT_APPLICABLE;
// registered_business requires RCCM + tax ID); an existing pre-change org
// with incomplete fields is never hard-blocked (banner instead).
import assert from 'node:assert/strict'

import {
  missingProfileFields,
  missingIdentityFields,
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
    identity_type: 'learner',
    country: 'CM',
    profile_completed: true, // server sets this on save
  }
  assert.equal(profileGateActive(complete), false)
  assert.equal(profileBlocking(complete), false)
})

check('LEARNER identity: RCCM/tax not required, NOT_APPLICABLE legal form ok, country still required', () => {
  const learnerOrg = {
    id: 2,
    identity_type: 'learner',
    registered_address: 'Nkolbisson, Yaoundé, Cameroon',
    country: 'CM',
    legal_form: 'NOT_APPLICABLE', // explicit skip value for learners
    fiscal_year_start_month: 1,
    rccm_number: null,
    tax_id: null,
    profile_completed: true,
  }
  // …never blocked and NO banner — a learner without registration numbers is
  // the expected state, not an incomplete profile…
  assert.equal(profileBlocking(learnerOrg), false)
  assert.equal(profileGateActive(learnerOrg), false)
  assert.equal(profileNeedsAttention(learnerOrg), false)
  assert.deepEqual(missingRegistrationFields(learnerOrg), [])
  assert.deepEqual(missingIdentityFields(learnerOrg), [])
  // …but country is required for EVERY identity type…
  assert.deepEqual(missingIdentityFields({ ...learnerOrg, country: null }), ['country'])
  // …and a learner who skipped the legal form cleanly (left unset) raises no
  // legal_form banner either — only the business identities require it.
  assert.deepEqual(missingIdentityFields({ ...learnerOrg, legal_form: null }), [])
})

check('UNREGISTERED BUSINESS identity: country + legal_form required, RCCM/tax optional', () => {
  const informalOrg = {
    id: 3,
    identity_type: 'unregistered_business',
    registered_address: 'Nkolbisson, Yaoundé, Cameroon',
    country: 'CM',
    legal_form: 'ENTREPRISE_INDIVIDUELLE',
    fiscal_year_start_month: 1,
    rccm_number: null, // optional for this identity
    tax_id: null,
    profile_completed: true,
  }
  assert.equal(profileBlocking(informalOrg), false)
  assert.equal(profileNeedsAttention(informalOrg), false)
  assert.deepEqual(missingRegistrationFields(informalOrg), [])
  // Missing the legal form DOES raise the banner for this identity…
  assert.deepEqual(missingIdentityFields({ ...informalOrg, legal_form: null }), ['legal_form'])
  assert.equal(profileNeedsAttention({ ...informalOrg, legal_form: null }), true)
})

check('REGISTERED BUSINESS identity: country + legal_form + RCCM + tax ALL drive requirements', () => {
  const full = {
    identity_type: 'registered_business',
    registered_address: 'Bonanjo, Douala, Cameroon',
    country: 'CM',
    legal_form: 'SARL',
    rccm_number: 'RC/DLA/2024/B/1234',
    tax_id: 'M012345678901X',
    fiscal_year_start_month: 1,
  }
  assert.deepEqual(missingProfileFields(full), [])
  assert.deepEqual(missingIdentityFields(full), [])
  assert.deepEqual(missingRegistrationFields(full), [])
  assert.equal(profileNeedsAttention(full), false)
  // Missing either registration number raises the banner for this identity:
  assert.deepEqual(missingRegistrationFields({ ...full, rccm_number: null }), ['rccm_number'])
  assert.deepEqual(
    missingRegistrationFields({ ...full, tax_id: null }),
    ['tax_id'],
  )
  assert.equal(profileNeedsAttention({ ...full, tax_id: null }), true)
  // NOT_APPLICABLE is a learner-only value — a business identity without a
  // real legal form is simply missing it.
  assert.deepEqual(missingIdentityFields({ ...full, legal_form: null }), ['legal_form'])
})

check('an EXISTING pre-mandate org with an incomplete profile is NOT hard-blocked', () => {
  // Migration 0011 backfills profile_completed=true for every org that
  // existed before the mandate (the profile fields were optional then); the
  // Part-2 identity columns stay nullable so old orgs remain valid.
  const preMandate = { id: 4, name: 'Old Co', fiscal_year_start_month: 1, profile_completed: true }
  assert.equal(profileGateActive(preMandate), false)
  // …and it gets the completion prompt instead (identity + registration gaps
  // are soft attention, never a lockout):
  assert.equal(profileNeedsAttention(preMandate), true)
})

check('an undefined/missing flag fails SAFE to not-gated (no legacy lockout)', () => {
  assert.equal(profileGateActive({ id: 5 }), false)
  assert.equal(profileGateActive(undefined), false)
})

if (!process.exitCode) {
  console.log(`all profile checks passed (${passed})`)
}