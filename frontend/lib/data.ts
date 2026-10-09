export type Metric = {
  label: string;
  value: string;
  hint: string;
  help: string;
};

export type FlowStep = {
  id: 'build' | 'review' | 'approve' | 'export';
  title: string;
  description: string;
};

export const flowSteps: FlowStep[] = [
  {
    id: 'build',
    title: 'Build the plan',
    description:
      'The assistant collects your accounts, opportunities and service issues, then ranks each account using fixed rules.',
  },
  {
    id: 'review',
    title: 'Review the evidence',
    description:
      'Open any account to see the facts and source records behind its ranking and recommended action.',
  },
  {
    id: 'approve',
    title: 'Approve or edit',
    description:
      'Nothing is sent or changed until you approve. You can rename an action first if you disagree.',
  },
  {
    id: 'export',
    title: 'Export to your CRM',
    description:
      'Approved actions download as a CSV ready for your CRM. Exporting again will not create duplicates.',
  },
];

export type GlossaryEntry = {
  term: string;
  meaning: string;
};

export const glossary: GlossaryEntry[] = [
  {
    term: 'Priority score (0–100)',
    meaning:
      'A fixed-rules number built from opportunity value, past sales performance, product adoption, unresolved service issues, deal stage and territory rules. The AI never does the maths.',
  },
  {
    term: 'Compliance checks',
    meaning:
      'Automatic rules that confirm the account is owned by the right representative, that you are allowed to see it, and that the contact method is permitted.',
  },
  {
    term: 'Evidence / citation',
    meaning:
      'The exact source record (account, opportunity, service issue or playbook) behind every claim in a recommendation.',
  },
  {
    term: 'Stale data',
    meaning:
      'A record that has not been updated within the freshness limit. It is flagged instead of being used silently.',
  },
  {
    term: 'Playbook',
    meaning:
      'An approved sales strategy that tells you how to approach a particular situation.',
  },
  {
    term: 'Idempotent export',
    meaning:
      'Running the same export more than once returns the same file instead of creating duplicate actions.',
  },
];

const PLAN_STATUS_LABELS: Record<string, string> = {
  PENDING_APPROVAL: 'Waiting for your approval',
  APPROVED: 'Approved',
  REJECTED: 'Rejected',
  EXPORTED: 'Exported to CRM',
};

export function formatPlanStatus(status: string): string {
  return PLAN_STATUS_LABELS[status] ?? status;
}

const PRIORITY_LABELS: Record<string, string> = {
  HIGH: 'High priority — work first',
  MEDIUM: 'Medium priority — schedule soon',
  LOW: 'Low priority — keep an eye on',
};

export function formatPriority(level: string): string {
  return PRIORITY_LABELS[level] ?? `${level} priority`;
}

const COMPLIANCE_LABELS: Record<string, string> = {
  passed: 'All checks passed',
  warning: 'Review advised',
  failed: 'Needs review before action',
};

export function formatCompliance(status: string): string {
  return COMPLIANCE_LABELS[status] ?? status;
}

const ITEM_STATUS_LABELS: Record<string, string> = {
  PENDING: 'Awaiting approval',
  APPROVED: 'Approved',
  REJECTED: 'Rejected',
};

export function formatItemStatus(status: string): string {
  return ITEM_STATUS_LABELS[status] ?? status;
}

const AUDIT_LABELS: Record<string, string> = {
  PLAN_CREATED: 'Plan created',
  PLAN_EDITED: 'Plan edited',
  PLAN_APPROVED: 'Plan approved',
  PLAN_REJECTED: 'Plan rejected',
  PLAN_EXPORTED: 'Approved actions exported',
  PLAN_EXPORT_DUPLICATE: 'Duplicate export detected',
};

export function formatAuditEvent(eventType: string): string {
  return AUDIT_LABELS[eventType] ?? eventType;
}
