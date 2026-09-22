import { useEffect, useMemo, useState } from 'react'
import { CaseFile } from './components/CaseFile'
import { Composer } from './components/Composer'
import { Conversation } from './components/Conversation'
import { Letterhead } from './components/Letterhead'
import { useChat } from './hooks/useChat'
import { useHealth } from './hooks/useHealth'

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
  const line = useHealth()
  const { entries, sending, send, clear, caseFile } = useChat(userId)

  useEffect(() => {
    try {
      localStorage.setItem(USER_KEY, userId)
    } catch {
      /* ignore */
    }
  }, [userId])

  // Number cited passages once per section, in order of first citation, so the
  // [n] markers in the correspondence match the case file.
  const passages = useMemo(() => {
    const seen = new Map<string, number>()
    const list: Array<(typeof caseFile.citations)[number] & { number: number }> = []
    for (const c of caseFile.citations) {
      if (seen.has(c.section)) continue
      const number = seen.size + 1
      seen.set(c.section, number)
      list.push({ ...c, number })
    }
    return { list, numbers: seen }
  }, [caseFile.citations])

  return (
    <div className="mx-auto max-w-[1400px]">
      <Letterhead line={line} />

      <main className="grid gap-12 px-4 py-8 sm:px-8 lg:grid-cols-12 lg:px-12">
        <section className="lg:col-span-7">
          <Conversation entries={entries} sending={sending} citationNumbers={passages.numbers} onPick={send} />
          <div className="mt-6">
            <Composer disabled={sending} onSend={send} />
          </div>
        </section>

        <div className="lg:col-span-5">
          <CaseFile
            userId={userId}
            onChangeUser={setUserId}
            onNewFile={clear}
            passages={passages.list}
            ledger={caseFile.ledger}
          />
        </div>
      </main>

      <footer className="px-4 pb-8 sm:px-8 lg:px-12">
        <div className="border-t border-rule pt-3 font-mono text-[0.66rem] text-ink-2">
          Answers are drawn from the OmniCare General Insurance Policy 2026. Claim decisions are made by adjusters, never by
          this desk.
        </div>
      </footer>
    </div>
  )
}
