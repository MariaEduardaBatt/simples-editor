import { useCallback, useEffect, useRef, useState } from 'react'

type ConnectionState = 'idle' | 'connecting' | 'compiling' | 'executing' | 'done' | 'error'

interface WsIncoming {
  type: string
  [key: string]: unknown
}

interface RunCallbacks {
  onStdout?: (data: string) => void
  onStderr?: (data: string) => void
  onExit?: (code: number, durationMs: number) => void
  onAsmGenerated?: (asm: string) => void
  onCompileError?: (phase: string, line: number, column: number, message: string) => void
  onAssembleError?: (stderr: string) => void
  onLinkError?: (stderr: string) => void
  onTimeout?: (limitS: number) => void
  onInternalError?: (message: string) => void
  onCompileStarted?: () => void
  onExecStarted?: () => void
}

export function useRunWebSocket(callbacks: RunCallbacks, token: string) {
  const wsRef = useRef<WebSocket | null>(null)
  const [state, setState] = useState<ConnectionState>('idle')

  const close = useCallback(() => {
    const ws = wsRef.current
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      ws.close()
    }
    wsRef.current = null
    setState('idle')
  }, [])

  const stop = useCallback(() => {
    const ws = wsRef.current
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'stop' }))
    }
  }, [])

  const sendStdin = useCallback((data: string) => {
    const ws = wsRef.current
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'stdin', data }))
    }
  }, [])

  const start = useCallback((code: string) => {
    if (!token) return
    close()

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/ws/run`

    setState('connecting')
    const ws = new WebSocket(url, ['bearer.' + token])

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'compile_and_run', code }))
    }

    ws.onmessage = (ev: MessageEvent) => {
      let msg: WsIncoming
      try {
        msg = JSON.parse(ev.data as string)
      } catch {
        return
      }

      switch (msg.type) {
        case 'compile_started':
          setState('compiling')
          callbacks.onCompileStarted?.()
          break

        case 'asm_generated':
          callbacks.onAsmGenerated?.(msg.asm as string)
          break

        case 'exec_started':
          setState('executing')
          callbacks.onExecStarted?.()
          break

        case 'stdout':
          callbacks.onStdout?.(msg.data as string)
          break

        case 'stderr':
          callbacks.onStderr?.(msg.data as string)
          break

        case 'exit':
          setState('done')
          callbacks.onExit?.(msg.code as number, msg.duration_ms as number)
          break

        case 'compile_error':
          setState('error')
          callbacks.onCompileError?.(
            msg.phase as string,
            msg.line as number,
            msg.column as number,
            msg.message as string,
          )
          break

        case 'assemble_error':
          setState('error')
          callbacks.onAssembleError?.(msg.stderr as string)
          break

        case 'link_error':
          setState('error')
          callbacks.onLinkError?.(msg.stderr as string)
          break

        case 'timeout':
          setState('error')
          callbacks.onTimeout?.(msg.limit_s as number)
          break

        case 'internal_error':
          setState('error')
          callbacks.onInternalError?.(msg.message as string)
          break

        case 'pong':
          break
      }
    }

    ws.onerror = () => {
      setState('error')
      callbacks.onInternalError?.('conexão perdida com o servidor')
    }

    ws.onclose = () => {
      if (wsRef.current === ws) {
        wsRef.current = null
        setState((prev) => (prev === 'idle' || prev === 'error' ? prev : 'done'))
      }
    }

    wsRef.current = ws
  }, [callbacks, close, token])

  useEffect(() => {
    return () => {
      close()
    }
  }, [close])

  return { start, stop, sendStdin, close, state }
}
