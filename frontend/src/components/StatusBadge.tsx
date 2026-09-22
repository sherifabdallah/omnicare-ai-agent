const STYLES: Record<string, string> = {
  approved: 'bg-success-bg text-success border-success/30',
  submitted: 'bg-brand-subtle text-brand border-brand-border',
  'under review': 'bg-warn-bg text-warn border-warn/30',
  rejected: 'bg-danger-bg text-danger border-danger/30',
}

export function StatusBadge({ status }: { status: string }) {
  const style = STYLES[status.toLowerCase()] ?? 'bg-surface-2 text-muted border-border'
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${style}`}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {status}
    </span>
  )
}
