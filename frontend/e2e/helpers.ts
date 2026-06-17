import { type Page } from '@playwright/test'

const RUN_BUTTON = 'button:has-text("Run")'
const STOP_BUTTON = 'button:has-text("Stop")'
const LOGOUT_BUTTON = 'button:has-text("Sair")'

export async function clickRun(page: Page) {
  await page.click(RUN_BUTTON)
}

export async function clickStop(page: Page) {
  await page.click(STOP_BUTTON)
}

export async function clickLogout(page: Page) {
  await page.click(LOGOUT_BUTTON)
}

export async function waitForRunEnabled(page: Page) {
  await page.waitForSelector(`${RUN_BUTTON}:not([disabled])`)
}

export async function waitForStopEnabled(page: Page) {
  await page.waitForSelector(`${STOP_BUTTON}:not([disabled])`)
}

export async function waitForStopDisabled(page: Page) {
  await page.waitForSelector(`${STOP_BUTTON}[disabled]`)
}

export async function setEditorContent(page: Page, code: string) {
  await page.evaluate((text: string) => {
    const editor = (window as Record<string, unknown>).__monacoEditor as {
      getModel?: () => { setValue?: (v: string) => void } | null
    } | null
    const model = editor?.getModel?.()
    if (model) {
      model.setValue?.(text)
    }
  }, code)
}

export async function getEditorContent(page: Page): Promise<string> {
  return page.evaluate(() => {
    const editor = (window as Record<string, unknown>).__monacoEditor as {
      getModel?: () => { getValue?: () => string } | null
    } | null
    const model = editor?.getModel?.()
    return model?.getValue?.() ?? ''
  })
}

export async function getTerminalText(page: Page): Promise<string> {
  return page.evaluate(() => {
    const term = (window as Record<string, unknown>).__xtermTerminal as {
      buffer?: { active?: { length?: number; getLine?: (y: number) => { translateToString?: () => string } | null } }
    } | null
    const buffer = term?.buffer?.active
    if (!buffer || typeof buffer.length !== 'number') return ''
    const lines: string[] = []
    for (let y = 0; y < buffer.length; y++) {
      const line = buffer.getLine?.(y)
      if (line) {
        lines.push(line.translateToString?.() ?? '')
      }
    }
    return lines.join('\n')
  })
}

export async function waitForTerminalText(page: Page, text: string, timeout = 25_000) {
  await page.waitForFunction(
    (expected: string) => {
      const term = (window as Record<string, unknown>).__xtermTerminal as {
        buffer?: { active?: { length?: number; getLine?: (y: number) => { translateToString?: () => string } | null } }
      } | null
      const buffer = term?.buffer?.active
      if (!buffer || typeof buffer.length !== 'number') return false
      for (let y = 0; y < buffer.length; y++) {
        const line = buffer.getLine?.(y)
        if (line && (line.translateToString?.() ?? '').includes(expected)) {
          return true
        }
      }
      return false
    },
    text,
    { timeout },
  )
}

export function isLoginPage(page: Page) {
  return page.locator('h1:has-text("Entrar na IDE")')
}

export function isIdePage(page: Page) {
  return page.locator('text=Simples Editor')
}
