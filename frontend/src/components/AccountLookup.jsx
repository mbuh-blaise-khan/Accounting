// Bidirectional code <-> name lookup over an organization's OWN chart.
// The caller passes only that org's accounts (the API list is org-scoped),
// so lookups can never match accounts from another workspace.
//
// Typing a code suggests the account with that code; typing a name (in either
// language) suggests matching accounts and their codes. Matches are shown with
// the code and both language names.
import { useEffect, useMemo, useRef, useState } from 'react'
import { useLanguage } from '../i18n/index.jsx'
import { searchAccounts } from '../utils/accountLookup.js'

export default function AccountLookup({
  accounts,
  value: selected,
  onChange,
  label,
  placeholder,
  compact = false,
}) {
  const { t } = useLanguage()
  const [query, setQuery] = useState(
    selected ? `${selected.code} — ${selected.name_en}` : ''
  )
  const [open, setOpen] = useState(false)
  const [highlight, setHighlight] = useState(0)
  const wrapperRef = useRef(null)

  const matches = useMemo(() => {
    if (!open) return []
    return searchAccounts(accounts, query)
  }, [accounts, query, open])

  // Close on outside click / Escape.
  useEffect(() => {
    function onDown(e) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    function onKey(e) {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onDown)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDown)
      document.removeEventListener('keydown', onKey)
    }
  }, [])

  function pick(account) {
    setQuery(`${account.code} — ${account.name_en}`)
    setOpen(false)
    onChange(account)
  }

  // In compact mode the label is shown as placeholder text inside the input
  // (used for inline journal-entry grid rows).
  const inputCls = compact
    ? 'w-full rounded-md border border-slate-300 px-2 py-1 text-xs text-slate-800 placeholder-slate-400 focus:border-blue-500 focus:outline-none'
    : 'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none'

  return (
    <div ref={wrapperRef} className="relative">
      {label && !compact && (
        <label className="block text-sm font-medium text-slate-700">{label}</label>
      )}
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value)
          setOpen(true)
          setHighlight(0)
        }}
        onFocus={() => setOpen(true)}
                placeholder={placeholder || t('coa.lookupPlaceholder')}
        className={inputCls}
        aria-autocomplete="list"
        aria-expanded={open}
      />
            {open && matches.length > 0 && (
        <ul
          role="listbox"
          className={`absolute z-10 mt-1 w-full overflow-y-auto rounded-lg border border-slate-200 bg-white py-1 shadow-lg ${
            compact ? 'max-h-40' : 'max-h-64'
          }`}
        >
          {matches.map((a, i) => (
            <li
              key={a.id}
              role="option"
              aria-selected={selected?.id === a.id}
              onMouseDown={(e) => {
                // prevent blur-before-click
                e.preventDefault()
                pick(a)
              }}
              onMouseEnter={() => setHighlight(i)}
              className={`cursor-pointer px-2 py-1 ${
                compact ? 'text-xs' : 'text-sm'
              } ${
                i === highlight || selected?.id === a.id
                  ? 'bg-blue-50 font-medium'
                  : 'hover:bg-slate-50'
              }`}
            >
              <span className="font-mono text-xs text-slate-500">{a.code}</span>
              {' — '}
              <span className="text-slate-800">{a.name_en}</span>
              <span className="mx-1 text-slate-400">·</span>
              <span className="text-slate-500">{a.name_fr}</span>
            </li>
          ))}
        </ul>
      )}
      {open && query.trim() && matches.length === 0 && (
        <p className="absolute z-10 mt-1 w-full rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs text-slate-500 shadow-lg">
          {t('coa.noResults')}
        </p>
      )}
    </div>
  )
}
