// Workspace archive / restore / conditional permanent-delete rules — PURE
// functions (no React, no DOM) so the product rules are provable in plain
// node (`npm run test:ws-archive`), exactly like the other utils.
//
// Product rules (archive-first policy):
// - Archive is the PRIMARY action, always available to the owner: it hides
//   the workspace from the active list and makes it read-only at the SERVICE
//   layer while deleting nothing (profile, accounts, drafts, posted
//   transactions, reports and memberships all stay; history remains
//   readable). Restore is always available.
// - Permanent delete is SECONDARY and conditional: only offered (and only
//   possible server-side) when the workspace has ZERO posted AND ZERO
//   reversed transactions (`has_protected_history === false` from the API).
//   Workspaces with protected history show a clear disabled state pointing
//   at archive instead — there is no bypass anywhere.
// - Permanent delete requires typing the EXACT workspace name. The dialog
//   enforces it in the UI, but the API re-validates it server-side — this
//   module's check is UX, never the only gate.
// - Retention note: IFRS/OHADA do NOT define a universal record-retention
//   period (duties vary by jurisdiction); archive-first is this product's
//   safe data-integrity policy because posted records are treated as
//   immutable.

/** True when the workspace is archived (nullable archived_at from the API). */
export function isArchived(org) {
  return Boolean(org && org.archived_at)
}

/** True when the workspace has protected accounting history (any posted OR
 * reversed transaction) — permanently undeletable by design. */
export function hasProtectedHistory(org) {
  return Boolean(org && org.has_protected_history === true)
}

/**
 * Permanent-delete eligibility: active AND zero posted/reversed history.
 * The server re-checks this authoritatively; this drives only the UI offer.
 */
export function isDeleteEligible(org) {
  return Boolean(org) && !isArchived(org) && !hasProtectedHistory(org)
}

/**
 * Partition the full org payload into { active, archived } lists for the
 * "Your Workspaces" screen. Safe on stale payloads (missing archived_at
 * counts as active).
 */
export function partitionWorkspaces(orgs) {
  const list = Array.isArray(orgs) ? orgs : []
  const active = []
  const archived = []
  for (const org of list) {
    if (isArchived(org)) archived.push(org)
    else active.push(org)
  }
  return { active, archived }
}

/**
 * Typed-name confirmation check (UI-side; the API validates again).
 * Returns an i18n key describing the problem, or null when acceptable.
 * The exact match is case- and whitespace-sensitive on the TRIMMED value —
 * the user must type the name as it is, per "Type the exact workspace name".
 */
export function validateDeleteConfirmation(input, orgName) {
  const value = typeof input === 'string' ? input : ''
  if (value.length === 0) return 'ws.deleteConfirmRequired'
  if (value.trim() !== orgName) return 'ws.deleteConfirmMismatch'
  return null
}

/**
 * Per-workspace actions for the compact menu on an ACTIVE workspace card.
 * - archive: always available to the owner (primary action).
 * - delete: enabled only for eligible workspaces; with protected history it
 *   renders DISABLED with an explanatory reason (archive instead).
 * Archived-only controls (openReadonly / restore) NEVER appear here.
 */
export function workspaceActions(org) {
  if (!org || isArchived(org)) return []
  const protectedHistory = hasProtectedHistory(org)
  return [
    { key: 'archive', disabled: false, reason: null },
    {
      key: 'delete',
      disabled: protectedHistory,
      reason: protectedHistory ? 'ws.deleteBlockedProtected' : null,
    },
  ]
}

/** Actions for an ARCHIVED workspace card, in render order:
 * openReadonly (the primary archived action — opens the SAME workspace shell
 * in read-only mode, restoring nothing), restore (owner), delete when
 * eligible. Delete of an archived workspace follows the same eligibility rule
 * — the server is the authoritative gate. */
export function archivedWorkspaceActions(org) {
  if (!org || !isArchived(org)) return []
  const protectedHistory = hasProtectedHistory(org)
  return [
    { key: 'openReadonly', disabled: false, reason: null },
    { key: 'restore', disabled: false, reason: null },
    {
      key: 'delete',
      disabled: protectedHistory,
      reason: protectedHistory ? 'ws.deleteBlockedProtected' : null,
    },
  ]
}

/**
 * Mutation-capable sections of an opened workspace that must render disabled
 * when the workspace is archived: new transaction and Learn (its practice
 * connector posts a real transaction). Historical reads stay available —
 * NEVER in this list, including the two read-only VIEWABLE sections:
 * chart of accounts and business profile open fine while archived (their
 * edit/create controls are hidden in the pages themselves; the service layer
 * rejects any mutation with 409 regardless).
 */
const ARCHIVED_DISABLED_SECTIONS = [
  'newTransaction',
  'learn',
  'lesson',
]

/** True when a given workspace section is disabled for an archived workspace. */
export function isSectionDisabledWhenArchived(section) {
  return ARCHIVED_DISABLED_SECTIONS.includes(section)
}
