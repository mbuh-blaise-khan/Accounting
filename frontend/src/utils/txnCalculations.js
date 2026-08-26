// Pure calculation helpers for the journal-entry grid (Session 6c).
// Extracted from NewTransactionPage so the totals / balance / canPost /
// payload-mapping logic can be unit-tested without React.
//
// Line shape used by the grid:
//   { account_id: string|number|null, debit: string, credit: string, ... }

export function toNumber(value) {
  // Accept '', '50000', 50000, null — always returns a non-negative number.
  if (value == null) return 0
  const n = Number(value)
  return Number.isNaN(n) ? 0 : n
}

// Sum all debit / credit amounts across the grid lines.
export function sumLines(lines) {
  let totalDebit = 0
  let totalCredit = 0
  for (const l of lines) {
    totalDebit += toNumber(l.debit)
    totalCredit += toNumber(l.credit)
  }
  return { totalDebit, totalCredit }
}

// A line is "filled" when exactly one of debit/credit is > 0.
export function isLineFilled(line) {
  const d = toNumber(line.debit)
  const c = toNumber(line.credit)
  return (d > 0 || c > 0) && !(d > 0 && c > 0)
}

// Balanced = every line has exactly one side, totals match, at least one of each.
export function isBalanced(lines) {
  const { totalDebit, totalCredit } = sumLines(lines)
  if (totalDebit === 0 && totalCredit === 0) return false
  const allFilled = lines.every((l) => isLineFilled(l))
  const hasDebit = lines.some((l) => toNumber(l.debit) > 0)
  const hasCredit = lines.some((l) => toNumber(l.credit) > 0)
  return allFilled && hasDebit && hasCredit && totalDebit === totalCredit
}

// Can we enable the Post button? Requires a description, >= 2 lines, every line
// filled (exactly one side), at least one debit + one credit, and balance.
export function canPost(description, lines) {
  if (!description || !description.trim()) return false
  if (lines.length < 2) return false
  if (!lines.every((l) => l.account_id != null && String(l.account_id) !== '')) return false
  if (!lines.every(isLineFilled)) return false
  return isBalanced(lines)
}

// Per-field validation run when the user actually clicks "Post transaction"
// (Part F). Returns exactly WHICH required fields are empty so the page can
// show inline messages next to each one — an account with no amount, an amount
// with no account, or a missing description must block the post even if the
// remaining lines happen to balance.
export function validatePost(description, lines) {
  const lineErrors = {}
  for (const l of lines) {
    const hasAccount = l.account_id != null && String(l.account_id) !== ''
    const d = toNumber(l.debit)
    const c = toNumber(l.credit)
    if (!hasAccount) lineErrors[l.id] = 'account'
    else if (d > 0 && c > 0) lineErrors[l.id] = 'bothSides'
    else if (d === 0 && c === 0) lineErrors[l.id] = 'amount'
  }
  const descriptionError = !description || !description.trim() ? 'description' : ''
  const { totalDebit, totalCredit } = sumLines(lines)
  const balanceError = totalDebit !== totalCredit ? 'unbalanced' : ''
  const ok =
    !descriptionError &&
    !balanceError &&
    Object.keys(lineErrors).length === 0
  return { ok, descriptionError, lineErrors, balanceError }
}

// Map grid lines → the { account_id, debit, credit, narration } payload the
// backend expects. `narration` is the per-line "libellé" shown in the Journal.
export function toPayload(description, lines, organizationId) {
  return {
    organization_id: organizationId,
    description: description.trim(),
    lines: lines.map((l) => ({
      account_id: Number(l.account_id),
      debit: toNumber(l.debit),
      credit: toNumber(l.credit),
      narration: (l.libelle || '').trim() || null,
    })),
  }
}