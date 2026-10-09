import { flowSteps } from '@/lib/data';

export type StepState = 'done' | 'active' | 'todo';

const CIRCLE_STYLES: Record<StepState, string> = {
  done: 'bg-emerald-600 text-white',
  active: 'bg-blue-600 text-white ring-4 ring-blue-100',
  todo: 'bg-slate-200 text-slate-600',
};

const CARD_STYLES: Record<StepState, string> = {
  done: 'border-emerald-200 bg-emerald-50/60',
  active: 'border-blue-300 bg-blue-50/60 shadow-sm',
  todo: 'border-slate-200 bg-white',
};

const STATE_LABELS: Record<StepState, string> = {
  done: 'Done',
  active: 'You are here',
  todo: 'Next',
};

export default function HowItWorks({
  stepStates,
}: {
  stepStates: Record<string, StepState>;
}) {
  return (
    <section aria-labelledby="how-it-works-heading" className="card p-6">
      <h2 id="how-it-works-heading" className="section-title">
        How this works
      </h2>
      <p className="section-subtitle">
        Four steps. You stay in control at step 3 — the assistant never contacts a customer or
        changes your CRM on its own.
      </p>

      <ol className="mt-5 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
        {flowSteps.map((step, index) => {
          const state = stepStates[step.id] ?? 'todo';
          return (
            <li
              key={step.id}
              className={`rounded-xl border p-4 ${CARD_STYLES[state]}`}
              aria-current={state === 'active' ? 'step' : undefined}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold ${CIRCLE_STYLES[state]}`}
                >
                  {state === 'done' ? '✓' : index + 1}
                </span>
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Step {index + 1}
                </span>
                <span
                  className={`ml-auto text-xs font-semibold ${
                    state === 'active'
                      ? 'text-blue-700'
                      : state === 'done'
                        ? 'text-emerald-700'
                        : 'text-slate-400'
                  }`}
                >
                  {STATE_LABELS[state]}
                </span>
              </div>
              <h3 className="mt-3 text-sm font-semibold text-slate-900">{step.title}</h3>
              <p className="mt-1 text-sm text-slate-600">{step.description}</p>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
