import MetricCard from '@/components/MetricCard';
import type { Metric } from '@/lib/data';

const PLACEHOLDER: Metric[] = [
  { label: 'Territories', value: '—', hint: 'loading…', help: 'Territories in the portfolio.' },
  { label: 'Accounts', value: '—', hint: 'loading…', help: 'Accounts across all territories.' },
  {
    label: 'High priority',
    value: '—',
    hint: 'loading…',
    help: 'Accounts scored as high priority by the ranking rules.',
  },
  {
    label: 'Open opportunities',
    value: '—',
    hint: 'loading…',
    help: 'Deals still open across the portfolio.',
  },
];

export default function MetricsSection({
  metrics,
  loading,
}: {
  metrics: Metric[];
  loading: boolean;
}) {
  const items = metrics.length > 0 ? metrics : PLACEHOLDER;

  return (
    <section aria-labelledby="portfolio-heading">
      <h2 id="portfolio-heading" className="section-title">
        Portfolio at a glance
      </h2>
      <p className="section-subtitle">
        A snapshot of the whole portfolio. Hover the <span className="font-semibold">?</span> on any
        card to see what the number means.
      </p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {items.map((metric) => (
          <MetricCard
            key={metric.label}
            metric={loading && metrics.length === 0 ? { ...metric, value: '…' } : metric}
          />
        ))}
      </div>
    </section>
  );
}
