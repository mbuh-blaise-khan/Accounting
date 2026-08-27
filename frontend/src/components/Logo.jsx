// Kinxta Docu — original brand mark.
//
// A simple, original SVG icon evoking a documentation/ledger sheet with a
// completion checkmark, drawn with Tailwind palette classes (slate + blue).
// NOT an image asset and not copied from any brand. For a real product this is
// swappable without changing call sites: pass `image` (a URL/src to an <img>)
// and it renders that instead of the SVG mark, keeping the same wordmark.
import React from 'react'

export default function Logo({
  image,
  wordmark = 'Kinxta Docu',
  showWordmark = true,
  iconSize = 'h-7 w-7',
  className = '',
}) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      {image ? (
        <img
          src={image}
          alt={wordmark}
          className={`${iconSize} rounded object-contain`}
        />
      ) : (
        // Ledger-document + checkmark motif (original drawing).
        <svg
          viewBox="0 0 40 40"
          aria-hidden="true"
          className={iconSize}
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <rect
            x="4"
            y="4"
            width="32"
            height="32"
            rx="6"
            className="fill-blue-600"
          />
          {/* Document page with ledger lines */}
          <rect x="10" y="10" width="20" height="20" rx="3" className="fill-white" />
          <path d="M15 16h10" className="stroke-slate-300" strokeWidth="2" strokeLinecap="round" />
          <path d="M15 21h10" className="stroke-slate-300" strokeWidth="2" strokeLinecap="round" />
          <path d="M15 26h6" className="stroke-slate-300" strokeWidth="2" strokeLinecap="round" />
          {/* completion check inside the page corner */}
          <path
            d="M23 25.5l2.2 2.2 4-4.6"
            className="stroke-green-500"
            strokeWidth="2.4"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      )}
      {showWordmark && (
        <span className="text-base font-bold tracking-tight text-slate-900">
          {wordmark}
        </span>
      )}
    </span>
  )
}