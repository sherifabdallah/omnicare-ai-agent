import { useEffect, useImperativeHandle, useRef, useState, type FormEvent, type KeyboardEvent, type Ref } from 'react'
import { SendIcon } from './icons'

const MAX = 2000

export interface ComposerHandle {
  focus: () => void
}

interface Props {
  disabled: boolean
  onSend: (message: string) => void
  ref?: Ref<ComposerHandle>
}

export function Composer({ disabled, onSend, ref }: Props) {
  const [value, setValue] = useState('')
  const area = useRef<HTMLTextAreaElement>(null)

  useImperativeHandle(ref, () => ({ focus: () => area.current?.focus() }), [])

  // Grow with the content, up to ~8 lines.
  useEffect(() => {
    const el = area.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`
  }, [value])

  const submit = (event?: FormEvent) => {
    event?.preventDefault()
    if (disabled || !value.trim()) return
    onSend(value)
    setValue('')
  }

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      submit()
    }
  }

  const remaining = MAX - value.length
  const canSend = !disabled && value.trim().length > 0

  return (
    <form onSubmit={submit} className="mx-auto w-full max-w-3xl">
      <div className="flex items-end gap-2 rounded-xl border border-border bg-surface p-2 shadow-sm transition-colors focus-within:border-brand">
        <label htmlFor="composer" className="sr-only">
          Message the assistant
        </label>
        <textarea
          id="composer"
          ref={area}
          value={value}
          onChange={(e) => setValue(e.target.value.slice(0, MAX))}
          onKeyDown={onKeyDown}
          rows={1}
          placeholder="Ask about coverage, a claim status, or file a new claim…"
          className="max-h-[180px] min-h-[2.5rem] flex-1 resize-none bg-transparent px-2 py-2 text-[0.9375rem] leading-relaxed outline-none placeholder:text-subtle"
        />
        <button
          type="submit"
          disabled={!canSend}
          aria-label="Send message"
          className="focus-ring grid size-9 shrink-0 place-items-center rounded-lg bg-brand text-brand-fg transition-all hover:bg-brand-hover disabled:cursor-not-allowed disabled:bg-surface-3 disabled:text-subtle"
        >
          <SendIcon className="size-4" />
        </button>
      </div>

      <div className="mt-1.5 flex items-center justify-between px-1 text-[0.7rem] text-subtle">
        <span>
          <kbd className="font-sans font-medium">Enter</kbd> to send ·{' '}
          <kbd className="font-sans font-medium">Shift + Enter</kbd> for a new line
        </span>
        {remaining < 200 && <span className="tabular">{remaining} characters left</span>}
      </div>
    </form>
  )
}
