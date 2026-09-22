import { useEffect, useState, type FormEvent } from 'react'
import type { LineStatus } from '../hooks/useHealth'
import type { Theme } from '../hooks/useTheme'
import { CloseIcon, FileIcon, MoonIcon, PlusFileIcon, PlusIcon, SearchIcon, ShieldIcon, SunIcon } from './icons'

interface Props {
  userId: string
  onChangeUser: (id: string) => void
  onNewChat: () => void
  onQuickAction: (prompt: string) => void
  status: LineStatus
  theme: Theme
  onToggleTheme: () => void
  onClose?: () => void
}

const QUICK_ACTIONS = [
  { icon: SearchIcon, label: 'Coverage question', prompt: 'What does my policy cover for water damage?' },
  { icon: FileIcon, label: 'Claim status', prompt: 'What is the status of claim CLM-8821?' },
  { icon: PlusFileIcon, label: 'File a claim', prompt: 'I would like to file a new claim.' },
]

export function Sidebar({
  userId,
  onChangeUser,
  onNewChat,
  onQuickAction,
  status,
  theme,
  onToggleTheme,
  onClose,
}: Props) {
  return (
    <div className="flex h-full flex-col bg-surface">
      <div className="flex items-center gap-2.5 px-4 py-4">
        <div className="grid size-9 shrink-0 place-items-center rounded-lg bg-brand text-brand-fg">
          <ShieldIcon className="size-5" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold">OmniCare</p>
          <p className="truncate text-xs text-muted">Policyholder assistance</p>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close menu"
            className="focus-ring grid size-8 place-items-center rounded-lg text-muted hover:bg-surface-2 hover:text-fg lg:hidden"
          >
            <CloseIcon className="size-4" />
          </button>
        )}
      </div>

      <div className="px-3">
        <button
          type="button"
          onClick={onNewChat}
          className="focus-ring flex w-full items-center justify-center gap-2 rounded-lg border border-border bg-surface px-3 py-2.5 text-sm font-medium transition-colors hover:border-brand-border hover:bg-brand-subtle hover:text-brand"
        >
          <PlusIcon className="size-4" />
          New conversation
        </button>
      </div>

      <nav className="mt-6 px-3" aria-label="Quick actions">
        <h2 className="px-2 text-xs font-semibold tracking-wide text-subtle uppercase">Quick actions</h2>
        <ul className="mt-1.5 space-y-0.5">
          {QUICK_ACTIONS.map(({ icon: Icon, label, prompt }) => (
            <li key={label}>
              <button
                type="button"
                onClick={() => onQuickAction(prompt)}
                className="focus-ring flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-sm text-muted transition-colors hover:bg-surface-2 hover:text-fg"
              >
                <Icon className="size-4 shrink-0" />
                {label}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="mt-6 px-3">
        <h2 className="px-2 text-xs font-semibold tracking-wide text-subtle uppercase">Policyholder</h2>
        <UserField userId={userId} onChangeUser={onChangeUser} />
      </div>

      <div className="mt-auto border-t border-border p-3">
        <ConnectionStatus status={status} />
        <button
          type="button"
          onClick={onToggleTheme}
          className="focus-ring mt-2 flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-sm text-muted transition-colors hover:bg-surface-2 hover:text-fg"
        >
          {theme === 'dark' ? <SunIcon className="size-4" /> : <MoonIcon className="size-4" />}
          {theme === 'dark' ? 'Light theme' : 'Dark theme'}
        </button>
      </div>
    </div>
  )
}

function UserField({ userId, onChangeUser }: Pick<Props, 'userId' | 'onChangeUser'>) {
  const [draft, setDraft] = useState(userId)
  useEffect(() => setDraft(userId), [userId])

  const valid = /^[A-Za-z0-9_-]{1,64}$/.test(draft)
  const dirty = draft !== userId

  const submit = (event: FormEvent) => {
    event.preventDefault()
    if (valid && dirty) onChangeUser(draft)
  }

  return (
    <form onSubmit={submit} className="mt-1.5 px-2">
      <label htmlFor="user-id" className="sr-only">
        Policyholder id
      </label>
      <input
        id="user-id"
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        spellCheck={false}
        aria-invalid={!valid}
        className={`focus-ring w-full rounded-lg border bg-surface-2 px-2.5 py-2 font-mono text-sm tabular outline-none ${
          valid ? 'border-border' : 'border-danger text-danger'
        }`}
      />
      {dirty && valid && (
        <button
          type="submit"
          className="focus-ring mt-1.5 w-full rounded-lg bg-brand px-2.5 py-1.5 text-xs font-medium text-brand-fg hover:bg-brand-hover"
        >
          Switch to this policyholder
        </button>
      )}
      <p className="mt-1.5 text-xs leading-relaxed text-subtle">
        {valid ? 'Each policyholder has a separate conversation.' : 'Letters, digits, _ and - only.'}
      </p>
    </form>
  )
}

function ConnectionStatus({ status }: { status: LineStatus }) {
  if (status.state === 'checking') {
    return <Row color="bg-subtle" label="Connecting…" detail="checking service" />
  }
  if (status.state === 'closed') {
    return <Row color="bg-danger" label="Service offline" detail="backend unreachable" />
  }
  return <Row color="bg-success" label="Service online" detail={status.health.llm_model} />
}

function Row({ color, label, detail }: { color: string; label: string; detail: string }) {
  return (
    <div className="flex items-center gap-2.5 rounded-lg px-2 py-2">
      <span className={`size-2 shrink-0 rounded-full ${color}`} />
      <span className="min-w-0 flex-1">
        <span className="block text-xs font-medium">{label}</span>
        <span className="block truncate font-mono text-[0.7rem] text-subtle">{detail}</span>
      </span>
    </div>
  )
}
