import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { GalaxyBackground } from '../components/GalaxyBackground'

export function AppShell() {
  const navigate = useNavigate()
  const { session, signOut } = useAuth()

  async function handleLogout() {
    await signOut()
    navigate('/login', { replace: true })
  }

  return (
    <main className="relative min-h-screen">
      <GalaxyBackground />
      <div className="relative mx-auto max-w-5xl px-6 py-6">
        <header className="glass glow-purple rounded-2xl px-6 py-4">
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

        <section className="glass glow-cyan mx-auto mt-6 rounded-2xl px-6 py-8">
          <h1 className="bg-gradient-to-r from-nebula-400 to-cyan-400 bg-clip-text text-2xl font-semibold text-transparent">
            IDE liberada
          </h1>
          <p className="mt-3 text-sm leading-6 text-white/40">
            Esta area confirma o acesso autenticado; os paineis de editor, NASM e terminal entram em
            issues seguintes.
          </p>
        </section>
      </div>
    </main>
  )
}
