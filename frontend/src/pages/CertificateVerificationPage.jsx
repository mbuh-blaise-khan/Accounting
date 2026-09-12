import { useEffect, useState } from 'react';
import { certificateVerificationUrl, fetchPublicCertificate } from '../services/api.js';
import { useLanguage } from '../i18n/index.jsx';
import { formatCertificateDate, isCredentialIdShape, verificationState } from '../utils/certificatePresentation.js';
import Logo from '../components/Logo.jsx';
import LanguageToggle from '../components/LanguageToggle.jsx';
import QrCode from '../components/QrCode.jsx';

export default function CertificateVerificationPage({ credentialId, onHome }) {
  const { t, lang } = useLanguage();
  const [phase, setPhase] = useState('loading');
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!isCredentialIdShape(credentialId)) {
        if (!cancelled) setPhase('notfound');
        return;
      }
      setPhase('loading');
      setResult(null);
      try {
        const data = await fetchPublicCertificate(credentialId.trim());
        if (cancelled) return;
        setResult(data);
        setPhase(verificationState(data) === 'valid' ? 'valid' : 'revoked');
      } catch (err) {
        if (cancelled) return;
        const msg = String(err && err.message ? err.message : '');
        if (/404|not found/i.test(msg) || /Invalid credential/i.test(msg)) {
          setPhase('notfound');
        } else {
          setPhase('error');
        }
      }
    }
    load();
    return () => { cancelled = true; };
  }, [credentialId]);

  const verifyUrl = result && result.credential_id
    ? certificateVerificationUrl(result.credential_id)
    : null;

  async function handleCopy() {
    if (!verifyUrl) return;
    try {
      await navigator.clipboard.writeText(verifyUrl);
    } catch {
      const el = document.getElementById('verify-url-input');
      if (el) { el.focus(); el.select(); }
    }
    setCopied(true);
  }

  function handlePrint() {
    window.print();
  }

  return (
    <div className="min-h-screen bg-slate-50 cert-print-area">
      <header className="no-print border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
          <button type="button" onClick={onHome} className="flex items-center gap-2">
            <Logo wordmark={t('app.title')} />
          </button>
          <LanguageToggle />
        </div>
      </header>

      <main className="mx-auto w-full max-w-3xl px-4 py-8">
        <h1 className="mb-6 text-2xl font-bold text-slate-900">{t('verify.title')}</h1>

        {phase === 'loading' ? (
          <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
            <p className="text-slate-500">{t('verify.loading')}</p>
          </div>
        ) : null}

        {phase === 'valid' && result ? (
          <div className="space-y-6">
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
              <div className="flex items-start gap-3">
                <span className="text-2xl" aria-hidden="true">✓</span>
                <div>
                  <p className="font-semibold text-emerald-800">{t('verify.validTitle')}</p>
                  <p className="mt-1 text-sm text-emerald-700">{t('verify.validMessage')}</p>
                </div>
              </div>
            </div>
            <div className="cert-sheet relative overflow-hidden rounded-lg border-2 border-amber-300 bg-gradient-to-b from-amber-50 via-white to-white p-6 sm:p-8 shadow-sm">
              <div className="pointer-events-none absolute inset-2 rounded-md border border-amber-200" aria-hidden="true" />
              <div className="relative text-center">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-amber-700">{result.issuer}</p>
                <h2 className="mt-3 text-xl font-bold text-slate-900 sm:text-2xl">{result.wording}</h2>
                <p className="mx-auto mt-2 h-px w-24 bg-amber-300" aria-hidden="true" />
                <p className="mt-5 text-sm text-slate-500">{t('verify.recipient')}</p>
                <p className="mt-0.5 text-lg font-semibold text-slate-900">{result.recipient_name || '—'}</p>
                <p className="mt-4 text-sm text-slate-500">{t('certificate.courseLabel')}</p>
                <p className="font-semibold text-slate-900">{result.course_title}</p>
                <dl className="mt-5 flex flex-wrap justify-center gap-8 text-xs">
                  <div>
                    <dt className="text-slate-400">{t('verify.issuedOn')}</dt>
                    <dd className="mt-0.5 font-semibold text-slate-700">{formatCertificateDate(result.issued_at, lang)}</dd>
                  </div>
                  <div>
                    <dt className="text-slate-400">{t('verify.completedOn')}</dt>
                    <dd className="mt-0.5 font-semibold text-slate-700">{formatCertificateDate(result.completed_at, lang)}</dd>
                  </div>
                  <div>
                    <dt className="text-slate-400">{t('verify.credentialId')}</dt>
                    <dd className="mt-0.5 font-mono font-semibold text-slate-700">{result.credential_id}</dd>
                  </div>
                </dl>
                <p className="mt-5 text-xs text-slate-500">{t('verify.courseScopeLabel')}</p>
                <p className="mx-auto mt-1 max-w-md text-xs text-slate-600">{t('verify.courseScope')}</p>
                {verifyUrl ? (
                  <div className="no-print mt-6 flex flex-col items-center gap-3 border-t border-amber-200 pt-5">
                    <QrCode value={verifyUrl} label={t('verify.scanToVerify')} />
                    <p className="text-xs text-slate-500">{t('verify.scanToVerify')}</p>
                    <div className="flex w-full max-w-md items-center gap-2">
                      <input id="verify-url-input" type="text" readOnly value={verifyUrl}
                        aria-label={t('verify.copyLink')}
                        className="min-w-0 flex-1 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 font-mono text-[11px] text-slate-600" />
                      <button type="button" onClick={handleCopy} aria-live="polite"
                        className="shrink-0 rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-100">
                        {copied ? t('verify.linkCopied') : t('verify.copyLink')}
                      </button>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
            <div className="no-print flex flex-wrap items-center justify-center gap-2">
              <button type="button" onClick={handlePrint} className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700">
                {t('verify.print')}
              </button>
              <button type="button" onClick={onHome} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
                {t('verify.home')}
              </button>
            </div>
          </div>
        ) : null}

        {phase === 'revoked' && result ? (
          <div className="space-y-6">
            <div className="rounded-xl border border-red-300 bg-red-50 p-5">
              <div className="flex items-start gap-3">
                <span className="text-2xl" aria-hidden="true">✗</span>
                <div>
                  <p className="font-semibold text-red-800">{t('verify.revokedTitle')}</p>
                  <p className="mt-1 text-sm text-red-700">{t('verify.revokedMessage')}</p>
                </div>
              </div>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900">{result.wording}</h2>
              <dl className="mt-4 space-y-2 text-sm">
                <div className="flex justify-between gap-4">
                  <dt className="text-slate-500">{t('verify.recipient')}</dt>
                  <dd className="font-semibold text-slate-800">{result.recipient_name || '—'}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-slate-500">{t('verify.credentialId')}</dt>
                  <dd className="font-mono font-semibold text-slate-800">{result.credential_id}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-slate-500">{t('verify.issuedOn')}</dt>
                  <dd className="font-semibold text-slate-800">{formatCertificateDate(result.issued_at, lang)}</dd>
                </div>
              </dl>
              <p className="mt-4 rounded-lg bg-red-50 p-3 text-xs font-semibold text-red-700">
                {t('verify.revokedMessage')}
              </p>
            </div>
            <div className="no-print flex flex-wrap items-center justify-center gap-2">
              <button type="button" onClick={onHome} className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700">
                {t('verify.home')}
              </button>
            </div>
          </div>
        ) : null}

        {phase === 'notfound' ? (
          <div className="space-y-6">
            <div className="rounded-xl border border-slate-300 bg-slate-50 p-8 text-center shadow-sm">
              <span className="mx-auto block text-4xl text-slate-400" aria-hidden="true">🔍</span>
              <h2 className="mt-4 text-lg font-bold text-slate-900">{t('verify.notFoundTitle')}</h2>
              <p className="mx-auto mt-2 max-w-md text-sm text-slate-600">{t('verify.notFoundMessage')}</p>
            </div>
            <div className="no-print flex flex-wrap items-center justify-center gap-2">
              <button type="button" onClick={onHome} className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700">
                {t('verify.home')}
              </button>
            </div>
          </div>
        ) : null}

        {phase === 'error' ? (
          <div className="space-y-6">
            <div className="rounded-xl border border-amber-300 bg-amber-50 p-8 text-center shadow-sm">
              <span className="mx-auto block text-4xl text-amber-500" aria-hidden="true">!</span>
              <h2 className="mt-4 text-lg font-bold text-slate-900">{t('verify.errorTitle')}</h2>
              <p className="mx-auto mt-2 max-w-md text-sm text-slate-600">{t('verify.errorMessage')}</p>
            </div>
            <div className="no-print flex flex-wrap items-center justify-center gap-2">
              <button type="button" onClick={() => window.location.reload()} className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700">
                {t('verify.retry')}
              </button>
              <button type="button" onClick={onHome} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
                {t('verify.home')}
              </button>
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );
}
