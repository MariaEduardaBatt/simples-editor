import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'

export function AppShell() {
  const navigate = useNavigate()
  const { session, signOut } = useAuth()

  async function handleLogout() {
    await signOut()
    navigate('/login', { replace: true })
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-6 text-slate-100">
      <header className="mx-auto flex max-w-5xl items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/80 px-5 py-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-sky-400">Simples Editor</p>
          <p className="mt-1 text-sm text-slate-300">Sessao ativa para {session?.user.email ?? 'usuario autenticado'}</p>
        </div>
        <button
          className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-100 hover:border-slate-500"
          type="button"
          onClick={handleLogout}
        >
          Sair
        </button>
      </header>

      <section className="mx-auto mt-6 max-w-5xl rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h1 className="text-2xl font-semibold">IDE liberada</h1>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          Esta area confirma o acesso autenticado; os paineis de editor, NASM e terminal entram em
          issues seguintes.
        </p>
      </section>
    </main>
  )
}
