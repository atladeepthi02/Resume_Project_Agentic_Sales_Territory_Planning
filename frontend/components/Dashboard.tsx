'use client';

import { useCallback, useEffect, useState } from 'react';
import ApprovalPanel from '@/components/ApprovalPanel';
import AuditTimeline from '@/components/AuditTimeline';
import Glossary from '@/components/Glossary';
import Header from '@/components/Header';
import HowItWorks, { type StepState } from '@/components/HowItWorks';
import MetricsSection from '@/components/MetricsSection';
import PlanItemsPanel from '@/components/PlanItemsPanel';
import PlanSummary from '@/components/PlanSummary';
import type { Metric } from '@/lib/data';
import {
  approvePlan,
  createPlan,
  DEFAULT_TERRITORY_ID,
  DEFAULT_USER_ID,
  exportPlan,
  getAudit,
  getHealth,
  getMetrics,
  rejectPlan,
  type AuditEvent,
  type ExportResult,
  type Health,
  type Metrics,
  type Plan,
} from '@/lib/api';

type LoadState = 'loading' | 'ready' | 'error';

type ActionState = {
  status: 'idle' | 'loading' | 'done' | 'error';
  message: string | null;
  error: string | null;
};

function computeStepStates(plan: Plan | null, exported: boolean): Record<string, StepState> {
  if (!plan) {
    return { build: 'active', review: 'todo', approve: 'todo', export: 'todo' };
  }
  if (exported || plan.status === 'EXPORTED') {
    return { build: 'done', review: 'done', approve: 'done', export: 'done' };
  }
  if (plan.status === 'APPROVED') {
    return { build: 'done', review: 'done', approve: 'done', export: 'active' };
  }
  if (plan.status === 'REJECTED') {
    return { build: 'done', review: 'done', approve: 'done', export: 'todo' };
  }
  return { build: 'done', review: 'active', approve: 'todo', export: 'todo' };
}

export default function Dashboard() {
  const [health, setHealth] = useState<Health | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [state, setState] = useState<LoadState>('loading');
  const [error, setError] = useState<string | null>(null);
  const [action, setAction] = useState<ActionState>({
    status: 'idle',
    message: null,
    error: null,
  });
  const [exportResult, setExportResult] = useState<ExportResult | null>(null);

  const refreshAudit = useCallback(async (planId: string) => {
    try {
      const trail = await getAudit(planId);
      setEvents(trail.events);
    } catch {
      setEvents([]);
    }
  }, []);

  const loadDashboard = useCallback(async () => {
    setState('loading');
    setError(null);
    setAction({ status: 'idle', message: null, error: null });
    setExportResult(null);
    try {
      const [healthData, metricsData, planData] = await Promise.all([
        getHealth(),
        getMetrics(),
        createPlan(DEFAULT_TERRITORY_ID, DEFAULT_USER_ID),
      ]);
      setHealth(healthData);
      setMetrics(metricsData);
      setPlan(planData);
      await refreshAudit(planData.plan_id);
      setState('ready');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      setState('error');
    }
  }, [refreshAudit]);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const handleApprove = useCallback(async () => {
    if (!plan) return;
    setAction({ status: 'loading', message: null, error: null });
    try {
      const updated = await approvePlan(plan.plan_id, DEFAULT_USER_ID);
      setPlan(updated);
      await refreshAudit(plan.plan_id);
      setAction({ status: 'done', message: 'Plan approved. You can now export the actions.', error: null });
    } catch (err) {
      setAction({
        status: 'error',
        message: null,
        error: err instanceof Error ? err.message : 'Failed to approve plan',
      });
    }
  }, [plan, refreshAudit]);

  const handleReject = useCallback(async () => {
    if (!plan) return;
    setAction({ status: 'loading', message: null, error: null });
    try {
      const updated = await rejectPlan(plan.plan_id, DEFAULT_USER_ID, 'Rejected by manager.');
      setPlan(updated);
      await refreshAudit(plan.plan_id);
      setAction({ status: 'done', message: 'Plan rejected. Nothing will be exported.', error: null });
    } catch (err) {
      setAction({
        status: 'error',
        message: null,
        error: err instanceof Error ? err.message : 'Failed to reject plan',
      });
    }
  }, [plan, refreshAudit]);

  const handleExport = useCallback(async () => {
    if (!plan) return;
    setAction({ status: 'loading', message: null, error: null });
    try {
      const result = await exportPlan(plan.plan_id, 'csv');
      setExportResult(result);
      await refreshAudit(plan.plan_id);
      setAction({
        status: 'done',
        message: result.duplicate
          ? 'This exact export already existed, so no duplicates were created.'
          : 'Export ready — the CSV file has downloaded.',
        error: null,
      });
      const blob = new Blob([result.content], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${result.plan_id}-v${result.plan_version}.csv`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setAction({
        status: 'error',
        message: null,
        error: err instanceof Error ? err.message : 'Failed to export plan',
      });
    }
  }, [plan, refreshAudit]);

  const liveMetrics: Metric[] = metrics
    ? [
        {
          label: 'Territories',
          value: String(metrics.total_territories),
          hint: 'in the portfolio',
          help: 'Number of territories the portfolio covers.',
        },
        {
          label: 'Accounts',
          value: String(metrics.total_accounts),
          hint: 'total customers',
          help: 'Customer accounts across all territories.',
        },
        {
          label: 'High priority',
          value: String(metrics.high_priority_accounts),
          hint: 'score as high priority',
          help: 'Accounts the ranking rules place in the high-priority band.',
        },
        {
          label: 'Open opportunities',
          value: String(metrics.open_opportunities),
          hint: `$${(metrics.pipeline_value / 1_000_000).toFixed(1)}M in play`,
          help: 'Deals still open, with their combined pipeline value.',
        },
      ]
    : [];

  const statusKind: 'ok' | 'connecting' | 'error' =
    state === 'error' ? 'error' : health ? 'ok' : 'connecting';
  const statusLabel =
    state === 'error'
      ? 'Backend unavailable'
      : health
        ? `Connected · ${health.environment}`
        : 'Connecting…';

  return (
    <main className="min-h-screen bg-slate-50 pb-16">
      <Header status={statusLabel} statusKind={statusKind} />

      <div className="mx-auto max-w-6xl space-y-8 px-6 py-8">
        <HowItWorks stepStates={computeStepStates(plan, Boolean(exportResult))} />

        <PlanSummary
          plan={plan}
          loading={state === 'loading'}
          error={state === 'error' ? error : null}
          onBuild={() => {
            void loadDashboard();
          }}
        />

        <MetricsSection metrics={liveMetrics} loading={state === 'loading'} />

        <PlanItemsPanel items={plan?.items ?? []} loading={state === 'loading'} />

        <ApprovalPanel
          plan={plan}
          status={action.status}
          message={action.message}
          error={action.error}
          exportResult={exportResult}
          onApprove={() => {
            void handleApprove();
          }}
          onReject={() => {
            void handleReject();
          }}
          onExport={() => {
            void handleExport();
          }}
        />

        <AuditTimeline events={events} loading={state === 'loading'} />

        <Glossary />

        <footer className="border-t border-slate-200 pt-6 text-center text-xs text-slate-500">
          Decision-support only. Recommendations are grounded in your records, and no action is taken
          without a manager&apos;s approval.
        </footer>
      </div>
    </main>
  );
}
