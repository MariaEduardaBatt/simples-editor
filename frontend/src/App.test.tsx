import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import App from './App'

vi.mock('./lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
      onAuthStateChange: vi.fn().mockReturnValue({
        data: { subscription: { unsubscribe: vi.fn() } }
      }),
      signInWithPassword: vi.fn(),
      signOut: vi.fn()
    }
  }
}))

vi.mock('./auth/useAuth', () => ({
  useAuth: () => ({
    loading: false,
    session: null,
    signIn: vi.fn(),
    signOut: vi.fn()
  })
}))

describe('App routing', () => {
  it('redirects unauthenticated users to /login', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    )

    expect(screen.getByRole('heading', { name: /entrar na ide/i })).toBeInTheDocument()
  })
})
