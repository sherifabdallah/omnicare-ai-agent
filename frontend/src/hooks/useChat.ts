import { useCallback, useEffect, useMemo, useReducer, useRef } from 'react'
import { api, ApiError } from '../api/client'
import type { ChatResponse, Citation, ToolCall } from '../api/types'

export interface Entry {
  id: string
  role: 'user' | 'assistant'
  text: string
  at: string // ISO timestamp
  blocked?: boolean
  error?: boolean
  citations?: Citation[]
  toolCalls?: ToolCall[]
}

interface State {
  entries: Entry[]
  sending: boolean
}

type Action =
  | { type: 'hydrate'; entries: Entry[] }
  | { type: 'send'; entry: Entry }
  | { type: 'receive'; entry: Entry }
  | { type: 'clear' }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'hydrate':
      return { entries: action.entries, sending: false }
    case 'send':
      return { entries: [...state.entries, action.entry], sending: true }
    case 'receive':
      return { entries: [...state.entries, action.entry], sending: false }
    case 'clear':
      return { entries: [], sending: false }
  }
}

const storageKey = (userId: string) => `omnicare.file.${userId}`

function load(userId: string): Entry[] {
  try {
    const raw = localStorage.getItem(storageKey(userId))
    return raw ? (JSON.parse(raw) as Entry[]) : []
  } catch {
    return []
  }
}

function persist(userId: string, entries: Entry[]) {
  try {
    localStorage.setItem(storageKey(userId), JSON.stringify(entries))
  } catch {
    /* storage unavailable: the conversation still lives in memory */
  }
}

const uid = () => (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`)

function toEntry(reply: ChatResponse): Entry {
  return {
    id: uid(),
    role: 'assistant',
    text: reply.response,
    at: new Date().toISOString(),
    blocked: reply.blocked,
    citations: reply.citations,
    toolCalls: reply.tool_calls,
  }
}

function failureEntry(err: unknown): Entry {
  const text =
    err instanceof ApiError
      ? err.status === 422
        ? `The request was rejected: ${err.message}`
        : err.message
      : 'The assistant could not be reached. Is the backend running?'
  return { id: uid(), role: 'assistant', text, at: new Date().toISOString(), error: true }
}

export function useChat(userId: string) {
  const [state, dispatch] = useReducer(reducer, { entries: [], sending: false })
  const userRef = useRef(userId)

  // Switch files when the policyholder id changes.
  useEffect(() => {
    userRef.current = userId
    dispatch({ type: 'hydrate', entries: load(userId) })
  }, [userId])

  useEffect(() => {
    persist(userRef.current, state.entries)
  }, [state.entries])

  const send = useCallback(
    async (message: string) => {
      const trimmed = message.trim()
      if (!trimmed || state.sending) return
      dispatch({ type: 'send', entry: { id: uid(), role: 'user', text: trimmed, at: new Date().toISOString() } })
      try {
        const reply = await api.chat({ user_id: userRef.current, message: trimmed })
        dispatch({ type: 'receive', entry: toEntry(reply) })
      } catch (err) {
        dispatch({ type: 'receive', entry: failureEntry(err) })
      }
    },
    [state.sending],
  )

  const clear = useCallback(async () => {
    dispatch({ type: 'clear' })
    try {
      await api.reset(userRef.current)
    } catch {
      /* backend memory is best-effort; the local file is cleared regardless */
    }
  }, [])

  // Everything cited or invoked so far, newest first, for the case file panel.
  const caseFile = useMemo(() => {
    const citations: Array<Citation & { entryId: string }> = []
    const ledger: Array<ToolCall & { entryId: string; at: string }> = []
    for (const entry of state.entries) {
      entry.citations?.forEach((c) => citations.push({ ...c, entryId: entry.id }))
      entry.toolCalls?.forEach((t) => ledger.push({ ...t, entryId: entry.id, at: entry.at }))
    }
    return { citations, ledger }
  }, [state.entries])

  return { entries: state.entries, sending: state.sending, send, clear, caseFile }
}
