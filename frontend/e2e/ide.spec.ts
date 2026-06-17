import { test, expect } from '@playwright/test'
import { clickRun, clickStop, clickLogout, waitForTerminalText, setEditorContent, getTerminalText } from './helpers'

const TEST_EMAIL = process.env.E2E_TEST_EMAIL ?? ''
const TEST_PASSWORD = process.env.E2E_TEST_PASSWORD ?? ''
const HAS_CREDENTIALS = !!(TEST_EMAIL && TEST_PASSWORD)

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login')
  await page.fill('#email', TEST_EMAIL)
  await page.fill('#password', TEST_PASSWORD)
  await page.click('button[type="submit"]')
  await page.waitForURL('/')
}

test.describe('IDE unauthenticated', () => {
  test('redirects unauthenticated user to /login', async ({ page }) => {
    await page.goto('/')
    await page.waitForURL('/login')
    await expect(page.locator('h1')).toContainText('Entrar na IDE')
  })
})

test.describe('IDE authenticated flow', () => {
  test.skip(!HAS_CREDENTIALS, 'E2E_TEST_EMAIL/E2E_TEST_PASSWORD not set')

  test.beforeEach(async ({ page }) => {
    await login(page)
  })

  test('IDE loads with all panels visible', async ({ page }) => {
    await expect(page.locator('text=Simples Editor')).toBeVisible()
    await expect(page.locator('text=Run')).toBeVisible()
    await expect(page.locator('text=Stop')).toBeVisible()
    await expect(page.locator('text=Terminal')).toBeVisible()
    await expect(page.locator('.monaco-editor')).toBeVisible()
  })

  test('header shows user email', async ({ page }) => {
    await expect(page.locator('text=@').first()).toBeVisible()
  })

  test('run button is enabled, stop button is disabled on load', async ({ page }) => {
    await page.waitForSelector('.monaco-editor')
    await expect(page.locator('button:has-text("Run")')).toBeEnabled()
    await expect(page.locator('button:has-text("Stop")')).toBeDisabled()
  })

  test('logout navigates to /login', async ({ page }) => {
    await clickLogout(page)
    await page.waitForURL('/login')
    await expect(page.locator('h1')).toContainText('Entrar na IDE')
  })
})

test.describe('Run and execution flow', () => {
  test.skip(!HAS_CREDENTIALS, 'E2E_TEST_EMAIL/E2E_TEST_PASSWORD not set')

  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.waitForSelector('.monaco-editor')
  })

  test('shows compiling message when Run is clicked', async ({ page }) => {
    test.setTimeout(90_000)

    await clickRun(page)
    await waitForTerminalText(page, 'compilando')
    const text = await getTerminalText(page)
    expect(text).toContain('compilando')
  })

  test('stop button interrupts running code', async ({ page }) => {
    test.setTimeout(90_000)

    await setEditorContent(page, `programa loop_infinito
inicio
  enquanto 1 = 1 faca
  fimenquanto
fim`)

    await clickRun(page)
    await page.waitForTimeout(2000)

    await clickStop(page)
    await waitForTerminalText(page, 'processo encerrado')
  })

  test('code with stdin accepts terminal input', async ({ page }) => {
    test.setTimeout(90_000)

    await setEditorContent(page, `programa entrada
  inteiro x
inicio
  leia x
  escreva "OK"
fim`)

    await clickRun(page)
    await page.waitForTimeout(3000)
    await page.keyboard.type('42')
    await page.keyboard.press('Enter')
    await waitForTerminalText(page, 'OK')
  })
})

test.describe('Compile error flow', () => {
  test.skip(!HAS_CREDENTIALS, 'E2E_TEST_EMAIL/E2E_TEST_PASSWORD not set')

  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.waitForSelector('.monaco-editor')
  })

  test('invalid code shows error in terminal', async ({ page }) => {
    test.setTimeout(90_000)

    await setEditorContent(page, `programa erro
inicio
  escreva "teste
fim`)

    await clickRun(page)
    await waitForTerminalText(page, 'erro')
  })
})
