export function NasmPanel() {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-2">
        <span className="text-xs font-medium uppercase tracking-wider text-white/40">
          NASM x32
        </span>
        <span className="rounded-md border border-white/[0.06] bg-white/[0.03] px-2 py-0.5 text-[10px] text-white/30">
          read-only
        </span>
      </div>
      <div className="flex min-h-0 flex-1 items-center justify-center">
        <div className="text-center">
          <p className="text-sm text-white/20">Nenhum assembly gerado</p>
          <p className="mt-1 text-xs text-white/10">
            Execute seu programa para ver o NASM correspondente
          </p>
        </div>
      </div>
    </div>
  )
}
