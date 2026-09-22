import type { CSSProperties } from 'react'

interface Props {
  label: string
  rotate?: number
  size?: 'sm' | 'md'
  className?: string
}

/** A rubber stamp. Pressed once (animated) when it first appears. */
export function Stamp({ label, rotate = -6, size = 'md', className = '' }: Props) {
  const style = { '--stamp-rotate': `${rotate}deg` } as CSSProperties
  const text = size === 'sm' ? 'text-[0.7rem]' : 'text-base'
  return (
    <span className={`stamp select-none ${text} ${className}`} style={style} aria-label={label} role="img">
      {label}
    </span>
  )
}

/** Maps a claim status to stamp copy (statuses come from the backend as free text). */
export function statusStamp(status: unknown): string | null {
  if (typeof status !== 'string') return null
  const known: Record<string, string> = {
    approved: 'Approved',
    'under review': 'Under review',
    submitted: 'Received',
    rejected: 'Rejected',
  }
  return known[status.toLowerCase()] ?? status
}
