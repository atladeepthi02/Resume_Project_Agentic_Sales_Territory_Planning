const NAV_LINKS = [
  { href: '#overview', label: 'Overview' },
  { href: '#accounts', label: 'Accounts' },
  { href: '#approval', label: 'Approval' },
  { href: '#history', label: 'History' },
  { href: '#glossary', label: 'Glossary' },
];

const STATUS_STYLES: Record<string, string> = {
  ok: 'border-emerald-300 bg-emerald-50 text-emerald-700',
  connecting: 'border-amber-300 bg-amber-50 text-amber-700',
  error: 'border-red-300 bg-red-50 text-red-700',
};

export default function Header({
  status,
  statusKind,
}: {
  status: string;
  statusKind: 'ok' | 'connecting' | 'error';
}) {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-start gap-3">
          <div
            aria-hidden
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-lg font-bold text-white"
          >
            ST
          </div>
          <div>
            <h1 className="text-lg font-bold leading-tight text-slate-900">
              Sales Territory Planning Assistant
            </h1>
            <p className="mt-1 max-w-2xl text-sm text-slate-600">
              See which accounts to work on first, <strong>why</strong> they matter, and{' '}
              <strong>what to do next</strong> — then approve the plan before anything reaches your
              CRM.
            </p>
          </div>
        </div>

        <div className="flex flex-col items-start gap-3 sm:flex-row sm:items-center">
          <nav aria-label="Page sections" className="flex flex-wrap gap-1">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
              >
                {link.label}
              </a>
            ))}
          </nav>
          <span className={`chip ${STATUS_STYLES[statusKind]}`} title="Backend connection status">
            <span
              aria-hidden
              className="h-2 w-2 rounded-full bg-current"
            />
            {status}
          </span>
        </div>
      </div>
    </header>
  );
}
