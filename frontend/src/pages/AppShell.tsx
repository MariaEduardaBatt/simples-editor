import { useCallback, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Group, Panel, Separator } from 'react-resizable-panels'
import { useAuth } from '../auth/useAuth'
import { GalaxyBackground } from '../components/GalaxyBackground'
import { EditorPanel } from '../components/EditorPanel'
import { NasmPanel } from '../components/NasmPanel'
import { TerminalPanel, type TerminalPanelHandle } from '../components/TerminalPanel'
import { Toolbar } from '../components/Toolbar'
import { useRunWebSocket } from '../hooks/useRunWebSocket'

export function AppShell() {
  const navigate = useNavigate()
  const { session, signOut } = useAuth()
  const [code, setCode] = useState('')
  const [nasmOutput, setNasmOutput] = useState<string | undefined>()
  const [compileMarkers, setCompileMarkers] = useState<Array<{ line: number; column: number; message: string }>>([])

  const terminalRef = useRef<TerminalPanelHandle>(null)

  const handleStdout = useCallback((data: string) => {
    terminalRef.current?.write(data)
  }, [])

  const handleStderr = useCallback((data: string) => {
    terminalRef.current?.write(data)
  }, [])

  const handleExit = useCallback((code: number, durationMs: number) => {
    terminalRef.current?.write(`\r\n\x1b[2mprocesso encerrado com código ${code} (${durationMs}ms)\x1b[0m\r\n`)
  }, [])

  const handleAsmGenerated = useCallback((asm: string) => {
    setNasmOutput(asm)
    setCompileMarkers([])
  }, [])

  const handleCompileError = useCallback(
    (phase: string, line: number, column: number, message: string) => {
      setNasmOutput(undefined)
      terminalRef.current?.write(`\r\n\x1b[31m[${phase}:${line}:${column}] ${message}\x1b[0m\r\n`)
      setCompileMarkers([{ line, column, message }])
    },
    [],
  )

  const handleAssembleError = useCallback((stderr: string) => {
    setNasmOutput(undefined)
    terminalRef.current?.write(`\r\n\x1b[31m[erro de montagem]\n${stderr}\x1b[0m\r\n`)
  }, [])

  const handleLinkError = useCallback((stderr: string) => {
    setNasmOutput(undefined)
    terminalRef.current?.write(`\r\n\x1b[31m[erro de ligação]\n${stderr}\x1b[0m\r\n`)
  }, [])

  const handleTimeout = useCallback((limitS: number) => {
    terminalRef.current?.write(`\r\n\x1b[33m[tempo limite de ${limitS}s excedido]\x1b[0m\r\n`)
  }, [])

  const handleInternalError = useCallback((message: string) => {
    terminalRef.current?.write(`\r\n\x1b[31m[erro interno] ${message}\x1b[0m\r\n`)
  }, [])

  const handleCompileStarted = useCallback(() => {
    terminalRef.current?.clear()
    terminalRef.current?.write('\x1b[2mcompilando…\x1b[0m\r\n')
  }, [])

  const handleExecStarted = useCallback(() => {
    terminalRef.current?.write('\x1b[2mexecutando…\x1b[0m\r\n')
  }, [])

  const ws = useRunWebSocket({
    onStdout: handleStdout,
    onStderr: handleStderr,
    onExit: handleExit,
    onAsmGenerated: handleAsmGenerated,
    onCompileError: handleCompileError,
    onAssembleError: handleAssembleError,
    onLinkError: handleLinkError,
    onTimeout: handleTimeout,
    onInternalError: handleInternalError,
    onCompileStarted: handleCompileStarted,
    onExecStarted: handleExecStarted,
  }, session?.access_token ?? '')

  const isRunning = ws.state === 'connecting' || ws.state === 'compiling' || ws.state === 'executing'

  const handleCodeChange = useCallback((newCode: string) => {
    setCode(newCode)
  }, [])

  const handleRun = useCallback(
    (source: string) => {
      ws.start(source)
    },
    [ws],
  )

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
        <Toolbar code={code} onRun={handleRun} onStop={ws.stop} isRunning={isRunning} />

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
                    <NasmPanel code={nasmOutput} isCompiling={isRunning} />
                  </div>
                </Panel>
              </Group>
            </Panel>
            <Separator className="flex h-3 items-center justify-center group">
              <div className="h-0.5 w-12 rounded-full bg-white/[0.06] transition group-hover:bg-white/20" />
            </Separator>
            <Panel defaultSize={30} minSize={15}>
              <div className="h-full overflow-hidden rounded-2xl border border-white/[0.06] bg-[#0a0a0f]">
                <TerminalPanel ref={terminalRef} onStdin={ws.sendStdin} />
              </div>
            </Panel>
          </Group>
        </div>
      </div>
    </main>
  )
}
