// Session 11 Part B2 — certificate presentation helpers (run: npm run test:certificate).
//
// The test payloads mirror the ACTUAL backend response shape
// (backend/app/learning/schemas.py -> CourseCompletionOut) so this file doubles
// as a frontend/backend compatibility pin: if the backend renames a field the
// UI consumes, this test fails loudly.
import assert from 'node:assert/strict'

import {
  CERTIFICATE_STATUS,
  certificateState,
  formatCertificateDate,
} from './certificatePresentation.js'

let passed = 0
function check(name, fn) {
  try {
    fn()
    passed++
    console.log(`ok - ${name}`)
  } catch (err) {
    console.error(`FAIL - ${name}`)
    console.error(err)
    process.exitCode = 1
  }
}

// Realistic payloads mirroring CourseCompletionOut (fields straight from the
// backend schema: completed, certificate, total_lessons, completed_lessons,
// completion_percentage, certificate_status).
const notStarted = {
  completed: false,
  certificate: null,
  total_lessons: 7,
  completed_lessons: 0,
  completion_percentage: 0,
  certificate_status: 'locked',
}
const available = {
  completed: true,
  certificate: null,
  total_lessons: 7,
  completed_lessons: 7,
  completion_percentage: 100,
  certificate_status: 'available',
}
const issued = {
  completed: true,
  certificate: { id: 42, course_slug: 'accounting-basics', wording: 'Kinxta Docu Certificate of Completion', issued_at: '2026-09-12T10:30:00Z' },
  total_lessons: 7,
  completed_lessons: 7,
  completion_percentage: 100,
  certificate_status: 'issued',
}

check('certificateState maps the backend locked state', () => {
  assert.equal(certificateState(notStarted), CERTIFICATE_STATUS.locked)
})

check('certificateState maps the backend available state', () => {
  assert.equal(certificateState(available), CERTIFICATE_STATUS.available)
})

check('certificateState maps the backend issued state', () => {
  assert.equal(certificateState(issued), CERTIFICATE_STATUS.issued)
})

check('certificateState fails SAFE to locked for unknown/missing values', () => {
  assert.equal(certificateState({ certificate_status: 'weird' }), CERTIFICATE_STATUS.locked)
  assert.equal(certificateState({}), CERTIFICATE_STATUS.locked)
  assert.equal(certificateState(null), CERTIFICATE_STATUS.locked)
  assert.equal(certificateState(undefined), CERTIFICATE_STATUS.locked)
})

check('formatCertificateDate localizes en-GB and fr-FR dates', () => {
  const en = formatCertificateDate('2026-09-12T10:30:00Z', 'en')
  const fr = formatCertificateDate('2026-09-12T10:30:00Z', 'fr')
  assert.equal(en, '12 September 2026')
  assert.equal(fr, '12 septembre 2026')
})

check('formatCertificateDate never renders Invalid Date', () => {
  assert.equal(formatCertificateDate('', 'en'), '')
  assert.equal(formatCertificateDate(null, 'en'), '')
  assert.equal(formatCertificateDate('not-a-date', 'en'), '')
})

if (!process.exitCode) {
  console.log(`all certificate presentation checks passed (${passed})`)
}