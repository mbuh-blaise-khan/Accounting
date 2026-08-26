// Type-ahead account filter for Journal / Cash Book / General Ledger (Part B).
//
// Those pages used a plain <select> that required scrolling through 80+ chart
// rows. This wrapper reuses the existing AccountLookup autocomplete (same
// progressive prefix-narrowing already built for transaction entry) for the
// "filter the page by one account" use case: type part of a code (OHADA) or a
// name (both frameworks) to narrow live, pick a suggestion, or clear back to
// "all accounts". What happens AFTER selection is unchanged from the old
// <select> — it just sets the page's account-id filter.
import AccountLookup from './AccountLookup.jsx'

export default function AccountFilterSelect({
  accounts,
  framework,
  value, // selected Account object or null
  onChange, // (accountId: number | '') => void
  t,
  nameOf,
}) {
  const hasValue = Boolean(value)
  return (
    <div className="relative">
      <div className="flex items-start gap-2">
        <div className="min-w-0 flex-1">
          <AccountLookup
            accounts={accounts}
            framework={framework}
            value={value || null}
            onChange={(acct) => onChange(acct ? acct.id : '')}
            placeholder={t('journal.allAccounts')}
          />
        </div>
        {hasValue && (
          <button
            type="button"
            onClick={() => onChange('')}
            title={t('journal.clearAccount')}
            className="mt-1 shrink-0 rounded-lg border border-slate-300 px-2 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100"
          >
            ✕
          </button>
        )}
      </div>
      {hasValue && (
        <span className="mt-0.5 block truncate text-xs text-slate-500">
          {framework !== 'OHADA' && value.code ? `${value.code} — ` : ''}
          {nameOf(value)}
        </span>
      )}
    </div>
  )
}