import { useState } from 'react'
import type { ToolCall } from '../api/types'
import { asClaim, toolLabel, toolSummary } from '../lib/format'
import { ClaimCard } from './ClaimCard'
import { AlertIcon, CheckIcon, ChevronIcon, ToolIcon } from './icons'

function failed(call: ToolCall): boolean {
  return call.status !== 'success' || Boolean((call.result as { error?: unknown } | null)?.error)
}

/** What the assistant actually did: claim records get a card, the rest a compact row. */
export function ToolActivity({ calls }: { calls: ToolCall[] }) {
  if (calls.length === 0) return null

  const claims = calls.map((c) => asClaim(c.result)).filter((c) => c !== null)

  return (
    <>
      {claims.map((claim) => (
        <ClaimCard key={claim.claim_id} claim={claim} />
      ))}
      <Details calls={calls} />
    </>
  )
}

function Details({ calls }: { calls: ToolCall[] }) {
  const [open, setOpen] = useState(false)
  const anyFailed = calls.some(failed)

  return (
    <div className="mt-3">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="focus-ring inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium text-muted transition-colors hover:bg-surface-2 hover:text-fg"
      >
        <ToolIcon className="size-3.5" />
        {calls.length} action{calls.length > 1 ? 's' : ''} taken
        {anyFailed && <AlertIcon className="size-3.5 text-warn" />}
        <ChevronIcon className={`size-3.5 transition-transform ${open ? 'rotate-90' : ''}`} />
      </button>

      {open && (
        <ul className="mt-2 space-y-1.5">
          {calls.map((call, i) => {
            const bad = failed(call)
            return (
              <li key={`${call.name}-${i}`} className="rounded-md border border-border bg-surface-2/60 p-2.5">
                <div className="flex items-start gap-2">
                  {bad ? (
                    <AlertIcon className="mt-0.5 size-4 shrink-0 text-warn" />
                  ) : (
                    <CheckIcon className="mt-0.5 size-4 shrink-0 text-success" />
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium">{toolLabel(call.name)}</p>
                    <p className="mt-0.5 break-words font-mono text-[0.7rem] text-muted">
                      {toolSummary(call.name, call.args, call.result)}
                    </p>
                  </div>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
