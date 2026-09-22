// Wire contract of the backend (backend/app/api/v1/dtos).

export interface ChatRequest {
  user_id: string
  message: string
}

export interface ToolCall {
  name: string
  args: Record<string, unknown>
  result: unknown
  status: 'success' | 'error' | 'pending' | string
}

export interface Citation {
  source: string
  section: string
  excerpt: string
  score: number
}

export interface ChatResponse {
  response: string
  sources: string[]
  tool_calls: ToolCall[]
  citations: Citation[]
  blocked: boolean
}

export interface Health {
  status: string
  version: string
  llm_provider: string
  llm_model: string
}
