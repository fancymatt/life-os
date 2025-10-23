import { useState, useEffect } from 'react'
import api from '../../../api/client'
import { formatDate } from './helpers'
import LazyImage from '../LazyImage'

/**
 * Visualization Configs Entity Configuration
 */

/**
 * Visualization Config Editor Component
 * Separate component to allow hooks for loading art styles
 */
function VisualizationConfigEditor({ entity, editedData, editedTitle, handlers }) {
  const [artStyles, setArtStyles] = useState([])
  const [loadingArtStyles, setLoadingArtStyles] = useState(false)

  // Load art styles on mount
  useEffect(() => {
    const loadArtStyles = async () => {
      setLoadingArtStyles(true)
      try {
        const response = await api.get('/presets/art_styles')
        const presets = response.data.presets || response.data || []
        setArtStyles(Array.isArray(presets) ? presets : [])
      } catch (err) {
        console.error('Failed to load art styles:', err)
        setArtStyles([])
      } finally {
        setLoadingArtStyles(false)
      }
    }
    loadArtStyles()
  }, [])

  const formStyle = {
    padding: '2rem'
  }

  const labelStyle = {
    display: 'block',
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: '0.5rem',
    fontWeight: 500,
    fontSize: '0.95rem'
  }

  const inputStyle = {
    width: '100%',
    padding: '0.75rem',
    background: 'rgba(0, 0, 0, 0.3)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '8px',
    color: 'white',
    fontSize: '1rem'
  }

  const fieldStyle = {
    marginBottom: '1.5rem'
  }

  return (
    <div style={formStyle}>
      {/* Display Name */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Display Name *</label>
        <input
          type="text"
          value={editedTitle}
          onChange={(e) => handlers.setEditedTitle(e.target.value)}
          style={inputStyle}
          placeholder="e.g., Product Photography, Lifestyle Shot"
        />
      </div>

      {/* Entity Type */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Entity Type *</label>
        <select
          value={editedData.entity_type || ''}
          onChange={(e) => handlers.updateField('entity_type', e.target.value)}
          style={inputStyle}
          disabled
        >
          <option value="character">Character</option>
          <option value="clothing_item">Clothing Item</option>
          <option value="outfit">Outfit</option>
          <option value="expression">Expression</option>
          <option value="makeup">Makeup</option>
          <option value="accessories">Accessories</option>
          <option value="art_style">Art Style</option>
          <option value="visual_style">Visual Style</option>
          <option value="hair_style">Hair Style</option>
          <option value="hair_color">Hair Color</option>
        </select>
        <small style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.85rem', display: 'block', marginTop: '0.5rem' }}>
          Cannot be changed after creation
        </small>
      </div>

      {/* Composition Style */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Composition Style (Optional)</label>
        <select
          value={editedData.composition_style || ''}
          onChange={(e) => handlers.updateField('composition_style', e.target.value || null)}
          style={inputStyle}
        >
          <option value="">None</option>
          <option value="mannequin">Mannequin</option>
          <option value="flat_lay">Flat Lay</option>
          <option value="scene">Scene</option>
          <option value="portrait">Portrait</option>
          <option value="product">Product</option>
          <option value="lifestyle">Lifestyle</option>
          <option value="technical">Technical</option>
        </select>
      </div>

      {/* Framing */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Framing (Optional)</label>
        <select
          value={editedData.framing || ''}
          onChange={(e) => handlers.updateField('framing', e.target.value || null)}
          style={inputStyle}
        >
          <option value="">None</option>
          <option value="extreme_closeup">Extreme Closeup</option>
          <option value="closeup">Closeup</option>
          <option value="medium">Medium</option>
          <option value="full">Full</option>
          <option value="wide">Wide</option>
        </select>
      </div>

      {/* Camera Angle */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Camera Angle (Optional)</label>
        <select
          value={editedData.angle || ''}
          onChange={(e) => handlers.updateField('angle', e.target.value || null)}
          style={inputStyle}
        >
          <option value="">None</option>
          <option value="front">Front</option>
          <option value="three_quarter">3/4 View</option>
          <option value="side">Side</option>
          <option value="top_down">Top Down</option>
          <option value="eye_level">Eye Level</option>
          <option value="low_angle">Low Angle</option>
          <option value="high_angle">High Angle</option>
        </select>
      </div>

      {/* Background */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Background (Optional)</label>
        <select
          value={editedData.background || ''}
          onChange={(e) => handlers.updateField('background', e.target.value || null)}
          style={inputStyle}
        >
          <option value="">None</option>
          <option value="white">White</option>
          <option value="black">Black</option>
          <option value="transparent">Transparent</option>
          <option value="gradient">Gradient</option>
          <option value="simple_scene">Simple Scene</option>
          <option value="detailed_scene">Detailed Scene</option>
        </select>
      </div>

      {/* Lighting */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Lighting (Optional)</label>
        <select
          value={editedData.lighting || ''}
          onChange={(e) => handlers.updateField('lighting', e.target.value || null)}
          style={inputStyle}
        >
          <option value="">None</option>
          <option value="soft_even">Soft Even</option>
          <option value="dramatic">Dramatic</option>
          <option value="natural">Natural</option>
          <option value="golden_hour">Golden Hour</option>
          <option value="studio">Studio</option>
          <option value="ambient">Ambient</option>
        </select>
      </div>

      {/* Art Style */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Art Style (Optional)</label>
        <select
          value={editedData.art_style_id || ''}
          onChange={(e) => handlers.updateField('art_style_id', e.target.value || null)}
          style={inputStyle}
          disabled={loadingArtStyles}
        >
          <option value="">None</option>
          {artStyles.map(style => (
            <option key={style.preset_id || style._id} value={style.preset_id || style._id}>
              {style.display_name || style.preset_id || 'Unnamed Style'}
            </option>
          ))}
        </select>
      </div>

      {/* Additional Instructions */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Additional Instructions</label>
        <textarea
          value={editedData.additional_instructions || ''}
          onChange={(e) => handlers.updateField('additional_instructions', e.target.value)}
          rows={4}
          style={{...inputStyle, resize: 'vertical', fontFamily: 'inherit'}}
          placeholder="Optional free-form instructions for the visualizer..."
        />
      </div>

      {/* Image Size */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Image Size</label>
        <select
          value={editedData.image_size || '1024x1024'}
          onChange={(e) => handlers.updateField('image_size', e.target.value)}
          style={inputStyle}
        >
          <option value="1024x1024">1024x1024 (Square)</option>
          <option value="1024x768">1024x768 (4:3)</option>
          <option value="768x1024">768x1024 (3:4)</option>
        </select>
      </div>

      {/* Model */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Model</label>
        <input
          type="text"
          value={editedData.model || 'gemini/gemini-2.5-flash-image'}
          onChange={(e) => handlers.updateField('model', e.target.value)}
          style={inputStyle}
        />
      </div>

      {/* Is Default */}
      <div style={{...fieldStyle, display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
        <input
          type="checkbox"
          checked={editedData.is_default || false}
          onChange={(e) => handlers.updateField('is_default', e.target.checked)}
          style={{ width: 'auto', cursor: 'pointer' }}
        />
        <label style={{...labelStyle, margin: 0, cursor: 'pointer'}}>
          Set as default for {editedData.entity_type?.replace('_', ' ') || 'this entity type'}
        </label>
      </div>
    </div>
  )
}

export const visualizationConfigsConfig = {
  entityType: 'visualization config',
  title: 'Visualization Configs',
  icon: '🎨',
  emptyMessage: 'No visualization configs yet. Create one to customize how entity previews are generated!',
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  defaultSort: 'newest',
  searchFields: ['display_name', 'entity_type'],

  actions: [
    // New Config action will be implemented with inline create form later
  ],

  fetchEntities: async () => {
    const response = await api.get('/visualization-configs/')
    return (response.data.configs || []).map(config => ({
      id: config.config_id,
      title: config.display_name,
      config_id: config.config_id,
      entity_type: config.entity_type,
      createdAt: config.created_at,
      data: config // Store full config data
    }))
  },

  loadFullData: async (entity) => {
    // Data already loaded, just return it
    return entity.data
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (entity) => (
    <div className="entity-card">
      <div className="entity-card-image" style={{ height: '280px', background: 'rgba(0, 0, 0, 0.3)' }}>
        {entity.data.reference_image_path ? (
          <LazyImage
            src={entity.data.reference_image_path}
            alt={entity.title}
            onError={(e) => {
              e.target.style.display = 'none'
              e.target.parentElement.innerHTML = `<div class="entity-card-placeholder">🎨</div>`
            }}
          />
        ) : (
          <div className="entity-card-placeholder">🎨</div>
        )}
      </div>
      <div className="entity-card-content">
        <h3 className="entity-card-title">{entity.title}</h3>
        <p className="entity-card-date" style={{ textTransform: 'capitalize' }}>
          {entity.entity_type.replace('_', ' ')}
        </p>
        {entity.data.is_default && (
          <span style={{
            display: 'inline-block',
            padding: '0.25rem 0.5rem',
            background: 'rgba(76, 175, 80, 0.2)',
            border: '1px solid rgba(76, 175, 80, 0.3)',
            borderRadius: '4px',
            color: '#4CAF50',
            fontSize: '0.75rem',
            fontWeight: '600',
            marginTop: '0.5rem'
          }}>
            DEFAULT
          </span>
        )}
      </div>
    </div>
  ),

  renderPreview: (entity, onUpdate) => {
    // Return a component that can use hooks
    const PreviewWithUpload = () => {
      const [uploading, setUploading] = useState(false)

      const handleUpload = async (e) => {
        const file = e.target.files?.[0]
        if (!file) return

        setUploading(true)
        try {
          const formData = new FormData()
          formData.append('file', file)

          const response = await api.post(
            `/visualization-configs/${entity.config_id}/upload-reference`,
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            }
          )

          // Update entity with new reference image path
          if (onUpdate) {
            await onUpdate()
          }
        } catch (err) {
          console.error('Failed to upload reference image:', err)
          alert('Failed to upload reference image')
        } finally {
          setUploading(false)
        }
      }

      return (
        <div>
          {entity.data.reference_image_path ? (
            <img
              src={entity.data.reference_image_path}
              alt={entity.title}
              style={{ width: '100%', height: 'auto', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)', marginBottom: '1rem' }}
              onError={(e) => e.target.style.display = 'none'}
            />
          ) : (
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: '12px',
              padding: '4rem',
              textAlign: 'center',
              color: 'rgba(255, 255, 255, 0.3)',
              fontSize: '4rem',
              marginBottom: '1rem'
            }}>
              🎨
            </div>
          )}

          {/* Upload Button */}
          <div style={{ marginTop: '1rem' }}>
            <label style={{
              display: 'inline-block',
              padding: '0.75rem 1.5rem',
              background: uploading ? 'rgba(255, 255, 255, 0.1)' : 'rgba(59, 130, 246, 0.8)',
              color: 'white',
              borderRadius: '8px',
              cursor: uploading ? 'not-allowed' : 'pointer',
              fontWeight: 500,
              fontSize: '0.95rem',
              transition: 'all 0.2s ease',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              {uploading ? 'Uploading...' : (entity.data.reference_image_path ? 'Replace Reference Image' : 'Upload Reference Image')}
              <input
                type="file"
                accept="image/*"
                onChange={handleUpload}
                disabled={uploading}
                style={{ display: 'none' }}
              />
            </label>
          </div>
        </div>
      )
    }

    return <PreviewWithUpload />
  },

  renderEdit: (entity, editedData, editedTitle, handlers) => (
    <VisualizationConfigEditor
      entity={entity}
      editedData={editedData}
      editedTitle={editedTitle}
      handlers={handlers}
    />
  ),

  saveEntity: async (entity, updates) => {
    const response = await api.put(
      `/visualization-configs/${entity.config_id}`,
      {
        ...updates.data,
        display_name: updates.title
      }
    )
    return response.data
  },

  deleteEntity: async (entity) => {
    await api.delete(`/visualization-configs/${entity.config_id}`)
  }
}
