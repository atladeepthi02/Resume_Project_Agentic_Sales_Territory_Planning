'use client';

import type { ExportResult, Plan } from '@/lib/api';
import { formatPlanStatus } from '@/lib/data';

type Props = {
  plan: Plan | null;
  status: 'idle' | 'loading' | 'done' | 'error';
  message: string | null;
  error: string | null;
  exportResult: ExportResult | null;
  onApprove: () => void;
  onReject: () => void;
  onExport: () => void;
};

export default function ApprovalPanel({
  plan,
  status,
  message,
  error,
  exportResult,
  onApprove,
  onReject,
  onExport,
}: Props) {
  const busy = status === 'loading';
  const canDecide = Boolean(plan) && plan?.status === 'PENDING_APPROVAL' && !busy;
  const approvedCount = plan?.items.filter((item) => item.status === 'APPROVED').length ?? 0;
  const canExport = approvedCount > 0 && !busy && Boolean(plan);

  return (
    <section
      id="approval"
      aria-labelledby="approval-heading"
      className="card scroll-mt-6 p-6"
    >
      <h2 id="approval-heading" className="section-title">
        Your approval
      </h2>
      <p className="section-subtitle">
        This is the safety gate. <strong>Nothing is contacted or changed</strong> until a sales
        manager approves. Only approved actions can be exported.
      </p>

      <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="text-sm font-semibold text-slate-900">
            {plan ? `Plan ${plan.plan_id}` : 'No plan yet'}
          </div>
          {plan && (
            <span className="chip border-blue-300 bg-white text-blue-700">
              {formatPlanStatus(plan.status)}
            </span>
          )}
        </div>
        <p className="mt-2 text-sm text-slate-600">
          {plan
            ? `${approvedCount} of ${plan.items.length} accounts approved · version ${plan.version}`
            : 'Build a plan to enable approval.'}
        </p>
        {plan?.approval && (
          <p className="mt-2 text-xs text-slate-500">
            Last decision: {plan.approval.decision} by {plan.approval.approver_id} on{' '}
            {new Date(plan.approval.timestamp).toLocaleString()}
          </p>
        )}
      </div>

      {status === 'done' && message && (
        <p className="mt-3 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">
          {message}
        </p>
      )}
      {status === 'error' && error && (
        <p className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
          {error}
        </p>
      )}

      <div className="mt-4 flex flex-wrap gap-3">
        <button type="button" onClick={onApprove} disabled={!canDecide} className="btn-success">
          Approve plan
        </button>
        <button type="button" onClick={onReject} disabled={!canDecide} className="btn-danger">
          Reject plan
        </button>
        <button type="button" onClick={onExport} disabled={!canExport} className="btn-secondary">
          Export approved actions (CSV)
        </button>
      </div>

      {!canDecide && plan && plan.status !== 'PENDING_APPROVAL' && (
        <p className="mt-3 text-xs text-slate-500">
          Approve and reject become available when the plan is waiting for approval. Build a new
          plan to start another review.
        </p>
      )}

      {exportResult && (
        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
          <div className="font-semibold text-slate-700">
            Export {exportResult.export_id}
          </div>
          <div className="mt-1">
            {exportResult.item_count} approved action(s) · {exportResult.format.toUpperCase()}
            {exportResult.duplicate ? ' · identical export already existed (no duplicates created)' : ''}
          </div>
        </div>
      )}

      <div className="mt-4 rounded-lg border border-slate-200 p-4">
        <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          What happens after you approve?
        </div>
        <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-slate-600">
          <li>Each approved account is marked <strong>Approved</strong> and recorded in the audit trail.</li>
          <li>You can then export approved actions as a CRM-ready CSV.</li>
          <li>Rejecting keeps everything as a draft; nothing is exported.</li>
        </ul>
      </div>
    </section>
  );
}
