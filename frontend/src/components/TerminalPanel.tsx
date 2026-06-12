export function TerminalPanel() {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-2">
        <span className="text-xs font-medium uppercase tracking-wider text-white/40">
          Terminal
        </span>
        <span className="rounded-md border border-white/[0.06] bg-white/[0.03] px-2 py-0.5 text-[10px] text-white/30">
          Ctrl+C interrompe
        </span>
      </div>
      <div className="flex min-h-0 flex-1 items-center justify-center bg-[#0a0a0f]">
        <div className="text-center">
          <p className="font-mono text-sm text-white/20">
            ── Terminal aguardando execução ──
          </p>
          <p className="mt-2 font-mono text-xs text-white/10">
            Pressione Run para compilar e executar seu programa
          </p>
        </div>
      </div>
    </div>
  )
}
