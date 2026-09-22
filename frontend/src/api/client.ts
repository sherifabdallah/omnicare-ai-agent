import type { ChatRequest, ChatResponse, Health } from './types'

// Same-origin by default: Vite proxies /api in dev, nginx does in Docker.
const BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')
const API = `${BASE}/api/v1`

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!response.ok) {
    throw new ApiError(await describeError(response), response.status)
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T)
}

async function describeError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown }
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((d: { loc?: unknown[]; msg?: string }) => `${(d.loc ?? []).slice(-1)[0] ?? 'field'}: ${d.msg ?? 'invalid'}`)
        .join('; ')
    }
  } catch {
    /* non-JSON body */
  }
  return `${response.status} ${response.statusText}`
}

export const api = {
  health: () => request<Health>('/health'),
  chat: (body: ChatRequest) => request<ChatResponse>('/chat', { method: 'POST', body: JSON.stringify(body) }),
  reset: (userId: string) => request<void>(`/conversations/${encodeURIComponent(userId)}`, { method: 'DELETE' }),
}
