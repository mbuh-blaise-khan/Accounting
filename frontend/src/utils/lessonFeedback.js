// Session 11 Part C1 — post-answer feedback presentation helpers.
//
// The SERVER owns all feedback substance: the explanation, the plain-language
// correction, the encouragement and the (optional) remediation target are
// authored in the backend seed content and returned only from
// POST /learning/attempts. These helpers only:
//   - read the server's verdict (result.is_correct) and its `feedback` object;
//   - project a small, whitelisted view for rendering;
//   - build a stable DOM anchor for the remediation section.
//
// They never map option keys, never know which option is correct, and never
// hold answer text — the correct answer is only ever rendered from what the
// grading response already returned (pre-existing Part A behaviour). Keeping
// that rule here makes it testable (see lessonFeedback.test.mjs).

export const FEEDBACK_STATUS = Object.freeze({
  correct: 'correct',
  incorrect: 'incorrect',
})

/** Stable DOM id for a lesson section (sections carry a server-side id). */
export const SECTION_ANCHOR_PREFIX = 'lesson-section-'

function nonEmptyString(value) {
  return typeof value === 'string' && value.trim() ? value : null
}

/** 'correct' | 'incorrect' | null (null = nothing was graded yet). */
export function feedbackStatus(result) {
  if (!result || typeof result.is_correct !== 'boolean') return null
  return result.is_correct ? FEEDBACK_STATUS.correct : FEEDBACK_STATUS.incorrect
}

/**
 * The optional "Review this concept" target, or null when the server did not
 * provide a usable one. Never invents a section: an incomplete payload is
 * treated as "no remediation".
 */
export function remediationTarget(result) {
  const rem = result && result.feedback ? result.feedback.remediation : null
  if (!rem) return null
  if (rem.lesson_id == null || rem.section_id == null) return null
  return {
    lessonId: rem.lesson_id,
    sectionId: rem.section_id,
    sectionPosition: rem.section_position ?? null,
    sectionTitle: nonEmptyString(rem.section_title),
    actionLabel: nonEmptyString(rem.action_label),
  }
}

/** DOM anchor for a section, from a section object or a remediation target. */
export function sectionAnchorId(sectionOrTarget) {
  if (!sectionOrTarget) return null
  const id = sectionOrTarget.sectionId ?? sectionOrTarget.id
  if (id != null) return `${SECTION_ANCHOR_PREFIX}${id}`
  const position = sectionOrTarget.sectionPosition ?? sectionOrTarget.position
  return position != null ? `${SECTION_ANCHOR_PREFIX}pos-${position}` : null
}

/**
 * Small whitelisted view of one graded attempt for rendering.
 *
 * Deliberately excludes every grading detail the payload may carry
 * (correct_option_key, correct_text, answers' is_correct flags, progress…):
 * the UI renders the verdict and the server's prose, nothing else.
 * `explanation`/`correction`/`encouragement` fall back to the pre-existing
 * top-level explanation fields so a response without `feedback` still works.
 */
export function feedbackProjection(result, fr = false) {
  const status = feedbackStatus(result)
  if (!status) return null
  const fb = result.feedback || {}
  const explanation =
    nonEmptyString(fb.explanation) ??
    nonEmptyString(fr ? result.explanation_fr : result.explanation_en)
  const remediation = status === FEEDBACK_STATUS.incorrect
    ? remediationTarget(result)
    : null
  return {
    status,
    explanation,
    correction:
      status === FEEDBACK_STATUS.incorrect
        ? nonEmptyString(fb.correction)
        : null,
    encouragement:
      status === FEEDBACK_STATUS.correct
        ? nonEmptyString(fb.encouragement)
        : null,
    remediation,
  }
}
