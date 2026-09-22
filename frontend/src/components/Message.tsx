import type { Message as MessageModel } from '../hooks/useChat'
import { time } from '../lib/format'
import { Markdown } from './Markdown'
import { Sources } from './Sources'
import { ToolActivity } from './ToolActivity'
import { AlertIcon, ShieldIcon, UserIcon } from './icons'

export function Message({ message }: { message: MessageModel }) {
  return message.role === 'user' ? <UserMessage message={message} /> : <AssistantMessage message={message} />
}

function UserMessage({ message }: { message: MessageModel }) {
  return (
    <article data-testid="message" data-role="user" className="animate-in flex justify-end gap-3">
      <div className="max-w-[min(34rem,85%)]">
        <div className="rounded-xl rounded-br-sm bg-brand px-4 py-2.5 text-[0.9375rem] leading-relaxed text-brand-fg">
          {message.text}
        </div>
        <p className="mt-1 text-right text-[0.7rem] text-subtle tabular">{time(message.at)}</p>
      </div>
      <div className="mt-0.5 grid size-8 shrink-0 place-items-center rounded-full border border-border bg-surface-2 text-muted">
        <UserIcon className="size-4" />
      </div>
    </article>
  )
}

function AssistantMessage({ message }: { message: MessageModel }) {
  const variant = message.variant ?? 'normal'

  return (
    <article data-testid="message" data-role="assistant" data-variant={variant} className="animate-in flex gap-3">
      <div
        className={`mt-0.5 grid size-8 shrink-0 place-items-center rounded-full ${
          variant === 'normal' ? 'bg-brand text-brand-fg' : 'border border-border bg-surface-2 text-muted'
        }`}
      >
        <ShieldIcon className="size-4" />
      </div>

      <div className="min-w-0 flex-1">
        <div className="mb-1 flex items-baseline gap-2">
          <span className="text-sm font-semibold">OmniCare Assistant</span>
          <span className="text-[0.7rem] text-subtle tabular">{time(message.at)}</span>
        </div>

        {variant === 'normal' && (
          <>
            <div className="md text-fg">
              <Markdown text={message.text} />
            </div>
            <ToolActivity calls={message.toolCalls ?? []} />
            <Sources citations={message.citations ?? []} />
          </>
        )}

        {variant === 'blocked' && <Notice tone="warn" title="Request declined" body={message.text} />}
        {variant === 'error' && <Notice tone="danger" title="Something went wrong" body={message.text} />}
      </div>
    </article>
  )
}

function Notice({ tone, title, body }: { tone: 'warn' | 'danger'; title: string; body: string }) {
  const styles =
    tone === 'warn'
      ? 'border-warn/30 bg-warn-bg text-warn'
      : 'border-danger/30 bg-danger-bg text-danger'
  return (
    <div className={`flex gap-2.5 rounded-lg border p-3 ${styles}`} role="status">
      <AlertIcon className="mt-0.5 size-4 shrink-0" />
      <div className="min-w-0">
        <p className="text-sm font-semibold">{title}</p>
        <p className="mt-0.5 text-sm leading-relaxed text-fg">{body}</p>
      </div>
    </div>
  )
}
