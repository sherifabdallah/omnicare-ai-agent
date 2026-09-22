import type { Entry as EntryModel } from '../hooks/useChat'
import { clock } from '../lib/format'
import { Markdown } from './Markdown'
import { Stamp, statusStamp } from './Stamp'

interface Props {
  entry: EntryModel
  /** 1-based citation numbers for this entry, keyed by section, matching the case file. */
  citationNumbers: Map<string, number>
}

export function Entry({ entry, citationNumbers }: Props) {
  const isUser = entry.role === 'user'
  const time = clock(new Date(entry.at))

  return (
    <article className="grid gap-x-6 gap-y-2 py-6 sm:grid-cols-[7rem_1fr]">
      <header className="flex items-baseline justify-between sm:block">
        <p className={`label ${isUser ? 'text-ink' : 'text-stamp'}`}>{isUser ? 'You' : 'OmniCare'}</p>
        <p className="font-mono text-[0.7rem] text-ink-2 tabular sm:mt-1">{time}</p>
      </header>

      <div className="min-w-0">
        {isUser ? (
          <p className="font-display text-[1.15rem] leading-snug italic">{entry.text}</p>
        ) : (
          <AssistantBody entry={entry} citationNumbers={citationNumbers} />
        )}
      </div>
    </article>
  )
}

function AssistantBody({ entry, citationNumbers }: Props) {
  if (entry.blocked) {
    return (
      <div className="flex flex-wrap items-start gap-x-6 gap-y-3">
        <p className="max-w-prose leading-relaxed">{entry.text}</p>
        <Stamp label="Refused" rotate={-8} />
      </div>
    )
  }
  if (entry.error) {
    return (
      <p className="border-l-2 border-stamp pl-3 leading-relaxed text-stamp">
        {entry.text}
      </p>
    )
  }

  const stamps = stampsFor(entry)
  const cited = (entry.citations ?? []).map((c) => citationNumbers.get(c.section)).filter((n): n is number => !!n)

  return (
    <div>
      <div className="flex flex-wrap items-start gap-x-6 gap-y-3">
        <div className="max-w-prose leading-relaxed">
          <Markdown text={entry.text} />
        </div>
        {stamps.map((s, i) => (
          <Stamp key={s} label={s} rotate={i % 2 ? 5 : -7} />
        ))}
      </div>

      {cited.length > 0 && (
        <p className="mt-3 font-mono text-[0.7rem] text-ink-2">
          cites policy passage{cited.length > 1 ? 's' : ''}{' '}
          {cited.map((n) => (
            <a key={n} href={`#passage-${n}`} className="ml-1 text-ink underline underline-offset-2">
              [{n}]
            </a>
          ))}
        </p>
      )}
    </div>
  )
}

/** Claim statuses surfaced by tools become stamps on the reply. */
function stampsFor(entry: EntryModel): string[] {
  const labels = new Set<string>()
  for (const call of entry.toolCalls ?? []) {
    if (call.status !== 'success') continue
    const result = call.result as { status?: unknown; error?: unknown } | null
    if (!result || result.error) continue
    const label = statusStamp(result.status)
    if (label) labels.add(label)
  }
  return [...labels]
}
