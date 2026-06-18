import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react'
import { Terminal } from 'xterm'
import { FitAddon } from '@xterm/addon-fit'
import 'xterm/css/xterm.css'

export interface TerminalPanelHandle {
  write: (data: string) => void
  clear: () => void
  reset: () => void
}

interface TerminalPanelProps {
  onStdin?: (data: string) => void
}

export const TerminalPanel = forwardRef<TerminalPanelHandle, TerminalPanelProps>(
  function TerminalPanel({ onStdin }, ref) {
    const containerRef = useRef<HTMLDivElement>(null)
    const terminalRef = useRef<Terminal | null>(null)
    const fitRef = useRef<FitAddon | null>(null)
    const stdinBufferRef = useRef('')

    function flushBuffer() {
      if (!stdinBufferRef.current) return
      const line = stdinBufferRef.current + '\r'
      stdinBufferRef.current = ''
      onStdinRef.current?.(line)
    }

    useImperativeHandle(
      ref,
      () => ({
        write(data: string) {
          terminalRef.current?.write(data)
        },
        clear() {
          stdinBufferRef.current = ''
          terminalRef.current?.clear()
        },
        reset() {
          stdinBufferRef.current = ''
          const t = terminalRef.current
          if (t) {
            t.clear()
            t.write('── Terminal aguardando execução ──\r\n')
          }
        },
      }),
      [],
    )

  const onStdinRef = useRef(onStdin)
  onStdinRef.current = onStdin

    useEffect(() => {
      const container = containerRef.current
      if (!container) return

      const fitAddon = new FitAddon()
      fitRef.current = fitAddon

      const term = new Terminal({
        cursorBlink: true,
        cursorStyle: 'block',
        fontSize: 13,
        fontFamily: "'JetBrains Mono', 'Cascadia Code', 'Fira Code', monospace",
        theme: {
          background: '#0a0a0f',
          foreground: '#c8d6e5',
          cursor: '#00d4aa',
          selectionBackground: '#1a3a3a',
          black: '#1a1a2e',
          red: '#ff6b6b',
          green: '#00d4aa',
          yellow: '#ffd93d',
          blue: '#6bcbff',
          magenta: '#c084fc',
          cyan: '#22d3ee',
          white: '#c8d6e5',
          brightBlack: '#3d3d5c',
          brightRed: '#ff6b6b',
          brightGreen: '#00d4aa',
          brightYellow: '#ffd93d',
          brightBlue: '#6bcbff',
          brightMagenta: '#c084fc',
          brightCyan: '#22d3ee',
          brightWhite: '#ffffff',
        },
        allowProposedApi: true,
        cols: 80,
        rows: 12,
      })

      term.loadAddon(fitAddon)
      term.open(container)
      term.write('── Terminal aguardando execução ──\r\n')

      const disposables: { dispose: () => void }[] = []

      disposables.push(term.onData((data) => {
        for (let i = 0; i < data.length; i++) {
          const ch = data[i]

          if (ch === '\x7f') {
            if (stdinBufferRef.current.length > 0) {
              stdinBufferRef.current = stdinBufferRef.current.slice(0, -1)
              term.write('\b \b')
            }
            continue
          }

          if (ch === '\r' || ch === '\n') {
            const line = stdinBufferRef.current + '\r'
            stdinBufferRef.current = ''
            term.write('\r\n')
            onStdinRef.current?.(line)
            continue
          }

          if (ch.length === 1 && ch.charCodeAt(0) < 0x20 && ch !== '\t') {
            continue
          }

          stdinBufferRef.current += ch
          term.write(ch)
        }
      }))

      terminalRef.current = term
      ;(window as unknown as Record<string, unknown>).__xtermTerminal = term

      const resizeObserver = new ResizeObserver(() => {
        requestAnimationFrame(() => {
          fitAddon.fit()
        })
      })
      resizeObserver.observe(container)

      return () => {
        for (const d of disposables) d.dispose()
        resizeObserver.disconnect()
        term.dispose()
        terminalRef.current = null
        fitRef.current = null
      }
    }, [onStdin])

    useEffect(() => {
      const fitAddon = fitRef.current
      if (!fitAddon) return
      const timer = setTimeout(() => fitAddon.fit(), 0)
      return () => clearTimeout(timer)
    }, [])

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
        <div
          ref={containerRef}
          className="flex-1 overflow-hidden p-2"
          style={{ minHeight: 0 }}
        />
      </div>
    )
  },
)
