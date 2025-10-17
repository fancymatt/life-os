import { useState } from 'react'
import api from '../../api/client'
import Toast from '../Toast'

/**
 * Re-Analyze Character Appearance Button
 *
 * Calls the character appearance analyzer and updates the character's appearance fields.
 */
function ReAnalyzeButton({ character, onUpdate, variant = 'default' }) {
  const [analyzing, setAnalyzing] = useState(false)
  const [toast, setToast] = useState(null)

  const handleReAnalyze = async () => {
    if (!character.referenceImageUrl) {
      setToast({ message: 'No reference image available for analysis', type: 'error', duration: 3000 })
      return
    }

    setAnalyzing(true)
    setToast({ message: 'Analyzing appearance...', type: 'loading' })

    try {
      const response = await api.post(`/characters/${character.characterId}/re-analyze-appearance`)

      // Call the update handler with new data
      if (onUpdate) {
        onUpdate(response.data)
      }

      const successMessage = variant === 'edit'
        ? 'Appearance re-analyzed! Remember to save your changes.'
        : 'Appearance re-analyzed successfully!'

      setToast({ message: successMessage, type: 'success', duration: 4000 })
    } catch (err) {
      console.error('Failed to re-analyze appearance:', err)
      const errorMessage = err.response?.data?.detail || 'Failed to re-analyze appearance'
      setToast({ message: errorMessage, type: 'error', duration: 5000 })
    } finally {
      setAnalyzing(false)
    }
  }

  if (!character.referenceImageUrl) {
    return null
  }

  // Compact button for detail view
  if (variant === 'compact') {
    return (
      <>
        <button
          onClick={handleReAnalyze}
          disabled={analyzing}
          style={{
            padding: '0.5rem 1rem',
            background: analyzing ? 'rgba(100, 100, 100, 0.3)' : 'rgba(76, 175, 80, 0.2)',
            border: '1px solid rgba(76, 175, 80, 0.5)',
            borderRadius: '6px',
            color: analyzing ? 'rgba(255, 255, 255, 0.5)' : '#4CAF50',
            cursor: analyzing ? 'not-allowed' : 'pointer',
            fontSize: '0.9rem',
            fontWeight: 500,
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            if (!analyzing) {
              e.target.style.background = 'rgba(76, 175, 80, 0.3)'
              e.target.style.borderColor = 'rgba(76, 175, 80, 0.7)'
            }
          }}
          onMouseLeave={(e) => {
            if (!analyzing) {
              e.target.style.background = 'rgba(76, 175, 80, 0.2)'
              e.target.style.borderColor = 'rgba(76, 175, 80, 0.5)'
            }
          }}
        >
          {analyzing ? '🔄 Analyzing...' : '🔍 Re-Analyze Appearance'}
        </button>
        {toast && (
          <Toast
            message={toast.message}
            type={toast.type}
            duration={toast.duration}
            onClose={() => setToast(null)}
          />
        )}
      </>
    )
  }

  // Full-width button for edit view
  return (
    <>
      <div style={{ marginBottom: '2rem', paddingBottom: '1.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <button
          onClick={handleReAnalyze}
          disabled={analyzing}
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            background: analyzing ? 'rgba(100, 100, 100, 0.3)' : 'rgba(76, 175, 80, 0.2)',
            border: '1px solid rgba(76, 175, 80, 0.5)',
            borderRadius: '6px',
            color: analyzing ? 'rgba(255, 255, 255, 0.5)' : '#4CAF50',
            cursor: analyzing ? 'not-allowed' : 'pointer',
            fontSize: '0.95rem',
            fontWeight: 500,
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            if (!analyzing) {
              e.target.style.background = 'rgba(76, 175, 80, 0.3)'
              e.target.style.borderColor = 'rgba(76, 175, 80, 0.7)'
            }
          }}
          onMouseLeave={(e) => {
            if (!analyzing) {
              e.target.style.background = 'rgba(76, 175, 80, 0.2)'
              e.target.style.borderColor = 'rgba(76, 175, 80, 0.5)'
            }
          }}
        >
          {analyzing ? '🔄 Analyzing...' : '🔍 Re-Analyze Appearance from Image'}
        </button>
      </div>
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          duration={toast.duration}
          onClose={() => setToast(null)}
        />
      )}
    </>
  )
}

export default ReAnalyzeButton
