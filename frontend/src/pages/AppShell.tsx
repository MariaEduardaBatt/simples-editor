import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Group, Panel, Separator } from 'react-resizable-panels'
import { useAuth } from '../auth/useAuth'
import { GalaxyBackground } from '../components/GalaxyBackground'
import { EditorPanel } from '../components/EditorPanel'
import { NasmPanel } from '../components/NasmPanel'
import { TerminalPanel } from '../components/TerminalPanel'
import { Toolbar } from '../components/Toolbar'

export function AppShell() {
  const navigate = useNavigate()
  const { session, signOut } = useAuth()
  const [code, setCode] = useState('')
  const [nasmOutput, setNasmOutput] = useState<string | undefined>()
  const [terminalMessage, setTerminalMessage] = useState<string | undefined>()
  const [compileMarkers, setCompileMarkers] = useState<Array<{ line: number; column: number; message: string }>>([])
  const [isCompiling, setIsCompiling] = useState(false)

  const handleCodeChange = useCallback((newCode: string) => {
    setCode(newCode)
  }, [])

  const handleCompileResult = useCallback((result: { nasm?: string; error?: string | { phase: string; line: number; column: number; message: string } }) => {
    if (result.nasm) {
      setNasmOutput(result.nasm)
      setTerminalMessage(undefined)
      setCompileMarkers([])
    } else if (result.error) {
      setNasmOutput(undefined)
      if (typeof result.error === 'object') {
        setTerminalMessage(`[${result.error.phase}:${result.error.line}:${result.error.column}] ${result.error.message}`)
        setCompileMarkers([{ line: result.error.line, column: result.error.column, message: result.error.message }])
      } else {
        setTerminalMessage(result.error)
        setCompileMarkers([])
      }
    } else {
      setNasmOutput(undefined)
      setTerminalMessage(undefined)
      setCompileMarkers([])
    }
  }, [])

  async function handleLogout() {
    await signOut()
    navigate('/login', { replace: true })
  }

  return (
    <main className="relative flex h-screen flex-col">
      <GalaxyBackground />
      <header className="glass glow-purple mx-6 mt-6 rounded-2xl px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-nebula-400 to-cyan-400 text-xs font-bold text-white">
              S
            </span>
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-white/60">Simples Editor</p>
              <p className="mt-0.5 text-sm text-white/40">
                {session?.user.email ?? 'usuario autenticado'}
              </p>
            </div>
          </div>
          <button
            className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white/60 transition hover:border-white/20 hover:bg-white/[0.06] hover:text-white/80"
            type="button"
            onClick={handleLogout}
          >
            Sair
          </button>
        </div>
      </header>

      <div className="flex flex-1 flex-col overflow-hidden py-4">
        <Toolbar code={code} onCompileResult={handleCompileResult} isCompiling={isCompiling} setIsCompiling={setIsCompiling} />

        <div className="mx-6 mt-3 min-h-0 flex-1">
          <Group orientation="vertical" className="h-full">
            <Panel defaultSize={70} minSize={30}>
              <Group orientation="horizontal" className="h-full">
                <Panel defaultSize={65} minSize={20} collapsible>
                  <div className="h-full overflow-hidden rounded-2xl border border-white/[0.06] bg-[#0a0a0f]">
                    <EditorPanel code={code} onCodeChange={handleCodeChange} markers={compileMarkers} />
                  </div>
                </Panel>
                <Separator className="flex w-3 items-center justify-center group">
                  <div className="h-12 w-0.5 rounded-full bg-white/[0.06] transition group-hover:bg-white/20" />
                </Separator>
                <Panel defaultSize={35} minSize={10} collapsible>
                  <div className="h-full overflow-hidden rounded-2xl border border-white/[0.06] bg-[#0a0a0f]">
                    <NasmPanel code={nasmOutput} isCompiling={isCompiling} />
                  </div>
                </Panel>
              </Group>
            </Panel>
            <Separator className="flex h-3 items-center justify-center group">
              <div className="h-0.5 w-12 rounded-full bg-white/[0.06] transition group-hover:bg-white/20" />
            </Separator>
            <Panel defaultSize={30} minSize={15}>
              <div className="h-full overflow-hidden rounded-2xl border border-white/[0.06] bg-[#0a0a0f]">
                <TerminalPanel message={terminalMessage} />
              </div>
            </Panel>
          </Group>
        </div>
      </div>
    </main>
  )
}
