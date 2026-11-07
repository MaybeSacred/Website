import { ref, watchEffect } from 'vue'

export type Theme = 'light' | 'dark'

const STORAGE_KEY = 'theme'

const readSavedTheme = (): Theme | null => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved === 'light' || saved === 'dark' ? saved : null
  } catch {
    return null
  }
}

const systemTheme = (): Theme =>
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'

// Shared across components so the map canvas can follow the page theme.
const theme = ref<Theme>(readSavedTheme() ?? systemTheme())

watchEffect(() => {
  if (typeof document !== 'undefined') {
    document.documentElement.dataset.theme = theme.value
    document.documentElement.dataset.bsTheme = theme.value
  }
})

export const useTheme = () => {
  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    try {
      localStorage.setItem(STORAGE_KEY, theme.value)
    } catch {
      // Storage may be unavailable (e.g. private mode); the toggle still works for this session.
    }
  }
  return { theme, toggleTheme }
}
