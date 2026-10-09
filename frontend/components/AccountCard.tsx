import type { PlanItem } from '@/lib/api';
import { formatCompliance, formatItemStatus, formatPriority } from '@/lib/data';

const COMPLIANCE_CHIP: Record<string, string> = {
  passed: 'border-emerald-300 bg-emerald-50 text-emerald-700',
  warning: 'border-amber-300 bg-amber-50 text-amber-700',
  failed: 'border-red-300 bg-red-50 text-red-700',
};

function PriorityBadge({ score, level }: { score: number; level: string }) {
  return (
    <div className="text-right">
      <div className="text-2xl font-bold leading-none text-slate-900">{Math.round(score)}</div>
      <div className="mt-1 text-xs font-semibold text-slate-500">of 100</div>
      <div
        className={`mt-1 text-xs font-semibold ${
          level === 'HIGH'
            ? 'text-red-600'
            : level === 'MEDIUM'
              ? 'text-amber-600'
              : 'text-slate-500'
        }`}
      >
        {formatPriority(level)}
      </div>
    </div>
  );
}

export default function AccountCard({ item }: { item: PlanItem }) {
  const failingChecks = item.compliance.checks.filter((check) => check.status !== 'passed');

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start gap-4">
        <span
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-900 text-sm font-bold text-white"
          title={`Priority rank ${item.priority_rank} of the plan`}
        >
          {item.priority_rank}
        </span>

        <div className="min-w-0 flex-1">
          <h3 className="truncate text-base font-semibold text-slate-900">
            {item.account_name}
          </h3>
          <p className="text-xs text-slate-500">
            {item.account_id} · Owner: {item.owner || 'unassigned'}
          </p>
        </div>

        <PriorityBadge score={item.priority_score} level={item.priority_level} />
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <span className={`chip ${COMPLIANCE_CHIP[item.compliance.status]}`}>
          {formatCompliance(item.compliance.status)}
        </span>
        <span className="chip border-slate-300 bg-slate-50 text-slate-600">
          {formatItemStatus(item.status)}
        </span>
        {item.requires_approval && (
          <span className="chip border-blue-300 bg-blue-50 text-blue-700">
            Needs your approval
          </span>
        )}
        {item.stale && (
          <span className="chip border-amber-300 bg-amber-50 text-amber-700">
            ⚠ Data may be outdated
          </span>
        )}
      </div>

      <div className="mt-4 rounded-lg border border-blue-200 bg-blue-50 p-3">
        <div className="text-xs font-semibold uppercase tracking-wide text-blue-700">
          Do this next
        </div>
        <p className="mt-1 text-sm font-medium text-slate-900">{item.recommended_action}</p>
      </div>

      <dl className="mt-3 space-y-2 text-sm">
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Why this account
          </dt>
          <dd className="text-slate-700">{item.reason}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Opportunity
          </dt>
          <dd className="text-slate-700">{item.opportunity_summary}</dd>
        </div>
      </dl>

      {item.stale_reason && (
        <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
          {item.stale_reason}
        </p>
      )}

      {item.missing_data.length > 0 && (
        <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
          Some details are missing and were <strong>not</strong> guessed:{' '}
          {item.missing_data.join(', ')}.
        </p>
      )}

      {failingChecks.length > 0 && (
        <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3">
          <div className="text-xs font-semibold uppercase tracking-wide text-red-700">
            Check that needs attention
          </div>
          <ul className="mt-1 space-y-1 text-xs text-red-800">
            {failingChecks.map((check) => (
              <li key={check.check}>
                <span className="font-semibold capitalize">{check.check}:</span> {check.detail}
              </li>
            ))}
          </ul>
        </div>
      )}

      <details className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3">
        <summary className="cursor-pointer text-sm font-semibold text-slate-700">
          See the facts behind this ({item.facts.length} sources)
        </summary>
        <ul className="mt-3 space-y-2 text-xs text-slate-600">
          {item.facts.map((fact, index) => (
            <li key={`${fact.source_id}-${index}`} className="flex flex-col gap-0.5">
              <span>{fact.text}</span>
              <span className="font-mono text-[11px] text-slate-400">source: {fact.source_id}</span>
            </li>
          ))}
        </ul>
        <div className="mt-3 border-t border-slate-200 pt-2 text-[11px] text-slate-500">
          Citations: {item.citations.join(', ')}
        </div>
      </details>

      {item.factors.length > 0 && (
        <details className="mt-2 rounded-lg border border-slate-200 bg-slate-50 p-3">
          <summary className="cursor-pointer text-sm font-semibold text-slate-700">
            How the priority score was built
          </summary>
          <ul className="mt-3 list-disc space-y-1 pl-4 text-xs text-slate-600">
            {item.factors.map((factor) => (
              <li key={factor}>{factor}</li>
            ))}
          </ul>
        </details>
      )}
    </article>
  );
}
