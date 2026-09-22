import { letterDate } from '../lib/format'
import type { LineStatus } from '../hooks/useHealth'

interface Props {
  line: LineStatus
}

export function Letterhead({ line }: Props) {
  return (
    <header className="px-4 pt-6 sm:px-8 lg:px-12">
      <div className="flex flex-wrap items-end justify-between gap-x-8 gap-y-3">
        <div>
          <p className="label mb-2">OmniCare Financial · Policyholder Assistance</p>
          <h1 className="font-display text-4xl leading-none font-medium tracking-tight sm:text-5xl">
            Correspondence
            <span className="text-ink-2 font-light italic"> &amp; </span>
            Claims Desk
          </h1>
        </div>

        <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 font-mono text-[0.75rem] text-ink-2 tabular">
          <dt className="label">Date</dt>
          <dd className="text-ink">{letterDate()}</dd>
          <dt className="label">Line</dt>
          <dd className="text-ink">
            <LineIndicator line={line} />
          </dd>
        </dl>
      </div>

      <div className="double-rule mt-5" aria-hidden="true" />
    </header>
  )
}

function LineIndicator({ line }: { line: LineStatus }) {
  if (line.state === 'checking') return <span>checking…</span>
  if (line.state === 'closed') {
    return (
      <span className="text-stamp">
        <Dot className="bg-stamp" /> closed · backend unreachable
      </span>
    )
  }
  return (
    <span>
      <Dot className="bg-ink" /> open · {line.health.llm_provider} / {line.health.llm_model}
    </span>
  )
}

function Dot({ className }: { className: string }) {
  return <span className={`mr-1.5 inline-block size-[7px] rounded-full align-[1px] ${className}`} />
}
