// Bidirectional code <-> name lookup over an organization's OWN chart.
// The caller passes only that org's accounts (the API list is org-scoped), so
// lookups can never match accounts from another workspace.
//
// Matching: case-insensitive substring on code OR name (both languages).
// Returns [] for an empty query.

export function searchAccounts(accounts, query) {
  const q = (query || '').trim().toLowerCase()
  if (!q) return []
  return accounts
    .filter(
      (a) =>
        a.code.toLowerCase().includes(q) ||
        a.name_en.toLowerCase().includes(q) ||
        a.name_fr.toLowerCase().includes(q)
    )
    .sort((a, b) => a.code.localeCompare(b.code))
}

export default searchAccounts