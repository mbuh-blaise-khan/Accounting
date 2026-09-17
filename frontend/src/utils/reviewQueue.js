// Session 11 Part C3 — review-queue presentation helpers.
//
// Pure functions only (project convention: plain-Node testable, no DOM): they
// turn the REAL C2 API payloads into small UI-ready views. The server owns all
// substance (questions, options, feedback prose, schedule); these helpers
// never map option keys, never hold answer text, and never decide whether an
// answer is correct — grading happened server-side (straight comparison).
//
// Real payload shapes pinned by reviewQueue.test.mjs:
//   GET  /learning/reviews/summary -> { total_active, due_now, scheduled, next_due_at }
//   GET  /learning/reviews         -> [{ id, lesson_id, question_id, question_en/fr,
//                                       kind, answers:[{option_key,text_en,text_fr}],
//                                       stage, due_at, last_outcome, is_due, ... }]
//   POST /learning/reviews/{id}/answer -> { review_id, correct, stage, due_at,
//                                       interval_days, feedback:{correct,
//                                       explanation, correction, encouragement,
//                                       remediation} }

export const REVIEW_SUMMARY_STATE = Object.freeze({
  empty: 'empty', // no active review cards at all
  due: 'due', // at least one card is due now
  scheduled: 'scheduled', // cards exist but none is due yet
})

function nonEmptyString(value) {
  return typeof value === 'string' && value.trim() ? value : null
}

/**
 * Which summary state should the Learn page show?
 * null = the summary has not loaded yet (caller renders nothing).
 */
export function reviewSummaryState(summary) {
  if (!summary || typeof summary !== 'object') return null
  const total = Number(summary.total_active) || 0
  const due = Number(summary.due_now) || 0
  if (total <= 0) return REVIEW_SUMMARY_STATE.empty
  return due > 0 ? REVIEW_SUMMARY_STATE.due : REVIEW_SUMMARY_STATE.scheduled
}

/**
 * Localized date/time for a next-review timestamp (C2 sends ISO UTC).
 * Returns '' for missing/invalid values so callers can hide the line entirely
 * instead of showing "Invalid Date".
 */
export function formatDueDate(iso, lang = 'en') {
  const date = new Date(iso)
  if (!iso || Number.isNaN(date.getTime())) return ''
  try {
    return new Intl.DateTimeFormat(lang === 'fr' ? 'fr-FR' : 'en-GB', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(date)
  } catch {
    return ''
  }
}

/**
 * Body for POST /learning/reviews/{id}/answer: `option_key` for MCQ cards,
 * trimmed `text` for short-answer cards, null when nothing usable was given
 * (the caller keeps the submit button disabled instead of sending junk).
 */
export function reviewAnswerPayload({ optionKey, text } = {}) {
  if (nonEmptyString(optionKey)) return { option_key: optionKey }
  if (nonEmptyString(text)) return { text: text.trim() }
  return null
}

/** The only confidence values the C2 attempts endpoint accepts. */
export const CONFIDENCE = Object.freeze({
  understood: 'understood',
  guessed: 'guessed',
})

/**
 * Body fragment for POST /learning/attempts (Part C2): an INVALID or missing
 * confidence contributes NOTHING to the payload — the request shape stays
 * byte-identical to the pre-C2 clients, and no unknown value can ever reach
 * the server (the backend would 422 it).
 *
 * Scope note: the C2 review-answer endpoint does NOT accept confidence, so
 * this is only used by the lesson flow.
 */
export function confidencePayload(confidence) {
  if (confidence === CONFIDENCE.understood || confidence === CONFIDENCE.guessed) {
    return { confidence }
  }
  return {}
}

/**
 * Adapt one graded review answer (C2 shape: `correct` at the top level) to
 * the verdict object the Part C1 lesson helpers consume (`is_correct`).
 *
 * This is a pure FIELD RENAMING for the already-graded result — it adds no
 * data, never touches options, and lets the review page reuse
 * `feedbackStatus` / `feedbackProjection` / `remediationTarget` verbatim
 * (same explanation/correction/remediation rendering as lessons).
 */
export function reviewResultView(result) {
  if (!result || typeof result.correct !== 'boolean') return null
  return { is_correct: result.correct, feedback: result.feedback || {} }
}