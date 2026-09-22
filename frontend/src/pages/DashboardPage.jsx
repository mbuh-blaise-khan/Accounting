// Protected practice space. Entered when the user picks Practice on the choice
// hub (App.jsx passes the intent decided from the user's workspaces).
//
// NEW-vs-RETURNING flow (Session 13, Part 4):
// - ZERO workspaces (intent 'create'): the CreateWorkspace flow (name /
//   framework / currency), then straight into the MANDATORY Business Profile
//   step (server-side profile_completed gate), then the full practice space.
// - ONE OR MORE workspaces (intent 'list'): a "Your Workspaces" list with
//   framework badges PLUS a clearly visible "+ Create a new business" option.
//   Opening a workspace with an already-completed profile goes straight into
//   the practice space — the mandatory profile form is NOT re-demanded (the
//   server-side gate only renders it when profile_completed is false).
//
// The hub itself lives in App.jsx (persistent, not gated on workspaces);
// `onBackToHub` returns there from anywhere without losing any state.
import { useEffect, useState } from 'react'
import {
  archiveOrganization,
  deleteOrganization,
  fetchArchivedOrganizations,
  fetchFrameworks,
  fetchOrganizations,
  restoreOrganization,
} from '../services/api.js'
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../i18n/index.jsx'
import CreateWorkspace from '../components/CreateWorkspace.jsx'
import Logo from '../components/Logo.jsx'
import ChartOfAccountsPage from './ChartOfAccountsPage.jsx'
import NewTransactionPage from './NewTransactionPage.jsx'
import JournalPage from './JournalPage.jsx'
import CashBookPage from './CashBookPage.jsx'
import GeneralLedgerPage from './GeneralLedgerPage.jsx'
import TrialBalancePage from './TrialBalancePage.jsx'
import FinancialStatementsPage from './FinancialStatementsPage.jsx'
import BusinessProfilePage from './BusinessProfilePage.jsx'
import LearnPage from './LearnPage.jsx'
import LessonDetailPage from './LessonDetailPage.jsx'
import { profileGateActive, profileNeedsAttention } from '../utils/profile.js'
import {
  archivedWorkspaceActions,
  hasProtectedHistory,
  isArchived,
  isDeleteEligible,
  isSectionDisabledWhenArchived,
  validateDeleteConfirmation,
  workspaceActions,
} from '../utils/workspaceArchive.js'

export default function DashboardPage({
  practiceIntent = null, // 'create' | 'list' | null (decided by App.jsx at entry)
  autoSelectOrgId = null, // e.g. the demo business from "Show me around"
  onAutoSelectHandled = null,
  onBackToHub = null,
}) {
  const { t } = useLanguage()
  const { user } = useAuth()
  const [orgs, setOrgs] = useState(null) // null = loading
  const [frameworks, setFrameworks] = useState([])
  const [error, setError] = useState(null)
  const [activeOrg, setActiveOrg] = useState(null) // set -> inside a workspace
  const [section, setSection] = useState('home')
  // 'create' = the new-business flow; 'list' = the workspace list.
  const [createMode, setCreateMode] = useState(practiceIntent === 'create')
  const [intentApplied, setIntentApplied] = useState(practiceIntent != null)
  // --- Archive / restore / conditional permanent delete (archive-first) ---
  // The ACTIVE list stays the default view; archived workspaces are only
  // fetched through the deliberate "Show archived workspaces" toggle.
  const [showArchived, setShowArchived] = useState(false)
  const [archivedOrgs, setArchivedOrgs] = useState(null) // null = not loaded
  const [actionError, setActionError] = useState(null)
  const [confirmArchiveOrg, setConfirmArchiveOrg] = useState(null)
  const [confirmDeleteOrg, setConfirmDeleteOrg] = useState(null)

  async function load() {
    setError(null)
    try {
      const [orgList, fwList] = await Promise.all([
        fetchOrganizations(),
        fetchFrameworks(),
      ])
      setOrgs(orgList)
      setFrameworks(fwList)
    } catch (err) {
      setError(err.message)
    }
  }

  async function loadArchived() {
    try {
      setArchivedOrgs(await fetchArchivedOrganizations())
    } catch (err) {
      setActionError(err.message)
    }
  }

  function toggleArchived() {
    const next = !showArchived
    setShowArchived(next)
    if (next) loadArchived()
  }

  // ARCHIVE (primary action): hides + read-only at the service layer,
  // deletes NOTHING. If the open workspace was archived elsewhere, the UI
  // leaves it safely instead of pointing at a now-read-only workspace.
  async function handleArchive(org) {
    setActionError(null)
    try {
      await archiveOrganization(org.id)
      setConfirmArchiveOrg(null)
      setActiveOrg((current) => (current && current.id === org.id ? null : current))
      setSection('home')
      setCreateMode(false)
      await load()
      if (showArchived) await loadArchived()
    } catch (err) {
      setConfirmArchiveOrg(null)
      setActionError(err.message)
    }
  }

  async function handleRestore(org) {
    setActionError(null)
    try {
      const restored = await restoreOrganization(org.id)
      // If this workspace is currently OPEN (read-only view), update it in
      // place so the archived banner clears and the mutation controls come
      // back WITHOUT exiting and re-opening (restore -> active mode again).
      setActiveOrg((current) =>
        current && current.id === restored.id ? { ...current, ...restored } : current
      )
      await load()
      if (showArchived) await loadArchived()
    } catch (err) {
      setActionError(err.message)
    }
  }

  // PERMANENT DELETE (secondary, eligible-only, owner-only). The typed name
  // is validated in the dialog AND again server-side; the backend re-checks
  // eligibility (zero posted/reversed) — there is no UI-only bypass.
  async function handleDelete(org, confirmName) {
    setActionError(null)
    try {
      await deleteOrganization(org.id, confirmName)
      setConfirmDeleteOrg(null)
      // Never leave the UI pointing at a removed workspace.
      setActiveOrg((current) => (current && current.id === org.id ? null : current))
      setSection('home')
      setCreateMode(false)
      await load()
      if (showArchived) await loadArchived()
    } catch (err) {
      setConfirmDeleteOrg(null)
      setActionError(err.message)
    }
  }

  useEffect(() => {
    load()
  }, [])

  // Apply the hub's practice intent once this page's own org data arrives
  // (e.g. intent arrived before the list was known).
  useEffect(() => {
    if (intentApplied || orgs === null) return
    setCreateMode(orgs.length === 0)
    setIntentApplied(true)
  }, [orgs, intentApplied])

  // "Show me around": auto-open the freshly created demo workspace. The
  // server-side profile gate inside WorkSpace shows the mandatory Business
  // Profile form first (a brand-new workspace starts profile_completed=false)
  // — never skipped, exactly like any other new workspace.
  useEffect(() => {
    if (autoSelectOrgId == null || orgs === null || activeOrg) return
    const match = orgs.find((o) => o.id === autoSelectOrgId)
    if (match) {
      setCreateMode(false)
      setActiveOrg(match)
      setSection('home')
      if (onAutoSelectHandled) onAutoSelectHandled()
    }
  }, [autoSelectOrgId, orgs, activeOrg, onAutoSelectHandled])

  // Single source of org-state updates from inside WorkSpace. WorkSpace is a
  // SEPARATE module-level component and can never see DashboardPage's
  // setActiveOrg directly, so the updater is passed down as a prop instead.
  function handleOrgUpdated(updated) {
    setActiveOrg((current) =>
      current && current.id === updated.id ? { ...current, ...updated } : current
    )
  }

  // NEW workspace -> straight into the MANDATORY Business Profile step (server
  // starts it at profile_completed=false, so the gate also survives reloads).
  function handleCreated(created) {
    setCreateMode(false)
    setActiveOrg(created)
    setSection('businessProfile')
    load() // refresh the workspace list in the background
  }

  // Open an EXISTING workspace from the list. No profile form is re-demanded
  // here: the server-side gate inside WorkSpace renders the mandatory step
  // ONLY when profile_completed is genuinely false.
  function openOrg(org) {
    setCreateMode(false)
    setActiveOrg(org)
    setSection('home')
  }

  function exitWorkspace() {
    setActiveOrg(null)
    setSection('home')
    setCreateMode(false) // with 1+ orgs the workspace list is Practice's home
  }

  if (activeOrg) {
    return (
      <WorkSpace
        org={activeOrg}
        section={section}
        onSectionChange={setSection}
        onExit={exitWorkspace}
        onOrgUpdated={handleOrgUpdated}
        onBackToHub={onBackToHub}
        onRestore={handleRestore}
      />
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto w-full max-w-2xl">
        <h2 className="text-xl font-bold text-slate-900">
          {t('dashboard.welcome')}, {user?.display_name}
        </h2>

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}

        {orgs === null ? (
          <p className="mt-10 text-center text-slate-500">{t('common.loading')}</p>
        ) : createMode ? (
          <div className="mt-8">
            {orgs.length > 0 && (
              <button
                type="button"
                onClick={() => setCreateMode(false)}
                className="mb-4 text-sm text-slate-500 hover:text-slate-700"
              >
                {t('dashboard.backToWorkspaces')}
              </button>
            )}
            <CreateWorkspace frameworks={frameworks} onCreated={handleCreated} />
          </div>
        ) : orgs.length === 0 ? (
          <div className="mt-8">
            <CreateWorkspace frameworks={frameworks} onCreated={handleCreated} />
          </div>
        ) : (
          <div className="mt-8">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                {t('dashboard.workspaces')}
              </h3>
              <button
                type="button"
                onClick={() => setCreateMode(true)}
                className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
              >
                {t('dashboard.createNewBusiness')}
              </button>
            </div>
            {actionError && (
              <p className="mt-3 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
                {actionError}
              </p>
            )}
            <ul className="mt-3 space-y-3">
              {orgs.map((org) => {
                const actions = workspaceActions(org)
                return (
                  <li
                    key={org.id}
                    className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-semibold text-slate-900">{org.name}</span>
                      <div className="flex items-center gap-2">
                        {org.is_demo && (
                          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                            Demo
                          </span>
                        )}
                        {/* Framework badge — required by the returning-user
                            list spec (name + framework badge). */}
                        <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                          {org.framework}
                        </span>
                      </div>
                    </div>
                    <dl className="mt-2 grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <dt className="text-slate-500">{t('dashboard.currency')}</dt>
                        <dd className="font-medium text-slate-800">{org.currency}</dd>
                      </div>
                    </dl>
                    <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
                      <button
                        type="button"
                        onClick={() => openOrg(org)}
                        className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                      >
                        {t('dashboard.open')}
                      </button>
                      {actions.map((action) => (
                        <button
                          key={action.key}
                          type="button"
                          disabled={action.disabled}
                          title={action.disabled ? t(action.reason) : undefined}
                          onClick={() =>
                            action.key === 'archive'
                              ? setConfirmArchiveOrg(org)
                              : setConfirmDeleteOrg(org)
                          }
                          className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
                            action.disabled
                              ? 'cursor-not-allowed border border-slate-200 bg-slate-100 text-slate-400'
                              : action.key === 'archive'
                                ? 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-100'
                                : 'border border-red-200 bg-white text-red-600 hover:bg-red-50'
                          }`}
                        >
                          {action.key === 'archive'
                            ? t('ws.archiveAction')
                            : t('ws.deleteAction')}
                        </button>
                      ))}
                    </div>
                    {hasProtectedHistory(org) && (
                      <p className="mt-2 text-xs text-slate-500">
                        {t('ws.deleteBlockedProtected')}
                      </p>
                    )}
                  </li>
                )
              })}
            </ul>
            {/* Deliberate archived-retrieval path: hidden by default, fetched
                only when the owner asks for it. */}
            <div className="mt-4 border-t border-slate-200 pt-3">
              <button
                type="button"
                onClick={toggleArchived}
                className="text-sm font-medium text-slate-500 hover:text-slate-700"
              >
                {showArchived ? t('ws.hideArchived') : t('ws.showArchived')}
              </button>
              {showArchived && (
                <ul className="mt-3 space-y-3">
                  {archivedOrgs === null ? (
                    <li className="text-sm text-slate-500">{t('common.loading')}</li>
                  ) : archivedOrgs.length === 0 ? (
                    <li className="text-sm text-slate-500">{t('ws.archivedEmpty')}</li>
                  ) : (
                    archivedOrgs.map((org) => {
                      const actions = archivedWorkspaceActions(org)
                      return (
                        <li
                          key={org.id}
                          className="rounded-xl border border-slate-300 bg-slate-50 p-4"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-semibold text-slate-700">
                              {org.name}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-600">
                                {t('ws.archivedBadge')}
                              </span>
                              <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                                {org.framework}
                              </span>
                            </div>
                          </div>
                          <p className="mt-1 text-xs text-slate-500">
                            {t('ws.archivedNotice')}
                          </p>
                          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
                            {actions.map((action) => (
                              <button
                                key={action.key}
                                type="button"
                                disabled={action.disabled}
                                title={action.disabled ? t(action.reason) : undefined}
                                onClick={() =>
                                  action.key === 'openReadonly'
                                    ? openOrg(org)
                                    : action.key === 'restore'
                                      ? handleRestore(org)
                                      : setConfirmDeleteOrg(org)
                                }
                                className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
                                  action.disabled
                                    ? 'cursor-not-allowed border border-slate-200 bg-slate-100 text-slate-400'
                                    : action.key === 'openReadonly'
                                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                                      : action.key === 'restore'
                                        ? 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-100'
                                        : 'border border-red-200 bg-white text-red-600 hover:bg-red-50'
                                }`}
                              >
                                {action.key === 'openReadonly'
                                  ? t('ws.openReadonlyAction')
                                  : action.key === 'restore'
                                    ? t('ws.restoreAction')
                                    : t('ws.deleteAction')}
                              </button>
                            ))}
                          </div>
                          {hasProtectedHistory(org) && (
                            <p className="mt-2 text-xs text-slate-500">
                              {t('ws.deleteBlockedProtected')}
                            </p>
                          )}
                        </li>
                      )
                    })
                  )}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>
      {/* Archive confirmation: a plain dialog — archive deletes NOTHING and
          is always reversible. */}
      {confirmArchiveOrg && (
        <ConfirmModal
          title={t('ws.archiveConfirmTitle')}
          body={t('ws.archiveConfirmBody')}
          confirmLabel={t('ws.archiveAction')}
          cancelLabel={t('ws.cancel')}
          onConfirm={() => handleArchive(confirmArchiveOrg)}
          onCancel={() => setConfirmArchiveOrg(null)}
        />
      )}
      {/* Permanent delete: the STRONGER typed-name confirmation. The exact
          name must be typed; the API validates it server-side again. */}
      {confirmDeleteOrg && (
        <DeleteWorkspaceModal
          org={confirmDeleteOrg}
          title={t('ws.deleteConfirmTitle')}
          body={t('ws.deleteConfirmBody')}
          label={t('ws.deleteConfirmLabel')}
          placeholder={t('ws.deleteConfirmPlaceholder')}
          confirmLabel={t('ws.deleteAction')}
          cancelLabel={t('ws.cancel')}
          validate={(input) =>
            validateDeleteConfirmation(input, confirmDeleteOrg.name)
          }
          errorLabel={t('ws.actionError')}
          notEligibleLabel={t('ws.deleteBlockedProtected')}
          onConfirm={handleDelete}
          onCancel={() => setConfirmDeleteOrg(null)}
        />
      )}
    </div>
  )
}


function NavBtn({ active, onClick, label, disabled = false, title }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={disabled ? title : undefined}
      className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
        disabled
          ? 'cursor-not-allowed text-slate-300'
          : active
            ? 'bg-blue-600 text-white'
            : 'text-slate-700 hover:bg-slate-100'
      }`}
    >
      {label}
    </button>
  )
}

// Simple confirm dialog (archive). Fixed overlay + centered card, usable on
// phone widths — the established modal pattern of this app.
function ConfirmModal({ title, body, confirmLabel, cancelLabel, onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-5 shadow-lg">
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        <p className="mt-2 text-sm text-slate-600">{body}</p>
        <div className="mt-4 flex justify-end gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

// Stronger typed-name confirmation for PERMANENT deletion. The exact
// workspace name must be typed; the button stays disabled until validation
// passes — and the API re-validates server-side regardless.
function DeleteWorkspaceModal({
  org,
  title,
  body,
  label,
  placeholder,
  confirmLabel,
  cancelLabel,
  validate,
  errorLabel,
  notEligibleLabel,
  onConfirm,
  onCancel,
}) {
  const { t } = useLanguage()
  const [value, setValue] = useState('')
  const [busy, setBusy] = useState(false)
  const [failed, setFailed] = useState(false)

  const problem = validate(value)
  const eligible = isDeleteEligible(org)
  const canSubmit = eligible && !problem && !busy

  async function submit() {
    if (!canSubmit) return
    setBusy(true)
    try {
      await onConfirm(org, value)
    } catch {
      setFailed(true)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-5 shadow-lg">
        <h3 className="text-lg font-semibold text-red-600">{title}</h3>
        <p className="mt-2 text-sm text-slate-600">{body}</p>
        {!eligible && (
          <p className="mt-3 rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            {notEligibleLabel}
          </p>
        )}
        <label
          htmlFor="delete-workspace-confirm"
          className="mt-4 block text-sm font-medium text-slate-800"
        >
          {label}
        </label>
        <input
          id="delete-workspace-confirm"
          type="text"
          value={value}
          disabled={!eligible}
          placeholder={placeholder}
          autoComplete="off"
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') submit()
          }}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none"
        />
        {value.length > 0 && problem && (
          <p className="mt-1 text-sm text-red-600">{t(problem)}</p>
        )}
        {failed && (
          <p className="mt-1 text-sm text-red-600">{errorLabel}</p>
        )}
        <div className="mt-4 flex justify-end gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={submit}
            disabled={!canSubmit}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium text-white ${
              canSubmit ? 'bg-red-600 hover:bg-red-700' : 'cursor-not-allowed bg-red-300'
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

function WorkSpace({ org, section, onSectionChange, onExit, onOrgUpdated, onBackToHub, onRestore }) {
  const { t } = useLanguage()
  const [ledgerAccount, setLedgerAccount] = useState(null) // preset by trial-balance drill-down
  const [lessonId, setLessonId] = useState(null) // lesson opened from Learn (Session 11 Part A)

  // ARCHIVED workspace = read-only mode. Historical/report views (journal,
  // cashbook, ledger, trial balance, financial statements) stay FULLY
  // readable; mutation-capable sections render disabled with an explanatory
  // hint, and the backend rejects any mutation anyway (409, service layer).
  const archived = isArchived(org)

  // MANDATORY Business-Profile gate. Driven by the SERVER-SIDE
  // profile_completed flag (migration 0011): a brand-new workspace starts
  // False, so the gate survives page reloads and the step genuinely cannot be
  // skipped. While gated, ONLY the BusinessProfilePage renders — no other
  // section is reachable through nav or home cards (real enforcement, not
  // cosmetic). Pre-mandate orgs are backfilled True and never hard-blocked.
  // A workspace with a COMPLETED profile never sees the form again.
  const gated = profileGateActive(org)

  // Pre-mandate / incomplete orgs: a DISMISSIBLE completion banner, never a
  // hard block (per-session dismissal; the mandate itself only hard-gates NEW
  // workspaces). Note: a learner workspace (registration fields intentionally
  // left empty) also matches this banner condition — it is informational only
  // and dismissible, which keeps the learner exempt from any block.
  const [bannerDismissed, setBannerDismissed] = useState(false)
  const showBanner = !gated && profileNeedsAttention(org) && !bannerDismissed

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 px-4 py-2 backdrop-blur">
        <div className="mx-auto flex max-w-3xl flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-3">
            {/* Persistent hub access from DEEP inside Practice (Part 2). */}
            {onBackToHub && (
              <button
                type="button"
                onClick={onBackToHub}
                title={t('choice.backToStart')}
                className="text-slate-400 transition-colors hover:text-slate-700"
              >
                <Logo wordmark={t('app.title')} showWordmark={false} iconSize="h-6 w-6" />
              </button>
            )}
            <button
              type="button"
              onClick={onExit}
              className="text-sm font-medium text-slate-600 hover:text-slate-900"
            >
              {org.name} — {t('dashboard.workspaces')}
            </button>
            {archived && (
              <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-600">
                {t('ws.archivedBadge')} — {t('ws.readonlyBadge')}
              </span>
            )}
          </div>
          {gated ? (
            // Gated: the other destinations are unreachable by design.
            <span className="text-sm font-medium text-slate-500">
              {t('bp.mandatoryTitle')}
            </span>
          ) : (
            <div className="flex gap-1">
              <NavBtn active={section === 'home'} onClick={() => onSectionChange('home')} label={t('ws.home')} />
              <NavBtn
                active={section === 'newTransaction'}
                onClick={() => onSectionChange('newTransaction')}
                label={t('ws.newTransaction')}
                disabled={archived}
                title={archived ? t('ws.archivedReadonlyHint') : undefined}
              />
              <NavBtn active={section === 'journal'} onClick={() => onSectionChange('journal')} label={t('ws.journal')} />
              <NavBtn active={section === 'cashbook'} onClick={() => onSectionChange('cashbook')} label={t('ws.cashbook')} />
              <NavBtn active={section === 'ledger'} onClick={() => onSectionChange('ledger')} label={t('ws.ledger')} />
              <NavBtn active={section === 'trialBalance'} onClick={() => onSectionChange('trialBalance')} label={t('ws.trialBalance')} />
              <NavBtn active={section === 'financialStatements'} onClick={() => onSectionChange('financialStatements')} label={t('ws.financialStatements')} />
              <NavBtn
                active={section === 'learn'}
                onClick={() => onSectionChange('learn')}
                label={t('ws.learn')}
                disabled={archived}
                title={archived ? t('ws.archivedReadonlyHint') : undefined}
              />
              <NavBtn
                active={section === 'accounts'}
                onClick={() => onSectionChange('accounts')}
                label={t('ws.accounts')}
              />
              <NavBtn
                active={section === 'businessProfile'}
                onClick={() => onSectionChange('businessProfile')}
                label={t('ws.businessProfile')}
              />
            </div>
          )}
        </div>
      </nav>
      <main>
        {/* Archived workspaces: clear read-only banner with Restore. Nothing
            was deleted — historical views below remain fully readable. */}
        {archived && !gated && (
          <div className="mx-auto max-w-3xl px-4 pt-4">
            <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-300 bg-slate-100 px-3 py-2 text-sm text-slate-700">
              <span>{t('ws.archivedNotice')}</span>
              {onRestore && (
                <button
                  type="button"
                  onClick={() => onRestore(org)}
                  className="rounded-lg border border-slate-400 bg-white px-2 py-1 font-medium text-slate-700 hover:bg-slate-200"
                >
                  {t('ws.restoreAction')}
                </button>
              )}
            </div>
          </div>
        )}
        {gated && (
          <BusinessProfilePage
            org={org}
            mandatory
            onSaved={onOrgUpdated}
            onDone={() => onSectionChange('home')}
          />
        )}
        {!gated && showBanner && (
          <div className="mx-auto max-w-3xl px-4 pt-4">
            <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-800">
              <span>{t('bp.banner')}</span>
              <span className="flex gap-2">
                <button
                  type="button"
                  onClick={() => onSectionChange('businessProfile')}
                  className="rounded-lg border border-amber-500 px-2 py-1 font-medium text-amber-800 hover:bg-amber-100"
                >
                  {t('bp.bannerAction')}
                </button>
                <button
                  type="button"
                  onClick={() => setBannerDismissed(true)}
                  className="rounded-lg px-2 py-1 text-amber-700 hover:bg-amber-100"
                >
                  {t('bp.bannerDismiss')}
                </button>
              </span>
            </div>
          </div>
        )}
        {/* Every section below is hard-guarded by !gated: while the mandatory
            Business Profile step is outstanding, NO other feature renders,
            regardless of what `section` happens to be (real enforcement). */}
        {!gated && section === 'home' && (
          <OrgHome
            org={org}
            onAccounts={() => onSectionChange('accounts')}
            onNewTransaction={() => onSectionChange('newTransaction')}
            onJournal={() => onSectionChange('journal')}
            onCashBook={() => onSectionChange('cashbook')}
            onLedger={() => onSectionChange('ledger')}
            onTrialBalance={() => onSectionChange('trialBalance')}
            onFinancialStatements={() => onSectionChange('financialStatements')}
            onBusinessProfile={() => onSectionChange('businessProfile')}
          />
        )}
        {!gated && section === 'accounts' && (
          <ChartOfAccountsPage
            org={org}
            onBack={() => onSectionChange('home')}
            readOnly={archived}
          />
        )}
        {!gated && section === 'newTransaction' && (
          <NewTransactionPage org={org} onBack={() => onSectionChange('home')} />
        )}
        {!gated && section === 'journal' && (
          <JournalPage org={org} onBack={() => onSectionChange('home')} />
        )}
        {!gated && section === 'cashbook' && (
          <CashBookPage org={org} onBack={() => onSectionChange('home')} />
        )}
        {!gated && section === 'ledger' && (
          <GeneralLedgerPage org={org} onBack={() => onSectionChange('home')} initialAccountId={ledgerAccount} />
        )}
        {!gated && section === 'trialBalance' && (
          <TrialBalancePage
            org={org}
            onBack={() => onSectionChange('home')}
            onOpenLedger={(accountId) => {
              setLedgerAccount(accountId)
              onSectionChange('ledger')
            }}
          />
        )}
        {!gated && section === 'financialStatements' && (
          <FinancialStatementsPage
            org={org}
            onBack={() => onSectionChange('home')}
            onOpenLedger={(accountId) => {
              setLedgerAccount(accountId)
              onSectionChange('ledger')
            }}
          />
        )}
        {!gated && section === 'businessProfile' && (
          <BusinessProfilePage
            org={org}
            onBack={() => onSectionChange('home')}
            onSaved={onOrgUpdated}
            readOnly={archived}
          />
        )}
        {/* Session 11 Part A — Learn Mode: lesson list, then lesson detail.
            The detail page receives the org id so lesson 4's practice
            connector can post a REAL transaction into this workspace
            (Learn Mode -> Practice Mode). */}
        {!gated && section === 'learn' && (
          <LearnPage
            onOpenLesson={(id) => {
              setLessonId(id)
              onSectionChange('lesson')
            }}
          />
        )}
        {!gated && section === 'lesson' && lessonId != null && (
          <LessonDetailPage
            lessonId={lessonId}
            orgId={org.id}
            onBack={() => onSectionChange('learn')}
          />
        )}
      </main>
    </div>
  )
}

function OrgHome({ org, onAccounts, onNewTransaction, onJournal, onCashBook, onLedger, onTrialBalance, onFinancialStatements, onBusinessProfile }) {
  const { t } = useLanguage()
  // Archived workspaces: the pure-mutation card (new transaction) renders
  // disabled with the explanatory hint; reports/history AND the read-only
  // viewable sections (chart of accounts, business profile) stay fully
  // clickable — the pages hide their own edit controls and the service layer
  // rejects any mutation with 409 anyway.
  const archived = isArchived(org)
  const readonlyHint = archived ? t('ws.archivedReadonlyHint') : undefined
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h2 className="text-2xl font-bold text-slate-900">{org.name}</h2>
      <p className="mt-1 text-sm text-slate-600">
        {t('dashboard.framework')} {org.framework} · {t('dashboard.currency')} {org.currency}
      </p>
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <BigCard
          title={t('ws.newTransactionTitle')}
          desc={t('ws.newTransactionDesc')}
          action={t('ws.newTransaction')}
          onClick={onNewTransaction}
          disabled={archived}
          hintTitle={readonlyHint}
        />
        <BigCard
          title={t('ws.journalTitle')}
          desc={t('ws.journalDesc')}
          action={t('ws.journal')}
          onClick={onJournal}
        />
        <BigCard
          title={t('ws.cashbookTitle')}
          desc={t('ws.cashbookDesc')}
          action={t('ws.cashbook')}
          onClick={onCashBook}
        />
        <BigCard
          title={t('ws.ledgerTitle')}
          desc={t('ws.ledgerDesc')}
          action={t('ws.ledger')}
          onClick={onLedger}
        />
        <BigCard
          title={t('ws.trialBalanceTitle')}
          desc={t('ws.trialBalanceDesc')}
          action={t('ws.trialBalanceAction')}
          onClick={onTrialBalance}
        />
        <BigCard
          title={t('ws.financialStatementsTitle')}
          desc={t('ws.financialStatementsDesc')}
          action={t('ws.financialStatementsAction')}
          onClick={onFinancialStatements}
        />
        <BigCard
          title={t('ws.accountsTitle')}
          desc={t('ws.accountsDesc')}
          action={t('ws.accounts')}
          onClick={onAccounts}
        />
        <BigCard
          title={t('bp.title')}
          desc={t('bp.subtitle')}
          action={t('ws.businessProfile')}
          onClick={onBusinessProfile}
        />
      </div>
    </div>
  )
}

function BigCard({ title, desc, action, onClick, disabled = false, hintTitle }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={disabled ? hintTitle : undefined}
      className={`rounded-xl border p-5 text-left shadow-sm ${
        disabled
          ? 'cursor-not-allowed border-slate-200 bg-slate-100'
          : 'border-slate-200 bg-white hover:border-blue-300'
      }`}
    >
      <h3 className="font-semibold text-slate-900">{title}</h3>
      <p className="mt-1 text-sm text-slate-600">{desc}</p>
      <span className="mt-3 inline-block text-sm font-medium text-blue-600">{action} →</span>
    </button>
  )
}
