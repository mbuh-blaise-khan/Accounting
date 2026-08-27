// Shared drill-down block (Part 4): status badge, "reversal of" cross-link
// and the Reverse action for POSTED transactions. Posted entries are immutable
// (.clinerules): correction = a NEW posted mirror entry with debit/credit
// sides swapped, linked back via reverse_of_id. The original is never edited
// or deleted — only flagged `reversed`.
import { useState } from 'react'
import { reverseTransaction } from '../services/api.js'
import { useLanguage } from '../i18n/index.jsx'

const BADGE_STYLES = {
  posted: 'bg-green-100 text-green-800',
  reversed: 'bg-amber-100 text-amber-800',
  draft: 'bg-slate-100 text-slate-700',
}

export function refLabel(id) {
  return `TX-${String(id).padStart(4, '0')}`
}

export default function TxnStatusBlock({ txn, org, onReversed }) {
  const { t } = useLanguage()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  async function handleReverse() {
    // Plain-language confirm BEFORE anything is posted.
    if (!window.confirm(t('txn.reverseConfirm'))) return
    setBusy(true)
    setError(null)
    setSuccess(null)
    try {
      const mirror = await reverseTransaction(org.id, txn.id)
      setSuccess(t('txn.reverseSuccess'))
      if (onReversed) onReversed(mirror)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm">
      <div className="flex flex-wrap items-center gap-2">
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
            BADGE_STYLES[txn.status] || 'bg-slate-100 text-slate-700'
          }`}
        >
          {t(`journal.status_${txn.status}`)}
        </span>
        {txn.reverse_of_id != null && (
          <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-xs font-medium text-slate-700">
            {t('txn.reversalOf')} {refLabel(txn.reverse_of_id)}
          </span>
        )}
        <span className="flex-1" />
        {txn.status === 'posted' && (
          <button
            type="button"
            onClick={handleReverse}
            disabled={busy}
            className="rounded-lg border border-amber-400 bg-white px-3 py-1.5 text-sm font-medium text-amber-700 hover:bg-amber-50 disabled:opacity-50"
          >
            {busy ? t('common.loading') : t('txn.reverseAction')}
          </button>
        )}
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      {success && (
        <p className="mt-2 text-sm text-green-700">{success}</p>
      )}
    </div>
  )
}
