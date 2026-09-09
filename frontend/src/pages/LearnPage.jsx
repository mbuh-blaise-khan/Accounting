import { useEffect, useState } from 'react';
import { useLanguage } from '../i18n/index.jsx';
import { fetchLessons } from '../services/api';

/**
 * Learn Mode — lesson list with per-lesson and overall progress.
 *
 * Lesson titles/summaries come from the backend in both languages; the active
 * UI language decides which variant is shown, so the existing language toggle
 * is respected without extra state here.
 */
export default function LearnPage({ onOpenLesson }) {
  const { t, lang } = useLanguage();
  const [lessons, setLessons] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let alive = true;
    setError('');
    setLessons(null);
    fetchLessons()
      .then((data) => {
        if (alive) setLessons(data);
      })
      .catch(() => {
        if (alive) setError(t('learn.loadError'));
      });
    return () => {
      alive = false;
    };
    // lang re-fetches so freshly toggled UI language re-renders server
    // content; `t` changes with lang and is intentionally excluded.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  if (error) {
    return <p className="p-4 text-sm text-red-600">{error}</p>;
  }
  if (!lessons) {
    return <p className="p-4 text-sm text-slate-500">{t('learn.loading')}</p>;
  }

  const completed = lessons.filter(
    (l) => l.progress && l.progress.status === 'completed'
  ).length;
  const overallPct = lessons.length
    ? Math.round((completed / lessons.length) * 100)
    : 0;
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
        <div className="flex items-center justify-between text-sm font-medium text-slate-700">
          <span>{t('learn.progressOverall')}</span>
          <span>
            {completed}/{lessons.length} · {overallPct}%
          </span>
        </div>
        <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-emerald-500 transition-all"
            style={{ width: `${overallPct}%` }}
          />
        </div>
      </div>

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
