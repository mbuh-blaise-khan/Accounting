// Report exporting/printing checks (Session 10). Plain assert (no node:test) so
// failures are visible even in non-TTY shells — same convention as the other
// src/utils/*.test.mjs files. Run with:  npm run test:reports
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

import { toCsv } from './csvExport.js'
import {
  formatReportDate,
  formatReportDateTime,
  formatReportNumber,
  reportAccountColumns,
  reportCsvHeader,
} from './reportPresentation.js'

const t = (key) =>
  ({
    'journal.accountNo': 'N° compte',
    'report.business': 'Business',
    'report.title': 'Report',
    'report.period': 'Period',
    'report.asAt': 'As at',
    'report.generated': 'Generated on',
  })[key]

let failures_count = 0
function check(name, fn) {
  try {
    fn()
    console.log(`ok - ${name}`)
  } catch (err) {
    failures_count += 1
    console.log(`FAIL - ${name}`)
    console.log(`       ${err.message}`)
  }
}

// ---- CSV includes header rows (report info + blank separator + columns) ----
check('CSV includes report-info header rows and a blank separator before data', () => {
  const csv = toCsv(
    ['Date', 'Debit'],
    [
      ['27/08/2026', 100],
      ['28/08/2026', 200],
    ],
    [
      ['Business', 'Acme SARL'],
      ['Period', 'P'],
    ]
  )
  const lines = csv.trimEnd().split('\r\n')
  assert.strictEqual(lines[0], '\uFEFFBusiness,Acme SARL', 'first line = info header with BOM')
  assert.strictEqual(lines[1], 'Period,P')
  assert.strictEqual(lines[2], '', 'blank row separates info header from column header')
  assert.strictEqual(lines[3], 'Date,Debit')
  assert.strictEqual(lines[4], '27/08/2026,100')
  assert.strictEqual(lines[5], '28/08/2026,200')
})

check('CSV accepts TWO header rows (grouped columns, e.g. trial balance)', () => {
  const csv = toCsv(
    [
      ['Closing', 'Closing'],
      ['Debit', 'Credit'],
    ],
    [['27/08/2026', 100, 200]]
  )
  assert.ok(csv.includes('Closing,Closing\r\nDebit,Credit'), 'both header rows are present in order')
})

check('CSV escapes commas/quotes (no broken columns)', () => {
  const csv = toCsv(['Account', 'Note'], [['Caisse, trésorerie', 'said "hi"']])
  assert.ok(csv.includes('"Caisse, trésorerie","said ""hi"""'), 'cells with commas/quotes are quoted')
})

// ---- consistent date + number formatting (not raw toLocaleString dumps) ----
check('formatReportDate is a fixed DD/MM/YYYY, not locale-dependent', () => {
  assert.strictEqual(formatReportDate('2026-08-27'), '27/08/2026')
  assert.strictEqual(formatReportDate('2026-12-01'), '01/12/2026')
  assert.strictEqual(formatReportDate(''), '')
  assert.strictEqual(formatReportDate('not-a-date'), 'not-a-date') // leaves garbage alone
})

check('formatReportDateTime carries the real current timestamp', () => {
  const out = formatReportDateTime(new Date(2026, 7, 27, 9, 5, 0))
  assert.match(out, /^27\/08\/2026 09:05$/)
})

check('report numbers format consistently', () => {
  assert.strictEqual(formatReportNumber('1234567'), '1,234,567')
  assert.strictEqual(formatReportNumber(0), '0')
  assert.strictEqual(formatReportNumber('abc'), '') // invalid -> empty, not "NaN"
})

// ---- OHADA includes N° compte / IFRS omits it ----
check('OHADA report includes the account-code column; IFRS omits it', () => {
  assert.deepEqual(reportAccountColumns(true, t), ['N° compte'])
  assert.deepEqual(reportAccountColumns(false, t), [])
})

// ---- reportCsvHeader builds the same report-info block used on screen ----
check('reportCsvHeader carries workspace, title+framework, period and generated-on', () => {
  const rows = reportCsvHeader({
    organization: { name: 'Acme SARL' },
    title: 'Trial balance',
    framework: 'OHADA',
    period: 'As at 27/08/2026',
    generatedAt: new Date(2026, 7, 27, 9, 5),
    t,
  })
  assert.deepEqual(rows[0], ['Business', 'Acme SARL'])
  assert.ok(String(rows[1][1]).includes('OHADA'), 'title row carries the framework label')
  assert.deepEqual(rows[2], ['Period', 'As at 27/08/2026'])
  assert.ok(String(rows[3][1]).startsWith('27/08/2026 09:05'), 'generated-on has the current timestamp')
  assert.strictEqual(rows.length, 4, 'no trailing empty row (csvExport adds the blank separator itself)')
})

// ---- print CSS must NOT leak into the normal on-screen view ----
check("print CSS lives only inside @media print (doesn't leak on screen)", () => {
  const css = readFileSync(new URL('../index.css', import.meta.url), 'utf-8')
  const mediaIdx = css.indexOf('@media print')
  assert.notStrictEqual(mediaIdx, -1, 'index.css contains a @media print block')
  const beforeMedia = css.slice(0, mediaIdx)
  for (const sel of ['.no-print', '.report-page', '.report-content', '.report-header', '.report-table']) {
    assert.ok(
      !beforeMedia.includes(sel),
      `.${sel} rule must only be defined inside @media print (no screen leak)`
    )
  }
  assert.ok(css.slice(mediaIdx).includes('.no-print { display: none'), 'print block hides the no-print controls')
})

if (failures_count > 0) {
  console.error(`${failures_count} check(s) failed`)
  process.exitCode = 1
} else {
  console.log('all report checks passed')
}