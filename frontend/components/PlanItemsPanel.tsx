'use client';

import { useMemo, useState } from 'react';
import AccountCard from '@/components/AccountCard';
import type { PlanItem } from '@/lib/api';

export default function PlanItemsPanel({
  items,
  loading,
}: {
  items: PlanItem[];
  loading: boolean;
}) {
  const [onlyAttention, setOnlyAttention] = useState(false);

  const needsAttention = useMemo(
    () => items.filter((item) => item.compliance.status !== 'passed' || item.stale).length,
    [items],
  );

  const visible = onlyAttention
    ? items.filter((item) => item.compliance.status !== 'passed' || item.stale)
    : items;

  return (
    <section aria-labelledby="accounts-heading">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 id="accounts-heading" className="section-title">
            Accounts, ranked
          </h2>
          <p className="section-subtitle">
            Highest priority first. Each card explains the rank, the next action, and the exact
            records behind it.
          </p>
        </div>
        {items.length > 0 && (
          <label className="inline-flex cursor-pointer items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={onlyAttention}
              onChange={(event) => setOnlyAttention(event.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-blue-600"
            />
            Only accounts needing review ({needsAttention})
          </label>
        )}
      </div>

      {loading && items.length === 0 && (
        <div className="mt-4 card p-6 text-sm text-slate-500">
          Building the plan and checking compliance…
        </div>
      )}

      {!loading && items.length === 0 && (
        <div className="mt-4 card p-6 text-sm text-slate-500">
          No accounts yet. Use <strong>Build the plan</strong> above to get started.
        </div>
      )}

      {!loading && items.length > 0 && visible.length === 0 && (
        <div className="mt-4 card p-6 text-sm text-slate-500">
          Good news — no accounts need review.
        </div>
      )}

      <div className="mt-4 space-y-4">
        {visible.map((item) => (
          <AccountCard key={item.item_id} item={item} />
        ))}
      </div>
    </section>
  );
}
