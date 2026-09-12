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

/**
 * Credential-ID validation for the public verification page (Session 11
 * Part B3). Malformed ids must render a safe not-found state WITHOUT a
 * network call: ours always start with 'kinxta-' and contain only URL-safe
 * characters (we never accept the sequential integer PK).
 */
export function isCredentialIdShape(id) {
  if (!id || typeof id !== 'string') return false;
  const trimmed = id.trim();
  if (trimmed.length < 10 || trimmed.length > 120) return false;
  return /^kinxta-[A-Za-z0-9_-]+$/.test(trimmed);
}

/**
 * Backend-status normalization for the public verification page: any stored
 * status other than 'valid' renders as 'revoked' (fail closed — a revoked
 * certificate must never look valid because its credential still exists).
 */
export function verificationState(result) {
  if (!result) return 'missing';
  if (result.status === 'revoked') return 'revoked';
  if (result.status === 'valid') return 'valid';
  return 'revoked';
}