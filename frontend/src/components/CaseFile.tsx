import { useState, type FormEvent } from 'react'
import type { Citation, ToolCall } from '../api/types'
import { clock, describeToolCall } from '../lib/format'

interface Props {
  userId: string
  onChangeUser: (id: string) => void
  onNewFile: () => void
  passages: Array<Citation & { number: number }>
  ledger: Array<ToolCall & { at: string }>
}

/** The right-hand panel: who the file belongs to, what the policy said, what the desk did. */
export function CaseFile({ userId, onChangeUser, onNewFile, passages, ledger }: Props) {
  return (
    <aside className="border-ink lg:sticky lg:top-6 lg:border-l lg:pl-8">
      <Policyholder userId={userId} onChangeUser={onChangeUser} onNewFile={onNewFile} />
      <Passages passages={passages} />
      <Ledger ledger={ledger} />
    </aside>
  )
}

function Policyholder({ userId, onChangeUser, onNewFile }: Pick<Props, 'userId' | 'onChangeUser' | 'onNewFile'>) {
  const [draft, setDraft] = useState(userId)
  const valid = /^[A-Za-z0-9_-]{1,64}$/.test(draft)
  const dirty = draft !== userId

  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (valid && dirty) onChangeUser(draft)
  }

  return (
    <section>
      <p className="label">Case file</p>
      <form onSubmit={submit} className="mt-2 flex items-end gap-3">
        <label className="grow">
          <span className="sr-only">Policyholder id</span>
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            spellCheck={false}
            className={`w-full border-b bg-transparent py-1 font-mono text-[0.95rem] tabular focus:outline-none ${
              valid ? 'border-rule focus:border-ink' : 'border-stamp text-stamp'
            }`}
            aria-invalid={!valid}
          />
        </label>
        {dirty ? (
          <button
            type="submit"
            disabled={!valid}
            className="border border-ink px-3 py-1 font-mono text-[0.68rem] tracking-[0.14em] uppercase hover:bg-ink hover:text-paper disabled:opacity-40"
          >
            Open
          </button>
        ) : (
          <button
            type="button"
            onClick={onNewFile}
            className="border border-rule-strong px-3 py-1 font-mono text-[0.68rem] tracking-[0.14em] text-ink-2 uppercase transition-colors hover:border-ink hover:text-ink"
          >
            New file
          </button>
        )}
      </form>
      <p className="mt-1.5 font-mono text-[0.68rem] text-ink-2">
        {valid ? 'The desk keeps a separate memory per policyholder id.' : 'Letters, digits, _ and - only.'}
      </p>
    </section>
  )
}

function Passages({ passages }: Pick<Props, 'passages'>) {
  return (
    <section className="mt-10">
      <div className="flex items-baseline justify-between">
        <p className="label">Cited policy passages</p>
        <p className="font-mono text-[0.68rem] text-ink-2 tabular">{passages.length || '—'}</p>
      </div>

      {passages.length === 0 ? (
        <p className="mt-3 max-w-[38ch] text-[0.9rem] leading-relaxed text-ink-2">
          When the desk answers a coverage question it quotes the policy here, highlighted, with the section it came
          from.
        </p>
      ) : (
        <ol className="mt-3 space-y-5">
          {passages.map((p) => (
            <li key={p.number} id={`passage-${p.number}`} className="grid grid-cols-[2rem_1fr] gap-2 scroll-mt-6">
              <span className="font-mono text-[0.75rem] text-ink-2 tabular">[{p.number}]</span>
              <div>
                <p className="font-display text-[0.95rem] font-medium">{p.section}</p>
                <p className="mt-1.5 text-[0.9rem] leading-relaxed">
                  <span className="marked">{p.excerpt}</span>
                </p>
                <p className="mt-1.5 font-mono text-[0.66rem] text-ink-2 tabular">
                  {p.source} · relevance {p.score.toFixed(2)}
                </p>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}

function Ledger({ ledger }: Pick<Props, 'ledger'>) {
  return (
    <section className="mt-10">
      <div className="flex items-baseline justify-between">
        <p className="label">Desk ledger</p>
        <p className="font-mono text-[0.68rem] text-ink-2 tabular">{ledger.length || '—'}</p>
      </div>

      {ledger.length === 0 ? (
        <p className="mt-3 max-w-[38ch] text-[0.9rem] leading-relaxed text-ink-2">
          Every tool the desk uses — policy search, claim lookup, claim submission — is recorded here with its outcome.
        </p>
      ) : (
        <table className="mt-3 w-full border-t border-ink font-mono text-[0.72rem] tabular">
          <tbody>
            {ledger.map((row, i) => {
              const ok = row.status === 'success' && !(row.result as { error?: unknown } | null)?.error
              return (
                <tr key={`${row.at}-${i}`} className="border-b border-rule align-top">
                  <td className="py-2 pr-3 whitespace-nowrap text-ink-2">{clock(new Date(row.at))}</td>
                  <td className="py-2 pr-3 whitespace-nowrap">{row.name}</td>
                  <td className="w-full py-2 pr-3 break-words text-ink-2">
                    {describeToolCall(row.name, row.args, row.result)}
                  </td>
                  <td className={`py-2 text-right ${ok ? 'text-ink' : 'text-stamp'}`}>{ok ? '✓' : '✕'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}
    </section>
  )
}
