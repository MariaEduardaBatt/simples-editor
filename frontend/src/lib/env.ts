export function requiredEnv(name: 'VITE_SUPABASE_URL' | 'VITE_SUPABASE_ANON_KEY'): string {
  const value = import.meta.env[name]

  if (!value) {
    throw new Error(`${name} is required`)
  }

  return value
}
