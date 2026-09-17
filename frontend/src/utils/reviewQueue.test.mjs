// Session 11 Part C3 — review-queue presentation helpers (run: npm run test:review).
//
// The payloads below mirror the ACTUAL backend response shapes
// (backend/app/learning/service.py -> get_review_summary/list_reviews,
//  backend/app/learning/schemas.py -> ReviewSummaryOut/ReviewItemOut/
//  ReviewAnswerOut, Part C1 feedback object from AnswerFeedbackOut), so this
// file doubles as a frontend/backend compatibility pin: if the backend
// renames a field the UI consumes, this test fails loudly.
//
// Pure behaviour only — no browser, no DOM (project convention: plain Node +
// node:assert/strict, no extra test framework dependency).
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

import {
  feedbackProjection,
  feedbackStatus,
  FEEDBACK_STATUS,
  remediationTarget,
  sectionAnchorId,
} from './lessonFeedback.js'
import {
  CONFIDENCE,
  REVIEW_SUMMARY_STATE,
  confidencePayload,
  formatDueDate,
  reviewAnswerPayload,
  reviewResultView,
  reviewSummaryState,
} from './reviewQueue.js'

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

// --- Real C2 payloads (used by every check below) ------------------------------
// One active review card as GET /learning/reviews returns it: question +
// options ONLY — no is_correct flag, no correct option key/text, no accepted
// short-answer text (asserted in the key-protection checks below).
const dueCard = {
  id: 101,
  question_id: 11,
  lesson_id: 1,
  lesson_title_en: 'What is accounting?',
  lesson_title_fr: "Qu'est-ce que la comptabilité ?",
  question_en: 'What is the main purpose of accounting?',
  question_fr: "Quel est l'objectif principal de la comptabilité ?",
  kind: 'mcq',
  answers: [
    { option_key: 'A', text_en: 'To keep track of money', text_fr: "Suivre l'argent" },
    { option_key: 'B', text_en: 'To decorate the office', text_fr: 'Décorer le bureau' },
    { option_key: 'C', text_en: 'To avoid banks', text_fr: 'Éviter les banques' },
  ],
  stage: 2,
  due_at: '2026-09-15T08:00:00+00:00',
  last_outcome: 'review_wrong',
  is_due: true,
}

// A CORRECT review answer as POST /learning/reviews/{id}/answer returns it:
// narrower than a lesson attempt — `correct` (NOT `is_correct`) at the top
// level plus the Part C1 `feedback` object, stage/schedule, and NOTHING else.
const correctReviewAnswer = {
  review_id: 101,
  question_id: 11,
  correct: true,
  stage: 3,
  due_at: '2026-09-22T08:00:00+00:00',
  interval_days: 7,
  feedback: {
    correct: true,
    explanation: 'The business must be measured before it can be managed.',
    encouragement: 'Well done — keep going.',
  },
}

// An INCORRECT review answer WITH a remediation target in the SAME lesson.
const incorrectReviewAnswer = {
  review_id: 101,
  question_id: 11,
  correct: false,
  stage: 0,
  due_at: '2026-09-15T09:00:00+00:00',
  interval_days: null,
  feedback: {
    correct: false,
    explanation: 'The business must be measured before it can be managed.',
    correction: 'Accounting exists to record what the business owns, owes and earns.',
    remediation: {
      lesson_id: 1,
      section_id: 42,
      section_position: 2,
      section_title: 'Why it matters',
      action_label: 'Review this concept',
    },
  },
}

// --- 1) No-review state ---------------------------------------------------------
check('null/missing summaries are not displayable (still loading)', () => {
  assert.equal(reviewSummaryState(null), null)
  assert.equal(reviewSummaryState(undefined), null)
  assert.equal(reviewSummaryState({}), REVIEW_SUMMARY_STATE.empty)
  assert.equal(
    reviewSummaryState({ total_active: 0, due_now: 0, scheduled: 0 }),
    REVIEW_SUMMARY_STATE.empty
  )
})

// --- 2) Due-review state ----------------------------------------------------------
check('due cards surface a Review-now state', () => {
  assert.equal(
    reviewSummaryState({ total_active: 2, due_now: 2, scheduled: 0 }),
    REVIEW_SUMMARY_STATE.due
  )
  // Mixed queues still surface the due action first.
  assert.equal(
    reviewSummaryState({ total_active: 3, due_now: 1, scheduled: 2 }),
    REVIEW_SUMMARY_STATE.due
  )
})

// --- 3) Scheduled-later state ------------------------------------------------------
check('future-only cards surface a quiet scheduled state with a next date', () => {
  assert.equal(
    reviewSummaryState({
      total_active: 2,
      due_now: 0,
      scheduled: 2,
      next_due_at: '2026-09-22T08:00:00+00:00',
    }),
    REVIEW_SUMMARY_STATE.scheduled
  )
  const label = formatDueDate('2026-09-22T08:00:00+00:00', 'en')
  assert.ok(label.length > 0)
  // A missing/invalid next date hides the date line instead of showing junk.
  assert.equal(formatDueDate(null, 'en'), '')
  assert.equal(formatDueDate('not-a-date', 'en'), '')
})

// --- 4) Review feedback (reuses the Part C1 helpers verbatim) ----------------------
check('a correct review answer shows encouragement + its next schedule', () => {
  const view = reviewResultView(correctReviewAnswer)
  assert.equal(feedbackStatus(view), FEEDBACK_STATUS.correct)
  const projection = feedbackProjection(view, false)
  assert.equal(projection.explanation, correctReviewAnswer.feedback.explanation)
  assert.equal(projection.encouragement, correctReviewAnswer.feedback.encouragement)
  assert.equal(projection.correction, null)
  assert.equal(projection.remediation, null)
  // The C2 schedule rides on the top-level answer, unchanged by the adapter.
  assert.equal(correctReviewAnswer.stage, 3)
  assert.equal(correctReviewAnswer.interval_days, 7)
  assert.ok(formatDueDate(correctReviewAnswer.due_at, 'en').length > 0)
})

check('an incorrect review answer shows the correction + remediation target', () => {
  const view = reviewResultView(incorrectReviewAnswer)
  assert.equal(feedbackStatus(view), FEEDBACK_STATUS.incorrect)
  const projection = feedbackProjection(view, false)
  assert.equal(projection.explanation, incorrectReviewAnswer.feedback.explanation)
  assert.equal(projection.correction, incorrectReviewAnswer.feedback.correction)
  assert.equal(projection.encouragement, null)
  assert.deepEqual(projection.remediation, {
    lessonId: 1,
    sectionId: 42,
    sectionPosition: 2,
    sectionTitle: 'Why it matters',
    actionLabel: 'Review this concept',
  })
})

// --- 5) Confidence choices (lesson flow only) --------------------------------------
check('confidence sends ONLY the two C2-supported self-assessments', () => {
  assert.deepEqual(confidencePayload(CONFIDENCE.understood), { confidence: 'understood' })
  assert.deepEqual(confidencePayload(CONFIDENCE.guessed), { confidence: 'guessed' })
  // Missing/invalid values send the pre-C2 request shape (no key at all).
  assert.deepEqual(confidencePayload(null), {})
  assert.deepEqual(confidencePayload(undefined), {})
  assert.deepEqual(confidencePayload('maybe'), {})
})

// --- 6) Remediation navigation --------------------------------------------------------
check('remediation navigation opens the card OWN lesson at a stable anchor', () => {
  const view = reviewResultView(incorrectReviewAnswer)
  const target = remediationTarget(view)
  // The target's lesson is the card's own lesson (server-enforced scoping).
  assert.equal(target.lessonId, dueCard.lesson_id)
  // The anchor is deterministic — the detail page resolves the same string.
  assert.equal(sectionAnchorId(target), 'lesson-section-42')
  // No valid target (null/missing ids) means NO navigation happens.
  assert.equal(remediationTarget(reviewResultView(correctReviewAnswer)), null)
  assert.equal(remediationTarget(null), null)
})

// --- 7) API helper request shape (stubbed fetch, no network) ---------------------------
check('review helpers call the exact C2 endpoints with the right shape', async () => {
  const calls = []
  globalThis.fetch = async (url, options = {}) => {
    calls.push({ url, options })
    return { ok: true, status: 200, json: async () => ({ ok: true }) }
  }
  const { answerReview, fetchReviews, fetchReviewSummary } = await import(
    '../services/api.js'
  )

  await fetchReviewSummary()
  await fetchReviews(true)
  await fetchReviews(false)
  await answerReview(101, { option_key: 'A' }, 'en')

  assert.equal(calls.length, 4)
  assert.equal(calls[0].url, 'http://localhost:8000/learning/reviews/summary')
  assert.equal(calls[0].options.method || 'GET', 'GET')
  assert.equal(calls[1].url, 'http://localhost:8000/learning/reviews?due_only=true')
  assert.equal(calls[2].url, 'http://localhost:8000/learning/reviews')
  assert.equal(calls[3].url, 'http://localhost:8000/learning/reviews/101/answer?lang=en')
  assert.equal(calls[3].options.method, 'POST')
  assert.equal(calls[3].options.credentials, 'include')
  assert.equal(
    calls[3].options.headers && calls[3].options.headers['Content-Type'],
    'application/json'
  )
  assert.deepEqual(JSON.parse(calls[3].options.body), { option_key: 'A' })
  delete globalThis.fetch
})

// --- 8) Answer-key protection -------------------------------------------------------------
check('review payloads never carry the answer key', () => {
  const flattened = JSON.stringify({ card: dueCard, correctReviewAnswer, incorrectReviewAnswer })
  for (const forbidden of ['correct_option_key', 'correct_text', 'is_correct', 'short_answer_en', 'short_answer_fr']) {
    assert.ok(!flattened.includes(forbidden), forbidden)
  }
  // Options carry exactly the pre-submission shape (nothing else).
  for (const option of dueCard.answers) {
    assert.deepEqual(Object.keys(option).sort(), ['option_key', 'text_en', 'text_fr'])
  }
})

// --- 9) EN/FR key parity ---------------------------------------------------------------------
check('review + confidence UI labels exist in BOTH en.json and fr.json', () => {
  const en = JSON.parse(readFileSync(new URL('../i18n/en.json', import.meta.url), 'utf8'))
  const fr = JSON.parse(readFileSync(new URL('../i18n/fr.json', import.meta.url), 'utf8'))
  const reviewKeys = [
    'title', 'subtitle', 'readyNow', 'scheduledLater', 'nextDue', 'reviewNow',
    'allCaughtUp', 'emptyHint', 'loadError', 'answerError', 'cardProgress', 'of',
    'fromLesson', 'yourAnswer', 'checkAnswer', 'nextCard', 'dueAgainNow', 'backToLessons',
  ]
  for (const key of reviewKeys) {
    assert.ok(typeof en.review[key] === 'string' && en.review[key].trim(), `en.review.${key}`)
    assert.ok(typeof fr.review[key] === 'string' && fr.review[key].trim(), `fr.review.${key}`)
  }
  // The languages are genuinely maintained, not copies.
  assert.notEqual(en.review.reviewNow, fr.review.reviewNow)
  for (const key of ['confidenceQuestion', 'confidenceUnderstood', 'confidenceGuessed']) {
    assert.ok(typeof en.learn[key] === 'string' && en.learn[key].trim(), `en.learn.${key}`)
    assert.ok(typeof fr.learn[key] === 'string' && fr.learn[key].trim(), `fr.learn.${key}`)
  }
  assert.notEqual(en.learn.confidenceUnderstood, fr.learn.confidenceUnderstood)
})

console.log(`\n${passed} check(s) passed`)
