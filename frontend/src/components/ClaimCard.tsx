import { money, type ClaimRecord } from '../lib/format'
import { StatusBadge } from './StatusBadge'

/** Renders a claim returned by a tool as a structured card instead of raw JSON. */
export function ClaimCard({ claim }: { claim: ClaimRecord }) {
  return (
    <div className="mt-3 overflow-hidden rounded-lg border border-border bg-surface">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border bg-surface-2 px-4 py-2.5">
        <span className="font-mono text-sm font-medium tabular">{claim.claim_id}</span>
        <StatusBadge status={claim.status} />
      </div>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-3 p-4 sm:grid-cols-3">
        <Field label="Policy" value={claim.policy_number} mono />
        <Field label="Type" value={claim.claim_type} />
        <Field label="Amount" value={money(claim.amount)} mono />
        {claim.description && (
          <div className="col-span-2 sm:col-span-3">
            <dt className="text-xs font-medium text-muted">Description</dt>
            <dd className="mt-1 text-sm">{claim.description}</dd>
          </div>
        )}
      </dl>
    </div>
  )
}

function Field({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs font-medium text-muted">{label}</dt>
      <dd className={`mt-1 text-sm ${mono ? 'font-mono tabular' : ''}`}>{value}</dd>
    </div>
  )
}
