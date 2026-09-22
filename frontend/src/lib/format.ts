export function time(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function money(value: unknown): string {
  const n = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(n)) return String(value ?? '')
  return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 })
}

export function percent(score: number): string {
  return `${Math.round(score * 100)}%`
}

export const TOOL_LABELS: Record<string, string> = {
  search_policy: 'Searched policy document',
  get_claim_status: 'Looked up claim',
  submit_claim: 'Submitted claim',
}

export function toolLabel(name: string): string {
  return TOOL_LABELS[name] ?? name
}

/** Short, human summary of what a tool call did. */
export function toolSummary(name: string, args: Record<string, unknown>, result: unknown): string {
  const r = (result ?? {}) as Record<string, unknown>
  if (r.error) return String(r.error)
  switch (name) {
    case 'search_policy':
      return `"${String(args.query ?? '')}"`
    case 'get_claim_status':
      return `${String(r.claim_id ?? args.claim_id ?? '')} - ${String(r.status ?? 'not found')}`
    case 'submit_claim':
      return r.claim_id ? `${String(r.claim_id)} created` : String(args.policy_number ?? '')
    default:
      return ''
  }
}

export interface ClaimRecord {
  claim_id: string
  policy_number: string
  claim_type: string
  status: string
  amount: number
  description?: string
}

/** A tool result is a claim record when it carries a claim id. */
export function asClaim(result: unknown): ClaimRecord | null {
  if (!result || typeof result !== 'object') return null
  const r = result as Record<string, unknown>
  return typeof r.claim_id === 'string' && typeof r.status === 'string' ? (r as unknown as ClaimRecord) : null
}
