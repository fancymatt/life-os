import { useEffect } from 'react'

/**
 * Keyboard Shortcuts Help Modal
 *
 * Displays all available keyboard shortcuts for the EntityBrowser.
 * Opens with '?' key, closes with Escape or clicking outside.
 */
function KeyboardShortcutsModal({ isOpen, onClose }) {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
  const modKey = isMac ? '⌘' : 'Ctrl'

  useEffect(() => {
    if (!isOpen) return

    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const shortcuts = [
    {
      category: 'Navigation',
      items: [
        { keys: ['Escape'], description: 'Go back to list' },
        { keys: ['←', '→'], description: 'Navigate between entities' },
        { keys: [modKey, 'K'], description: 'Focus search' }
      ]
    },
    {
      category: 'Editing',
      items: [
        { keys: [modKey, 'S'], description: 'Save changes' },
        { keys: [modKey, 'Enter'], description: 'Save and close' },
        { keys: ['Delete'], description: 'Delete current entity' }
      ]
    },
    {
      category: 'Help',
      items: [
        { keys: ['?'], description: 'Show this help' }
      ]
    }
  ]

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.7)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 10000,
        padding: '2rem'
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(30, 30, 40, 0.98) 0%, rgba(20, 20, 30, 0.98) 100%)',
          borderRadius: '16px',
          maxWidth: '600px',
          width: '100%',
          maxHeight: '80vh',
          overflow: 'auto',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1)',
          padding: '2rem'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ color: 'white', margin: '0 0 0.5rem 0', fontSize: '1.75rem' }}>
            Keyboard Shortcuts
          </h2>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', margin: 0, fontSize: '0.95rem' }}>
            Press ? to toggle this help
          </p>
        </div>

        {shortcuts.map((section, idx) => (
          <div key={idx} style={{ marginBottom: idx < shortcuts.length - 1 ? '2rem' : 0 }}>
            <h3 style={{
              color: 'rgba(255, 255, 255, 0.8)',
              margin: '0 0 1rem 0',
              fontSize: '1.1rem',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              {section.category}
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {section.items.map((item, itemIdx) => (
                <div
                  key={itemIdx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem 1rem',
                    background: 'rgba(255, 255, 255, 0.03)',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.08)'
                  }}
                >
                  <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: '0.95rem' }}>
                    {item.description}
                  </span>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    {item.keys.map((key, keyIdx) => (
                      <span key={keyIdx} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        {keyIdx > 0 && (
                          <span style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: '0.85rem', margin: '0 0.25rem' }}>
                            +
                          </span>
                        )}
                        <kbd
                          style={{
                            padding: '0.35rem 0.65rem',
                            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
                            border: '1px solid rgba(102, 126, 234, 0.3)',
                            borderRadius: '6px',
                            color: '#a5b4fc',
                            fontSize: '0.85rem',
                            fontWeight: 500,
                            fontFamily: 'monospace',
                            minWidth: '28px',
                            textAlign: 'center',
                            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)'
                          }}
                        >
                          {key}
                        </kbd>
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        <div style={{
          marginTop: '2rem',
          paddingTop: '1.5rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          textAlign: 'center'
        }}>
          <button
            onClick={onClose}
            style={{
              padding: '0.75rem 2rem',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'transform 0.2s, box-shadow 0.2s',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)'
              e.target.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)'
              e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)'
            }}
          >
            Got it!
          </button>
        </div>
      </div>
    </div>
  )
}

export default KeyboardShortcutsModal
