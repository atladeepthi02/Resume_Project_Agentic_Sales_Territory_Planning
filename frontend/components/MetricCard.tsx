import type { Metric } from '@/lib/data';

export default function MetricCard({ metric }: { metric: Metric }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between gap-2">
        <div className="text-sm font-medium text-slate-600">{metric.label}</div>
        <span
          title={metric.help}
          aria-label={metric.help}
          className="flex h-5 w-5 cursor-help items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-500"
        >
          ?
        </span>
      </div>
      <div className="mt-3 text-3xl font-bold text-slate-900">{metric.value}</div>
      <div className="mt-1 text-xs text-slate-500">{metric.hint}</div>
    </div>
  );
}
