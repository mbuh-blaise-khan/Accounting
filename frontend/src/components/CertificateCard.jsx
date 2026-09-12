import { useState } from 'react';
import { useAuth } from '../context/AuthContext.jsx';
import { useLanguage } from '../i18n/index.jsx';
import { certificateVerificationUrl } from '../services/api.js';
import { formatCertificateDate } from '../utils/certificatePresentation';
import QrCode from './QrCode.jsx';

/**
 * Polished ON-SCREEN certificate (Session 11 Part B2 + B3).
 *
 * The wording comes straight from the backend Certificate row
 * (certificate_service.CERTIFICATE_WORDING) so the exact string
 * "Kinxta Docu Certificate of Completion" is never hard-coded in the UI —
 * the backend stays the single source of truth.
 *
 * Session 11 Part B3 additions: verification-link display + copy, a
 * dependency-free QR code of that same public URL, and a print action
 * (window.print(); @media print hides header/nav/.no-print so ONLY the
 * certificate sheet prints — browser "Save as PDF" via the print dialog).
 * QR/copy/print render ONLY when a real issued certificate exists.
 */
export default function CertificateCard({ certificate }) {
  const { t, lang } = useLanguage();
  const { user } = useAuth();
  const [copied, setCopied] = useState(false);
  if (!certificate) return null;

  const credentialId = certificate.credential_id || null;
  const verifyUrl = credentialId ? certificateVerificationUrl(credentialId) : null;

  async function handleCopy() {
    if (!verifyUrl) return;
    try {
      await navigator.clipboard.writeText(verifyUrl);
    } catch {
      // Fallback: select the visible read-only input so the user can copy it.
      const el = document.getElementById('cert-verify-url');
      if (el) {
        el.focus();
        el.select();
      }
    }
    setCopied(true);
  }

  function handlePrint() {
    window.print();
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="cert-sheet relative overflow-hidden rounded-lg border-2 border-amber-300 bg-gradient-to-b from-amber-50 via-white to-white p-6 sm:p-8">
        {/* Decorative inner frame */}
        <div className="pointer-events-none absolute inset-2 rounded-md border border-amber-200" aria-hidden="true" />
        <div className="relative text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-amber-700">
            {t('app.title')}
          </p>
          <h3 className="mt-3 text-xl font-bold text-slate-900 sm:text-2xl">
            {certificate.wording}
          </h3>
          <p className="mx-auto mt-2 h-px w-24 bg-amber-300" aria-hidden="true" />

          <p className="mt-5 text-sm text-slate-500">{t('certificate.issuedTo')}</p>
          <p className="mt-0.5 text-lg font-semibold text-slate-900">
            {user?.display_name || '—'}
          </p>

          <p className="mt-4 text-sm text-slate-500">{t('certificate.courseLabel')}</p>
          <p className="font-semibold text-slate-900">{t('certificate.courseName')}</p>

          <p className="mt-4 text-sm text-slate-500">
            {t('certificate.issuedOn')}{' '}
            <span className="font-semibold text-slate-800">
              {formatCertificateDate(certificate.issued_at, lang)}
            </span>
          </p>

          <dl className="mt-5 flex flex-wrap justify-center gap-8 text-xs">
            <div>
              <dt className="text-slate-400">{t('certificate.certId')}</dt>
              <dd className="mt-0.5 font-mono font-semibold text-slate-700">
                {credentialId ? credentialId : `#${certificate.id}`}
              </dd>
            </div>
            <div>
              <dt className="text-slate-400">{t('certificate.course')}</dt>
              <dd className="mt-0.5 font-mono font-semibold text-slate-700">
                {certificate.course_slug}
              </dd>
            </div>
          </dl>

          {verifyUrl ? (
            <div className="no-print mt-6 flex flex-col items-center gap-3 border-t border-amber-200 pt-5">
              <QrCode value={verifyUrl} label={t('certificate.scanToVerify')} />
              <p className="text-xs text-slate-500">{t('certificate.scanToVerify')}</p>
              <div className="flex w-full max-w-md items-center gap-2">
                <input
                  id="cert-verify-url"
                  type="text"
                  readOnly
                  value={verifyUrl}
                  aria-label={t('certificate.verificationLink')}
                  className="min-w-0 flex-1 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 font-mono text-[11px] text-slate-600"
                />
                <button
                  type="button"
                  onClick={handleCopy}
                  aria-live="polite"
                  className="shrink-0 rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-100"
                >
                  {copied ? t('certificate.linkCopied') : t('certificate.copyLink')}
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </div>
      <div className="no-print mt-3 flex flex-wrap items-center justify-center gap-2">
        <button
          type="button"
          onClick={handlePrint}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
        >
          {t('certificate.print')}
        </button>
        {verifyUrl ? (
          <a
            href={verifyUrl}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
          >
            {t('certificate.openVerification')}
          </a>
        ) : null}
      </div>
      <p className="no-print mt-3 text-center text-[11px] text-slate-400">
        {t('certificate.printHint')}
      </p>
      <p className="mt-1 text-center text-[11px] text-slate-400">
        {t('certificate.previewNote')}
      </p>
    </div>
  );
}