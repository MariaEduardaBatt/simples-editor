import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error)
    console.error('Component stack:', info.componentStack)
  }

  render() {
    if (this.state.error) {
      return (
        <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#020015] p-8">
          <h1 className="text-xl font-bold text-red-400">Erro na aplicacao</h1>
          <pre className="max-w-2xl overflow-auto rounded-lg border border-red-900/50 bg-red-950/40 p-4 text-sm text-red-300">
            {this.state.error.message}
          </pre>
          <button
            className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white/60 transition hover:border-white/20 hover:bg-white/[0.06]"
            onClick={() => this.setState({ error: null })}
          >
            Tentar novamente
          </button>
        </main>
      )
    }

    return this.props.children
  }
}
