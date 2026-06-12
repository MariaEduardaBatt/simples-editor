import { describe, expect, it, vi } from 'vitest'
import { requiredEnv } from './env'

describe('requiredEnv', () => {
  it('throws when a required env var is missing', () => {
    vi.stubEnv('VITE_SUPABASE_URL', '')

    expect(() => requiredEnv('VITE_SUPABASE_URL')).toThrow('VITE_SUPABASE_URL is required')
  })
})
