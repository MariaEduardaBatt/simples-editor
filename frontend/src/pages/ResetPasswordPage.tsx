import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { GalaxyBackground } from '../components/GalaxyBackground'

export function ResetPasswordPage() {
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const hash = window.location.hash
    if (!hash.includes('type=recovery')) {
      navigate('/login', { replace: true })
      return
    }
    setChecking(false)
  }, [navigate])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!password || !confirmPassword) {
      setError('Preencha todos os campos.')
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

    const { error: updateError } = await supabase.auth.updateUser({ password })

    setLoading(false)

    if (updateError) {
      setError(updateError.message)
      return
    }

    setDone(true)
  }

  if (checking) {
    return (
      <main className="relative flex min-h-screen items-center justify-center px-6">
        <GalaxyBackground />
        <section className="glow-purple glass relative w-full max-w-md rounded-3xl p-8 text-center">
          <p className="text-sm text-white/60">Verificando...</p>
        </section>
      </main>
    )
  }

  if (done) {
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
            Senha redefinida!
          </h1>
          <p className="mt-4 text-sm leading-6 text-white/40">
            Sua senha foi alterada com sucesso. Faca login com sua nova senha.
          </p>

          <Link
            to="/login"
            className="mt-8 inline-block w-full rounded-xl bg-gradient-to-r from-nebula-500 to-cyan-500 px-4 py-3 text-sm font-medium text-white transition hover:from-nebula-400 hover:to-cyan-400"
          >
            Ir para o login
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
          Redefinir senha
        </h1>
        <p className="mt-2 text-sm leading-6 text-white/40">
          Escolha uma nova senha para sua conta.
        </p>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit} noValidate>
          <div>
            <label htmlFor="password" className="text-xs font-medium uppercase tracking-wider text-white/40">Nova senha</label>
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
            <label htmlFor="confirmPassword" className="text-xs font-medium uppercase tracking-wider text-white/40">Confirmar nova senha</label>
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
            {loading ? 'Redefinindo...' : 'Redefinir senha'}
          </button>
        </form>
      </section>
    </main>
  )
}
