import { test, expect } from '@playwright/test'

const TEST_EMAIL = process.env.E2E_TEST_EMAIL ?? ''
const TEST_PASSWORD = process.env.E2E_TEST_PASSWORD ?? ''
const HAS_CREDENTIALS = !!(TEST_EMAIL && TEST_PASSWORD)

test.describe('LoginPage', () => {
  test('redirects unauthenticated user to /login', async ({ page }) => {
    await page.goto('/')
    await page.waitForURL('/login')
    await expect(page.locator('h1')).toContainText('Entrar na IDE')
  })

  test('shows login form with email, password and submit button', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('#email')).toBeVisible()
    await expect(page.locator('#password')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('shows error when email is empty', async ({ page }) => {
    await page.goto('/login')
    await page.fill('#email', '')
    await page.fill('#password', 'somepass')
    await page.click('button[type="submit"]')
    await expect(page.locator('[role="alert"]')).toContainText('Informe um email e uma senha.')
  })

  test('shows error when password is empty', async ({ page }) => {
    await page.goto('/login')
    await page.fill('#email', 'test@test.com')
    await page.fill('#password', '')
    await page.click('button[type="submit"]')
    await expect(page.locator('[role="alert"]')).toContainText('Informe um email e uma senha.')
  })

  test('shows error for invalid email format', async ({ page }) => {
    await page.goto('/login')
    await page.fill('#email', 'invalid-email')
    await page.fill('#password', 'somepass')
    await page.click('button[type="submit"]')
    await expect(page.locator('[role="alert"]')).toContainText('Informe um email valido.')
  })

  test('shows loading state on submit', async ({ page }) => {
    await page.goto('/login')
    await page.fill('#email', 'test@test.com')
    await page.fill('#password', 'password123')
    await page.click('button[type="submit"]')
    await expect(page.locator('button[type="submit"]')).toBeDisabled()
    await expect(page.locator('button[type="submit"]')).toContainText('Entrando...')
  })

  test.describe('with valid credentials', () => {
    test.skip(!HAS_CREDENTIALS, 'E2E_TEST_EMAIL/E2E_TEST_PASSWORD not set')

    test('logs in successfully and redirects to IDE', async ({ page }) => {
      await page.goto('/login')
      await page.fill('#email', TEST_EMAIL)
      await page.fill('#password', TEST_PASSWORD)
      await page.click('button[type="submit"]')

      await page.waitForURL('/')
      await expect(page.locator('text=Simples Editor')).toBeVisible()
    })
  })
})
