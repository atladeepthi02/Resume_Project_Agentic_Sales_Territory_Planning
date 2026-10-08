const metrics = [
  { label: 'Total Territories', value: '12', delta: '+2 this quarter' },
  { label: 'Total Accounts', value: '184', delta: '+18 this month' },
  { label: 'High Priority', value: '31', delta: '8 at risk' },
  { label: 'Open Opportunities', value: '246', delta: '$8.7M pipeline' },
];

const plan = [
  'Triage',
  'Data Retrieval',
  'KPI Analysis',
  'Prioritization',
  'RAG',
  'Investigation',
  'Planning',
  'Validation',
  'Approval',
  'Action',
];

const priorities = [
  { account: 'Northwind Foods', score: 91, level: 'HIGH', health: 'HEALTHY', action: 'Executive expansion review' },
  { account: 'Summit Health', score: 88, level: 'HIGH', health: 'HEALTHY', action: 'Renewal discussion' },
  { account: 'Harbor Retail', score: 74, level: 'MEDIUM', health: 'WATCH', action: 'Service recovery plan' },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl p-6">
        <header className="mb-8 flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-blue-400">Sales operations</p>
            <h1 className="mt-2 text-3xl font-bold">Agentic Sales Territory Planning</h1>
          </div>
          <div className="rounded-full border border-blue-500/40 bg-blue-500/10 px-4 py-2 text-sm text-blue-200">
            Workflow status: Active
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-4">
          {metrics.map((metric) => (
            <div key={metric.label} className="rounded-xl border border-slate-800 bg-slate-900 p-5 shadow-lg shadow-slate-950/30">
              <div className="text-sm text-slate-400">{metric.label}</div>
              <div className="mt-3 text-3xl font-semibold text-white">{metric.value}</div>
              <div className="mt-2 text-xs text-emerald-400">{metric.delta}</div>
            </div>
          ))}
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1.5fr_1fr]">
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Territory planning</h2>
              <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white">Create plan</button>
            </div>
            <div className="space-y-4">
              <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                <div className="text-sm text-slate-400">Territory</div>
                <div className="mt-2 text-lg font-semibold">T001 · North Region</div>
                <div className="mt-3 text-sm text-slate-300">Strong growth with several expansion opportunities and a single unresolved service issue requiring follow-up.</div>
              </div>
              <div className="grid gap-3 md:grid-cols-3">
                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                  <div className="text-sm text-slate-400">Revenue</div>
                  <div className="mt-2 text-2xl font-semibold">$5.2M</div>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                  <div className="text-sm text-slate-400">Pipeline</div>
                  <div className="mt-2 text-2xl font-semibold">$2.1M</div>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                  <div className="text-sm text-slate-400">Coverage gap</div>
                  <div className="mt-2 text-2xl font-semibold">3 accounts</div>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <h2 className="text-xl font-semibold">Workflow panel</h2>
            <div className="mt-4 space-y-3">
              {plan.map((step, index) => (
                <div key={step} className={`flex items-center gap-3 rounded-lg border p-3 ${index === 7 ? 'border-blue-500 bg-blue-500/10 text-blue-100' : 'border-slate-700 bg-slate-950 text-slate-300'}`}>
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-800 text-xs font-semibold">{index + 1}</div>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <h2 className="text-xl font-semibold">Top priority accounts</h2>
            <div className="mt-4 space-y-3">
              {priorities.map((item) => (
                <div key={item.account} className="rounded-lg border border-slate-700 bg-slate-950 p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{item.account}</div>
                      <div className="text-sm text-slate-400">{item.health}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-blue-400">{item.score}</div>
                      <div className="text-xs uppercase tracking-wide text-slate-300">{item.level}</div>
                    </div>
                  </div>
                  <div className="mt-3 text-sm text-slate-300">Recommended action: {item.action}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
            <h2 className="text-xl font-semibold">Human approval</h2>
            <div className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 p-4">
              <div className="text-sm text-amber-200">Action requiring review</div>
              <div className="mt-2 text-lg font-semibold text-white">High-value expansion plan</div>
              <div className="mt-2 text-sm text-slate-200">Account: Northwind Foods</div>
              <div className="mt-4 flex gap-3">
                <button className="rounded-md bg-emerald-600 px-3 py-2 text-sm font-medium text-white">Approve</button>
                <button className="rounded-md border border-slate-600 px-3 py-2 text-sm font-medium text-slate-200">Reject</button>
                <button className="rounded-md border border-slate-600 px-3 py-2 text-sm font-medium text-slate-200">Modify</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
