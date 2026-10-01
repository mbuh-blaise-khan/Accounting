// Session 18 hotfix — lesson sequencing + progress presentation helpers.
//
// PURE functions only (project convention: plain-Node testable, no DOM, no new
// dependency). The SERVER is authoritative for both the fixed normal question
// sequence and progress: the learning service heals/deduplicates legacy
// duplicate positions before serving, and the review endpoint records each
// review answer as an attempt on the SAME immutable question id before
// rolling mastery up. These helpers only:
//   - project the server's fixed sequence defensively (one entry per immutable
//     id AND per seeded position, ascending position) so a malformed legacy
//     payload can never render the same question twice in the numbered lesson
//     flow, and a review card is never part of that sequence;
//   - clamp the displayed question number into 1..total (never above the
//     denominator, never below 1);
//   - build a bounded view of the server's progress payload for the progress
//     bar (display-only clamps — the backend stays authoritative).
//
// They never compute a score, never mark an answer correct and never invent
// progress: every displayed number comes from the server payload.

function isQuestionLike(value) {
  return Boolean(value) && typeof value === 'object';
}

/**
 * The lesson's fixed normal sequence as the UI must render it: entries with a
 * usable id AND position, deduplicated by immutable id and by seeded position
 * (first occurrence in server order wins) and ordered by position.
 */
export function uniqueQuestionSequence(questions) {
  if (!Array.isArray(questions)) return []
  const out = []
  const seenIds = new Set()
  const seenPositions = new Set()
  for (const q of questions) {
    if (!isQuestionLike(q)) continue
    if (q.id == null || q.position == null) continue
    if (seenIds.has(q.id) || seenPositions.has(q.position)) continue
    seenIds.add(q.id)
    seenPositions.add(q.position)
    out.push(q)
  }
  return out.sort((a, b) => a.position - b.position)
}

/** Index clamped into [0, total - 1]; 0 when the lesson has no questions. */
export function safeQuestionIndex(index, total) {
  const n = Number(total) || 0
  if (n <= 0) return 0
  const i = Number(index) || 0
  return Math.min(Math.max(i, 0), n - 1)
}

/** 1-based displayed number clamped to 1..total (0 when there is none). */
export function displayedQuestionNumber(index, total) {
  const n = Number(total) || 0
  if (n <= 0) return 0
  return safeQuestionIndex(index, n) + 1
}

/** Next index after a graded answer — never past `total` (completion marker). */
export function nextQuestionIndex(index, total) {
  const n = Number(total) || 0
  if (n <= 0) return 0
  const i = Number(index) || 0
  return Math.min(Math.max(i, 0) + 1, n)
}

/**
 * Bounded view of the server's progress payload:
 * `{ status, answered, total, correct, score, percent, practicePosted }`.
 *
 * `percent` mirrors the server's answered count over the server's own total
 * (the lesson progress bar), `score` is the server's current mastery
 * (`best_score`) — which the review-correction flow now updates. Clamps are
 * display guards only; the backend remains the source of truth.
 */
export function lessonProgressView(progress, fallbackTotal = 0) {
  const p = progress && typeof progress === 'object' ? progress : {}
  const total = Math.max(Number(p.questions_total) || Number(fallbackTotal) || 0, 0)
  const rawAnswered = Math.max(Number(p.questions_answered) || 0, 0)
  const answered = total > 0 ? Math.min(rawAnswered, total) : rawAnswered
  const correct = Math.max(Number(p.questions_correct) || 0, 0)
  const score = Math.min(Math.max(Number(p.best_score) || 0, 0), 100)
  const percent = total > 0 ? Math.min(Math.round((answered / total) * 100), 100) : 0
  return {
    status: p.status || 'not_started',
    answered,
    total,
    correct,
    score,
    percent,
    practicePosted: Boolean(p.practice_posted),
  }
}
