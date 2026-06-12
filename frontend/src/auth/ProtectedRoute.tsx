import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './useAuth'
import { GalaxyBackground } from '../components/GalaxyBackground'

export function ProtectedRoute() {
  const { loading, session } = useAuth()

  if (loading) {
    return (
      <main className="relative flex min-h-screen items-center justify-center">
        <GalaxyBackground />
        <div className="glass glow-purple relative rounded-2xl px-8 py-6">
          <p className="text-sm text-white/40">Carregando sessao...</p>
        </div>
      </main>
    )
  }

  if (!session) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
