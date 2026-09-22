export function clock(date: Date = new Date()): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
}

export function letterDate(date: Date = new Date()): string {
  return date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
}

export function money(value: unknown): string {
  const n = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(n)) return String(value ?? '')
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 })
}

/** One-line human summary of a tool call for the ledger. */
export function describeToolCall(name: string, args: Record<string, unknown>, result: unknown): string {
  const r = (result ?? {}) as Record<string, unknown>
  switch (name) {
    case 'search_policy':
      return `"${String(args.query ?? '')}"`
    case 'get_claim_status':
      return r.error ? `${String(args.claim_id)} · ${String(r.error)}` : `${String(r.claim_id ?? args.claim_id)} → ${String(r.status ?? '?')}`
    case 'submit_claim':
      return r.claim_id
        ? `${String(r.claim_id)} · ${String(r.claim_type)} · ${money(r.amount)}`
        : `${String(args.policy_number ?? '')} · ${String(args.claim_type ?? '')} · ${money(args.amount)}`
    default:
      return JSON.stringify(args)
  }
}
