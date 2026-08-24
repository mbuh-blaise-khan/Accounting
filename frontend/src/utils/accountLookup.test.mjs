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

check('OHADA code-subtree search + sort (by code)', () => {
  // Mirrors real SYSCOHADA prefixes: 60 -> 601 -> 6011/6012, and 57 -> 571 -> 5711/5712.
  const ohada = [
    { id: 1, code: '60', name_en: 'Purchases', name_fr: 'Achats' },
    { id: 2, code: '601', name_en: 'Materials', name_fr: 'Fournitures' },
    { id: 3, code: '6011', name_en: 'Raw materials', name_fr: 'Matieres prem' },
    { id: 4, code: '6012', name_en: 'Work in progress', name_fr: 'Travaux encours' },
    { id: 5, code: '603', name_en: 'Services purchased', name_fr: 'Prestations' },
    { id: 6, code: '51', name_en: 'Pooled funds', name_fr: 'Fonds de placement' },
    { id: 7, code: '512', name_en: 'Current bank accounts', name_fr: 'Banques (courant)' },
    { id: 8, code: '571', name_en: 'Cash - national currency', name_fr: 'Caisse - monnaie' },
    { id: 9, code: '5711', name_en: 'Cash in hand', name_fr: 'Caisse' },
    { id: 10, code: '5712', name_en: 'Cash in banks', name_fr: 'Banque' },
  ]
  assert.deepEqual(searchAccounts(ohada, '571').map((a) => a.code), ['571', '5711', '5712'])
  assert.deepEqual(
    searchAccounts(ohada, '60').map((a) => a.code),
    ['60', '601', '6011', '6012', '603']
  )
  assert.deepEqual(searchAccounts(ohada, '6011').map((a) => a.code), ['6011'])
  // Name search still works alongside code matching on the OHADA (bidirectional) view.
  assert.deepEqual(searchAccounts(ohada, 'caisse').map((a) => a.code), ['571', '5711'])
})

check('OHADA progressive digit-narrowing is REAL prefix matching', () => {
  // SYSCOHADA hierarchy: one digit = class, more digits = deeper sub-account.
  // The same chart as the code-subtree check above, so the queries are real codes.
  const ohada = [
    { id: 1, code: '60', name_en: 'Purchases', name_fr: 'Achats' },
    { id: 2, code: '601', name_en: 'Materials', name_fr: 'Fournitures' },
    { id: 3, code: '6011', name_en: 'Raw materials', name_fr: 'Matieres prem' },
    { id: 4, code: '6012', name_en: 'Work in progress', name_fr: 'Travaux encours' },
    { id: 5, code: '603', name_en: 'Services purchased', name_fr: 'Prestations' },
    { id: 6, code: '51', name_en: 'Pooled funds', name_fr: 'Fonds de placement' },
    { id: 7, code: '512', name_en: 'Current bank accounts', name_fr: 'Banque (courant)' },
    { id: 8, code: '571', name_en: 'Cash - national currency', name_fr: 'Caisse - monnaie' },
    { id: 9, code: '5711', name_en: 'Cash in hand', name_fr: 'Caisse' },
    { id: 10, code: '5712', name_en: 'Cash in banks', name_fr: 'Banque' },
  ]
  // "5" => the whole of Class 5 (everything whose code starts with 5).
  assert.deepEqual(searchAccounts(ohada, '5').map((a) => a.code), ['51', '512', '571', '5711', '5712'])
  // "51" narrows to accounts under 51 only.
  assert.deepEqual(searchAccounts(ohada, '51').map((a) => a.code), ['51', '512'])
  // "512" reaches the leaf level.
  assert.deepEqual(searchAccounts(ohada, '512').map((a) => a.code), ['512'])
  // "57" -> cash sub-tree; "5711" -> deepest seeded sub-account.
  assert.deepEqual(searchAccounts(ohada, '57').map((a) => a.code), ['571', '5711', '5712'])
  assert.deepEqual(searchAccounts(ohada, '5711').map((a) => a.code), ['5711'])
  // Prefix, NOT substring-anywhere: "011" appears in 6011 but must NOT match.
  assert.deepEqual(searchAccounts(ohada, '011'), [])
  // A name fragment with letters never prefix-matches codes (falls back to name).
})

if (failures > 0) {
  console.error(`${failures} check(s) failed`)
  process.exitCode = 1
} else {
  console.log('all account-lookup checks passed')
}