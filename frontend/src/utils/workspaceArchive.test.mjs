// Workspace archive / delete UI rules (run: npm run test:ws-archive) —
// proves the archive-first product contract: archive is always available and
// deletes nothing; permanent delete is only offered for eligible workspaces
// (zero posted/reversed transactions); typed-name confirmation is validated
// (the API re-checks it server-side); archived workspaces keep historical
// sections readable while mutation sections are disabled; EN/FR i18n keys
// stay in perfect parity.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

import {
  isArchived,
  hasProtectedHistory,
  isDeleteEligible,
  partitionWorkspaces,
  validateDeleteConfirmation,
  workspaceActions,
  archivedWorkspaceActions,
  isSectionDisabledWhenArchived,
} from './workspaceArchive.js'

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

const activeEligible = {
  id: 1,
  name: 'Drafts Only',
  archived_at: null,
  has_protected_history: false,
}
const activeProtected = {
  id: 2,
  name: 'Has Posted',
  archived_at: null,
  has_protected_history: true,
}
const archivedWorkspace = {
  id: 3,
  name: 'Archived Co',
  archived_at: '2026-09-18T12:00:00Z',
  has_protected_history: true,
}

check('archive/active state detection (nullable archived_at)', () => {
  assert.equal(isArchived(activeEligible), false)
  assert.equal(isArchived(archivedWorkspace), true)
  // Missing/stale payload counts as active (fail-safe to visible).
  assert.equal(isArchived({ id: 4 }), false)
  assert.equal(isArchived(undefined), false)
})

check('delete eligibility: only active + zero posted/reversed history', () => {
  assert.equal(isDeleteEligible(activeEligible), true)
  assert.equal(isDeleteEligible(activeProtected), false)
  assert.equal(isDeleteEligible(archivedWorkspace), false)
  assert.equal(hasProtectedHistory(activeProtected), true)
  assert.equal(hasProtectedHistory(activeEligible), false)
})

check('active list partition: archived workspaces leave the default list', () => {
  const { active, archived } = partitionWorkspaces([
    activeEligible,
    activeProtected,
    archivedWorkspace,
  ])
  assert.deepEqual(active.map((o) => o.id), [1, 2])
  assert.deepEqual(archived.map((o) => o.id), [3])
  // Non-array input is safe.
  assert.deepEqual(partitionWorkspaces(null), { active: [], archived: [] })
})

check('action menu: archive ALWAYS available; delete only when eligible', () => {
  const eligible = workspaceActions(activeEligible)
  assert.deepEqual(eligible.map((a) => a.key), ['archive', 'delete'])
  assert.equal(eligible[0].disabled, false)
  assert.equal(eligible[1].disabled, false)

  // Protected history: delete renders DISABLED with the archive-instead reason.
  const [archiveAct, deleteAct] = workspaceActions(activeProtected)
  assert.equal(archiveAct.disabled, false)
  assert.equal(deleteAct.disabled, true)
  assert.equal(deleteAct.reason, 'ws.deleteBlockedProtected')
  // Archived workspaces never appear in the ACTIVE menu.
  assert.deepEqual(workspaceActions(archivedWorkspace), [])
})

check('archived card actions: open read-only + restore + (conditional) delete', () => {
  const archivedEligible = { ...activeEligible, archived_at: '2026-09-18T12:00:00Z' }
  const [openAct, restoreAct, deleteAct] = archivedWorkspaceActions(archivedEligible)
  // "Open read-only" is the PRIMARY archived action and is never disabled.
  assert.equal(openAct.key, 'openReadonly')
  assert.equal(openAct.disabled, false)
  assert.equal(restoreAct.key, 'restore')
  assert.equal(restoreAct.disabled, false)
  assert.deepEqual(
    archivedWorkspaceActions(archivedEligible).map((a) => a.key),
    ['openReadonly', 'restore', 'delete']
  )
  assert.equal(deleteAct.disabled, false)
  // With protected history the delete stays disabled + explained.
  const [, , blocked] = archivedWorkspaceActions(archivedWorkspace)
  assert.equal(blocked.disabled, true)
  assert.equal(blocked.reason, 'ws.deleteBlockedProtected')
  // Active orgs never render the archived card menu.
  assert.deepEqual(archivedWorkspaceActions(activeEligible), [])
})

check('active workspace never shows archived-only controls (open read-only/restore)', () => {
  const activeKeys = workspaceActions(activeEligible).map((a) => a.key)
  assert.equal(activeKeys.includes('openReadonly'), false)
  assert.equal(activeKeys.includes('restore'), false)
  // And an active workspace never receives the archived card menu at all.
  assert.deepEqual(archivedWorkspaceActions(activeEligible), [])
  assert.deepEqual(archivedWorkspaceActions(undefined), [])
})

check('typed confirmation: exact workspace name required (UI layer)', () => {
  assert.equal(validateDeleteConfirmation('', 'Acme'), 'ws.deleteConfirmRequired')
  assert.equal(validateDeleteConfirmation('acme', 'Acme'), 'ws.deleteConfirmMismatch')
  assert.equal(validateDeleteConfirmation('Wrong', 'Acme'), 'ws.deleteConfirmMismatch')
  assert.equal(validateDeleteConfirmation('Acme', 'Acme'), null)
  // Non-string input is treated as empty (never crashes).
  assert.equal(validateDeleteConfirmation(undefined, 'Acme'), 'ws.deleteConfirmRequired')
})

check('archived workspace: mutation sections disabled, read/report views kept', () => {
  // Mutation-capable sections are disabled while archived…
  for (const section of ['newTransaction', 'learn']) {
    assert.equal(isSectionDisabledWhenArchived(section), true, section)
  }
  // …but historical/report views AND the read-only viewable sections stay
  // reachable — never disabled by archive. Chart of accounts and business
  // profile open in read-only mode (their own pages hide edit controls).
  for (const section of [
    'home',
    'journal',
    'cashbook',
    'ledger',
    'trialBalance',
    'financialStatements',
    'accounts',
    'businessProfile',
  ]) {
    assert.equal(isSectionDisabledWhenArchived(section), false, section)
  }
})

check('EN/FR i18n parity for every new archive/delete key', () => {
  const here = dirname(fileURLToPath(import.meta.url))
  const en = JSON.parse(readFileSync(join(here, '../i18n/en.json'), 'utf8'))
  const fr = JSON.parse(readFileSync(join(here, '../i18n/fr.json'), 'utf8'))

  const keys = [
    'ws.archiveAction',
    'ws.openReadonlyAction',
    'ws.readonlyBadge',
    'ws.restoreAction',
    'ws.deleteAction',
    'ws.archivedBadge',
    'ws.showArchived',
    'ws.hideArchived',
    'ws.archivedEmpty',
    'ws.archiveConfirmTitle',
    'ws.archiveConfirmBody',
    'ws.deleteConfirmTitle',
    'ws.deleteConfirmBody',
    'ws.deleteConfirmLabel',
    'ws.deleteConfirmPlaceholder',
    'ws.deleteConfirmRequired',
    'ws.deleteConfirmMismatch',
    'ws.deleteBlockedProtected',
    'ws.archivedNotice',
    'ws.archivedReadonlyHint',
    'ws.actionError',
    'ws.cancel',
    'ws.menuOpen',
  ]
  for (const key of keys) {
    assert.ok(typeof en[key] === 'string' && en[key].length > 0, `en missing ${key}`)
    assert.ok(typeof fr[key] === 'string' && fr[key].length > 0, `fr missing ${key}`)
  }
})

if (!process.exitCode) {
  console.log(`all workspaceArchive checks passed (${passed})`)
}
