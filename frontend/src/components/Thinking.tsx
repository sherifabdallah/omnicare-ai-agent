import { ShieldIcon } from './icons'

export function Thinking() {
  return (
    <div data-testid="thinking" className="animate-in flex gap-3" aria-live="polite" aria-label="Assistant is working">
      <div className="mt-0.5 grid size-8 shrink-0 place-items-center rounded-full bg-brand text-brand-fg">
        <ShieldIcon className="size-4" />
      </div>
      <div className="flex items-center gap-2 rounded-xl border border-border bg-surface px-4 py-3">
        <span className="flex gap-1">
          <Dot delay="0ms" />
          <Dot delay="150ms" />
          <Dot delay="300ms" />
        </span>
        <span className="text-sm text-muted">Working on it…</span>
      </div>
    </div>
  )
}

function Dot({ delay }: { delay: string }) {
  return <span className="dot size-1.5 rounded-full bg-muted" style={{ animationDelay: delay }} />
}
