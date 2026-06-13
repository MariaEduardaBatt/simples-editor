import { useAuth } from '../auth/useAuth'

interface CompileError {
  phase: string
  line: number
  column: number
  message: string
}

interface CompileResult {
  nasm?: string
  error?: string | CompileError
}

interface ToolbarProps {
  code?: string
  onCompileResult?: (result: CompileResult) => void
  isCompiling: boolean
  setIsCompiling: (v: boolean) => void
}

export function Toolbar({ code, onCompileResult, isCompiling, setIsCompiling }: ToolbarProps) {
  const { session } = useAuth()

  async function handleRun() {
    setIsCompiling(true)
    onCompileResult?.({})

    try {
      const source = code ?? ''

      const res = await fetch('/api/compile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ code: source }),
      })

      const text = await res.text()
      if (!text) {
        onCompileResult?.({ error: `servidor retornou ${res.status} (resposta vazia)` })
        return
      }

      const data = JSON.parse(text)
      onCompileResult?.(data)
    } catch (err) {
      onCompileResult?.({ error: String(err) })
    } finally {
      setIsCompiling(false)
    }
  }

  return (
    <div className="mx-6 flex items-center gap-3">
      <button
        className="flex items-center gap-2 rounded-xl border border-nebula-500/30 bg-nebula-500/10 px-5 py-2 text-sm font-medium text-nebula-300 transition hover:bg-nebula-500/20 hover:text-nebula-200 disabled:cursor-not-allowed disabled:opacity-50"
        type="button"
        onClick={handleRun}
        disabled={isCompiling}
      >
        <span className="text-base leading-none">{isCompiling ? '◌' : '▶'}</span>
        {isCompiling ? 'compilando…' : 'Run'}
      </button>
      <button
        className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white/40 transition hover:border-white/20 hover:text-white/60 disabled:opacity-30"
        type="button"
        disabled
      >
        <span className="text-base leading-none">■</span>
        Stop
      </button>
      <button
        className="rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-2 text-sm text-white/30 transition hover:border-white/10 hover:text-white/50"
        type="button"
      >
        Limpar
      </button>

      <div className="ml-auto">
        <button
          className="flex items-center gap-1 rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-2 text-sm text-white/30 transition hover:border-white/10 hover:text-white/50"
          type="button"
        >
          exemplos
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    </div>
  )
}
