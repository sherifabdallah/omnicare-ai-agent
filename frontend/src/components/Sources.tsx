import { useState } from 'react'
import type { Citation } from '../api/types'
import { percent } from '../lib/format'
import { BookIcon, ChevronIcon } from './icons'

/** Policy passages backing an answer, collapsed by default after the first one. */
export function Sources({ citations }: { citations: Citation[] }) {
  const [open, setOpen] = useState(false)
  if (citations.length === 0) return null

  const visible = open ? citations : citations.slice(0, 1)
  const hidden = citations.length - visible.length

  return (
    <section className="mt-3 rounded-lg border border-border bg-surface-2/60" aria-label="Sources">
      <h3 className="flex items-center gap-2 px-3 pt-2.5 text-xs font-semibold text-muted">
        <BookIcon className="size-3.5" />
        Sources from the policy document
      </h3>

      <ol className="space-y-2 p-3 pt-2">
        {visible.map((c, i) => (
          <li key={`${c.section}-${i}`} className="rounded-md border border-border bg-surface p-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="text-sm font-medium">
                <span className="mr-1.5 text-muted">[{i + 1}]</span>
                {c.section}
              </p>
              <span className="shrink-0 font-mono text-[0.7rem] text-muted tabular">
                {percent(c.score)} match
              </span>
            </div>
            <p className="mt-1.5 text-sm leading-relaxed text-muted">{c.excerpt}</p>
            <p className="mt-2 font-mono text-[0.7rem] text-subtle">{c.source}</p>
          </li>
        ))}
      </ol>

      {citations.length > 1 && (
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="focus-ring flex w-full items-center gap-1.5 rounded-b-lg border-t border-border px-3 py-2 text-xs font-medium text-muted transition-colors hover:bg-surface-3 hover:text-fg"
        >
          <ChevronIcon className={`size-3.5 transition-transform ${open ? 'rotate-90' : ''}`} />
          {open ? 'Show less' : `Show ${hidden} more source${hidden > 1 ? 's' : ''}`}
        </button>
      )}
    </section>
  )
}
