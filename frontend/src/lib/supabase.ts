import { createClient } from '@supabase/supabase-js'
import { requiredEnv } from './env'

function normalizeUrl(raw: string): string {
  try {
    const url = new URL(raw)
    return `${url.protocol}//${url.host}`
  } catch {
    return raw
  }
}

export const supabase = createClient(
  normalizeUrl(requiredEnv('VITE_SUPABASE_URL')),
  requiredEnv('VITE_SUPABASE_ANON_KEY')
)
