// Bidirectional code <-> name lookup over an organization's OWN chart.
// The caller passes only that org's accounts (the API list is org-scoped), so
// lookups can never match accounts from another workspace.
//
// Matching: the account NUMBER (OHADA codes) is matched by PREFIX so digit entry
// progressively narrows the chart the way SYSCOHADA's hierarchy works — "5"
// suggests the whole of Class 5, "51" narrows to accounts under 51, "512"
// narrows further, down to the deepest seeded sub-account. NAMES are matched
// case-insensitively by substring, in either language. When `byNameOnly` is set
// (IFRS, Part B — no codes) name matches only. Returns [] for an empty query.
// Null-safe: a record with no code cannot crash a name search.

export function searchAccounts(accounts, query, options = {}) {
  const { byNameOnly = false } = options
  const q = (query || '').trim().toLowerCase()
  if (!q) return []
  const nameHit = (a) =>
    (a.name_en || '').toLowerCase().includes(q) ||
    (a.name_fr || '').toLowerCase().includes(q)
  // Prefix match (NOT substring-anywhere): digits progressively narrow the chart.
  const codeHit = (a) => (a.code || '').toLowerCase().startsWith(q)
  const sortKey = (a) => (byNameOnly ? a.name_en || '' : a.code || '')
  return accounts
    .filter((a) => (byNameOnly ? nameHit(a) : nameHit(a) || codeHit(a)))
    .sort((a, b) => String(sortKey(a)).localeCompare(String(sortKey(b))))
}

export default searchAccounts