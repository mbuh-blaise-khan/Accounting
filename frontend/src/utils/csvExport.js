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
 * Build a CSV string from report header rows and data rows.
 *
 * Report layout (all four report types):
 *   1. `metadataRows`  — the report-info block (workspace, title+framework,
 *                        period, "Generated on [timestamp]") produced by
 *                        reportPresentation.reportCsvHeader().
 *   2. an EMPTY row     — separates the report info from the column headers.
 *   3. `headerRows`     — the column header, as ONE or MORE header rows. The
 *                        trial balance passes two rows (a group row such as
 *                        "Opening balance" above its "Debit/Credit" sub-row);
 *                        the journal/ledger/cash book pass a single row.
 *   4. the data `rows`.
 * Every report therefore "includes header rows" for the same info shown on
 * screen, with a blank row. Numbers are kept as raw values (no thousands
 * separators) so spreadsheet apps can sum them; dates are pre-formatted by the
 * caller (formatReportDate) so they are identical across screen/print/CSV.
 *
 * @param {string[]|Array<string[]>} headerRows one header row, or several rows
 * @param {Array<Array<*>>} rows one array of cells per row, same order
 * @param {Array<Array<*>>} [metadataRows] report-info rows (see above)
 * @returns {string} CSV text with a UTF-8 BOM and \r\n line endings
 */
export function toCsv(headerRows, rows, metadataRows = []) {
  const headerBlocks = Array.isArray(headerRows[0]) ? headerRows : [headerRows]
  const lines = [...metadataRows, [], ...headerBlocks, ...rows].map((cells) =>
    cells.map(csvEscape).join(',')
  )
  return `\uFEFF${lines.join('\r\n')}\r\n`
}

/**
 * Trigger a browser download of `rows` as <filename>.csv.
 * @param {string} filename without extension
 * @param {string[]|Array<string[]>} headerRows column titles (one or more rows)
 * @param {Array<Array<*>>} rows cell values in display order
 * @param {Array<Array<*>>} [metadataRows=[]] report-info rows joined above the header
 */
export function downloadCsv(filename, headerRows, rows, metadataRows = []) {
  const blob = new Blob([toCsv(headerRows, rows, metadataRows)], {
    type: 'text/csv;charset=utf-8',
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${filename}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
