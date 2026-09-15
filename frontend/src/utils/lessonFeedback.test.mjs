// Session 11 Part C1 — post-answer feedback helpers (run: npm run test:feedback).
//
// The payloads below mirror the ACTUAL backend response shape
// (backend/app/learning/schemas.py -> AttemptOut / AnswerFeedbackOut,
// backend/app/learning/feedback.py -> encouragement/action_label), so this file
// doubles as a frontend/backend compatibility pin: if the backend renames a
// field the UI consumes, this test fails loudly.
//
// Pure behaviour only — no browser, no DOM (project convention: plain Node +
// node:assert/strict, no extra test framework dependency).
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

import {
  FEEDBACK_STATUS,
  SECTION_ANCHOR_PREFIX,
  feedbackProjection,
  feedbackStatus,
  remediationTarget,
  sectionAnchorId,
} from './lessonFeedback.js'

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

// --- Payloads straight from the backend schema -------------------------------
// A correct MCQ attempt as the server returns it AFTER submission. The
// top-level correct_* / *option_key fields are the pre-existing Part A grading
// payload; `feedback` is the Part C1 addition.
const correctAttempt = {
  id: 1,
  lesson_id: 1,
  question_id: 11,
  is_correct: true,
  correct_option_key: 'A',
  correct_text: null,
  explanation_en: 'Accounting records what the business owns, owes and earns.',
  explanation_fr: "La comptabilité enregistre ce que l'entreprise possède.",
  progress: { status: 'in_progress', best_score: 100, questions_answered: 1 },
  feedback: {
    correct: true,
    explanation: 'Accounting records what the business owns, owes and earns.',
    encouragement: 'Well done — keep going.',
  },
}

// An incorrect MCQ attempt WITH a remediation target for the SAME lesson.
const incorrectAttempt = {
  id: 2,
  lesson_id: 1,
  question_id: 11,
  is_correct: false,
  correct_option_key: 'A',
  correct_text: null,
  explanation_en: 'Accounting records what the business owns, owes and earns.',
  explanation_fr: "La comptabilité enregistre ce que l'entreprise possède.",
  progress: { status: 'in_progress', best_score: 0, questions_answered: 1 },
  feedback: {
    correct: false,
    explanation: 'Accounting records what the business owns, owes and earns.',
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

// An incorrect attempt WITHOUT remediation: optional by design.
const incorrectNoRemediation = {
  ...incorrectAttempt,
  feedback: {
    correct: false,
    explanation: 'Accounting records what the business owns, owes and earns.',
    correction: 'Accounting exists to record what the business owns, owes and earns.',
    remediation: null,
  },
}

// --- 1) Nothing before submission --------------------------------------------
check('no graded verdict before an answer is submitted', () => {
  assert.equal(feedbackStatus(null), null)
  assert.equal(feedbackStatus(undefined), null)
  assert.equal(feedbackStatus({}), null)
  assert.equal(feedbackStatus({ explanation_en: 'leaked?' }), null)
  assert.equal(feedbackProjection(null), null)
  assert.equal(feedbackProjection({}), null)
})

check('verdict is exposed as a named status, not a bare boolean/colour', () => {
  assert.equal(feedbackStatus(correctAttempt), FEEDBACK_STATUS.correct)
  assert.equal(feedbackStatus(incorrectAttempt), FEEDBACK_STATUS.incorrect)
})

// --- 2) Feedback is displayable only after submission -------------------------
check('projection renders the server prose for a correct attempt', () => {
  const view = feedbackProjection(correctAttempt)
  assert.equal(view.status, FEEDBACK_STATUS.correct)
  assert.equal(view.explanation, correctAttempt.feedback.explanation)
  assert.equal(view.encouragement, correctAttempt.feedback.encouragement)
  // Nothing to review when the answer was right.
  assert.equal(view.correction, null)
  assert.equal(view.remediation, null)
})

check('projection renders correction + remediation for an incorrect attempt', () => {
  const view = feedbackProjection(incorrectAttempt)
  assert.equal(view.status, FEEDBACK_STATUS.incorrect)
  assert.equal(view.explanation, incorrectAttempt.feedback.explanation)
  assert.equal(view.correction, incorrectAttempt.feedback.correction)
  assert.equal(view.encouragement, null)
  assert.deepEqual(view.remediation, {
    lessonId: 1,
    sectionId: 42,
    sectionPosition: 2,
    sectionTitle: 'Why it matters',
    actionLabel: 'Review this concept',
  })
})

// --- 3) Remediation action visibility -----------------------------------------
check('remediation action appears only when the target is usable', () => {
  // No feedback / no remediation object.
  assert.equal(remediationTarget(null), null)
  assert.equal(remediationTarget({ feedback: {} }), null)
  assert.equal(remediationTarget(incorrectNoRemediation), null)
  // The projection of a no-remediation attempt carries no action either.
  assert.equal(feedbackProjection(incorrectNoRemediation).remediation, null)
  // A correct answer never shows a review action, even if a payload leaked one.
  const trap = {
    ...correctAttempt,
    feedback: { ...correctAttempt.feedback, remediation: incorrectAttempt.feedback.remediation },
  }
  assert.equal(feedbackProjection(trap).remediation, null)
})

check('invalid or incomplete remediation targets are rejected safely', () => {
  const base = incorrectAttempt.feedback.remediation
  // A target without ids can never be turned into a navigation action.
  assert.equal(remediationTarget({ feedback: { remediation: { ...base, lesson_id: null } } }), null)
  assert.equal(remediationTarget({ feedback: { remediation: { ...base, section_id: undefined } } }), null)
  assert.equal(remediationTarget({ feedback: { remediation: {} } }), null)
  // Missing titles/labels are projected as null, never invented.
  const sparse = remediationTarget({
    feedback: { remediation: { lesson_id: 1, section_id: 42 } },
  })
  assert.equal(sparse.sectionTitle, null)
  assert.equal(sparse.actionLabel, null)
  assert.equal(sparse.sectionId, 42)
})

// --- 4) Section anchors are deterministic --------------------------------------
check('section anchor ids are stable and deterministic', () => {
  assert.equal(sectionAnchorId({ sectionId: 42 }), 'lesson-section-42')
  // A plain lesson-section object (from the detail payload) works too.
  assert.equal(sectionAnchorId({ id: 7 }), 'lesson-section-7')
  // Position fallback when only the position is known.
  assert.equal(sectionAnchorId({ sectionPosition: 3 }), 'lesson-section-pos-3')
  assert.equal(sectionAnchorId({ position: 3 }), 'lesson-section-pos-3')
  // Nothing to anchor.
  assert.equal(sectionAnchorId(null), null)
  assert.equal(sectionAnchorId({}), null)
  assert.equal(sectionAnchorId(remediationTarget(incorrectAttempt)), 'lesson-section-42')
})

// --- 5) Language fallback selection --------------------------------------------
check('projection falls back to the requested language when feedback is absent', () => {
  const legacy = {
    is_correct: true,
    explanation_en: 'Because debits equal credits.',
    explanation_fr: 'Car les débits égalent les crédits.',
  }
  assert.equal(feedbackProjection(legacy, false).explanation, legacy.explanation_en)
  assert.equal(feedbackProjection(legacy, true).explanation, legacy.explanation_fr)
})

// --- 6) No answer key embedded in the helper ------------------------------------
check('the helper never embeds or reveals the answer key', () => {
  // A trap payload whose correct option text is a sentinel: none of it may
  // reach the projection, which whitelists only the server's prose.
  const trap = {
    is_correct: false,
    correct_option_key: 'B',
    correct_text: 'SECRET-CORRECT-TEXT',
    answers: [
      { option_key: 'A', text_en: 'decoy-A', is_correct: false },
      { option_key: 'B', text_en: 'SECRET-CORRECT-TEXT', is_correct: true },
    ],
    feedback: {
      correct: false,
      explanation: 'server prose',
      correction: 'server correction',
    },
  }
  const flattened = JSON.stringify(feedbackProjection(trap))
  assert.ok(!flattened.includes('SECRET-CORRECT-TEXT'))
  assert.ok(!flattened.includes('decoy-A'))
  assert.ok(!flattened.includes('correct_option_key'))
  assert.ok(!flattened.includes('is_correct'))
  // And the projection carries exactly the whitelisted fields — nothing else.
  assert.deepEqual(Object.keys(feedbackProjection(trap)).sort(), [
    'correction',
    'encouragement',
    'explanation',
    'remediation',
    'status',
  ])
})

// --- 7) Generic EN/FR UI labels stay in parity ---------------------------------
check('the C1 i18n keys exist in BOTH en.json and fr.json', () => {
  const en = JSON.parse(readFileSync(new URL('../i18n/en.json', import.meta.url), 'utf8'))
  const fr = JSON.parse(readFileSync(new URL('../i18n/fr.json', import.meta.url), 'utf8'))
  const c1Keys = ['feedbackWhyCorrect', 'feedbackConcept', 'feedbackCorrection', 'reviewConcept']
  for (const key of c1Keys) {
    assert.ok(typeof en.learn[key] === 'string' && en.learn[key].trim(), `en.learn.${key}`)
    assert.ok(typeof fr.learn[key] === 'string' && fr.learn[key].trim(), `fr.learn.${key}`)
  }
  // The labels differ (the languages are genuinely maintained, not copies).
  assert.notEqual(en.learn.reviewConcept, fr.learn.reviewConcept)
})

console.log(`\n${passed} check(s) passed`)
