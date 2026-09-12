import { useAuth } from '../context/AuthContext.jsx';
import { useLanguage } from '../i18n/index.jsx';
import { formatCertificateDate } from '../utils/certificatePresentation';

/**
 * Polished ON-SCREEN certificate preview (Session 11 Part B2).
 *
 * Presentation FOUNDATION only: no PDF export, no QR code, no public
 * verification URL, no badges/blockchain — those belong to later bounded
 * sessions. The wording comes straight from the backend Certificate row
 * (certificate_service.CERTIFICATE_WORDING) so the exact string
 * "Kinxta Docu Certificate of Completion" is never hard-coded in the UI —
 * the backend stays the single source of truth.
 */
export default function CertificateCard({ certificate }) {
  const { t, lang } = useLanguage();
  const { user } = useAuth();
  if (!certificate) return null;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="relative overflow-hidden rounded-lg border-2 border-amber-300 bg-gradient-to-b from-amber-50 via-white to-white p-6 sm:p-8">
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

          <dl className="mt-5 flex justify-center gap-8 text-xs">
            <div>
              <dt className="text-slate-400">{t('certificate.certId')}</dt>
              <dd className="mt-0.5 font-mono font-semibold text-slate-700">
                #{certificate.id}
              </dd>
            </div>
            <div>
              <dt className="text-slate-400">{t('certificate.course')}</dt>
              <dd className="mt-0.5 font-mono font-semibold text-slate-700">
                {certificate.course_slug}
              </dd>
            </div>
          </dl>
        </div>
      </div>
      <p className="mt-3 text-center text-[11px] text-slate-400">
        {t('certificate.previewNote')}
      </p>
    </div>
  );
}