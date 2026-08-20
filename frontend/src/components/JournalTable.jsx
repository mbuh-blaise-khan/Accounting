// Shared read-only table for the Journal and Cash Book (Session 7).
//
// Columns follow the researched journal layouts:
//   OHADA: date (posted_at, FIRST — Part C) | N° compte | intitulé | libellé |
//          débit | crédit (+ reference/description/source/status metadata)
//   IFRS:  same structure WITHOUT the account-number column (Part B).
// Every row links back to its originating transaction detail (drill-down).
// The table is horizontally scrollable on phone-width screens.
export default function JournalTable({ rows, org, nameOf, t, onViewTxn }) {
  const isOhada = org.framework === 'OHADA'

  function fmtAmount(n) {
    return (Number(n) || 0).toLocaleString()
  }

  function fmtDate(iso) {
    if (!iso) return '—'
    const d = new Date(iso)
    return d.toLocaleString()
  }

  const totalDebit = rows.reduce((s, r) => s + (Number(r.debit) || 0), 0)
  const totalCredit = rows.reduce((s, r) => s + (Number(r.credit) || 0), 0)

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
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.id}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
              >
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
                <td className="px-3 py-2 text-slate-800">{nameOf(r)}</td>
                <td className="max-w-[180px] truncate px-3 py-2 text-slate-600">
                  {r.narration || '—'}
                </td>
                <td className="whitespace-nowrap px-3 py-2 text-right text-slate-800">
                  {Number(r.debit) > 0 ? fmtAmount(r.debit) : ''}
                </td>
                <td className="whitespace-nowrap px-3 py-2 text-right text-slate-800">
                  {Number(r.credit) > 0 ? fmtAmount(r.credit) : ''}
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
            ))}
          </tbody>
          <tfoot>
            <tr className="border-t border-slate-200 bg-slate-50 font-semibold text-slate-800">
              <td className="px-3 py-2" colSpan={isOhada ? 6 : 5}>
                {t('journal.totals')}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-right">
                {fmtAmount(totalDebit)}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-right">
                {fmtAmount(totalCredit)}
              </td>
              <td colSpan={3}></td>
            </tr>
          </tfoot>
        </table>
      </div>

      {/* Mobile: stacked cards (no horizontal scrolling) */}
      <div className="mt-3 space-y-3 sm:hidden">
        {rows.map((r) => (
          <div key={r.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="font-semibold text-slate-900">{nameOf(r)}</p>
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
                <span className="font-medium">
                  {Number(r.debit) > 0 ? fmtAmount(r.debit) : '—'}
                </span>
              </span>
              <span className="text-slate-700">
                {t('journal.credit')}:{' '}
                <span className="font-medium">
                  {Number(r.credit) > 0 ? fmtAmount(r.credit) : '—'}
                </span>
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}