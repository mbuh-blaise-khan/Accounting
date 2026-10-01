// Session 18 hotfix — lesson sequencing + progress presentation regression net
// (run: npm run test:progression).
//
// Pure behaviour only — no browser, no DOM (project convention: plain Node +
// node:assert/strict, no extra test framework dependency). Payload fixtures
// mirror the ACTUAL backend shapes (backend/app/learning/schemas.py ->
// LessonDetailOut / QuestionOut / LessonProgressOut) so this file doubles as a
// frontend/backend compatibility pin for the fixed Lesson 1 sequence.
//
// Covers the frontend acceptance list for the hotfix:
//   1. the fixed 18-question sequence renders with NO duplicate adjacent
//      ids/positions (even if a legacy payload still carries duplicates);
//   2. a wrong Question 3 followed by Continue lands on the DISTINCT Q4/18;
//   3. Question 4 is never a duplicate of Question 3;
//   4. the UI can never present a question position above 18;
//   5. the lesson page and the Learn dashboard RE-FETCH authoritative
//      progress on (re)mount — pinned as a source contract;
//   6. 17/18 -> 94% before the review correction, 18/18 -> 100% after it
//      (server-provided payloads, no client-side score maths);
//   7. the caught-up review state still works (review summary helper).
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

import {
  displayedQuestionNumber,
  lessonProgressView,
  nextQuestionIndex,
  safeQuestionIndex,
  uniqueQuestionSequence,
} from './lessonProgress.js'
import { REVIEW_SUMMARY_STATE, reviewSummaryState } from './reviewQueue.js'

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

const HERE = dirname(fileURLToPath(import.meta.url))
const PAGES = join(HERE, '..', 'pages')
const APP = join(HERE, '..', 'App.jsx')

function readSource(path) {
  return readFileSync(path, 'utf8')
}

// --- Fixtures: the ACTUAL Lesson 1 shape -------------------------------------
// Healthy payload: 10 original positions (ids 1, 2, 77-84) + the fixed tail
// (ids 85-92 at positions 11-18) — exactly what the healed server serves.
const ORIGINAL_IDS = [1, 2, 77, 78, 79, 80, 81, 82, 83, 84]
const TAIL_IDS = [85, 86, 87, 88, 89, 90, 91, 92]
const healthy18 = [
  ...ORIGINAL_IDS.map((id, i) => ({
    id,
    position: i + 1,
    question_en: `Question ${i + 1}`,
    question_fr: `Question ${i + 1} FR`,
    kind: i + 1 === 7 ? 'short_answer' : 'mcq',
    answers: [{ option_key: 'A', text_en: 'A', text_fr: 'A' }],
  })),
  ...TAIL_IDS.map((id, i) => ({
    id,
    position: 11 + i,
    question_en: `Question ${11 + i}`,
    question_fr: `Question ${11 + i} FR`,
    kind: i === 4 ? 'short_answer' : 'mcq',
    answers: [{ option_key: 'A', text_en: 'A', text_fr: 'A' }],
  })),
]

// Legacy corrupted payload (the reported defect): positions 3-10 exist TWICE
// with byte-identical content under two different ids — exactly what the dev
// database served before the heal ("Question 3 == Question 4", total 18).
const legacyCorrupted = [
  { id: 1, position: 1, question_en: 'Question 1' },
  { id: 2, position: 2, question_en: 'Question 2' },
  ...[3, 4, 5, 6, 7, 8, 9, 10].flatMap((pos, i) => [
    { id: 77 + i, position: pos, question_en: `Question ${pos}` },
    { id: 85 + i, position: pos, question_en: `Question ${pos}` },
  ]),
]

// Server progress payloads (LessonProgressOut) for the reported flow.
const progressBeforeReview = {
  status: 'completed',
  best_score: 94,
  questions_total: 18,
  questions_answered: 18,
  questions_correct: 17,
  practice_posted: false,
}
const progressAfterReview = {
  ...progressBeforeReview,
  best_score: 100,
  questions_correct: 18,
}

// --- 1) Fixed unique sequence -------------------------------------------------
check('the fixed Lesson 1 sequence is 18 unique ids/positions in order', () => {
  const seq = uniqueQuestionSequence(healthy18)
  assert.equal(seq.length, 18)
  assert.deepEqual(
    seq.map((q) => q.position),
    [...Array(18).keys()].map((n) => n + 1),
  )
  assert.equal(new Set(seq.map((q) => q.id)).size, 18)
  assert.equal(new Set(seq.map((q) => q.position)).size, 18)
})

check('no two adjacent questions share an id, position or text', () => {
  const seq = uniqueQuestionSequence(healthy18)
  for (let i = 1; i < seq.length; i++) {
    assert.notEqual(seq[i].id, seq[i - 1].id)
    assert.notEqual(seq[i].position, seq[i - 1].position)
    assert.notEqual(seq[i].question_en, seq[i - 1].question_en)
  }
})

check('a legacy duplicate-position payload can never render twice', () => {
  const seq = uniqueQuestionSequence(legacyCorrupted)
  const positions = seq.map((q) => q.position)
  assert.deepEqual(
    positions,
    [...Array(10).keys()].map((n) => n + 1),
  )
  assert.equal(new Set(positions).size, positions.length)
  for (let i = 1; i < seq.length; i++) {
    assert.notEqual(seq[i].question_en, seq[i - 1].question_en)
  }
})

check('degenerate payloads are ignored, never crash the sequence', () => {
  assert.deepEqual(uniqueQuestionSequence(null), [])
  assert.deepEqual(uniqueQuestionSequence('nope'), [])
  assert.deepEqual(
    uniqueQuestionSequence([{ position: 1 }, { id: 3 }, null, { id: 4, position: 2 }]),
    [{ id: 4, position: 2 }],
  )
})

// --- 2 & 3) Wrong Q3 then Continue -> distinct Q4/18 --------------------------
check('Continue after a wrong Q3 lands on the DISTINCT Question 4/18', () => {
  const seq = uniqueQuestionSequence(healthy18)
  const q3 = seq[2]
  assert.equal(q3.position, 3)
  assert.equal(displayedQuestionNumber(2, seq.length), 3) // "Question 3/18"
  const nextIdx = nextQuestionIndex(2, seq.length) // Continue
  assert.equal(nextIdx, 3)
  assert.equal(displayedQuestionNumber(nextIdx, seq.length), 4) // "Question 4/18"
  const q4 = seq[nextIdx]
  assert.notEqual(q4.id, q3.id)
  assert.notEqual(q4.position, q3.position)
  assert.notEqual(q4.question_en, q3.question_en)
})

check('Question 4 is not a duplicate of Question 3', () => {
  const seq = uniqueQuestionSequence(healthy18)
  const q3 = seq.find((q) => q.position === 3)
  const q4 = seq.find((q) => q.position === 4)
  assert.ok(q3 && q4)
  assert.notEqual(q3.id, q4.id)
  assert.notEqual(q3.question_en, q4.question_en)
  assert.equal(seq.filter((q) => q.id === q3.id).length, 1)
  assert.equal(seq.filter((q) => q.position === 3).length, 1)
})

// --- 4) Never above 18 --------------------------------------------------------
check('the displayed question number can never exceed the denominator', () => {
  for (let i = 0; i < 18; i++) {
    assert.equal(displayedQuestionNumber(i, 18), i + 1)
  }
  assert.equal(displayedQuestionNumber(18, 18), 18) // completion marker
  assert.equal(displayedQuestionNumber(99, 18), 18) // stale state clamp
  assert.equal(safeQuestionIndex(25, 18), 17)
  assert.equal(nextQuestionIndex(17, 18), 18)
  assert.equal(nextQuestionIndex(18, 18), 18) // never 19
  assert.equal(nextQuestionIndex(18, 10), 10) // never past the real total
  assert.equal(displayedQuestionNumber(0, 0), 0) // empty lesson
})

// --- 5) Re-fetch contract after review completion ----------------------------
check('LessonDetailPage re-fetches the lesson on mount / lesson change', () => {
  const src = readSource(join(PAGES, 'LessonDetailPage.jsx'))
  assert.match(src, /fetchLesson\(lessonId\)/)
  assert.match(src, /\}, \[lessonId, lang\]\);/)
})

check('LearnPage re-fetches the lesson list on mount / reload', () => {
  const src = readSource(join(PAGES, 'LearnPage.jsx'))
  assert.match(src, /fetchLessons\(\)/)
  assert.match(src, /\}, \[lang, reloadKey\]\);/)
})

check('review and dashboard views are mounted exclusively (remount -> refetch)', () => {
  const src = readSource(APP)
  assert.match(src, /\{lessonId != null \? \(/)
  assert.match(src, /\) : reviewOpen \? \(/)
  assert.match(src, /<ReviewPage/)
  assert.match(src, /<LearnPage/)
})

// --- 6) 94% before the review correction, 100% after it ----------------------
check('progress view shows 18/18 at 94% before the review correction', () => {
  const view = lessonProgressView(progressBeforeReview)
  assert.equal(view.total, 18)
  assert.equal(view.answered, 18)
  assert.equal(view.correct, 17)
  assert.equal(view.score, 94) // server's best_score, displayed as-is
  assert.equal(view.percent, 100) // 18/18 questions VISITED (progress bar)
  assert.equal(view.status, 'completed')
})

check('progress view shows 18/18 at 100% after the review correction', () => {
  const view = lessonProgressView(progressAfterReview)
  assert.equal(view.answered, 18)
  assert.equal(view.correct, 18)
  assert.equal(view.score, 100)
  assert.equal(view.percent, 100)
  assert.equal(view.status, 'completed')
})

check('progress view clamps hostile values and survives a missing payload', () => {
  const view = lessonProgressView({
    questions_total: 18,
    questions_answered: 99,
    questions_correct: 18,
    best_score: 250,
  })
  assert.equal(view.answered, 18) // never above the denominator
  assert.equal(view.score, 100) // never above 100
  assert.equal(view.percent, 100)
  const empty = lessonProgressView(null, 18)
  assert.deepEqual(
    [empty.answered, empty.total, empty.score, empty.percent, empty.status],
    [0, 18, 0, 0, 'not_started'],
  )
})

// --- 7) The caught-up review state keeps working ------------------------------
check('the caught-up review state still works after answering all due cards', () => {
  const empty = reviewSummaryState({ total_active: 0, due_now: 0, scheduled: 0 })
  assert.equal(empty, REVIEW_SUMMARY_STATE.empty)
  const due = reviewSummaryState({ total_active: 1, due_now: 1, scheduled: 0 })
  assert.equal(due, REVIEW_SUMMARY_STATE.due)
  const caughtUp = reviewSummaryState({ total_active: 1, due_now: 0, scheduled: 1 })
  assert.equal(caughtUp, REVIEW_SUMMARY_STATE.scheduled)
  assert.equal(reviewSummaryState(null), null)
})

console.log(`\n${passed} checks passed`)


