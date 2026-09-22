import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Health } from '../api/types'

export type LineStatus = { state: 'checking' } | { state: 'open'; health: Health } | { state: 'closed' }

/** Polls the backend health endpoint so the letterhead can show whether the line is open. */
export function useHealth(intervalMs = 30_000): LineStatus {
  const [status, setStatus] = useState<LineStatus>({ state: 'checking' })

  useEffect(() => {
    let cancelled = false
    const check = async () => {
      try {
        const health = await api.health()
        if (!cancelled) setStatus({ state: 'open', health })
      } catch {
        if (!cancelled) setStatus({ state: 'closed' })
      }
    }
    void check()
    const timer = setInterval(check, intervalMs)
    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [intervalMs])

  return status
}
