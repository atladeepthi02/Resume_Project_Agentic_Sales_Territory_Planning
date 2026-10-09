import { glossary } from '@/lib/data';

export default function Glossary() {
  return (
    <section id="glossary" aria-labelledby="glossary-heading" className="card scroll-mt-6 p-6">
      <h2 id="glossary-heading" className="section-title">
        Glossary — plain-language definitions
      </h2>
      <p className="section-subtitle">New to the terms on this page? Start here.</p>

      <dl className="mt-4 grid gap-4 md:grid-cols-2">
        {glossary.map((entry) => (
          <div key={entry.term} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <dt className="text-sm font-semibold text-slate-900">{entry.term}</dt>
            <dd className="mt-1 text-sm text-slate-600">{entry.meaning}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
