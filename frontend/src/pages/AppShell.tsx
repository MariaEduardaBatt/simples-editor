import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { GalaxyBackground } from '../components/GalaxyBackground'
import { SimplesEditor } from '../components/SimplesEditor'

export function AppShell() {
  const navigate = useNavigate()
  const { session, signOut } = useAuth()

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

      <div className="mx-6 my-4 flex min-h-0 flex-1">
        <section className="glass flex flex-1 overflow-hidden rounded-2xl">
          <SimplesEditor />
        </section>
      </div>
    </main>
  )
}
