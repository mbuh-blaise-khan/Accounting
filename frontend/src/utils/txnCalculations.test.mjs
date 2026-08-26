// Plain assert-based checks (no node:test) so failures are visible even in
// non-TTY shells. Run with:  npm run test:txn  (or `node src/utils/txnCalculations.test.mjs`)
// Session 6c: tests for the journal-entry grid calculation helpers.
import assert from 'node:assert/strict'

import {
  canPost,
  isBalanced,
  isLineFilled,
  sumLines,
  toNumber,
  toPayload,
  validatePost,
} from './txnCalculations.js'

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

// --- toNumber ----------------------------------------------------
check('toNumber handles empty / null / negative', () => {
  assert.equal(toNumber(''), 0)
  assert.equal(toNumber(null), 0)
  assert.equal(toNumber(undefined), 0)
  assert.equal(toNumber('abc'), 0) // non-numeric -> 0 (not NaN)
  assert.equal(toNumber(50000), 50000)
  assert.equal(toNumber('50000'), 50000)
})

// --- sumLines ----------------------------------------------------
check('sumLines totals debits and credits separately', () => {
  const lines = [
    { debit: '50000', credit: '' },
    { debit: '', credit: '50000' },
    { debit: '0', credit: '0' },
  ]
  const { totalDebit, totalCredit } = sumLines(lines)
  assert.equal(totalDebit, 50000)
  assert.equal(totalCredit, 50000)
})

check('sumLines with no lines returns zeros', () => {
  const { totalDebit, totalCredit } = sumLines([])
  assert.equal(totalDebit, 0)
  assert.equal(totalCredit, 0)
})

// --- isLineFilled ------------------------------------------------
check('isLineFilled: exactly one side positive', () => {
  assert.equal(isLineFilled({ debit: '100', credit: '' }), true)
  assert.equal(isLineFilled({ debit: '', credit: '100' }), true)
  assert.equal(isLineFilled({ debit: '100', credit: '0' }), true) // one side > 0
  assert.equal(isLineFilled({ debit: '0', credit: '0' }), false) // neither
  assert.equal(isLineFilled({ debit: '100', credit: '50' }), false) // both
  assert.equal(isLineFilled({ debit: '', credit: '' }), false)
})

// --- isBalanced --------------------------------------------------
check('isBalanced: balanced debits == credits', () => {
  const balanced = [
    { debit: '50000', credit: '' },
    { debit: '', credit: '50000' },
  ]
  assert.equal(isBalanced(balanced), true)
})

check('isBalanced: unbalanced debits != credits', () => {
  const unbalanced = [
    { debit: '50000', credit: '' },
    { debit: '', credit: '40000' },
  ]
  assert.equal(isBalanced(unbalanced), false)
})

check('isBalanced: all-zero is not balanced', () => {
  const empty = [
    { debit: '', credit: '' },
    { debit: '', credit: '' },
  ]
  assert.equal(isBalanced(empty), false)
})

check('isBalanced: needs at least one debit and one credit', () => {
  const onlyDebits = [
    { debit: '50000', credit: '' },
    { debit: '10000', credit: '' },
  ]
  assert.equal(isBalanced(onlyDebits), false)
})

// --- canPost -----------------------------------------------------
check('canPost: balanced + complete + description -> true', () => {
  const lines = [
    { account_id: 1, debit: '50000', credit: '' },
    { account_id: 2, debit: '', credit: '50000' },
  ]
  assert.equal(canPost('Sold goods for cash', lines), true)
})

check('canPost: missing description -> false', () => {
  const lines = [
    { account_id: 1, debit: '50000', credit: '' },
    { account_id: 2, debit: '', credit: '50000' },
  ]
  assert.equal(canPost('  ', lines), false)
  assert.equal(canPost('', lines), false)
})

check('canPost: missing account -> false', () => {
  const lines = [
    { account_id: '', debit: '50000', credit: '' },
    { account_id: 2, debit: '', credit: '50000' },
  ]
  assert.equal(canPost('Sold goods for cash', lines), false)
})

check('canPost: only one line -> false', () => {
  const lines = [{ account_id: 1, debit: '50000', credit: '' }]
  assert.equal(canPost('test', lines), false)
})

check('canPost: unbalanced -> false', () => {
  const lines = [
    { account_id: 1, debit: '50000', credit: '' },
    { account_id: 2, debit: '', credit: '40000' },
  ]
  assert.equal(canPost('test', lines), false)
})

check('canPost: both sides filled on one line -> false', () => {
  const lines = [
    { account_id: 1, debit: '50000', credit: '100' },
    { account_id: 2, debit: '', credit: '50100' },
  ]
  assert.equal(canPost('test', lines), false)
})

// --- toPayload ---------------------------------------------------
check('toPayload maps grid lines to backend shape', () => {
  const lines = [
    { account_id: 5, debit: '50000', credit: '', account: { id: 5, code: '57', name_en: 'Cash' }, libelle: 'Cash sale' },
    { account_id: 9, debit: '', credit: '50000', account: { id: 9, code: '70', name_en: 'Sales' }, libelle: '' },
  ]
  const payload = toPayload('Sold goods for cash', lines, 1)
  assert.equal(payload.organization_id, 1)
  assert.equal(payload.description, 'Sold goods for cash')
  assert.equal(payload.lines.length, 2)
  assert.equal(payload.lines[0].account_id, 5)
  assert.equal(payload.lines[0].debit, 50000)
  assert.equal(payload.lines[0].credit, 0)
  assert.equal(payload.lines[1].credit, 50000)
  assert.equal(payload.lines[1].debit, 0)
  // Session 7: the per-line libellé is carried through as `narration`.
  assert.equal(payload.lines[0].narration, 'Cash sale')
  assert.equal(payload.lines[1].narration, null)
})

// --- validatePost (Part F: required-field validation) ---------------------
check('validatePost: fully filled valid entry -> ok=true, no errors', () => {
  const lines = [
    { id: 1, account_id: 1, debit: '50000', credit: '' },
    { id: 2, account_id: 2, debit: '', credit: '50000' },
  ]
  const r = validatePost('Sold goods for cash', lines)
  assert.equal(r.ok, true)
  assert.equal(r.descriptionError, '')
  assert.equal(r.balanceError, '')
  assert.equal(Object.keys(r.lineErrors).length, 0)
})

check('validatePost: missing description -> descriptionError set, ok=false', () => {
  const lines = [
    { id: 1, account_id: 1, debit: '50000', credit: '' },
    { id: 2, account_id: 2, debit: '', credit: '50000' },
  ]
  const r = validatePost('  ', lines)
  assert.equal(r.ok, false)
  assert.equal(r.descriptionError, 'description')
})

check('validatePost: missing account on a line -> lineErrors[line.id]=account', () => {
  const lines = [
    { id: 1, account_id: '', debit: '50000', credit: '' },
    { id: 2, account_id: 2, debit: '', credit: '50000' },
  ]
  const r = validatePost('Sale', lines)
  assert.equal(r.ok, false)
  assert.equal(r.lineErrors[1], 'account')
})

check('validatePost: missing amount on a line -> lineErrors[line.id]=amount', () => {
  const lines = [
    { id: 1, account_id: 1, debit: '', credit: '' },
    { id: 2, account_id: 2, debit: '', credit: '50000' },
  ]
  const r = validatePost('Sale', lines)
  assert.equal(r.ok, false)
  assert.equal(r.lineErrors[1], 'amount')
})

check('validatePost: both debit and credit on one line -> lineErrors=amount (bothSides)', () => {
  const lines = [
    { id: 1, account_id: 1, debit: '50000', credit: '100' },
    { id: 2, account_id: 2, debit: '', credit: '50100' },
  ]
  const r = validatePost('Sale', lines)
  assert.equal(r.ok, false)
  assert.equal(r.lineErrors[1], 'bothSides')
})

check('validatePost: unbalanced -> balanceError set, ok=false', () => {
  const lines = [
    { id: 1, account_id: 1, debit: '50000', credit: '' },
    { id: 2, account_id: 2, debit: '', credit: '40000' },
  ]
  const r = validatePost('Sale', lines)
  assert.equal(r.ok, false)
  assert.equal(r.balanceError, 'unbalanced')
})

if (failures > 0) {
  console.error(`${failures} check(s) failed`)
  process.exitCode = 1
} else {
  console.log('all txn-calculations checks passed')
}