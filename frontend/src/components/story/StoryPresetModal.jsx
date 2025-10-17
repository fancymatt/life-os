import { useState } from 'react'
import api from '../../api/client'

/**
 * Story Preset Creation Modal
 *
 * Generic modal for creating story themes, audiences, and prose styles.
 * Renders fields based on category configuration.
 */
function StoryPresetModal({ isOpen, onClose, onPresetCreated, category, config }) {
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  })
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.name.trim()) {
      setError('Name is required')
      return
    }

    setCreating(true)
    setError(null)

    try {
      // Build the preset data based on category
      let defaultData = {}

      // Add category-specific default fields
      if (category === 'story_themes') {
        defaultData = {
          suggested_name: formData.name.trim(),
          description: formData.description.trim() || 'A story theme',
          setting_guidance: '',
          tone: '',
          common_elements: [],
          story_structure_notes: '',
          world_building: ''
        }
      } else if (category === 'story_audiences') {
        defaultData = {
          suggested_name: formData.name.trim(),
          description: formData.description.trim() || 'A story audience',
          age_range: '',
          reading_level: '',
          content_considerations: '',
          engagement_style: ''
        }
      } else if (category === 'story_prose_styles') {
        defaultData = {
          suggested_name: formData.name.trim(),
          description: formData.description.trim() || 'A prose style',
          tone: '',
          pacing: '',
          vocabulary_level: '',
          sentence_structure: '',
          narrative_voice: ''
        }
      }

      const response = await api.post(`/presets/${category}/`, {
        name: formData.name.trim(),
        data: defaultData,
        notes: `Created via entity browser`
      })

      // Reset form
      setFormData({
        name: '',
        description: ''
      })

      // Notify parent and close
      if (onPresetCreated) {
        onPresetCreated(response.data)
      }
      onClose()
    } catch (err) {
      console.error('Failed to create preset:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to create preset')
    } finally {
      setCreating(false)
    }
  }

  const handleCancel = () => {
    if (!creating) {
      setFormData({
        name: '',
        description: ''
      })
      setError(null)
      onClose()
    }
  }

  if (!isOpen) return null

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
      onClick={handleCancel}
    >
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(30, 30, 40, 0.98) 0%, rgba(20, 20, 30, 0.98) 100%)',
          borderRadius: '16px',
          maxWidth: '600px',
          width: '100%',
          maxHeight: '90vh',
          overflow: 'auto',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1)',
          padding: '2rem'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ color: 'white', margin: '0 0 0.5rem 0', fontSize: '1.75rem' }}>
            {config.icon} Create New {config.entityType.charAt(0).toUpperCase() + config.entityType.slice(1)}
          </h2>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', margin: 0, fontSize: '0.95rem' }}>
            Add a new {config.entityType} to your collection. You can customize the fields after creation.
          </p>
        </div>

        {error && (
          <div style={{
            marginBottom: '1.5rem',
            padding: '1rem',
            background: 'rgba(255, 100, 100, 0.1)',
            border: '1px solid rgba(255, 100, 100, 0.3)',
            borderRadius: '8px',
            color: '#ff6b6b'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Name */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{
              display: 'block',
              color: 'rgba(255, 255, 255, 0.9)',
              marginBottom: '0.5rem',
              fontWeight: 500
            }}>
              Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder={`Enter ${config.entityType} name...`}
              disabled={creating}
              style={{
                width: '100%',
                padding: '0.75rem',
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                color: 'white',
                fontSize: '1rem',
                outline: 'none'
              }}
            />
          </div>

          {/* Description */}
          <div style={{ marginBottom: '2rem' }}>
            <label style={{
              display: 'block',
              color: 'rgba(255, 255, 255, 0.9)',
              marginBottom: '0.5rem',
              fontWeight: 500
            }}>
              Description (optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              placeholder={`Brief description of this ${config.entityType}...`}
              disabled={creating}
              rows="3"
              style={{
                width: '100%',
                padding: '0.75rem',
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                color: 'white',
                fontSize: '0.95rem',
                resize: 'vertical',
                fontFamily: 'inherit',
                outline: 'none'
              }}
            />
            <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem', margin: '0.5rem 0 0 0' }}>
              You can add more specific fields like keywords, atmosphere, tone, etc. after creation.
            </p>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={handleCancel}
              disabled={creating}
              style={{
                padding: '0.75rem 1.5rem',
                background: 'rgba(255, 255, 255, 0.1)',
                color: 'white',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: 500,
                cursor: creating ? 'not-allowed' : 'pointer',
                opacity: creating ? 0.5 : 1
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating || !formData.name.trim()}
              style={{
                padding: '0.75rem 1.5rem',
                background: creating || !formData.name.trim()
                  ? 'rgba(102, 126, 234, 0.3)'
                  : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: 500,
                cursor: creating || !formData.name.trim() ? 'not-allowed' : 'pointer',
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
              }}
            >
              {creating ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default StoryPresetModal
