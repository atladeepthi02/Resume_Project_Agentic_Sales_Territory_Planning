const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export type Health = {
  status: string;
  environment: string;
  version?: string;
};

export type Metrics = {
  total_territories: number;
  total_accounts: number;
  high_priority_accounts: number;
  open_opportunities: number;
  pipeline_value: number;
  status: string;
};

export type Territory = {
  territory_id?: string;
  name?: string;
  owner?: string;
  capacity?: number;
  rules?: string[];
};

export type Account = {
  account_id: string;
  territory_id: string;
  name: string;
  industry: string;
  revenue: number;
  growth: number;
  health: string;
  owner?: string;
};

export type PrioritizationResult = {
  account_id: string;
  priority_score: number;
  priority_level: string;
  drivers: string[];
  risks: string[];
  evidence: string[];
};

export type TerritoryPlan = {
  territory_id: string;
  summary: string;
  priority_accounts: string[];
  recommended_actions: string[];
  coverage_gaps: string[];
  risks: string[];
  sources: string[];
};

export type ProposedAction = {
  action_type: string;
  account_id: string;
  reason: string;
  status: string;
};

export type WorkflowResult = {
  workflow_id: string;
  territory_id: string | null;
  final_response: string;
  territory_data: Territory;
  account_data: { accounts: Account[] };
  territory_plan: TerritoryPlan;
  prioritization_results: PrioritizationResult[];
  proposed_actions: ProposedAction[];
};

// -- Plan-centric API (PRD section 10) --------------------------------------

export type ComplianceStatus = 'passed' | 'failed' | 'warning';

export type ComplianceCheck = {
  check: string;
  status: ComplianceStatus;
  detail: string;
};

export type ComplianceResult = {
  status: ComplianceStatus;
  checks: ComplianceCheck[];
};

export type PlanItemFact = {
  text: string;
  source_id: string;
};

export type PlanItem = {
  item_id: string;
  account_id: string;
  account_name: string;
  owner: string;
  priority_rank: number;
  priority_score: number;
  priority_level: string;
  facts: PlanItemFact[];
  opportunity_summary: string;
  recommended_action: string;
  reason: string;
  citations: string[];
  requires_approval: boolean;
  compliance: ComplianceResult;
  factors: string[];
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  stale: boolean;
  stale_reason: string | null;
  missing_data: string[];
};

export type ApprovalRecord = {
  approver_id: string;
  decision: 'APPROVED' | 'REJECTED';
  timestamp: string;
  plan_version: number;
  item_ids: string[];
  reason: string | null;
};

export type Plan = {
  plan_id: string;
  territory_id: string;
  user_id: string;
  status: 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'EXPORTED';
  version: number;
  time_window: string;
  created_at: string;
  updated_at: string;
  items: PlanItem[];
  validation: ComplianceResult;
  approval: ApprovalRecord | null;
  stale_data: boolean;
  excluded_account_ids: string[];
  scoring_rules_version: string | null;
};

export type AuditEvent = {
  event_id: string;
  event_type: string;
  actor: string;
  timestamp: string;
  plan_version: number;
  details: Record<string, unknown>;
};

export type AuditTrail = {
  plan_id: string;
  events: AuditEvent[];
};

export type ExportResult = {
  export_id: string;
  plan_id: string;
  plan_version: number;
  format: 'csv' | 'json';
  item_count: number;
  checksum: string;
  duplicate: boolean;
  created_at: string;
  content: string;
};

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`GET ${path} failed (${response.status})`);
  }
  return (await response.json()) as T;
}

async function sendJson<T>(
  method: 'POST' | 'PATCH',
  path: string,
  body: unknown,
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`${method} ${path} failed (${response.status}) ${detail}`);
  }
  return (await response.json()) as T;
}

export const PLAN_QUERY =
  'Create a territory plan for Territory T001 and identify the top accounts.';

export const DEFAULT_TERRITORY_ID = 'T001';
export const DEFAULT_USER_ID = 'mgr-001';

export function getHealth() {
  return getJson<Health>('/health');
}

export function getMetrics() {
  return getJson<Metrics>('/api/metrics');
}

export function createPlan(
  territoryId: string = DEFAULT_TERRITORY_ID,
  userId: string = DEFAULT_USER_ID,
) {
  return sendJson<Plan>('POST', '/v1/plans', {
    territory_id: territoryId,
    user_id: userId,
  });
}

export function getPlan(planId: string) {
  return getJson<Plan>(`/v1/plans/${encodeURIComponent(planId)}`);
}

export function approvePlan(
  planId: string,
  userId: string = DEFAULT_USER_ID,
  itemIds?: string[],
) {
  return sendJson<Plan>('POST', `/v1/plans/${encodeURIComponent(planId)}/approve`, {
    user_id: userId,
    item_ids: itemIds,
  });
}

export function rejectPlan(
  planId: string,
  userId: string = DEFAULT_USER_ID,
  reason = 'Rejected by reviewer.',
) {
  return sendJson<Plan>('POST', `/v1/plans/${encodeURIComponent(planId)}/reject`, {
    user_id: userId,
    reason,
  });
}

export function editPlanItem(
  planId: string,
  userId: string,
  itemId: string,
  patch: { recommended_action?: string; reason?: string },
) {
  return sendJson<Plan>('PATCH', `/v1/plans/${encodeURIComponent(planId)}`, {
    user_id: userId,
    items: [{ item_id: itemId, ...patch }],
  });
}

export async function exportPlan(planId: string, format: 'csv' | 'json' = 'csv') {
  const response = await fetch(
    `${API_BASE}/v1/plans/${encodeURIComponent(planId)}/export?format=${format}`,
    { method: 'POST', headers: { 'Idempotency-Key': `${planId}-${format}` } },
  );
  if (!response.ok) {
    throw new Error(`POST export failed (${response.status})`);
  }
  return (await response.json()) as ExportResult;
}

export function getAudit(planId: string) {
  return getJson<AuditTrail>(`/v1/plans/${encodeURIComponent(planId)}/audit`);
}
