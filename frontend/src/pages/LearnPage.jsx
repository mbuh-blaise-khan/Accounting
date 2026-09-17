import { useEffect, useState } from 'react';
import { useLanguage } from '../i18n/index.jsx';
import {
  fetchLessons,
  fetchCourseCompletion,
  issueCertificate,
  fetchReviewSummary,
} from '../services/api';
import CertificateCard from '../components/CertificateCard';
import { certificateState } from '../utils/certificatePresentation';
import {
  formatDueDate,
  REVIEW_SUMMARY_STATE,
  reviewSummaryState,
} from '../utils/reviewQueue';

/**
 * Learn Mode — lesson list with per-lesson and overall progress.
 *
 * Lesson titles/summaries come from the backend in both languages; the active
 * UI language decides which variant is shown, so the existing language toggle
 * is respected without extra state here.
 *
 * Session 11 Part B2 — the completion summary and certificate states are read
 * from the AUTHORITATIVE server endpoint (GET /learning/completion), never
 * guessed from local progress: locked -> available (issue) -> issued.
 */
export default function LearnPage({ onOpenLesson, onStartReview }) {
  const { t, lang } = useLanguage();
  const [lessons, setLessons] = useState(null);
  const [completion, setCompletion] = useState(null); // CourseCompletionOut
  // Session 11 Part C3 — spaced-review summary (ReviewSummaryOut or null while
  // loading). Rows/errors are handled quietly here: a review summary failure
  // never blocks the lesson list or the certificate UI.
  const [reviewSummary, setReviewSummary] = useState(null);
  const [lessonsError, setLessonsError] = useState('');
  const [completionError, setCompletionError] = useState('');
  const [issueError, setIssueError] = useState('');
  const [issuing, setIssuing] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let alive = true;
    setLessonsError('');
    setCompletionError('');
    setLessons(null);
    setCompletion(null);
    setReviewSummary(null);
    fetchLessons()
      .then((data) => {
        if (alive) setLessons(data);
      })
      .catch(() => {
        if (alive) setLessonsError(t('learn.loadError'));
      });
    fetchCourseCompletion()
      .then((data) => {
        if (alive) setCompletion(data);
      })
      .catch(() => {
        if (alive) setCompletionError(t('certificate.loadError'));
      });
    fetchReviewSummary()
      .then((data) => {
        if (alive) setReviewSummary(data);
      })
      .catch(() => {
        // Quiet degradation (see above): lessons + certificate stay usable.
        if (alive) setReviewSummary({ total_active: 0, due_now: 0, scheduled: 0, next_due_at: null });
      });
    return () => {
      alive = false;
    };
    // lang re-fetches so freshly toggled UI language re-renders server
    // content; reloadKey drives the retry buttons. `t` changes with lang and
    // is intentionally excluded.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang, reloadKey]);

  const retry = () => setReloadKey((k) => k + 1);

  async function handleIssue() {
    if (issuing) return;
    setIssuing(true);
    setIssueError('');
    try {
      const cert = await issueCertificate();
      setCompletion((prev) => ({
        ...(prev || {}),
        completed: true,
        certificate: cert,
        certificate_status: 'issued',
      }));
    } catch {
      setIssueError(t('certificate.issueError'));
    } finally {
      setIssuing(false);
    }
  }

  if (lessonsError && !lessons) {
    return (
      <section className="mx-auto w-full max-w-3xl px-4 py-6">
        <p className="text-sm text-red-600">{lessonsError}</p>
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
  if (!lessons) {
    return <p className="p-4 text-sm text-slate-500">{t('learn.loading')}</p>;
  }

  // Authoritative server-side numbers first; fall back to local progress only
  // while the completion call is in flight or failed (safe read-only display
  // values — the completion DECISION always stays server-side).
  const server = completion || {};
  const completed =
    server.completed_lessons != null
      ? server.completed_lessons
      : lessons.filter((l) => l.progress && l.progress.status === 'completed')
          .length;
  const total = server.total_lessons != null ? server.total_lessons : lessons.length;
  const overallPct =
    server.completion_percentage != null
      ? server.completion_percentage
      : total
        ? Math.round((completed / total) * 100)
        : 0;
  const certStatus = certificateState(completion);
  const lessonTitle = (l) => (lang === 'fr' ? l.title_fr : l.title_en);
  const actionLabel = (p) => {
    const answered = p.questions_answered || 0;
    if (p.status === 'completed') return t('learn.review');
    if (answered > 0) return t('learn.continue');
    return t('learn.start');
  };
  return (
    <section className="mx-auto w-full max-w-3xl px-4 py-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{t('learn.title')}</h1>
        <p className="mt-1 text-sm text-slate-600">{t('learn.subtitle')}</p>
      </header>

      <div className="mb-6 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-2 text-sm font-medium text-slate-700">
          <span>{t('certificate.progressTitle')}</span>
          <span className="flex items-center gap-2">
            <CertificateStatusChip status={certStatus} t={t} />
            <span>
              {completed}/{total} · {overallPct}%
            </span>
          </span>
        </div>
        <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-emerald-500 transition-all"
            style={{ width: `${overallPct}%` }}
          />
        </div>
      </div>

      {completionError ? (
        <div className="mb-6 flex items-center justify-between gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
          <p className="text-sm text-amber-700">{completionError}</p>
          <button
            type="button"
            onClick={retry}
            className="shrink-0 text-sm font-semibold text-amber-700 hover:underline"
          >
            {t('certificate.retry')}
          </button>
        </div>
      ) : null}

      {completion ? (
        <div className="mb-6">
          {certStatus === 'locked' ? (
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-start gap-3">
                <span className="text-2xl" aria-hidden="true">
                  🔒
                </span>
                <div>
                  <p className="text-sm font-semibold text-slate-800">
                    {t('certificate.lockedTitle')}
                  </p>
                  <p className="mt-1 text-sm text-slate-600">
                    {t('certificate.lockedHint')}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">
                    {t('certificate.perfectScoreHint')}
                  </p>
                </div>
              </div>
            </div>
          ) : null}

          {certStatus === 'available' ? (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-start gap-3">
                  <span className="text-2xl" aria-hidden="true">
                    🎉
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-emerald-800">
                      {t('certificate.availableTitle')}
                    </p>
                    <p className="mt-1 text-sm text-emerald-700">
                      {t('certificate.availableHint')}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleIssue}
                  disabled={issuing}
                  className="shrink-0 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
                >
                  {issuing ? t('certificate.issuing') : t('certificate.issue')}
                </button>
              </div>
              {issueError ? (
                <div className="mt-3 flex items-center justify-between gap-3 rounded-lg bg-white/70 p-3">
                  <p className="text-sm text-red-600">{issueError}</p>
                  <button
                    type="button"
                    onClick={handleIssue}
                    className="shrink-0 whitespace-nowrap text-sm font-semibold text-red-600 hover:underline"
                  >
                    {t('certificate.retry')}
                  </button>
                </div>
              ) : null}
            </div>
          ) : null}

          {certStatus === 'issued' ? (
            <CertificateCard certificate={completion.certificate} />
          ) : null}
        </div>
      ) : null}

      {reviewSummary ? (
        <ReviewSummaryCard summary={reviewSummary} t={t} lang={lang} onStartReview={onStartReview} />
      ) : null}
      <ol className="space-y-3">
        {lessons.map((lesson, idx) => {
          const p = lesson.progress || {};
          const total = p.questions_total || 0;
          const answered = p.questions_answered || 0;
          const pct = total ? Math.round((answered / total) * 100) : 0;
          const status = p.status || 'not_started';
          return (
            <li key={lesson.id}>
              <button
                type="button"
                onClick={() => onOpenLesson(lesson.id)}
                className="w-full rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-emerald-300 hover:shadow"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                      {t('learn.lesson')} {idx + 1}
                    </p>
                    <h2 className="mt-0.5 text-base font-semibold text-slate-900">
                      {lessonTitle(lesson)}
                    </h2>
                  </div>
                  <span className={statusChipClass(status)}>
                    {statusLabel(t, status)}
                  </span>
                </div>
                <div className="mt-3 flex items-center gap-3">
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={progressBarClass(status)}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="shrink-0 text-xs text-slate-500">
                    {answered}/{total}
                    {p.best_score != null ? ` · ${p.best_score}%` : ''}
                  </span>
                </div>
              </button>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function statusLabel(t, status) {
  if (status === 'completed') return t('learn.completed');
  if (status === 'in_progress') return t('learn.inProgress');
  return t('learn.notStarted');
}

/**
 * Session 11 Part C3 — spaced-review summary card (derived ONLY from the
 * C2 `GET /learning/reviews/summary` payload):
 * - 'due'       → amber card with the due count and a "Review now" action;
 * - 'scheduled' → quiet slate card with the scheduled count + next due date;
 * - 'empty'     → renders nothing (calm Learn page; empty state lives on the
 *   review page when opened).
 */
function ReviewSummaryCard({ summary, t, lang, onStartReview }) {
  const state = reviewSummaryState(summary);
  if (state === REVIEW_SUMMARY_STATE.due) {
    return (
      <div className="mb-6 flex flex-col gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <span className="text-2xl" aria-hidden="true">
            ⏰
          </span>
          <div>
            <p className="text-sm font-semibold text-amber-800">
              {summary.due_now} {t('review.readyNow')}
            </p>
            <p className="mt-1 text-sm text-amber-700">{t('review.subtitle')}</p>
          </div>
        </div>
        <button
          type="button"
          onClick={onStartReview}
          className="shrink-0 rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-amber-700"
        >
          {t('review.reviewNow')}
        </button>
      </div>
    );
  }
  if (state === REVIEW_SUMMARY_STATE.scheduled) {
    const nextDue = formatDueDate(summary.next_due_at, lang);
    return (
      <div className="mb-6 flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <span className="text-2xl" aria-hidden="true">
          📅
        </span>
        <div>
          <p className="text-sm font-semibold text-slate-800">
            {summary.scheduled} {t('review.scheduledLater')}
          </p>
          {nextDue ? (
            <p className="mt-1 text-xs text-slate-500">
              {t('review.nextDue')}: {nextDue}
            </p>
          ) : null}
        </div>
      </div>
    );
  }
  return null;
}

/** Small status pill for the server-side completion summary. */
function CertificateStatusChip({ status, t }) {
  const base =
    'shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold whitespace-nowrap';
  if (status === 'issued') {
    return (
      <span className={`${base} bg-emerald-100 text-emerald-700`}>
        {t('certificate.statusIssued')}
      </span>
    );
  }
  if (status === 'available') {
    return (
      <span className={`${base} bg-emerald-50 text-emerald-600`}>
        {t('certificate.statusAvailable')}
      </span>
    );
  }
  return (
    <span className={`${base} bg-slate-100 text-slate-500`}>
      {t('certificate.statusLocked')}
    </span>
  );
}

function statusChipClass(status) {
  const base =
    'shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold whitespace-nowrap';
  if (status === 'completed') return `${base} bg-emerald-100 text-emerald-700`;
  if (status === 'in_progress') return `${base} bg-amber-100 text-amber-700`;
  return `${base} bg-slate-100 text-slate-500`;
}

function progressBarClass(status) {
  if (status === 'completed') return 'h-full rounded-full bg-emerald-500';
  if (status === 'in_progress') return 'h-full rounded-full bg-amber-500';
  return 'h-full rounded-full bg-slate-300';
}
