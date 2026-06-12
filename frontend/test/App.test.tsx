import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import App from '../src/App'

vi.mock('../src/lib/supabase', () => ({
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

vi.mock('../src/auth/useAuth', () => ({
  useAuth: () => ({
    loading: false,
    session: null,
    signIn: vi.fn(),
    signOut: vi.fn()
  })
}))

describe('App scaffold', () => {
  it('redirects unauthenticated users to /login', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )

    expect(screen.getByRole('heading', { name: /entrar na ide/i })).toBeInTheDocument()
  })
})
