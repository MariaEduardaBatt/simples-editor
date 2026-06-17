import { chromium, type FullConfig } from '@playwright/test'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const SUPABASE_URL = process.env.SUPABASE_URL ?? ''
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY ?? ''
const TEST_EMAIL = process.env.E2E_TEST_EMAIL ?? ''
const TEST_PASSWORD = process.env.E2E_TEST_PASSWORD ?? ''

const STORAGE_PATH = resolve(__dirname, '.auth.json')

async function globalSetup(config: FullConfig) {
  if (!TEST_EMAIL || !TEST_PASSWORD) {
    console.warn('[auth.setup] E2E_TEST_EMAIL/E2E_TEST_PASSWORD not set — skipping auth setup')
    return
  }

  const supabaseHost = new URL(SUPABASE_URL).hostname

  const response = await fetch(
    `https://${supabaseHost}/auth/v1/token?grant_type=password`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_ANON_KEY,
      },
      body: JSON.stringify({
        email: TEST_EMAIL,
        password: TEST_PASSWORD,
      }),
    },
  )

  if (!response.ok) {
    throw new Error(`[auth.setup] Supabase login failed: ${response.status} ${await response.text()}`)
  }

  const session = await response.json()

  const browser = await chromium.launch()
  const page = await browser.newPage()
  const baseUrl = config.projects[0].use.baseURL ?? 'http://localhost:80'

  const storageKey = `sb-${supabaseHost}-auth-token`

  await page.goto(baseUrl + '/login')
  await page.evaluate(
    ({ key, value }: { key: string; value: string }) => {
      localStorage.setItem(key, value)
    },
    { key: storageKey, value: JSON.stringify(session) },
  )

  await page.context().storageState({ path: STORAGE_PATH })
  await browser.close()
}

export default globalSetup
