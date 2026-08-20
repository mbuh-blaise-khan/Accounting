// Plain assert-based checks (no node:test) so failures are visible even in
// non-TTY shells. Run with:  npm run test:lookup   (or `node src/utils/accountLookup.test.mjs`)
import assert from 'node:assert/strict'

import { searchAccounts } from './accountLookup.js'

const acme = [
  { id: 1, code: '5711', name_en: 'Cash - national currency', name_fr: 'Caisse - monnaie nationale' },
  { id: 2, code: '701', name_en: 'Sales of goods for resale', name_fr: 'Ventes de marchandises' },
  { id: 3, code: '40', name_en: 'Suppliers and related accounts', name_fr: 'Fournisseurs' },
]
const otherCo = [
  { id: 99, code: '9999', name_en: 'Cash - national currency', name_fr: 'Caisse' },
]

let failures = 0
function check(name, fn) {
  try {
    fn()
    console.log(`ok - ${name}`)
  } catch (err) {
    failures += 1
    console.log(`FAIL - ${name}`)
    console.log(`       ${err.message}`)
  }
}

check('empty query returns nothing', () => {
  assert.deepEqual(searchAccounts(acme, ''), [])
  assert.deepEqual(searchAccounts(acme, '   '), [])
})

check('matches by code', () => {
  assert.deepEqual(searchAccounts(acme, '571').map((a) => a.code), ['5711'])
})

check('matches by name (English and French)', () => {
  assert.deepEqual(searchAccounts(acme, 'sales').map((a) => a.code), ['701'])
  assert.deepEqual(searchAccounts(acme, 'ventes').map((a) => a.code), ['701'])
  assert.deepEqual(searchAccounts(acme, 'caisse').map((a) => a.code), ['5711'])
})

check('case-insensitive substring match', () => {
  assert.deepEqual(searchAccounts(acme, 'SUPPLIERS').map((a) => a.code), ['40'])
})

check('does not leak accounts from another org', () => {
  // A same-named account that exists only in another workspace is NOT returned.
  assert.deepEqual(
    searchAccounts(acme, 'cash').map((a) => a.code),
    ['5711']
  )
  assert.deepEqual(
    searchAccounts(otherCo, 'cash').map((a) => a.code),
    ['9999']
  )
})

check('byNameOnly (IFRS): matches NAME only, never by code', () => {
  // IFRS accounts have no codes (Part B). A code-shaped query must NOT match,
  // even though the legacy account fixture carries numeric codes.
  assert.deepEqual(searchAccounts(acme, '571', { byNameOnly: true }), [])
  assert.deepEqual(
    searchAccounts(acme, 'caisse', { byNameOnly: true }).map((a) => a.id),
    [1]
  )
  assert.deepEqual(
    searchAccounts(acme, 'sales', { byNameOnly: true }).map((a) => a.name_en),
    ['Sales of goods for resale']
  )
})

check('byNameOnly tolerates accounts without a code (IFRS seed)', () => {
  const ifrs = [
    { id: 1, code: null, name_en: 'Cash and cash equivalents', name_fr: 'Trésorerie et équivalents' },
    { id: 2, code: null, name_en: 'Sales revenue', name_fr: 'Produits des ventes' },
  ]
  assert.deepEqual(searchAccounts(ifrs, 'cash', { byNameOnly: true }).map((a) => a.name_en), [
    'Cash and cash equivalents',
  ])
  assert.deepEqual(searchAccounts(ifrs, '1', { byNameOnly: true }), [])
})

if (failures > 0) {
  console.error(`${failures} check(s) failed`)
  process.exitCode = 1
} else {
  console.log('all account-lookup checks passed')
}