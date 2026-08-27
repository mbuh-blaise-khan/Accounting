// Minimal client-side CSV export (Part 3).
//
// WHY client-side: all three export targets (Journal, Cash Book, General
// Ledger) already hold exactly what is on screen — the currently filtered
// rows — in state. Generating the file from that data guarantees "export
// what you see", needs no new backend endpoint/dependency, and works
// offline. Values are numbers/strings already formatted for display.
//
// The BOM makes Excel open the UTF-8 file with accented French names intact.

function csvEscape(value) {
  if (value === null || value === undefined) return ''
  const s = String(value)
  // Quote whenever the field contains a quote, comma, newline or semicolon
  // (the Excel list separator on many FR locales). Double embedded quotes.
  if (/[",;\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`
  }
  return s
}

/**
 * Build a CSV string from a headers array and row arrays.
 * @param {string[]} headers column titles in display order
 * @param {Array<Array<*>>} rows one array of cells per row, same order
 * @returns {string} CSV text including a UTF-8 BOM and \r\n line endings
 */
export function toCsv(headers, rows, metadataRows = []) {
  const lines = [...metadataRows, [], headers, ...rows].map((cells) => cells.map(csvEscape).join(','))
  return `\uFEFF${lines.join('\r\n')}\r\n`
}

/**
 * Trigger a browser download of `rows` as <filename>.csv.
 * @param {string} filename without extension
 * @param {string[]} headers column titles in display order
 * @param {Array<Array<*>>} rows cell values in display order
 */
export function downloadCsv(filename, headers, rows, metadataRows = []) {
  const blob = new Blob([toCsv(headers, rows, metadataRows)], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${filename}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
