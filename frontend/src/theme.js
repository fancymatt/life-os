/**
 * Life-OS Design System & Theme Configuration
 *
 * Provides a comprehensive design token system with support for:
 * - Light/Dark/Auto themes
 * - Color tokens
 * - Spacing scale
 * - Typography scale
 * - Shadows & elevation
 * - Border radius values
 * - Transitions
 */

export const themes = {
  light: {
    // Background colors
    'bg-primary': '#ffffff',
    'bg-secondary': '#f5f5f7',
    'bg-tertiary': '#e8e8ed',
    'bg-elevated': '#ffffff',
    'bg-overlay': 'rgba(0, 0, 0, 0.5)',

    // Surface colors
    'surface-default': '#ffffff',
    'surface-subtle': '#f5f5f7',
    'surface-hover': '#f0f0f5',
    'surface-active': '#e8e8ed',

    // Text colors
    'text-primary': '#1d1d1f',
    'text-secondary': '#6e6e73',
    'text-tertiary': '#86868b',
    'text-disabled': '#c7c7cc',
    'text-inverse': '#ffffff',

    // Border colors
    'border-default': 'rgba(0, 0, 0, 0.12)',
    'border-subtle': 'rgba(0, 0, 0, 0.08)',
    'border-strong': 'rgba(0, 0, 0, 0.2)',

    // Brand colors
    'brand-primary': '#667eea',
    'brand-secondary': '#764ba2',
    'brand-hover': '#5568d3',
    'brand-active': '#4556c2',

    // Semantic colors
    'success': '#10b981',
    'success-bg': '#d1fae5',
    'warning': '#f59e0b',
    'warning-bg': '#fef3c7',
    'error': '#ef4444',
    'error-bg': '#fee2e2',
    'info': '#3b82f6',
    'info-bg': '#dbeafe',

    // Status colors
    'status-running': '#3b82f6',
    'status-completed': '#10b981',
    'status-failed': '#ef4444',
    'status-archived': '#f59e0b'
  },

  dark: {
    // Background colors
    'bg-primary': '#0f0f1e',
    'bg-secondary': '#1a1a2e',
    'bg-tertiary': '#16213e',
    'bg-elevated': '#1f1f2e',
    'bg-overlay': 'rgba(0, 0, 0, 0.7)',

    // Surface colors
    'surface-default': '#1a1a2e',
    'surface-subtle': '#16213e',
    'surface-hover': 'rgba(255, 255, 255, 0.08)',
    'surface-active': 'rgba(255, 255, 255, 0.12)',

    // Text colors
    'text-primary': '#ffffff',
    'text-secondary': 'rgba(255, 255, 255, 0.7)',
    'text-tertiary': 'rgba(255, 255, 255, 0.5)',
    'text-disabled': 'rgba(255, 255, 255, 0.3)',
    'text-inverse': '#1d1d1f',

    // Border colors
    'border-default': 'rgba(255, 255, 255, 0.12)',
    'border-subtle': 'rgba(255, 255, 255, 0.08)',
    'border-strong': 'rgba(255, 255, 255, 0.2)',

    // Brand colors
    'brand-primary': '#667eea',
    'brand-secondary': '#764ba2',
    'brand-hover': '#7b8ef0',
    'brand-active': '#8f9df4',

    // Semantic colors
    'success': '#34d399',
    'success-bg': 'rgba(16, 185, 129, 0.15)',
    'warning': '#fbbf24',
    'warning-bg': 'rgba(245, 158, 11, 0.15)',
    'error': '#f87171',
    'error-bg': 'rgba(239, 68, 68, 0.15)',
    'info': '#60a5fa',
    'info-bg': 'rgba(59, 130, 246, 0.15)',

    // Status colors
    'status-running': '#60a5fa',
    'status-completed': '#34d399',
    'status-failed': '#f87171',
    'status-archived': '#fbbf24'
  }
}

// Spacing scale (based on 4px grid)
export const spacing = {
  '0': '0',
  '1': '0.25rem',  // 4px
  '2': '0.5rem',   // 8px
  '3': '0.75rem',  // 12px
  '4': '1rem',     // 16px
  '5': '1.25rem',  // 20px
  '6': '1.5rem',   // 24px
  '8': '2rem',     // 32px
  '10': '2.5rem',  // 40px
  '12': '3rem',    // 48px
  '16': '4rem',    // 64px
  '20': '5rem',    // 80px
  '24': '6rem'     // 96px
}

// Typography scale
export const typography = {
  // Font families
  fontFamily: {
    sans: "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif",
    mono: "'Monaco', 'Courier New', monospace"
  },

  // Font sizes
  fontSize: {
    'xs': '0.75rem',    // 12px
    'sm': '0.875rem',   // 14px
    'base': '1rem',     // 16px
    'lg': '1.125rem',   // 18px
    'xl': '1.25rem',    // 20px
    '2xl': '1.5rem',    // 24px
    '3xl': '1.875rem',  // 30px
    '4xl': '2.25rem',   // 36px
    '5xl': '3rem'       // 48px
  },

  // Font weights
  fontWeight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700'
  },

  // Line heights
  lineHeight: {
    none: '1',
    tight: '1.25',
    snug: '1.375',
    normal: '1.5',
    relaxed: '1.625',
    loose: '2'
  }
}

// Shadows & elevation
export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)'
}

// Border radius
export const borderRadius = {
  none: '0',
  sm: '0.25rem',   // 4px
  base: '0.375rem', // 6px
  md: '0.5rem',    // 8px
  lg: '0.75rem',   // 12px
  xl: '1rem',      // 16px
  '2xl': '1.5rem', // 24px
  full: '9999px'
}

// Transitions
export const transitions = {
  fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
  base: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
  slow: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
  slower: '500ms cubic-bezier(0.4, 0, 0.2, 1)'
}

// Z-index scale
export const zIndex = {
  base: 0,
  dropdown: 100,
  sticky: 200,
  fixed: 300,
  overlay: 400,
  modal: 500,
  popover: 600,
  toast: 700,
  tooltip: 800
}

/**
 * Apply theme to document
 * @param {string} theme - 'light', 'dark', or 'auto'
 */
export function applyTheme(theme) {
  const root = document.documentElement

  // Handle auto theme
  if (theme === 'auto') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    theme = prefersDark ? 'dark' : 'light'
  }

  // Apply theme class
  root.setAttribute('data-theme', theme)

  // Apply CSS variables
  const colors = themes[theme]
  Object.entries(colors).forEach(([key, value]) => {
    root.style.setProperty(`--color-${key}`, value)
  })

  // Apply spacing variables
  Object.entries(spacing).forEach(([key, value]) => {
    root.style.setProperty(`--spacing-${key}`, value)
  })

  // Apply typography variables
  root.style.setProperty('--font-sans', typography.fontFamily.sans)
  root.style.setProperty('--font-mono', typography.fontFamily.mono)

  Object.entries(typography.fontSize).forEach(([key, value]) => {
    root.style.setProperty(`--text-${key}`, value)
  })

  Object.entries(typography.fontWeight).forEach(([key, value]) => {
    root.style.setProperty(`--font-${key}`, value)
  })

  // Apply shadow variables
  Object.entries(shadows).forEach(([key, value]) => {
    root.style.setProperty(`--shadow-${key}`, value)
  })

  // Apply border radius variables
  Object.entries(borderRadius).forEach(([key, value]) => {
    root.style.setProperty(`--radius-${key}`, value)
  })

  // Apply transition variables
  Object.entries(transitions).forEach(([key, value]) => {
    root.style.setProperty(`--transition-${key}`, value)
  })

  // Apply z-index variables
  Object.entries(zIndex).forEach(([key, value]) => {
    root.style.setProperty(`--z-${key}`, value)
  })
}

/**
 * Get current theme preference
 * @returns {string} 'light', 'dark', or 'auto'
 */
export function getThemePreference() {
  return localStorage.getItem('theme') || 'auto'
}

/**
 * Save theme preference
 * @param {string} theme - 'light', 'dark', or 'auto'
 */
export function saveThemePreference(theme) {
  localStorage.setItem('theme', theme)
  applyTheme(theme)
}

/**
 * Initialize theme on app load
 */
export function initializeTheme() {
  const savedTheme = getThemePreference()
  applyTheme(savedTheme)

  // Listen for system theme changes when in auto mode
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (getThemePreference() === 'auto') {
      applyTheme('auto')
    }
  })
}
