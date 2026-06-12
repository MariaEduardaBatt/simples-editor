import { SimplesEditor } from './SimplesEditor'

export function EditorPanel() {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-2">
        <span className="text-xs font-medium uppercase tracking-wider text-white/40">
          Editor SIMPLES
        </span>
      </div>
      <div className="min-h-0 flex-1">
        <SimplesEditor />
      </div>
    </div>
  )
}
