// Session 11 Part B2 — PURE presentation helpers that turn the server-side
// /learning/completion payload into the certificate UI's display state.
//
// No React, no DOM, no hard-coded English/French strings (all UI strings live
// in src/i18n/*.json): these are provable in plain node (`npm run test:certificate`).
// The completion DECISION is never made here — it comes from the backend
// (certificate_service), which is the single source of truth.

/** The three certificate UI states, matching the backend's certificate_status. */
export const CERTIFICATE_STATUS = Object.freeze({
  locked: 'locked',
  available: 'available',
  issued: 'issued',
});

/**
 * Normalize the server's `certificate_status` to one of the three UI states.
 * Unknown/missing values fail SAFE to 'locked' — the UI must never show an
 * issue button or a certificate the backend would not grant (POST -> 403).
 */
export function certificateState(completion) {
  const status = completion && completion.certificate_status;
  if (status === CERTIFICATE_STATUS.available || status === CERTIFICATE_STATUS.issued) {
    return status;
  }
  return CERTIFICATE_STATUS.locked;
}

/**
 * Localized date label for `issued_at` ("12 September 2026" / "12 septembre 2026").
 * Returns '' for a missing or invalid value so the UI never renders
 * "Invalid Date".
 */
export function formatCertificateDate(iso, lang) {
  if (!iso) return '';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '';
  try {
    return date.toLocaleDateString(lang === 'fr' ? 'fr-FR' : 'en-GB', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return String(date.getFullYear());
  }
}