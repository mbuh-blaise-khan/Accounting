// Cash Book page (Session 7): the Journal view filtered to cash/bank-account
// movements only. Reuses the same read-only table, filters and drill-down.
import JournalPage from './JournalPage.jsx'

export default function CashBookPage({ org, onBack }) {
  return <JournalPage org={org} onBack={onBack} cashbook />
}