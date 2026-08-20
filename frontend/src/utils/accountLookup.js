// Bidirectional code <-> name lookup over an organization's OWN chart.
// The caller passes only that org's accounts (the API list is org-scoped), so
// lookups can never match accounts from another workspace.
//
// Matching: case-insensitive substring on code OR name (both languages) — unless
// `byNameOnly` is set (IFRS, which has no codes), in which case name matches
// only. Returns [] for an empty query. Null-safe: a record with no code cannot
// crash a name search (IFRS accounts are seeded without codes, Part B).

export function searchAccounts(accounts, query, options = {}) {
  const { byNameOnly = false } = options
  const q = (query || '').trim().toLowerCase()
  if (!q) return []
  const nameHit = (a) =>
    (a.name_en || '').toLowerCase().includes(q) ||
    (a.name_fr || '').toLowerCase().includes(q)
  const codeHit = (a) => (a.code || '').toLowerCase().includes(q)
  const sortKey = (a) => (byNameOnly ? a.name_en || '' : a.code || '')
  return accounts
    .filter((a) => (byNameOnly ? nameHit(a) : nameHit(a) || codeHit(a)))
    .sort((a, b) => String(sortKey(a)).localeCompare(String(sortKey(b))))
}

export default searchAccounts