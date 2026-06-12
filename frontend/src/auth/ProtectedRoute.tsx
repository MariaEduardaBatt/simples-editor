import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './useAuth'

export function ProtectedRoute() {
  const { loading, session } = useAuth()

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center text-slate-300">
        Loading session...
      </main>
    )
  }

  if (!session) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
