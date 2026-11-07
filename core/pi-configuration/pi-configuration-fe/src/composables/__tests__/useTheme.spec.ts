import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const stubSystemDark = (dark: boolean) =>
  vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: dark }))

const loadTheme = async () => {
  vi.resetModules()
  return (await import('../useTheme')).useTheme()
}

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    delete document.documentElement.dataset.theme
    delete document.documentElement.dataset.bsTheme
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('follows the OS preference when nothing is saved', async () => {
    stubSystemDark(true)
    expect((await loadTheme()).theme.value).toBe('dark')
    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(document.documentElement.dataset.bsTheme).toBe('dark')

    stubSystemDark(false)
    expect((await loadTheme()).theme.value).toBe('light')
    expect(document.documentElement.dataset.theme).toBe('light')
    expect(document.documentElement.dataset.bsTheme).toBe('light')
  })

  it('toggles, applies to the document, and persists across reloads', async () => {
    stubSystemDark(false)
    const { theme, toggleTheme } = await loadTheme()

    toggleTheme()
    await Promise.resolve()
    expect(theme.value).toBe('dark')
    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(document.documentElement.dataset.bsTheme).toBe('dark')
    expect(localStorage.getItem('theme')).toBe('dark')

    // A saved choice wins over the OS preference.
    expect((await loadTheme()).theme.value).toBe('dark')

    const reloaded = await loadTheme()
    reloaded.toggleTheme()
    await Promise.resolve()
    expect(document.documentElement.dataset.theme).toBe('light')
    expect(document.documentElement.dataset.bsTheme).toBe('light')
    expect(localStorage.getItem('theme')).toBe('light')
  })

  it('ignores invalid saved values', async () => {
    stubSystemDark(true)
    localStorage.setItem('theme', 'purple')
    expect((await loadTheme()).theme.value).toBe('dark')
  })
})
