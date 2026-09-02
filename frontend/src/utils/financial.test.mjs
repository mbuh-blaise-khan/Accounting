// Financial-statement presentation checks (Session 10, Part B). Plain assert
// so failures stay visible in non-TTY shells — same convention as the other
// src/utils/*.test.mjs files. Run: npm run test:financial
import assert from 'node:assert/strict'

import {
  incomeCsvParts,
  plainSummaryIncome,
  plainSummaryPosition,
  positionBalanceKind,
  positionCsvParts,
} from './financialPresentation.js'

// Minimal i18n stub: only the keys the helpers ask for. The {placeholders}
// in the summary templates MUST match the real en.json/fr.json wording.
const messages = {
  en: {
    'fs.summaryIncomeProfit':
      'You received {revenue} of revenue and spent {expenses} this period — a profit of {result}.',
    'fs.summaryIncomeLoss':
      'You received {revenue} of revenue and spent {expenses} this period — a loss of {result}.',
    'fs.summaryPosition':
      'Your business owns {assets}, owes {liabilities}, and has {equity} invested in it.',
    'fs.section.revenue': 'Revenue — ordinary activities',
    'fs.section.expenses': 'Expenses — ordinary activities',
    'fs.section.extraordinary': 'Extraordinary items (HAO — outside ordinary activities)',
    'fs.section.assets': 'ASSETS',
    'fs.section.liabilities': 'LIABILITIES',
    'fs.section.equity': 'EQUITY',
    'fs.total': 'Total',
    'fs.amount': 'Amount',
    'fs.ordinaryResult': 'RESULT OF ORDINARY ACTIVITIES',
    'fs.extraordinaryResult': 'Result of extraordinary activities (HAO)',
    'fs.netResult': 'NET RESULT',
    'fs.resultOfPeriod': 'Result of the period (not yet transferred to equity)',
    'fs.totalEquityAndResult': 'Total equity including the period result',
    'journal.accountNo': 'N° compte',
    'journal.accountName': 'Account name',
  },
  fr: {
    'fs.summaryIncomeProfit':
      'Vous avez reçu {revenue} de produits et dépensé {expenses} sur la période — un bénéfice de {result}.',
    'fs.summaryPosition':
      'Votre entreprise possède {assets}, doit {liabilities}, et dispose de {equity} investis en capitaux propres.',
    'fs.section.revenue': 'Produits — activités ordinaires',
  },
}
const makeT = (lang) => (key) => messages[lang][key] || messages.en[key] || key

// A payload shaped EXACTLY like the Part A backend response. The OHADA IS
// mirrors the Part A integration scenario: 2000 revenue - 500 expenses =
// 1500 ordinary, +1000/-200 HAO -> net 2300.
const OHADA_INCOME = {
  framework: 'OHADA',
  statement_name_en: 'Compte de résultat',
  statement_name_fr: 'Compte de résultat',
  revenue_total: '2000.00',
  expense_total: '500.00',
  ordinary_result: '1500.00',
  extraordinary_total: '1200.00',
  net_result: '2300.00',
  sections: [
    {
      key: 'revenue',
      label_en: 'Revenue',
      label_fr: 'Produits',
      total: '2000.00',
      lines: [
        { account_id: 11, code: '7011', name_en: 'Sales of goods - local', name_fr: 'Ventes - marché local', amount: '2000.00' },
      ],
    },
    {
      key: 'expenses',
      label_en: 'Expenses',
      label_fr: 'Charges',
      total: '500.00',
      lines: [
        { account_id: 12, code: '6011', name_en: 'Purchases of goods - local', name_fr: 'Achats - marché local', amount: '500.00' },
      ],
    },
    {
      key: 'extraordinary',
      label_en: 'Extraordinary items (HAO)',
      label_fr: 'Éléments extraordinaires (HAO)',
      total: '1200.00',
      lines: [
        { account_id: 13, code: '84', name_en: 'Income outside ordinary activities', name_fr: 'Produits HAO', amount: '1000.00' },
        { account_id: 14, code: '83', name_en: 'Expenses outside ordinary activities', name_fr: 'Charges HAO', amount: '200.00' },
      ],
    },
  ],
}

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

// ---- plain-language summary numbers MATCH the statement's own totals ----
check('income summary interpolates the statement totals (profit path)', () => {
  const s = plainSummaryIncome(OHADA_INCOME, makeT('en'))
  assert.ok(s.includes('2,000'), 'revenue total from the payload')
  assert.ok(s.includes('500'), 'expense total from the payload')
  assert.ok(s.includes('2,300'), 'net result from the payload')
  assert.ok(s.includes('a profit of'), 'profit wording when net_result >= 0')
  assert.ok(!s.includes('{'), 'no unfilled placeholders leak through')
})

check('income summary uses loss wording with an absolute result', () => {
  const loss = { ...OHADA_INCOME, net_result: '-750.00' }
  const s = plainSummaryIncome(loss, makeT('en'))
  assert.ok(s.includes('a loss of 750'), 'loss wording, magnitude without sign')
  assert.ok(!s.includes('-750'), 'no double negative in the sentence')
})

check('FR summary template fills from the FR payload labels', () => {
  const s = plainSummaryIncome(OHADA_INCOME, makeT('fr'))
  assert.ok(s.startsWith('Vous avez reçu 2,000'), 'FR template + same payload totals')
})

check('position summary carries assets/liabilities/equity verbatim', () => {
  const fp = { assets: '13000.00', liabilities: '3000.00', equity: '10000.00' }
  const s = plainSummaryPosition(fp, makeT('en'))
  assert.ok(s.includes('13,000') && s.includes('3,000') && s.includes('10,000'))
  assert.ok(!s.includes('{'))
})

// ---- position balance kinds (honest about the not-yet-booked result) ----
check('balance kind: exact when A = L + E with no P&L activity', () => {
  assert.strictEqual(positionBalanceKind({ assets: '100', liabilities: '30', equity: '70' }), 'exact')
})
check('balance kind: withResult when A = L + E + net_result', () => {
  // equity excludes the result (7700), so A = L + E fails but A = L + E +
  // result (13000 = 3000 + 7700 + 2300) holds -> 'withResult'.
  const kind = positionBalanceKind(
    { assets: '13000', liabilities: '3000', equity: '7700' },
    '2300.00'
  )
  assert.strictEqual(kind, 'withResult')
})
check('balance kind: none when neither identity holds (report an issue)', () => {
  assert.strictEqual(positionBalanceKind({ assets: '999', liabilities: '1', equity: '1' }, '5'), 'none')
})

// ---- CSV parts: OHADA carries N° compte, IFRS omits it (shared rule) ----
check('income CSV: OHADA rows include codes, section headers, results in order', () => {
  const { headerRows, rows } = incomeCsvParts(OHADA_INCOME, { t: makeT('en'), isOhada: true, lang: 'en' })
  assert.deepEqual(headerRows[0], ['N° compte', 'Account name', 'Amount'])
  assert.strictEqual(rows[0][0], 'Revenue — ordinary activities', 'section header row first')
  assert.strictEqual(rows[0][1], '', 'section header rows carry no amount')
  const sales = rows[1]
  assert.strictEqual(sales[0], '7011', 'OHADA code column present')
  assert.strictEqual(sales[2], 2000, 'amount as a raw number')
  assert.ok(
    rows.some((r) => r[0] === 'RESULT OF ORDINARY ACTIVITIES' && r[1] === 1500),
    'ordinary result row = revenue - expenses'
  )
  assert.ok(
    rows.some((r) => r[0] === 'Result of extraordinary activities (HAO)' && r[1] === 800),
    'HAO result row is SIGNED (1000 - 200)'
  )
  assert.ok(
    rows.some((r) => r[0] === 'NET RESULT' && r[1] === 2300),
    'final combined net result row'
  )
  assert.strictEqual(rows[rows.length - 1][0], 'NET RESULT', 'net result is the LAST row')
})

check('income CSV: IFRS omits the code column entirely', () => {
  const ifrsIncome = {
    ...OHADA_INCOME,
    statement_name_en: 'Statement of Profit or Loss',
    sections: OHADA_INCOME.sections.filter((s) => s.key !== 'extraordinary'),
    net_result: '1500.00',
  }
  const { headerRows, rows } = incomeCsvParts(ifrsIncome, { t: makeT('en'), isOhada: false, lang: 'en' })
  assert.deepEqual(headerRows[0], ['Account name', 'Amount'], 'no N° compte column for IFRS')
  const sales = rows[1]
  assert.strictEqual(sales[0], 'Sales of goods - local', 'name sits in the FIRST column')
  assert.ok(
    !rows.some((r) => r[0] === 'Result of extraordinary activities (HAO)'),
    'no HAO row when there is no extraordinary section (IFRS)'
  )
})

check('position CSV: result rows only when there IS P&L activity', () => {
  const fp = {
    assets: '13000.00',
    liabilities: '3000.00',
    equity: '10000.00',
    sections: [
      {
        key: 'assets',
        label_en: 'Assets',
        label_fr: 'Actif',
        total: '13000.00',
        lines: [{ account_id: 5, code: '5711', name_en: 'Cash', name_fr: 'Caisse', amount: '13000.00' }],
      },
      { key: 'liabilities', label_en: 'Liabilities', label_fr: 'Dettes', total: '3000.00', lines: [] },
      { key: 'equity', label_en: 'Equity', label_fr: 'Capitaux propres', total: '10000.00', lines: [] },
    ],
  }
  const withResult = positionCsvParts(fp, { t: makeT('en'), isOhada: true, lang: 'en', netResult: '2300.00' })
  assert.ok(withResult.rows.some((r) => r[0] === 'Result of the period (not yet transferred to equity)'))
  assert.ok(
    withResult.rows.some((r) => r[0] === 'Total equity including the period result' && r[1] === 12300),
    'equity + result arithmetic'
  )
  const noResult = positionCsvParts(fp, { t: makeT('en'), isOhada: false, lang: 'en', netResult: 0 })
  assert.ok(!noResult.rows.some((r) => String(r[0]).includes('period')), 'no result rows when net = 0')
})

check('summary numbers equal the statement totals they are built from', () => {
  // Requirement 9: the plain-language sentence and the statement CANNOT drift
  // apart — both come from the same payload object.
  const s = plainSummaryIncome(OHADA_INCOME, makeT('en'))
  assert.ok(s.includes('2,000'), 'revenue_total')
  assert.ok(s.includes('500'), 'expense_total')
  const csv = incomeCsvParts(OHADA_INCOME, { t: makeT('en'), isOhada: true, lang: 'en' })
  const netRow = csv.rows[csv.rows.length - 1]
  assert.strictEqual(netRow[1], 2300, 'CSV net result == payload net_result')
  assert.ok(s.includes('2,300'), 'summary net result == payload net_result')
})

if (failures_count > 0) {
  console.error(`${failures_count} check(s) failed`)
  process.exitCode = 1
} else {
  console.log('all financial statement checks passed')
}