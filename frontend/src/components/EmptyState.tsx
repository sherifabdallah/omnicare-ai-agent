import { FileIcon, PlusFileIcon, SearchIcon, ShieldIcon } from './icons'

export interface Suggestion {
  title: string
  detail: string
  prompt: string
  icon: 'search' | 'file' | 'new' | 'shield'
}

export const SUGGESTIONS: Suggestion[] = [
  {
    icon: 'search',
    title: 'Check my coverage',
    detail: 'Water damage from a burst pipe',
    prompt: 'Is water damage from a burst pipe covered? What is the deductible?',
  },
  {
    icon: 'search',
    title: 'Ask about limits',
    detail: 'Jewelry worth $3,000',
    prompt: 'Is my jewelry covered? I have a necklace worth $3,000.',
  },
  {
    icon: 'file',
    title: 'Track a claim',
    detail: 'Status of CLM-8821',
    prompt: 'What is the status of claim CLM-8821?',
  },
  {
    icon: 'new',
    title: 'File a new claim',
    detail: 'Water damage, POL-1092',
    prompt:
      'I want to submit a water damage claim for policy POL-1092 for $1,800. A pipe burst under my kitchen sink.',
  },
]

const ICONS = {
  search: SearchIcon,
  file: FileIcon,
  new: PlusFileIcon,
  shield: ShieldIcon,
}

export function EmptyState({ onPick }: { onPick: (prompt: string) => void }) {
  return (
    <div className="mx-auto max-w-2xl py-8 text-center sm:py-14">
      <div className="mx-auto grid size-12 place-items-center rounded-xl bg-brand text-brand-fg">
        <ShieldIcon className="size-6" />
      </div>
      <h2 className="mt-4 text-xl font-semibold tracking-tight sm:text-2xl">How can we help today?</h2>
      <p className="mx-auto mt-2 max-w-md text-[0.9375rem] leading-relaxed text-muted">
        Ask about your policy coverage, check the status of a claim, or file a new one. Coverage answers quote the
        policy document directly.
      </p>

      <ul className="mt-7 grid gap-3 text-left sm:grid-cols-2">
        {SUGGESTIONS.map((s) => {
          const Icon = ICONS[s.icon]
          return (
            <li key={s.title}>
              <button
                type="button"
                onClick={() => onPick(s.prompt)}
                className="focus-ring group flex w-full items-start gap-3 rounded-xl border border-border bg-surface p-3.5 text-left transition-all hover:border-brand-border hover:bg-brand-subtle"
              >
                <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-surface-2 text-muted transition-colors group-hover:bg-brand group-hover:text-brand-fg">
                  <Icon className="size-4" />
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-medium">{s.title}</span>
                  <span className="mt-0.5 block truncate text-xs text-muted">{s.detail}</span>
                </span>
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
