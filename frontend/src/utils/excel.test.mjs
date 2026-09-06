// Excel (.xlsx) export checks (Session 12). Builds a workbook with the SAME
// inputs the report pages pass (metadata/header/rows), then re-opens the buffer
// with exceljs and asserts the DATA round-trips correctly AND the formatting
// (bold headers, numeric number-format) is applied. Run: npm run test:excel
import assert from 'node:assert/strict'

import { buildExcelBuffer } from './excelExport.js'

const checks = []
function check(name, fn) {
  checks.push({ name, fn })
}

const metadataRows = [
  ['Business', 'Trial Balance (OHADA)'],
  ['Framework', 'OHADA'],
  ['Period', '01/01/2024 - 31/01/2024'],
]
const headerRows = [['N° compte', 'Account', 'Debit', 'Credit']]
const rows = [
  ['5711', 'Cash and cash equivalents', 13000, 0],
  ['16', 'Borrowings (financial liabilities)', 0, 3000],
  ['10', 'Share capital', 0, 10000],
]

async function open(buf) {
  const ExcelJS = (await import('exceljs')).default
  const wb = new ExcelJS.Workbook()
  await wb.xlsx.load(buf)
  return wb
}

check('buildExcelBuffer returns a valid openable .xlsx buffer', async () => {
  const buf = await buildExcelBuffer(headerRows, rows, metadataRows)
  const bytes = new Uint8Array(buf)
  assert.strictEqual(bytes[0], 0x50) // 'P'
  assert.strictEqual(bytes[1], 0x4b) // 'K'
  assert.strictEqual(bytes[2], 0x03) // \x03
  assert.strictEqual(bytes[3], 0x04) // \x04
})

check('Excel data round-trips with correct values', async () => {
  const buf = await buildExcelBuffer(headerRows, rows, metadataRows)
  const wb = await open(buf)
  // metadataRows (3) + 1 blank + 1 header => first DATA row is 1-based row 6
  const firstData = metadataRows.length + 1 + 1 + 1
  const row = wb.worksheets[0].getRow(firstData)
  assert.strictEqual(row.getCell(1).value, '5711')
  assert.strictEqual(row.getCell(2).value, 'Cash and cash equivalents')
  assert.strictEqual(Number(row.getCell(3).value), 13000)
  assert.strictEqual(Number(row.getCell(4).value), 0)
})

check('numeric cells carry a number format; headers are bold', async () => {
  const buf = await buildExcelBuffer(headerRows, rows, metadataRows)
  const wb = await open(buf)
  const ws = wb.worksheets[0]
  const headerRow = metadataRows.length + 2
  const hr = ws.getRow(headerRow)
  assert.strictEqual(hr.getCell(1).font.bold, true)
  assert.strictEqual(hr.getCell(2).font.bold, true)
  const num = ws.getRow(headerRow + 1).getCell(3)
  assert.ok(num.numFmt.includes('0.00'), `no number format: ${num.numFmt}`)
})

check('metadata block is present and italic-muted', async () => {
  const buf = await buildExcelBuffer(headerRows, rows, metadataRows)
  const wb = await open(buf)
  const ws = wb.worksheets[0]
  const cell = ws.getRow(1).getCell(1)
  assert.strictEqual(cell.value, 'Business')
  assert.strictEqual(cell.font.italic, true)
})

let failed = 0
for (const { name, fn } of checks) {
  try {
    await fn()
    console.log(`ok - ${name}`)
  } catch (e) {
    failed++
    console.error(`FAIL - ${name}\n  ${e.message}`)
  }
}

if (failed > 0) {
  console.error(`${failed} excel check(s) failed`)
  process.exitCode = 1
} else {
  console.log('all excel export checks passed')
}