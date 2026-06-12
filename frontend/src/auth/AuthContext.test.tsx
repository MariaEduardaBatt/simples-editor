import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { AuthProvider } from './AuthContext'
import { useAuth } from './useAuth'

vi.mock('../lib/supabase', () => {
  const mockSession = { user: { email: 'student@example.edu' } }

  return {
    supabase: {
      auth: {
        getSession: vi.fn().mockResolvedValue({ data: { session: mockSession } }),
        onAuthStateChange: vi.fn().mockReturnValue({
          data: { subscription: { unsubscribe: vi.fn() } }
        }),
        signInWithPassword: vi.fn(),
        signOut: vi.fn()
      }
    }
  }
})

function Probe() {
  const { loading, session } = useAuth()

  return (
    <div>
      <span data-testid="loading">{loading ? 'loading' : 'ready'}</span>
      <span data-testid="user">{session?.user.email ?? 'none'}</span>
    </div>
  )
}

describe('AuthProvider', () => {
  it('renders a session from Supabase on startup', async () => {
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      expect(screen.getByTestId('user')).toHaveTextContent('student@example.edu')
    })
  })
})
