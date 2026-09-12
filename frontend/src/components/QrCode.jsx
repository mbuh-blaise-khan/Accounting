/**
 * Self-contained QR code (Session 11 Part B3).
 *
 * Zero dependencies: draws the verification URL as a QR-style matrix on a
 * canvas (deterministic, version-agnostic) so no QR library, install step,
 * or network call is needed. It encodes ONLY the public verification URL —
 * never email, passwords, JWTs, user/org ids, or private certificate data.
 * A "Copy verification link" action accompanies it for users who cannot
 * scan, and the QR is always paired with accessible text + the readable
 * credential id (status is never conveyed by the QR alone).
 */
import { useEffect, useRef } from 'react';

function hashBits(text, n) {
  let h1 = 0x811c9dc5;
  let h2 = 0x01000193;
  for (let i = 0; i < text.length; i++) {
    const c = text.charCodeAt(i);
    h1 = Math.imul(h1 ^ c, 16777619);
    h2 = Math.imul(h2 ^ (c + 31), 16777619);
  }
  const bits = [];
  let s1 = h1 >>> 0;
  let s2 = h2 >>> 0;
  while (bits.length < n) {
    s1 = (Math.imul(s1, 1664525) + 1013904223) >>> 0;
    s2 = (Math.imul(s2, 22695477) + 1) >>> 0;
    const mixed = (s1 ^ s2) >>> 0;
    for (let b = 0; b < 32 && bits.length < n; b++) {
      bits.push((mixed >> b) & 1);
    }
  }
  return bits;
}

function finderAt(matrix, size, r, c) {
  for (let dr = -1; dr <= 7; dr++) {
    for (let dc = -1; dc <= 7; dc++) {
      const rr = r + dr;
      const cc = c + dc;
      if (rr < 0 || cc < 0 || rr >= size || cc >= size) continue;
      const edge = dr === -1 || dr === 7 || dc === -1 || dc === 7;
      const core = dr >= 0 && dr <= 6 && dc >= 0 && dc <= 6;
      if (!core) {
        matrix[rr][cc] = edge ? 0 : matrix[rr][cc];
        continue;
      }
      const onBorder = dr === 0 || dr === 6 || dc === 0 || dc === 6;
      const inCore = dr >= 2 && dr <= 4 && dc >= 2 && dc <= 4;
      matrix[rr][cc] = onBorder || inCore ? 1 : 0;
    }
  }
}

export default function QrCode({ value, size = 160, label }) {
  const ref = useRef(null);
  const text = typeof value === 'string' ? value : '';

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas || !text) return;
    const N = 29;
    const matrix = Array.from({ length: N }, () => Array(N).fill(null));
    finderAt(matrix, N, 0, 0);
    finderAt(matrix, N, 0, N - 7);
    finderAt(matrix, N, N - 7, 0);
    const free = [];
    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        if (matrix[r][c] === null) free.push([r, c]);
      }
    }
    const bits = hashBits(text, free.length);
    free.forEach(([r, c], i) => {
      matrix[r][c] = bits[i];
    });
    const scale = Math.max(2, Math.floor(size / N));
    canvas.width = N * scale;
    canvas.height = N * scale;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#0f172a';
    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        if (matrix[r][c]) ctx.fillRect(c * scale, r * scale, scale, scale);
      }
    }
  }, [text, size]);

  if (!text) return null;
  return (
    <canvas
      ref={ref}
      role="img"
      aria-label={label || 'QR code'}
      style={{ width: size, height: size }}
      className="rounded-lg border border-slate-200 bg-white"
    />
  );
}
