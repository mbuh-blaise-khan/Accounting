// Session 11 Part C3 — spaced-review queue experience.
//
// Reuses the Part C1 lesson presentation conventions verbatim (one question at
// a time, instant server-side feedback, explanation/correction/remediation via
// the Part C1 helpers, text with an icon — never colour alone):
//
// API (Part C2, all authenticated + user-scoped):
//   GET  /learning/reviews?due_only=true -> active cards due now
//   POST /learning/reviews/{id}/answer   -> {review_id, question_id, correct,
//                                          stage, due_at, interval_days, feedback}
//
// Notable data fact: the review card AND its answer response carry NO answer
// material — no is_correct flag, no correct option key/text, no accepted
// short answers. The response reuses the Part C1 `feedback` object, so
// `feedbackStatus` / `feedbackProjection` / `remediationTarget` (in
// utils/lessonFeedback.js) apply unchanged via utils/reviewQueue.js's
// `reviewResultView` adapter.
import { useEffect, useState } from 'react';
import { useLanguage } from '../i18n/index.jsx';
import { fetchReviews, answerReview } from '../services/api';
import {
  feedbackProjection,
  feedbackStatus,
  FEEDBACK_STATUS,
  remediationTarget,
  sectionAnchorId,
} from '../utils/lessonFeedback.js';
import {
  formatDueDate,
  reviewAnswerPayload,
  reviewResultView,
} from '../utils/reviewQueue.js';

export default function ReviewPage({ onBack, onOpenLesson }) {
  const { t, lang } = useLanguage();
  const [cards, setCards] = useState(null); // due cards, or null while loading
  const [index, setIndex] = useState(0); // position inside this session's queue
  const [answered, setAnswered] = useState(0); // cards answered this session
  const [selected, setSelected] = useState(null); // MCQ option_key
  const [textAnswer, setTextAnswer] = useState(''); // short-answer text
  const [result, setResult] = useState(null); // last ReviewAnswerOut
  const [answerError, setAnswerError] = useState('');
  const [checking, setChecking] = useState(false);
  const [loadError, setLoadError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let alive = true;
    setLoadError('');
    setAnswerError('');
    setCards(null);
    setIndex(0);
    setAnswered(0);
    setResult(null);
    fetchReviews(true)
      .then((data) => {
        if (alive) setCards(Array.isArray(data) ? data : []);
      })
      .catch(() => {
        if (alive) setLoadError(t('review.loadError'));
      });
    return () => {
      alive = false;
    };
    // lang re-fetches so freshly toggled UI language re-renders server
    // content; reloadKey drives the retry button. `t` is excluded to avoid
    // re-fetch loops — lang alone drives the reload.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang, reloadKey]);

  const retry = () => setReloadKey((k) => k + 1);

  /** Advance to the next card in this session's queue, or re-confirm it is empty. */
  function next() {
    const remaining = (cards || []).slice(index + 1);
    setCards(remaining.length ? remaining : cards);
    setResult(null);
    setSelected(null);
    setTextAnswer('');
    setAnswerError('');
    setIndex(0);
  }

  async function check() {
    const card = (cards || [])[index];
    if (checking || result || !card) return;
    const payload = reviewAnswerPayload({
      optionKey: selected,
      text: textAnswer,
    });
    if (!payload) return;
    setChecking(true);
    setAnswerError('');
    try {
      const answer = await answerReview(card.id, payload, lang);
      setResult(answer);
      setAnswered((n) => n + 1);
    } catch {
      setAnswerError(t('review.answerError'));
    } finally {
      setChecking(false);
    }
  }

  if (loadError && cards === null) {
    return (
      <section className="mx-auto w-full max-w-3xl px-4 py-6">
        <BackLink onBack={onBack} t={t} />
        <p className="text-sm text-red-600">{loadError}</p>
        <button
          type="button"
          onClick={retry}
          className="mt-3 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
        >
          {t('certificate.retry')}
        </button>
      </section>
    );
  }
  if (cards === null) {
    return (
      <section className="mx-auto w-full max-w-3xl px-4 py-6">
        <BackLink onBack={onBack} t={t} />
        <p className="text-sm text-slate-500">{t('learn.loading')}</p>
      </section>
    );
  }
  if (cards.length === 0) {
    // Genuine empty state (nothing due) AND completion state (session queue
    // exhausted behave the same: calm "all caught up").
    return (
      <section className="mx-auto w-full max-w-3xl px-4 py-6">
        <BackLink onBack={onBack} t={t} />
        <div className="py-8 text-center">
          <p className="text-2xl" aria-hidden="true">
            ✅
          </p>
          <p className="mt-2 text-lg font-bold text-emerald-700">
            {t('review.allCaughtUp')}
          </p>
          <p className="mx-auto mt-2 max-w-md text-sm text-slate-600">
            {t('review.emptyHint')}
          </p>
        </div>
      </section>
    );
  }

  const fr = lang === 'fr';
  const card = cards[index];
  const sessionTotal = answered + cards.length;

  return (
    <section className="mx-auto w-full max-w-3xl px-4 py-6">
      <BackLink onBack={onBack} t={t} />
      <header className="mb-6">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          {t('review.title')}
        </p>
        <h1 className="mt-0.5 text-2xl font-bold text-slate-900">
          {t('review.subtitle')}
        </h1>
      </header>

      <div
        className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
        onContextMenu={(e) => e.preventDefault()}
      >
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          {t('review.cardProgress')} {answered + 1} {t('review.of')} {sessionTotal}
        </p>
        <p className="mt-1 text-xs text-slate-500">
          {t('review.fromLesson')}: {fr ? card.lesson_title_fr : card.lesson_title_en}
        </p>
        <h2 className="mt-2 text-base font-semibold text-slate-900">
          {fr ? card.question_fr : card.question_en}
        </h2>

        {card.kind === 'short_answer' ? (
          <input
            type="text"
            value={textAnswer}
            onChange={(e) => setTextAnswer(e.target.value)}
            disabled={Boolean(result) || checking}
            maxLength={500}
            className="mt-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-emerald-500 focus:outline-none disabled:bg-slate-50"
            placeholder={t('review.yourAnswer')}
          />
        ) : (
          <div className="mt-4 space-y-2" role="radiogroup">
            {(card.answers || []).map((a) => (
              <label
                key={a.option_key}
                className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-sm transition ${
                  selected === a.option_key
                    ? 'border-emerald-500 bg-emerald-50 text-slate-900'
                    : 'border-slate-200 text-slate-700 hover:border-slate-300'
                } ${result ? 'cursor-default opacity-90' : ''}`}
              >
                <input
                  type="radio"
                  name={`review-${card.id}`}
                  value={a.option_key}
                  checked={selected === a.option_key}
                  onChange={() => setSelected(a.option_key)}
                  disabled={Boolean(result) || checking}
                  className="accent-emerald-600"
                />
                <span>{fr ? a.text_fr : a.text_en}</span>
              </label>
            ))}
          </div>
        )}

        {!result ? (
          <button
            type="button"
            onClick={check}
            disabled={
              checking ||
              (card.kind === 'short_answer' ? !textAnswer.trim() : !selected)
            }
            className="mt-4 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {t('review.checkAnswer')}
          </button>
        ) : (
          <ReviewFeedback
            result={result}
            fr={fr}
            t={t}
            lang={lang}
            onNext={next}
            onOpenLesson={onOpenLesson}
          />
        )}
        {answerError ? (
          <p className="mt-3 text-sm text-red-600">{answerError}</p>
        ) : null}
      </div>
    </section>
  );
}

function BackLink({ onBack, t }) {
  return (
    <button
      type="button"
      onClick={onBack}
      className="mb-4 inline-flex items-center gap-1 text-sm font-medium text-slate-500 transition hover:text-emerald-700"
    >
      ← {t('review.backToLessons')}
    </button>
  );
}

/**
 * Instant server-side feedback for the just-graded review answer.
 * The review response reuses the Part C1 `feedback` object, so its verdict,
 * explanation, correction and remediation target are rendered exactly like
 * the lesson flow. On top of that the C2 schedule is shown:
 * - correct   → the next due date (stage ladder 1 / 3 / 7 / 14 days);
 * - incorrect → "due again now" (stage reset to 0, due immediately).
 * The "Review this concept" action opens the lesson at the target section.
 */
function ReviewFeedback({ result, fr, t, lang, onNext, onOpenLesson }) {
  const view = reviewResultView(result);
  const status = feedbackStatus(view);
  const isCorrect = status === FEEDBACK_STATUS.correct;
  const { explanation, correction, encouragement, remediation } =
    feedbackProjection(view, fr);
  const nextDue = isCorrect ? formatDueDate(result.due_at, lang) : '';

  function openConcept() {
    const target = remediationTarget(view);
    if (!target) return;
    const anchor = sectionAnchorId(target);
    if (!anchor) return;
    // `target.lessonId` is the card's OWN lesson — opening it shows the exact
    // section the server pointed at.
    onOpenLesson(target.lessonId, anchor);
  }

  return (
    <div className="mt-4 space-y-3">
      <p
        className={`inline-flex items-center gap-2 rounded-lg border px-3 py-1 text-sm font-semibold ${
          isCorrect
            ? 'border-emerald-300 bg-emerald-50 text-emerald-800'
            : 'border-amber-300 bg-amber-50 text-amber-800'
        }`}
      >
        <span aria-hidden="true">{isCorrect ? '✓' : '!'}</span>
        {isCorrect ? t('learn.correct') : t('learn.incorrect')}
      </p>
      {explanation ? (
        <div className="rounded-lg bg-slate-50 p-3 text-sm leading-relaxed text-slate-700">
          <span className="font-semibold">
            {isCorrect ? t('learn.feedbackWhyCorrect') : t('learn.feedbackConcept')}:{' '}
          </span>
          {explanation}
        </div>
      ) : null}
      {correction ? (
        <div className="rounded-lg border border-slate-200 p-3 text-sm leading-relaxed text-slate-700">
          <span className="font-semibold">{t('learn.feedbackCorrection')}: </span>
          {correction}
        </div>
      ) : null}
      {encouragement ? (
        <p className="text-xs text-slate-500">{encouragement}</p>
      ) : null}
      {remediation ? (
        <button
          type="button"
          onClick={openConcept}
          className="inline-flex items-center gap-1 rounded-lg border border-amber-300 bg-amber-50 px-3 py-1.5 text-sm font-semibold text-amber-800 transition hover:bg-amber-100"
        >
          {remediation.actionLabel || t('learn.reviewConcept')}
        </button>
      ) : null}
      <div className="rounded-lg bg-emerald-50 p-3 text-xs text-emerald-800">
        {isCorrect && nextDue ? (
          <p>
            {t('review.nextDue')}: <span className="font-semibold">{nextDue}</span>
          </p>
        ) : null}
        {!isCorrect ? <p>{t('review.dueAgainNow')}</p> : null}
      </div>
      <button
        type="button"
        onClick={onNext}
        className="mt-1 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
      >
        {t('review.nextCard')}
      </button>
    </div>
  );
}