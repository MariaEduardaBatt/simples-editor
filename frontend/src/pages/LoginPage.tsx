import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { GalaxyBackground } from '../components/GalaxyBackground'

export function LoginPage() {
  const navigate = useNavigate()
  const { signIn } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const trimmedEmail = email.trim()
    if (!trimmedEmail || !password) {
      setError('Informe um email e uma senha.')
      return
    }

    if (!trimmedEmail.includes('@')) {
      setError('Informe um email valido.')
      return
    }

    setLoading(true)
    setError(null)

    const { error: signInError } = await signIn(trimmedEmail, password)

    setLoading(false)

    if (signInError) {
      setError(signInError.message)
      return
    }

    navigate('/', { replace: true })
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center px-6">
      <GalaxyBackground />
      <section className="glow-purple glass relative w-full max-w-md rounded-3xl p-8">
        <div className="flex items-center gap-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-nebula-400 to-cyan-400 text-xs font-bold text-white">
            S
          </span>
          <span className="text-sm uppercase tracking-[0.25em] text-white/60">Simples Editor</span>
        </div>

        <h1 className="mt-8 bg-gradient-to-r from-white to-white/60 bg-clip-text text-3xl font-semibold leading-tight text-transparent">
          Entrar na IDE
        </h1>
        <p className="mt-2 text-sm leading-6 text-white/40">
          Use seu email institucional e senha do Supabase para acessar o ambiente.
        </p>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit} noValidate>
          <div>
            <label htmlFor="email" className="text-xs font-medium uppercase tracking-wider text-white/40">Email</label>
            <input
              id="email"
              className="mt-2 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none ring-0 transition focus:border-nebula-400/50 focus:ring-1 focus:ring-nebula-400/20"
              type="email"
              name="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>

          <div>
            <label htmlFor="password" className="text-xs font-medium uppercase tracking-wider text-white/40">Senha</label>
            <input
              id="password"
              className="mt-2 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none ring-0 transition focus:border-nebula-400/50 focus:ring-1 focus:ring-nebula-400/20"
              type="password"
              name="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>

          {error ? (
            <p role="alert" className="rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-300">
              {error}
            </p>
          ) : null}

          <button
            className="w-full rounded-xl bg-gradient-to-r from-nebula-500 to-cyan-500 px-4 py-3 text-sm font-medium text-white transition hover:from-nebula-400 hover:to-cyan-400 disabled:cursor-not-allowed disabled:from-white/10 disabled:to-white/5 disabled:text-white/30"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </section>
    </main>
  )
}
