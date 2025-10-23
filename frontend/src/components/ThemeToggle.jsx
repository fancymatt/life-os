import { useState, useRef, useEffect } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import './ThemeToggle.css'

function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  const themes = [
    { value: 'light', label: 'Light', icon: '☀️' },
    { value: 'dark', label: 'Dark', icon: '🌙' },
    { value: 'auto', label: 'Auto', icon: '🌓' }
  ]

  const currentTheme = themes.find(t => t.value === theme) || themes[2]

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme)
    setIsOpen(false)
  }

  return (
    <div className="theme-toggle" ref={dropdownRef}>
      <button
        className="theme-toggle-button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle theme"
        title={`Current theme: ${currentTheme.label}`}
      >
        <span className="theme-icon">{currentTheme.icon}</span>
        <span className="theme-label">{currentTheme.label}</span>
        <span className={`theme-chevron ${isOpen ? 'open' : ''}`}>▼</span>
      </button>

      {isOpen && (
        <div className="theme-dropdown">
          {themes.map((themeOption) => (
            <button
              key={themeOption.value}
              className={`theme-option ${theme === themeOption.value ? 'active' : ''}`}
              onClick={() => handleThemeChange(themeOption.value)}
            >
              <span className="theme-option-icon">{themeOption.icon}</span>
              <span className="theme-option-label">{themeOption.label}</span>
              {theme === themeOption.value && (
                <span className="theme-checkmark">✓</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default ThemeToggle
