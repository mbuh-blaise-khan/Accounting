// Client-side Excel (.xlsx) export using exceljs — Session 11.
//
// WHY exceljs and not SheetJS/xlsx: the Community edition of SheetJS cannot
// style cells (no bold headers, no number formats); exceljs can do both, and
// the requirement is a REAL formatted workbook, not a renamed CSV.
//
// Same data source and same guarantee as downloadCsv(): the report page
// already holds exactly what is on screen, so "export what you see" holds.
// The interface MIRRORS csvExport.js exactly (metadataRows, headerRows,
// rows) so pages pass the same arrays to both exporters and the two files
// can never disagree on content.
//
// Formatting applied (requirement 1):
//   - metadata block rows in a muted italic, then a blank row
//   - column header row(s): BOLD, bottom border
//   - numeric cells: '#,##0.00' number format, right-aligned
//   - column widths sized from the longest value (capped for readability)
import ExcelJS from 'exceljs'

const NUMERIC_RE = /^-?[\d,\s]*\.?\d+$/

function isNumericCell(value) {
  return typeof value === 'number' || (typeof value === 'string' && value.trim() !== '' && NUMERIC_RE.test(value))
}

/**
 * Build an .xlsx workbook buffer from the same inputs as csvExport.toCsv().
 * @param {string[]|Array<string[]>} headerRows column titles (one or more rows)
 * @param {Array<Array<*>>} rows cell values in display order
 * @param {Array<Array<*>>} [metadataRows=[]] report-info rows above the header
 * @returns {Promise<Buffer>} the workbook buffer
 */
export async function buildExcelBuffer(headerRows, rows, metadataRows = []) {
  const wb = new ExcelJS.Workbook()
  wb.creator = 'Accounting Platform'
  const ws = wb.addWorksheet('Report', { views: [{ state: 'frozen', ySplit: metadataRows.length + 1 }] })

  const headerBlocks = Array.isArray(headerRows[0]) ? headerRows : [headerRows]
  const allRows = [...metadataRows, [], ...headerBlocks, ...rows]

  for (const cells of allRows) {
    const row = ws.addRow(cells)
    for (let c = 1; c <= cells.length; c++) {
      const cell = row.getCell(c)
      const v = cells[c - 1]
      if (isNumericCell(v)) {
        cell.numFmt = '#,##0.00'
        cell.alignment = { horizontal: 'right' }
      }
    }
  }

  // Metadata block: italic + muted; blank separator row untouched.
  metadataRows.forEach((_, i) => {
    const row = ws.getRow(i + 1)
    row.font = { italic: true, color: { argb: 'FF64748B' } }
  })

  // Column header row(s): bold with a bottom border.
  const firstHeader = metadataRows.length + 2 // 1-based, after the blank row
  headerBlocks.forEach((_, i) => {
    const row = ws.getRow(firstHeader + i)
    row.font = { bold: true }
    row.border = { bottom: { style: 'thin' } }
  })

  // Column widths from the longest cell (10..42 char cap).
  const colCount = Math.max(...allRows.map((r) => r.length))
  for (let c = 1; c <= colCount; c++) {
    let widest = 10
    for (const cells of allRows) {
      const s = String(cells[c - 1] ?? '')
      widest = Math.max(widest, Math.min(s.length + 2, 42))
    }
    ws.getColumn(c).width = widest
  }

  return wb.xlsx.writeBuffer()
}

/**
 * Trigger a browser download of `rows` as <filename>.xlsx.
 * Same argument order as downloadCsv() — call them side by side.
 */
export async function downloadExcel(filename, headerRows, rows, metadataRows = []) {
  const buffer = await buildExcelBuffer(headerRows, rows, metadataRows)
  const blob = new Blob([buffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${filename}.xlsx`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
