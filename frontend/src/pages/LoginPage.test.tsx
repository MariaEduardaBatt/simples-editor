import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { LoginPage } from './LoginPage'
import { AppShell } from './AppShell'

const signIn = vi.fn()

vi.mock('../auth/useAuth', () => ({
  useAuth: () => ({
    loading: false,
    session: null,
    signIn,
    signOut: vi.fn()
  })
}))

vi.mock('../lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn(),
      onAuthStateChange: vi.fn()
    }
  }
}))

describe('LoginPage', () => {
  afterEach(() => cleanup())

  beforeEach(() => {
    signIn.mockReset()
    signIn.mockResolvedValue({ error: null })
  })

  it('shows the email and password fields', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument()
  })

  it('blocks empty submission', async () => {
    const user = userEvent.setup()

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    await user.click(screen.getByRole('button', { name: /entrar/i }))

    expect(screen.getByRole('alert')).toHaveTextContent(/informe/i)
  })

  it('submits credentials and redirects on success', async () => {
    const user = userEvent.setup()

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<AppShell />} />
        </Routes>
      </MemoryRouter>
    )

    await user.type(screen.getByLabelText(/email/i), 'student@example.edu')
    await user.type(screen.getByLabelText(/senha/i), 'secret123')
    await user.click(screen.getByRole('button', { name: /entrar/i }))

    expect(signIn).toHaveBeenCalledWith('student@example.edu', 'secret123')
  })
})
