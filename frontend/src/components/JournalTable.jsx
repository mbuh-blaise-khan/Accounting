// Shared read-only table for the Journal and Cash Book (Session 7; Session 8
// adds visual grouping). Presentation only — no data, filter or totals change.
//
// Columns follow the researched journal layouts:
//   OHADA: date (posted_at, FIRST — Part C) | N° compte | intitulé | libellé |
//          débit | crédit (+ reference/description/source/status metadata)
//   IFRS:  same structure WITHOUT the account-number column (Part B).
// Every row links back to its originating transaction detail (drill-down).
// The table is horizontally scrollable on phone-width screens.
//
// Session 8 grouping (user feedback on Session 7):
// 1. A distinct DATE separator band is rendered above the first transaction of
//    each day, so entries from different days/weeks are obvious when scanning.
// 2. Rows of one transaction (same reference) read as ONE visual unit: a thin
//    divider starts each new transaction and group backgrounds alternate.
// 3. Double-entry convention: credit-side rows are indented (account name and
//    amount shifted right) versus debit rows, so debits vs credits can be told
//    apart at a glance without re-reading the column headers.
function buildDisplay(rows) {
  const items = []
  let lastDateKey = null
  let lastRef = null
  let band = 0
  let justDate = false
  for (const r of rows) {
    const d = r.date ? new Date(r.date) : null
    const dateKey = d ? `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}` : 'none'
    if (dateKey !== lastDateKey) {
      items.push({ kind: 'date', date: d, key: `d${items.length}` })
      lastDateKey = dateKey
      lastRef = null // a new day always starts a fresh transaction group
      justDate = true
    }
    const firstInTxn = r.reference !== lastRef
    if (firstInTxn) {
      band = (band + 1) % 2 // alternate background per TRANSACTION group
      lastRef = r.reference
      // A bold rule separates this transaction from the previous one. This is
      // the entry-level boundary (stronger than the faint row borders) so
      // TX-0012 / TX-0013 / TX-0014 read as unmistakable blocks.
      if (items.length > 0 && !justDate) {
        items.push({ kind: 'gap', key: `g${items.length}` })
      }
      justDate = false
    } else {
      justDate = false
    }
    items.push({ kind: 'row', row: r, band, firstInTxn })
  }
  return items
}

export default function JournalTable({ rows, org, nameOf, t, onViewTxn }) {
  const isOhada = org.framework === 'OHADA'
  const display = buildDisplay(rows)

  function fmtAmount(n) {
    return (Number(n) || 0).toLocaleString()
  }

  function fmtDate(iso) {
    if (!iso) return '—'
    return new Date(iso).toLocaleString()
  }

  function fmtDay(d) {
    if (!d) return t('journal.noDate')
    return d.toLocaleDateString(undefined, {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const totalDebit = rows.reduce((s, r) => s + (Number(r.debit) || 0), 0)
  const totalCredit = rows.reduce((s, r) => s + (Number(r.credit) || 0), 0)
  const colCount = isOhada ? 11 : 10

  // Row styling shared by every line of one transaction group. Transaction
  // BOUNDARIES are drawn by the dedicated gap rule lines, not by these faint
  // per-row borders, so different entries never blur together.
  function rowClass(item) {
    const { row: r, band } = item
    return [
      'border-b border-slate-100 hover:bg-slate-100/70',
      band ? 'bg-slate-50' : '',
      r.credit > 0 ? 'is-credit' : '',
    ]
      .filter(Boolean)
      .join(' ')
  }

  // One display item = a sticky DATE band, a bold TRANSACTION-boundary rule, or
  // one journal LINE.
  function renderItem(item) {
    if (item.kind === 'date') {
      return (
        <tr
          key={item.key}
          className="sticky top-0 z-[1] bg-slate-200/95 backdrop-blur-sm"
        >
          <td
            colSpan={colCount}
            className="border-y border-slate-300 px-3 py-1.5 text-xs font-bold uppercase tracking-wide text-slate-700"
          >
            {fmtDay(item.date)}
          </td>
        </tr>
      )
    }

    if (item.kind === 'gap') {
      // A bold, full-width rule between DIFFERENT transactions (double-entry
      // "ruling line" convention) — stronger than any in-transaction separator.
      return (
        <tr key={item.key} aria-hidden="true">
          <td colSpan={colCount} className="p-0">
            <div className="border-t-2 border-slate-400" />
          </td>
        </tr>
      )
    }

    const r = item.row
    const isCredit = Number(r.credit) > 0
    return (
      <tr key={r.id} className={rowClass(item)}>
        <td className="whitespace-nowrap px-3 py-2 text-slate-700">
          {fmtDate(r.date)}
        </td>
        <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-600">
          {r.reference}
        </td>
        <td className="max-w-[220px] truncate px-3 py-2 text-slate-700">
          {r.description || '—'}
        </td>
        {isOhada && (
          <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-600">
            {r.account_code || ''}
          </td>
        )}
        {/* Double-entry convention: credit-side names are indented well under
            their debit counterpart so the side reads without the header (Part D:
            strong, explicit offset — pl-16, not a faint nudge). */}
        <td
          className={`max-w-[210px] truncate px-3 py-2 ${
            isCredit ? 'pl-16 text-slate-700' : 'font-medium text-slate-900'
          }`}
        >
          {isCredit ? '↳ ' : ''}
          {nameOf(r)}
        </td>
        <td className="max-w-[180px] truncate px-3 py-2 text-slate-600">
          {r.narration || '—'}
        </td>
        <td className="whitespace-nowrap px-3 py-2 text-right font-medium text-slate-900">
          {Number(r.debit) > 0 ? fmtAmount(r.debit) : ''}
        </td>
        {/* Credit amounts sit visibly indented within their column (pl-14) so the
            credited line reads shifted right of the debit figure — not flush. */}
        <td
          className={`whitespace-nowrap text-right ${
            isCredit ? 'pl-14 pr-2 text-slate-700' : 'px-3 pr-3 font-light text-slate-300'
          } py-2`}
        >
          {isCredit ? `↳ ${fmtAmount(r.credit)}` : ''}
        </td>
        <td className="px-3 py-2 text-slate-600">{r.source || '—'}</td>
        <td className="px-3 py-2">
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
            {r.status}
          </span>
        </td>
        <td className="px-3 py-2 text-right">
          <button
            type="button"
            onClick={() => onViewTxn(r.transaction_id)}
            className="text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            {t('journal.view')} →
          </button>
        </td>
      </tr>
    )
  }

  return (
    <div>
      {/* Desktop table */}
      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase text-slate-500">
              <th className="px-3 py-2">{t('journal.date')}</th>
              <th className="px-3 py-2">{t('journal.reference')}</th>
              <th className="px-3 py-2">{t('journal.description')}</th>
              {isOhada && <th className="px-3 py-2">{t('journal.accountNo')}</th>}
              <th className="px-3 py-2">{t('journal.accountName')}</th>
              <th className="px-3 py-2">{t('journal.narration')}</th>
              <th className="px-3 py-2 text-right">{t('journal.debit')}</th>
              <th className="px-3 py-2 text-right">{t('journal.credit')}</th>
              <th className="px-3 py-2">{t('journal.source')}</th>
              <th className="px-3 py-2">{t('journal.status')}</th>
              <th className="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody>{display.map(renderItem)}</tbody>
          <tfoot>
            <tr className="border-t border-slate-200 bg-slate-50 font-semibold text-slate-800">
              <td className="px-3 py-2" colSpan={isOhada ? 6 : 5}>
                {t('journal.totals')}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-right">
                {fmtAmount(totalDebit)}
              </td>
              <td className="whitespace-nowrap px-3 py-2 pr-9 text-right">
                {fmtAmount(totalCredit)}
              </td>
              <td colSpan={3}></td>
            </tr>
          </tfoot>
        </table>
      </div>

      {/* Mobile: stacked cards (no horizontal scrolling), same grouping rules */}
      <div className="mt-3 space-y-2 sm:hidden">
        {display.map((item) => {
          if (item.kind === 'date') {
            return (
              <div
                key={item.key}
                className="rounded-lg bg-slate-200/90 px-3 py-1.5 text-xs font-bold uppercase tracking-wide text-slate-700"
              >
                {fmtDay(item.date)}
              </div>
            )
          }
          if (item.kind === 'gap') {
            return (
              <div key={item.key} className="border-t-2 border-slate-400" />
            )
          }
          const r = item.row
          const isCredit = Number(r.credit) > 0
          return (
            <div
              key={r.id}
              className={`rounded-xl border border-slate-200 p-4 shadow-sm ${
                item.band ? 'bg-slate-50' : 'bg-white'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div
                  className={`min-w-0 ${
                    isCredit ? 'border-l-4 border-blue-300 pl-4' : ''
                  }`}
                >
                  <p
                    className={`font-semibold ${
                      isCredit ? 'text-slate-700' : 'text-slate-900'
                    }`}
                  >
                    {isCredit ? '↳ ' : ''}
                    {nameOf(r)}
                  </p>
                  <p className="text-xs text-slate-500">
                    {fmtDate(r.date)} · {r.reference}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => onViewTxn(r.transaction_id)}
                  className="shrink-0 text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  {t('journal.view')} →
                </button>
              </div>
              <p className="mt-1 text-sm text-slate-700">{r.description || '—'}</p>
              {r.narration && (
                <p className="mt-0.5 text-xs text-slate-500">« {r.narration} »</p>
              )}
              <div className="mt-2 flex gap-4 text-sm">
                <span className="text-slate-700">
                  {t('journal.debit')}:{' '}
                  <span className={`font-medium ${isCredit ? 'text-slate-400' : 'text-slate-900'}`}>
                    {Number(r.debit) > 0 ? fmtAmount(r.debit) : '—'}
                  </span>
                </span>
                <span className="pl-6 text-slate-700">
                  {t('journal.credit')}:{' '}
                  <span className={`font-semibold ${isCredit ? 'text-slate-900' : 'text-slate-400'}`}>
                    {isCredit ? `↳ ${fmtAmount(r.credit)}` : '—'}
                  </span>
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}