import { useRef, useState } from 'react'
import { EXAMPLES, type Example } from '../lib/examples'

interface ToolbarProps {
  code?: string
  onRun?: (code: string) => void
  onStop?: () => void
  isRunning: boolean
  onExampleSelect?: (example: Example) => void
  onClear?: () => void
}

export function Toolbar({ code, onRun, onStop, isRunning, onExampleSelect, onClear }: ToolbarProps) {
  const [open, setOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  function handleRun() {
    const source = code ?? ''
    onRun?.(source)
  }

  function handleSelect(example: Example) {
    setOpen(false)
    onExampleSelect?.(example)
  }

  return (
    <div className="mx-6 flex items-center gap-3">
      <button
        className="flex items-center gap-2 rounded-xl border border-nebula-500/30 bg-nebula-500/10 px-5 py-2 text-sm font-medium text-nebula-300 transition enabled:border-nebula-400/60 enabled:bg-nebula-500/20 enabled:text-nebula-200 enabled:hover:bg-nebula-500/30 enabled:hover:text-nebula-100 disabled:cursor-not-allowed disabled:opacity-50"
        type="button"
        onClick={handleRun}
        disabled={isRunning}
      >
        <span className="text-base leading-none">{isRunning ? '◌' : '▶'}</span>
        {isRunning ? 'executando…' : 'Run'}
      </button>
      <button
        className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white/40 transition enabled:border-red-500/50 enabled:bg-red-500/10 enabled:text-red-300 enabled:hover:border-red-400 enabled:hover:bg-red-500/20 enabled:hover:text-red-200 disabled:opacity-30"
        type="button"
        onClick={onStop}
        disabled={!isRunning}
      >
        <span className="text-base leading-none">■</span>
        Stop
      </button>
      <button
        className="rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-2 text-sm text-white/30 transition hover:border-white/10 hover:text-white/50"
        type="button"
        onClick={onClear}
      >
        Limpar
      </button>

      <div className="relative ml-auto" ref={dropdownRef}>
        <button
          className="flex items-center gap-1 rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-2 text-sm text-white/30 transition hover:border-white/10 hover:text-white/50"
          type="button"
          onClick={() => setOpen(!open)}
        >
          exemplos
          <svg className={`h-3 w-3 transition ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {open && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
            <div className="absolute right-0 z-50 mt-2 w-52 overflow-hidden rounded-xl border border-white/[0.08] bg-[#0a0a0f]/95 backdrop-blur-xl">
              <div className="max-h-72 overflow-y-auto py-1">
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex.name}
                    className="flex w-full items-center px-4 py-2 text-left text-sm text-white/60 transition hover:bg-white/[0.04] hover:text-white/90"
                    type="button"
                    onClick={() => handleSelect(ex)}
                  >
                    {ex.label}
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
