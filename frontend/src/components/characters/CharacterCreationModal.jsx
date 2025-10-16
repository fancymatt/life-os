import { useState } from 'react'
import api from '../../api/client'

/**
 * Character Creation Modal
 *
 * Modal for creating new characters with name, personality, tags, and reference image.
 * Physical appearance is automatically analyzed from the reference image in the background.
 */
function CharacterCreationModal({ isOpen, onClose, onCharacterCreated }) {
  const [formData, setFormData] = useState({
    name: '',
    personality: '',
    tags: ''
  })
  const [referenceImage, setReferenceImage] = useState(null)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setReferenceImage(file)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.name.trim()) {
      setError('Character name is required')
      return
    }

    setCreating(true)
    setError(null)

    try {
      //Create FormData for multipart upload
      const submitData = new FormData()
      submitData.append('name', formData.name.trim())
      submitData.append('personality', formData.personality.trim())

      // Parse tags from comma-separated string
      const tags = formData.tags.split(',').map(t => t.trim()).filter(t => t)
      submitData.append('tags', JSON.stringify(tags))

      // Add reference image if provided
      if (referenceImage) {
        submitData.append('reference_image', referenceImage)
      }

      const response = await api.post('/characters/multipart', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      // Reset form
      setFormData({
        name: '',
        personality: '',
        tags: ''
      })
      setReferenceImage(null)

      // Notify parent and close
      if (onCharacterCreated) {
        onCharacterCreated(response.data)
      }
      onClose()
    } catch (err) {
      console.error('Failed to create character:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to create character')
    } finally {
      setCreating(false)
    }
  }

  const handleCancel = () => {
    if (!creating) {
      setFormData({
        name: '',
        personality: '',
        tags: ''
      })
      setReferenceImage(null)
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
            👤 Create New Character
          </h2>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', margin: 0, fontSize: '0.95rem' }}>
            Add a new character to your collection
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
          {/* Character Name */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{
              display: 'block',
              color: 'rgba(255, 255, 255, 0.9)',
              marginBottom: '0.5rem',
              fontWeight: 500
            }}>
              Character Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Enter character name..."
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

          {/* Personality */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{
              display: 'block',
              color: 'rgba(255, 255, 255, 0.9)',
              marginBottom: '0.5rem',
              fontWeight: 500
            }}>
              Personality
            </label>
            <textarea
              value={formData.personality}
              onChange={(e) => handleChange('personality', e.target.value)}
              placeholder="Describe the character's personality traits..."
              disabled={creating}
              rows="4"
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
          </div>

          {/* Tags */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{
              display: 'block',
              color: 'rgba(255, 255, 255, 0.9)',
              marginBottom: '0.5rem',
              fontWeight: 500
            }}>
              Tags (comma-separated)
            </label>
            <input
              type="text"
              value={formData.tags}
              onChange={(e) => handleChange('tags', e.target.value)}
              placeholder="protagonist, hero, adventure..."
              disabled={creating}
              style={{
                width: '100%',
                padding: '0.75rem',
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                color: 'white',
                fontSize: '0.95rem',
                outline: 'none'
              }}
            />
          </div>

          {/* Reference Image Upload */}
          <div style={{ marginBottom: '2rem' }}>
            <label style={{
              display: 'block',
              color: 'rgba(255, 255, 255, 0.9)',
              marginBottom: '0.5rem',
              fontWeight: 500
            }}>
              Reference Image
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              disabled={creating}
              style={{
                width: '100%',
                padding: '0.75rem',
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                color: 'white',
                fontSize: '0.95rem'
              }}
            />
            <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem', margin: '0.5rem 0 0 0', lineHeight: '1.4' }}>
              Upload an image of your character. Physical appearance will be automatically analyzed in the background.
            </p>
            {referenceImage && (
              <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(102, 126, 234, 0.1)', borderRadius: '8px', border: '1px solid rgba(102, 126, 234, 0.3)' }}>
                <p style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: '0.85rem', margin: '0 0 0.25rem 0' }}>
                  ✓ Selected: {referenceImage.name}
                </p>
                <p style={{ color: 'rgba(102, 126, 234, 0.9)', fontSize: '0.8rem', margin: 0 }}>
                  Appearance will be analyzed automatically after creation
                </p>
              </div>
            )}
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
              {creating
                ? (referenceImage ? 'Creating & Analyzing...' : 'Creating...')
                : 'Create Character'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CharacterCreationModal
