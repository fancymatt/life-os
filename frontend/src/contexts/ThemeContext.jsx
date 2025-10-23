import { createContext, useContext, useState, useEffect } from 'react'
import { initializeTheme, applyTheme, getThemePreference, saveThemePreference } from '../theme'

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(getThemePreference())

  // Initialize theme on mount
  useEffect(() => {
    initializeTheme()
  }, [])

  // Change theme
  const changeTheme = (newTheme) => {
    setTheme(newTheme)
    saveThemePreference(newTheme)
  }

  // Get effective theme (resolves 'auto' to 'light' or 'dark')
  const getEffectiveTheme = () => {
    if (theme === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return theme
  }

  const value = {
    theme,
    effectiveTheme: getEffectiveTheme(),
    setTheme: changeTheme
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
