import { useCallback, useEffect, useRef, useState } from 'react'
import { Composer, type ComposerHandle } from './components/Composer'
import { EmptyState } from './components/EmptyState'
import { Message } from './components/Message'
import { Sidebar } from './components/Sidebar'
import { Thinking } from './components/Thinking'
import { MenuIcon, ShieldIcon } from './components/icons'
import { useChat } from './hooks/useChat'
import { useHealth } from './hooks/useHealth'
import { useTheme } from './hooks/useTheme'

const USER_KEY = 'omnicare.policyholder'

function loadUser(): string {
  try {
    return localStorage.getItem(USER_KEY) || 'usr_123'
  } catch {
    return 'usr_123'
  }
}

export default function App() {
  const [userId, setUserId] = useState(loadUser)
  const [menuOpen, setMenuOpen] = useState(false)
  const [theme, toggleTheme] = useTheme()
  const status = useHealth()
  const { messages, sending, send, clear } = useChat(userId)

  const scrollRef = useRef<HTMLDivElement>(null)
  const composerRef = useRef<ComposerHandle>(null)

  useEffect(() => {
    try {
      localStorage.setItem(USER_KEY, userId)
    } catch {
      /* storage unavailable */
    }
  }, [userId])

  // Keep the newest message in view.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages.length, sending])

  const submit = useCallback(
    (prompt: string) => {
      setMenuOpen(false)
      void send(prompt)
    },
    [send],
  )

  const newChat = useCallback(() => {
    setMenuOpen(false)
    void clear()
    composerRef.current?.focus()
  }, [clear])

  return (
    <div className="flex h-dvh overflow-hidden bg-app">
      {/* Sidebar: permanent on desktop, drawer on mobile */}
      <aside className="hidden w-64 shrink-0 border-r border-border lg:block">
        <Sidebar
          userId={userId}
          onChangeUser={setUserId}
          onNewChat={newChat}
          onQuickAction={submit}
          status={status}
          theme={theme}
          onToggleTheme={toggleTheme}
        />
      </aside>

      {menuOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Close menu"
            onClick={() => setMenuOpen(false)}
            className="absolute inset-0 bg-black/40"
          />
          <aside className="absolute inset-y-0 left-0 w-72 border-r border-border shadow-xl">
            <Sidebar
              userId={userId}
              onChangeUser={setUserId}
              onNewChat={newChat}
              onQuickAction={submit}
              status={status}
              theme={theme}
              onToggleTheme={toggleTheme}
              onClose={() => setMenuOpen(false)}
            />
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center gap-3 border-b border-border bg-surface px-4">
          <button
            type="button"
            onClick={() => setMenuOpen(true)}
            aria-label="Open menu"
            className="focus-ring grid size-9 place-items-center rounded-lg text-muted hover:bg-surface-2 hover:text-fg lg:hidden"
          >
            <MenuIcon className="size-5" />
          </button>

          <div className="flex min-w-0 items-center gap-2">
            <ShieldIcon className="size-4 shrink-0 text-brand lg:hidden" />
            <h1 className="truncate text-sm font-semibold">Assistant</h1>
          </div>

          <span className="ml-auto hidden items-center gap-1.5 rounded-full border border-border bg-surface-2 px-2.5 py-1 font-mono text-[0.7rem] text-muted sm:inline-flex">
            <span className="size-1.5 rounded-full bg-brand" />
            {userId}
          </span>
        </header>

        <div ref={scrollRef} className="flex-1 overflow-y-auto overscroll-contain">
          <div
            className={`mx-auto flex max-w-3xl flex-col px-4 py-6 ${
              messages.length === 0 ? 'min-h-full justify-center' : ''
            }`}
          >
            {messages.length === 0 ? (
              <EmptyState onPick={submit} />
            ) : (
              <div className="space-y-6">
                {messages.map((message) => (
                  <Message key={message.id} message={message} />
                ))}
                {sending && <Thinking />}
              </div>
            )}
          </div>
        </div>

        <div className="shrink-0 border-t border-border bg-surface px-4 pt-3 pb-4">
          <Composer ref={composerRef} disabled={sending} onSend={submit} />
          <p className="mx-auto mt-2 max-w-3xl text-center text-[0.7rem] text-subtle">
            Coverage answers come from the OmniCare General Insurance Policy 2026. Claim decisions are made by an
            adjuster, not by this assistant.
          </p>
        </div>
      </div>
    </div>
  )
}
