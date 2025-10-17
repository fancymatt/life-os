import { useEffect } from 'react'
import './Toast.css'

/**
 * Toast Notification Component
 *
 * Displays toast notifications at the bottom of the screen.
 * Similar to the Composer's "Generating..." badge.
 *
 * @param {string} message - The message to display
 * @param {string} type - Type of toast: 'info', 'success', 'error', 'loading'
 * @param {number} duration - Auto-dismiss duration in ms (0 = no auto-dismiss)
 * @param {function} onClose - Callback when toast is dismissed
 */
function Toast({ message, type = 'info', duration = 0, onClose }) {
  useEffect(() => {
    // Auto-dismiss after duration (except for loading and duration=0)
    if (duration > 0 && type !== 'loading') {
      const timer = setTimeout(() => {
        if (onClose) onClose()
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [duration, type, onClose])

  const getIcon = () => {
    switch (type) {
      case 'loading':
        return <div className="toast-spinner"></div>
      case 'success':
        return '✓'
      case 'error':
        return '✕'
      default:
        return 'ℹ'
    }
  }

  const getClassName = () => {
    let className = 'toast'
    if (type) className += ` toast-${type}`
    return className
  }

  return (
    <div className={getClassName()}>
      <div className="toast-icon">{getIcon()}</div>
      <span className="toast-message">{message}</span>
    </div>
  )
}

export default Toast
