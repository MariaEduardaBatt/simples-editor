import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { GalaxyBackground } from '../components/GalaxyBackground'

export function RegisterPage() {
  const { signUp } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const trimmedEmail = email.trim()
    if (!trimmedEmail || !password || !confirmPassword) {
      setError('Preencha todos os campos.')
      return
    }

    if (!trimmedEmail.includes('@')) {
      setError('Informe um email valido.')
      return
    }

    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres.')
      return
    }

    if (password !== confirmPassword) {
      setError('As senhas nao conferem.')
      return
    }

    setLoading(true)
    setError(null)

    const { error: signUpError } = await signUp(trimmedEmail, password)

    setLoading(false)

    if (signUpError) {
      setError(signUpError.message)
      return
    }

    setSuccess(true)
  }

  if (success) {
    return (
      <main className="relative flex min-h-screen items-center justify-center px-6">
        <GalaxyBackground />
        <section className="glow-purple glass relative w-full max-w-md rounded-3xl p-8 text-center">
          <div className="flex items-center justify-center gap-3">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-nebula-400 to-cyan-400 text-xs font-bold text-white">
              S
            </span>
            <span className="text-sm uppercase tracking-[0.25em] text-white/60">Simples Editor</span>
          </div>

          <h1 className="mt-8 bg-gradient-to-r from-white to-white/60 bg-clip-text text-3xl font-semibold leading-tight text-transparent">
            Cadastro realizado!
          </h1>
          <p className="mt-4 text-sm leading-6 text-white/40">
            Enviamos um email de confirmacao para <strong className="text-white/60">{email}</strong>.
            Verifique sua caixa de entrada e siga as instrucoes para ativar sua conta.
          </p>

          <Link
            to="/login"
            className="mt-8 inline-block w-full rounded-xl bg-gradient-to-r from-nebula-500 to-cyan-500 px-4 py-3 text-sm font-medium text-white transition hover:from-nebula-400 hover:to-cyan-400"
          >
            Voltar para o login
          </Link>
        </section>
      </main>
    )
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
          Criar conta
        </h1>
        <p className="mt-2 text-sm leading-6 text-white/40">
          Cadastre-se para usar a IDE Simples Editor.
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
              autoComplete="new-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="text-xs font-medium uppercase tracking-wider text-white/40">Confirmar Senha</label>
            <input
              id="confirmPassword"
              className="mt-2 w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none ring-0 transition focus:border-nebula-400/50 focus:ring-1 focus:ring-nebula-400/20"
              type="password"
              name="confirmPassword"
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
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
            {loading ? 'Cadastrando...' : 'Cadastrar'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-white/30">
          Ja tem uma conta?{' '}
          <Link to="/login" className="text-nebula-400 hover:text-nebula-300 transition">
            Entrar
          </Link>
        </p>
      </section>
    </main>
  )
}
