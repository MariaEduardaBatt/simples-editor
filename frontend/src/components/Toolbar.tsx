interface ToolbarProps {
  code?: string
  onRun?: (code: string) => void
  onStop?: () => void
  isRunning: boolean
}

export function Toolbar({ code, onRun, onStop, isRunning }: ToolbarProps) {
  function handleRun() {
    const source = code ?? ''
    onRun?.(source)
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
