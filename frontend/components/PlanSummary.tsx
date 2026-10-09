import type { Plan } from '@/lib/api';
import { formatPlanStatus } from '@/lib/data';

function Stat({
  label,
  value,
  tone = 'neutral',
}: {
  label: string;
  value: string;
  tone?: 'neutral' | 'good' | 'warn' | 'bad';
}) {
  const toneStyles = {
    neutral: 'text-slate-900',
    good: 'text-emerald-700',
    warn: 'text-amber-700',
    bad: 'text-red-700',
  } as const;

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`mt-1 text-lg font-bold ${toneStyles[tone]}`}>{value}</div>
    </div>
  );
}

export default function PlanSummary({
  plan,
  loading,
  error,
  onBuild,
}: {
  plan: Plan | null;
  loading: boolean;
  error: string | null;
  onBuild: () => void;
}) {
  const needsAttention =
    plan?.items.filter((item) => item.compliance.status !== 'passed' || item.stale).length ?? 0;

  return (
    <section id="overview" aria-labelledby="overview-heading" className="card scroll-mt-6 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 id="overview-heading" className="section-title">
            Territory overview
          </h2>
          <p className="section-subtitle">
            A short, plain-language summary of the current plan and what it means.
          </p>
        </div>
        <button type="button" onClick={onBuild} disabled={loading} className="btn-primary">
          {loading ? 'Building…' : plan ? 'Build a fresh plan' : 'Build the plan'}
        </button>
      </div>

      {error && (
        <p className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
          Could not reach the backend: {error}. Check that the API is running at the configured URL.
        </p>
      )}

      {!plan && !error && (
        <p className="mt-4 text-sm text-slate-600">
          {loading
            ? 'Gathering accounts, opportunities and service issues…'
            : 'No plan yet. Click “Build the plan” to rank your territory accounts.'}
        </p>
      )}

      {plan && (
        <>
          <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm font-semibold text-slate-900">
                Territory {plan.territory_id}
              </span>
              <span className="chip border-slate-300 bg-slate-50 text-slate-600">
                {formatPlanStatus(plan.status)}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-600">
              {plan.items.length} account{plan.items.length === 1 ? '' : 's'} ranked from highest to
              lowest priority. {needsAttention > 0
                ? `${needsAttention} need a closer look before you approve.`
                : 'All checks passed, so you can approve with confidence.'}
              {plan.stale_data
                ? ' Some source data is older than the freshness limit and is flagged on the affected cards.'
                : ''}
            </p>
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Accounts ranked" value={String(plan.items.length)} />
            <Stat
              label="Need review"
              value={String(needsAttention)}
              tone={needsAttention > 0 ? 'warn' : 'good'}
            />
            <Stat
              label="Compliance"
              value={plan.validation.status === 'passed' ? 'Passed' : 'Needs review'}
              tone={
                plan.validation.status === 'passed'
                  ? 'good'
                  : plan.validation.status === 'failed'
                    ? 'bad'
                    : 'warn'
              }
            />
            <Stat
              label="Data freshness"
              value={plan.stale_data ? 'Some data stale' : 'Up to date'}
              tone={plan.stale_data ? 'warn' : 'good'}
            />
          </div>
        </>
      )}
    </section>
  );
}
