import { useEffect, useState } from 'react';
import { useLanguage } from '../i18n/index.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { fetchLesson, submitAttempt } from '../services/api';

/**
 * Lesson detail — content sections, then one question at a time with instant
 * server-side feedback (straight stored-answer comparison; no AI grading).
 *
 * Lesson 4 practice connector: a correct answer on a question flagged
 * posts_demo_transaction posts a REAL transaction into the workspace
 * (org passed down from WorkSpace), connecting Learn Mode to Practice Mode.
 *
 * Content-protection DETERRENTS — honest scope: NO website can block
 * screenshots or screen recording; that is a browser/OS limitation. What is
 * done here: right-click and text selection are disabled on lesson content,
 * a subtle watermark of the signed-in user is overlaid (traceability
 * deterrent, not blocking), and content is served per-request from the API
 * (never static/downloadable files).
 */
export default function LessonDetailPage({ lessonId, orgId, onBack }) {
  const { t, lang } = useLanguage();
  const { user } = useAuth();
  const [lesson, setLesson] = useState(null);
  const [error, setError] = useState('');
  const [qIndex, setQIndex] = useState(0);
  const [selected, setSelected] = useState(null); // MCQ option_key
  const [textAnswer, setTextAnswer] = useState(''); // short-answer text
  const [result, setResult] = useState(null); // last AttemptOut
  const [progress, setProgress] = useState(null); // latest progress
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    let alive = true;
    setError('');
    setLesson(null);
    setQIndex(0);
    setSelected(null);
    setTextAnswer('');
    setResult(null);
    setProgress(null);
    fetchLesson(lessonId)
      .then((data) => {
        if (alive) {
          setLesson(data);
          setProgress(data.progress);
        }
      })
      .catch(() => {
        if (alive) setError(t('learn.loadError'));
      });
    return () => {
      alive = false;
    };
    // Reload per lesson and per language so the server's language toggle is
    // always respected. `t` changes with lang; excluded to avoid re-fetch
    // loops — lang alone drives the reload.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lessonId, lang]);

  if (error) {
    return (
      <Shell onBack={onBack} t={t}>
        <p className="text-sm text-red-600">{error}</p>
      </Shell>
    );
  }
  if (!lesson) {
    return (
      <Shell onBack={onBack} t={t}>
        <p className="text-sm text-slate-500">{t('learn.loading')}</p>
      </Shell>
    );
  }

  const fr = lang === 'fr';
  const questions = lesson.questions || [];
  const total = questions.length;
  const done = qIndex >= total;
  const q = done ? null : questions[qIndex];

  async function check() {
    if (checking || result || !q) return;
    setChecking(true);
    try {
      const payload = { lesson_id: lesson.id };
      if (orgId != null) payload.organization_id = orgId;
      if (q.kind === 'short_answer') payload.text = textAnswer.trim();
      else payload.option_key = selected;
      const attempt = await submitAttempt(q.id, payload);
      setResult(attempt);
      setProgress(attempt.progress);
    } catch {
      setError(t('learn.loadError'));
    } finally {
      setChecking(false);
    }
  }

  function next() {
    setResult(null);
    setSelected(null);
    setTextAnswer('');
    setQIndex((i) => i + 1);
  }

  const watermarkLabel = user
    ? [user.display_name, user.email].filter(Boolean).join(' · ')
    : '';

  const p = progress || {};
  const answered = p.questions_answered || 0;
  const lessonPct = p.questions_total
    ? Math.round((answered / p.questions_total) * 100)
    : 0;
  const title = fr ? lesson.title_fr : lesson.title_en;

  return (
    <Shell onBack={onBack} t={t} watermarkLabel={watermarkLabel}>
      {/* Lesson header: label > title > progress — clear visual hierarchy */}
      <header className="mb-6">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          {t('learn.lesson')} {lesson.position}
        </p>
        <h1 className="mt-0.5 text-2xl font-bold text-slate-900">{title}</h1>
        <div className="mt-3 flex items-center gap-3">
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all"
              style={{ width: `${lessonPct}%` }}
            />
          </div>
          <span className="shrink-0 text-xs text-slate-500">
            {answered}/{p.questions_total || total}
            {p.best_score != null
              ? ` · ${t('learn.score')} ${p.best_score}%`
              : ''}
          </span>
        </div>
      </header>

      {/* Content sections — served per-request from the API, never static files */}
      <div className="space-y-4">
        {(lesson.sections || []).map((s) => (
          <div key={s.position}>
            {(fr ? s.heading_fr : s.heading_en) ? (
              <h2 className="text-base font-semibold text-slate-900">
                {fr ? s.heading_fr : s.heading_en}
              </h2>
            ) : null}
            <p className="mt-1 whitespace-pre-line text-sm leading-relaxed text-slate-700">
              {fr ? s.body_fr : s.body_en}
            </p>
          </div>
        ))}
      </div>

      {/* Questions — one at a time, instant server-side feedback */}
      <div className="mt-8 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        {done ? (
          <LessonComplete p={p} t={t} />
        ) : (
          <>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              {t('learn.question')} {qIndex + 1}/{total}
            </p>
            <h2 className="mt-1 text-base font-semibold text-slate-900">
              {fr ? q.question_fr : q.question_en}
            </h2>

            {q.posts_demo_transaction ? (
              <p className="mt-2 rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
                {t('learn.practiceHint')}
              </p>
            ) : null}

            {q.kind === 'short_answer' ? (
              <input
                type="text"
                value={textAnswer}
                onChange={(e) => setTextAnswer(e.target.value)}
                disabled={Boolean(result) || checking}
                maxLength={500}
                className="mt-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-emerald-500 focus:outline-none disabled:bg-slate-50"
                placeholder={t('learn.yourAnswer')}
              />
            ) : (
              <div className="mt-4 space-y-2" role="radiogroup">
                {(q.answers || []).map((a) => (
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
                      name={`q-${q.id}`}
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
                  (q.kind === 'short_answer' ? !textAnswer.trim() : !selected)
                }
                className="mt-4 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {t('learn.checkAnswer')}
              </button>
            ) : (
              <Feedback
                result={result}
                question={q}
                fr={fr}
                t={t}
                onNext={next}
              />
            )}
          </>
        )}
      </div>
    </Shell>
  );
}

/**
 * Shared lesson chrome: back link, content-selection deterrents, watermark.
 * Honest scope: this DETERS casual copying (right-click/selection disabled,
 * visible user watermark) — no web app can block screenshots or recording.
 */
function Shell({ onBack, t, watermarkLabel, children }) {
  return (
    <section
      className="relative mx-auto w-full max-w-3xl px-4 py-6"
      onContextMenu={(e) => e.preventDefault()}
    >
      <button
        type="button"
        onClick={onBack}
        className="mb-4 inline-flex items-center gap-1 text-sm font-medium text-slate-500 transition hover:text-emerald-700"
      >
        ← {t('learn.backToLessons')}
      </button>
      <div className="relative select-none">
        {watermarkLabel ? (
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 z-10 overflow-hidden"
          >
            <span className="absolute right-1 top-1 -rotate-12 text-[10px] font-medium uppercase tracking-widest text-slate-300">
              {watermarkLabel}
            </span>
            <span className="absolute bottom-24 left-1 -rotate-12 text-[10px] font-medium uppercase tracking-widest text-slate-200">
              {watermarkLabel}
            </span>
          </div>
        ) : null}
        {children}
      </div>
      <p className="mt-8 text-center text-[11px] text-slate-400">
        {t('learn.watermarkNote')}
      </p>
    </section>
  );
}

/** End-of-lesson banner shown once every question has been answered. */
function LessonComplete({ p, t }) {
  return (
    <div className="py-4 text-center">
      <p className="text-lg font-bold text-emerald-700">
        {t('learn.lessonComplete')}
      </p>
      {p.best_score != null ? (
        <p className="mt-1 text-sm text-slate-600">
          {t('learn.score')}: {p.best_score}%
        </p>
      ) : null}
      {p.practice_posted ? (
        <p className="mt-2 text-sm text-emerald-700">
          {t('learn.practicePosted')} {t('learn.viewInJournal')}
        </p>
      ) : null}
    </div>
  );
}

/**
 * Instant server-side feedback for the just-graded attempt. The correct
 * option/text and explanation are revealed ONLY here (they are absent from
 * the pre-grading payload — straight stored-answer comparison, no AI).
 */
function Feedback({ result, question, fr, t, onNext }) {
  const explanation = fr ? result.explanation_fr : result.explanation_en;
  let correctAnswer = null;
  if (!result.is_correct) {
    if (question.kind === 'short_answer') {
      correctAnswer = result.correct_text;
    } else if (result.correct_option_key) {
      const match = (question.answers || []).find(
        (a) => a.option_key === result.correct_option_key
      );
      correctAnswer = match ? (fr ? match.text_fr : match.text_en) : null;
    }
  }
  return (
    <div className="mt-4 space-y-3">
      <p
        className={`text-sm font-semibold ${
          result.is_correct ? 'text-emerald-700' : 'text-amber-700'
        }`}
      >
        {result.is_correct ? t('learn.correct') : t('learn.incorrect')}
      </p>
      {correctAnswer ? (
        <p className="text-sm text-slate-700">
          <span className="font-semibold">{t('learn.correctAnswerWas')}:</span>{' '}
          {correctAnswer}
        </p>
      ) : null}
      {explanation ? (
        <div className="rounded-lg bg-slate-50 p-3 text-sm leading-relaxed text-slate-700">
          <span className="font-semibold">{t('learn.explanation')}: </span>
          {explanation}
        </div>
      ) : null}
      {result.is_correct && result.practice_error ? (
        <p className="rounded-lg bg-amber-50 p-3 text-xs text-amber-700">
          {result.practice_error}
        </p>
      ) : null}
      <button
        type="button"
        onClick={onNext}
        className="mt-1 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
      >
        {t('learn.nextQuestion')}
      </button>
    </div>
  );
}
