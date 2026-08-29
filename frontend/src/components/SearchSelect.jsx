// Simple SEARCHABLE dropdown (type-to-filter) for the Business Profile's
// country and legal-form selectors. A plain unsearchable <select> is poor UX
// at this scale (17 OHADA states / ~200 IFRS countries / 10 legal forms), so
// this follows the same filter-as-you-type approach as the account lookup.
//
// Controlled by `value` (the option's `code`); the caller supplies the option
// list and the label/sub-label getters (language-aware). Options render on
// mousedown so clicking one wins over the input's blur.
import { useMemo, useState } from 'react'

export default function SearchSelect({
  id,
  options,
  value,
  onChange,
  placeholder,
  getOptionLabel,
  getOptionSub,
  disabled = false,
  inputCls,
}) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const selected = options.find((o) => o.code === value)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return options
    return options.filter((o) => getOptionLabel(o).toLowerCase().includes(q))
  }, [options, query, getOptionLabel])

  return (
    <div className="relative">
      <input
        id={id}
        type="text"
        autoComplete="off"
        disabled={disabled}
        value={open ? query : selected ? getOptionLabel(selected) : ''}
        onChange={(e) => {
          setQuery(e.target.value)
          setOpen(true)
        }}
        onFocus={() => {
          setQuery('')
          setOpen(true)
        }}
        onBlur={() => setTimeout(() => setOpen(false), 100)}
        placeholder={placeholder}
        className={inputCls}
      />
      {open && !disabled && (
        <ul className="absolute z-20 mt-1 max-h-60 w-full overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg">
          {filtered.length === 0 && (
            <li className="px-3 py-2 text-sm text-slate-500">—</li>
          )}
          {filtered.map((o) => (
            <li key={o.code}>
              <button
                type="button"
                onMouseDown={() => {
                  onChange(o.code)
                  setOpen(false)
                }}
                className="w-full px-3 py-2 text-left text-sm hover:bg-blue-50"
              >
                <span className="font-medium text-slate-800">{getOptionLabel(o)}</span>
                {getOptionSub && (
                  <span className="block text-xs text-slate-500">{getOptionSub(o)}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}