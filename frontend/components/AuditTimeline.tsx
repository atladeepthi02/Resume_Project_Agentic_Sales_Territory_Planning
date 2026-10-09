import type { AuditEvent } from '@/lib/api';
import { formatAuditEvent } from '@/lib/data';

const DOT_STYLES: Record<string, string> = {
  PLAN_CREATED: 'bg-slate-400',
  PLAN_EDITED: 'bg-amber-500',
  PLAN_APPROVED: 'bg-emerald-600',
  PLAN_REJECTED: 'bg-red-500',
  PLAN_EXPORTED: 'bg-blue-600',
  PLAN_EXPORT_DUPLICATE: 'bg-blue-400',
};

export default function AuditTimeline({
  events,
  loading,
}: {
  events: AuditEvent[];
  loading: boolean;
}) {
  return (
    <section id="history" aria-labelledby="history-heading" className="card scroll-mt-6 p-6">
      <h2 id="history-heading" className="section-title">
        What has happened to this plan
      </h2>
      <p className="section-subtitle">
        Every change is recorded so a decision can be traced later: who did it, when, and on which
        version.
      </p>

      {loading && events.length === 0 && (
        <p className="mt-4 text-sm text-slate-500">Loading history…</p>
      )}
      {!loading && events.length === 0 && (
        <p className="mt-4 text-sm text-slate-500">No activity recorded yet.</p>
      )}

      {events.length > 0 && (
        <ol className="mt-5 space-y-4">
          {events.map((event) => (
            <li key={event.event_id} className="flex gap-3">
              <span
                aria-hidden
                className={`mt-1.5 h-3 w-3 shrink-0 rounded-full ${
                  DOT_STYLES[event.event_type] ?? 'bg-slate-400'
                }`}
              />
              <div className="min-w-0">
                <div className="text-sm font-semibold text-slate-900">
                  {formatAuditEvent(event.event_type)}
                </div>
                <div className="text-xs text-slate-500">
                  {event.actor} · {new Date(event.timestamp).toLocaleString()} · version{' '}
                  {event.plan_version}
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
