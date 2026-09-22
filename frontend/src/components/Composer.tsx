import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'

interface Props {
  disabled: boolean
  onSend: (message: string) => void
}

const MAX = 2000

export function Composer({ disabled, onSend }: Props) {
  const [value, setValue] = useState('')
  const ref = useRef<HTMLTextAreaElement>(null)

  // Grow with content, up to a few lines.
  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.height = '0px'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }, [value])

  const submit = (e?: FormEvent) => {
    e?.preventDefault()
    if (disabled || !value.trim()) return
    onSend(value)
    setValue('')
  }

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <form onSubmit={submit} className="border-t border-ink pt-4">
      <label htmlFor="composer" className="label">
        Write to the desk
      </label>
      <div className="mt-2 grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end">
        <textarea
          id="composer"
          ref={ref}
          value={value}
          onChange={(e) => setValue(e.target.value.slice(0, MAX))}
          onKeyDown={onKeyDown}
          rows={1}
          placeholder="Ask about your coverage, check a claim, or file a new one…"
          className="w-full resize-none border-b border-rule bg-transparent py-2 font-display text-[1.15rem] leading-snug placeholder:text-ink-2/70 focus:border-ink focus:outline-none"
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="h-10 border border-ink px-5 font-mono text-[0.72rem] tracking-[0.14em] text-ink uppercase transition-colors duration-150 hover:bg-ink hover:text-paper disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-ink"
        >
          {disabled ? 'Sending' : 'Send'}
        </button>
      </div>
      <p className="mt-2 flex justify-between font-mono text-[0.68rem] text-ink-2 tabular">
        <span>Enter to send · Shift+Enter for a new line</span>
        <span>
          {value.length}/{MAX}
        </span>
      </p>
    </form>
  )
}
