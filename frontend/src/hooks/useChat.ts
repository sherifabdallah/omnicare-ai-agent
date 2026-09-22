import { useCallback, useEffect, useReducer, useRef } from 'react'
import { api, ApiError } from '../api/client'
import type { ChatResponse, Citation, ToolCall } from '../api/types'

export type MessageVariant = 'normal' | 'blocked' | 'error'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  text: string
  at: string // ISO timestamp
  variant?: MessageVariant
  citations?: Citation[]
  toolCalls?: ToolCall[]
}

interface State {
  messages: Message[]
  sending: boolean
}

type Action =
  | { type: 'hydrate'; messages: Message[] }
  | { type: 'send'; message: Message }
  | { type: 'receive'; message: Message }
  | { type: 'clear' }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'hydrate':
      return { messages: action.messages, sending: false }
    case 'send':
      return { messages: [...state.messages, action.message], sending: true }
    case 'receive':
      return { messages: [...state.messages, action.message], sending: false }
    case 'clear':
      return { messages: [], sending: false }
  }
}

const storageKey = (userId: string) => `omnicare.chat.${userId}`

function load(userId: string): Message[] {
  try {
    const raw = localStorage.getItem(storageKey(userId))
    return raw ? (JSON.parse(raw) as Message[]) : []
  } catch {
    return []
  }
}

function persist(userId: string, messages: Message[]) {
  try {
    localStorage.setItem(storageKey(userId), JSON.stringify(messages))
  } catch {
    /* storage unavailable: the conversation still lives in memory */
  }
}

const uid = () => (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`)

function toMessage(reply: ChatResponse): Message {
  return {
    id: uid(),
    role: 'assistant',
    text: reply.response,
    at: new Date().toISOString(),
    variant: reply.blocked ? 'blocked' : 'normal',
    citations: reply.citations,
    toolCalls: reply.tool_calls,
  }
}

function errorMessage(err: unknown): Message {
  const text =
    err instanceof ApiError
      ? err.status === 422
        ? `That request was rejected: ${err.message}`
        : err.message
      : 'Could not reach the assistant. Check that the backend is running and try again.'
  return { id: uid(), role: 'assistant', text, at: new Date().toISOString(), variant: 'error' }
}

export function useChat(userId: string) {
  const [state, dispatch] = useReducer(reducer, { messages: [], sending: false })
  const userRef = useRef(userId)
  const sendingRef = useRef(false)

  useEffect(() => {
    userRef.current = userId
    dispatch({ type: 'hydrate', messages: load(userId) })
  }, [userId])

  useEffect(() => {
    persist(userRef.current, state.messages)
  }, [state.messages])

  useEffect(() => {
    sendingRef.current = state.sending
  }, [state.sending])

  const send = useCallback(async (text: string) => {
    const message = text.trim()
    if (!message || sendingRef.current) return
    sendingRef.current = true
    dispatch({ type: 'send', message: { id: uid(), role: 'user', text: message, at: new Date().toISOString() } })
    try {
      const reply = await api.chat({ user_id: userRef.current, message })
      dispatch({ type: 'receive', message: toMessage(reply) })
    } catch (err) {
      dispatch({ type: 'receive', message: errorMessage(err) })
    }
  }, [])

  const clear = useCallback(async () => {
    dispatch({ type: 'clear' })
    try {
      await api.reset(userRef.current)
    } catch {
      /* backend memory is best-effort; the local history is cleared regardless */
    }
  }, [])

  return { messages: state.messages, sending: state.sending, send, clear }
}
