/**
 * Callout — a contextual info/warning/success banner.
 *
 * Variants:
 *   - info:    blue, for general guidance (default)
 *   - warning: amber, for cautions
 *   - success: green, for confirmations
 *
 * Usage:
 *   <Callout variant="info" title="Optional title">
 *     Body content (any JSX).
 *   </Callout>
 */
const STYLES = {
  info: {
    container: 'border-blue-200 bg-blue-50',
    title: 'text-blue-700',
    body: 'text-blue-700',
    icon: 'ℹ️',
  },
  warning: {
    container: 'border-amber-200 bg-amber-50',
    title: 'text-amber-700',
    body: 'text-amber-700',
    icon: '⚠️',
  },
  success: {
    container: 'border-emerald-200 bg-emerald-50',
    title: 'text-emerald-700',
    body: 'text-emerald-700',
    icon: '✅',
  },
};

export default function Callout({ variant = 'info', title, children }) {
  const v = STYLES[variant] || STYLES.info;
  return (
    <div className={`rounded-xl border-2 ${v.container} p-4`}>
      <div className="flex items-start gap-3">
        <span className="text-lg leading-none" aria-hidden="true">
          {v.icon}
        </span>
        <div className="min-w-0">
          {title && (
            <p className={`mb-1 text-sm font-semibold ${v.title}`}>{title}</p>
          )}
          <div className={`text-sm leading-relaxed ${v.body}`}>{children}</div>
        </div>
      </div>
    </div>
  );
}