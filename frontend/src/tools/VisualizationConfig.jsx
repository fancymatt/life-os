import { useState, useEffect } from 'react'
import api from '../api/client'
import './VisualizationConfig.css'

/**
 * Visualization Config Tool
 *
 * Manage visualization configurations for entity preview generation.
 * Control composition, framing, lighting, backgrounds, and art styles.
 */
function VisualizationConfig() {
  const [configs, setConfigs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [entityTypeFilter, setEntityTypeFilter] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingConfig, setEditingConfig] = useState(null)
  const [referenceImageFile, setReferenceImageFile] = useState(null)
  const [uploadingImage, setUploadingImage] = useState(false)

  // Art styles for dropdown
  const [artStyles, setArtStyles] = useState([])

  // Form state
  const [formData, setFormData] = useState({
    entity_type: 'clothing_item',
    display_name: '',
    composition_style: '',
    framing: '',
    angle: '',
    background: '',
    lighting: '',
    art_style_id: '',
    reference_image_path: '',
    additional_instructions: '',
    image_size: '1024x1024',
    model: 'gemini/gemini-2.5-flash-image',
    is_default: false
  })

  useEffect(() => {
    fetchConfigs()
    fetchArtStyles()
  }, [entityTypeFilter])

  const fetchConfigs = async () => {
    try {
      setLoading(true)
      setError(null)
      const params = entityTypeFilter ? { entity_type: entityTypeFilter } : {}
      const response = await api.get('/visualization-configs/', { params })
      setConfigs(response.data.configs)
    } catch (err) {
      console.error('Failed to fetch configs:', err)
      setError(err.response?.data?.detail || 'Failed to load visualization configs')
    } finally {
      setLoading(false)
    }
  }

  const fetchArtStyles = async () => {
    try {
      const response = await api.get('/presets/art_styles')
      // API returns { presets: [...] }, extract the array
      const presets = response.data.presets || response.data || []
      setArtStyles(Array.isArray(presets) ? presets : [])
    } catch (err) {
      console.error('Failed to fetch art styles:', err)
      // Set empty array on error to prevent crashes
      setArtStyles([])
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      await api.post('/visualization-configs/', formData)
      setShowCreateForm(false)
      resetForm()
      fetchConfigs()
    } catch (err) {
      console.error('Failed to create config:', err)
      setError(err.response?.data?.detail || 'Failed to create config')
    }
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    console.log('📝 Submitting update with formData:', formData)
    console.log('   reference_image_path:', formData.reference_image_path)
    try {
      await api.put(`/visualization-configs/${editingConfig.config_id}`, formData)
      setEditingConfig(null)
      resetForm()
      fetchConfigs()
    } catch (err) {
      console.error('Failed to update config:', err)
      setError(err.response?.data?.detail || 'Failed to update config')
    }
  }

  const handleDelete = async (configId) => {
    if (!confirm('Are you sure you want to delete this visualization config?')) {
      return
    }

    try {
      await api.delete(`/visualization-configs/${configId}`)
      fetchConfigs()
    } catch (err) {
      console.error('Failed to delete config:', err)
      setError(err.response?.data?.detail || 'Failed to delete config')
    }
  }

  const handleEdit = (config) => {
    setEditingConfig(config)
    setFormData({
      entity_type: config.entity_type,
      display_name: config.display_name,
      composition_style: config.composition_style,
      framing: config.framing,
      angle: config.angle,
      background: config.background,
      lighting: config.lighting,
      art_style_id: config.art_style_id || '',
      reference_image_path: config.reference_image_path || '',
      additional_instructions: config.additional_instructions || '',
      image_size: config.image_size,
      model: config.model,
      is_default: config.is_default
    })
    setShowCreateForm(true)
  }

  const resetForm = () => {
    setFormData({
      entity_type: 'clothing_item',
      display_name: '',
      composition_style: '',
      framing: '',
      angle: '',
      background: '',
      lighting: '',
      art_style_id: '',
      reference_image_path: '',
      additional_instructions: '',
      image_size: '1024x1024',
      model: 'gemini/gemini-2.5-flash-image',
      is_default: false
    })
  }

  const handleCancelEdit = () => {
    setEditingConfig(null)
    setShowCreateForm(false)
    setReferenceImageFile(null)
    resetForm()
  }

  const handleReferenceImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setReferenceImageFile(file)
    }
  }

  const handleUploadReferenceImage = async () => {
    if (!referenceImageFile) return

    setUploadingImage(true)
    setError(null)

    try {
      // Convert image to base64 (same pattern as outfit analyzer)
      const reader = new FileReader()
      reader.onloadend = async () => {
        try {
          const base64Data = reader.result.split(',')[1]

          // Send as JSON with base64 data
          const response = await api.post('/analyze/upload', {
            filename: referenceImageFile.name,
            image_data: base64Data
          })

          console.log('📤 Upload response:', response.data)
          console.log('📝 Current formData before update:', formData)

          // Update form data with the uploaded file path
          const updatedFormData = { ...formData, reference_image_path: response.data.url }
          console.log('📝 Updated formData:', updatedFormData)
          setFormData(updatedFormData)
          setReferenceImageFile(null)
          setUploadingImage(false)
        } catch (err) {
          console.error('Failed to upload image:', err)

          // Handle error message safely
          let errorMessage = 'Failed to upload image'
          if (err.response?.data?.detail) {
            if (typeof err.response.data.detail === 'string') {
              errorMessage = err.response.data.detail
            } else if (Array.isArray(err.response.data.detail)) {
              errorMessage = err.response.data.detail.map(e => e.msg || JSON.stringify(e)).join(', ')
            } else {
              errorMessage = JSON.stringify(err.response.data.detail)
            }
          } else if (err.message) {
            errorMessage = err.message
          }

          setError(errorMessage)
          setUploadingImage(false)
        }
      }

      // Read file as base64
      reader.readAsDataURL(referenceImageFile)
    } catch (err) {
      console.error('Failed to upload image:', err)

      // Handle error message safely (FastAPI validation errors can have complex structures)
      let errorMessage = 'Failed to upload image'
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail
        } else if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map(e => e.msg || JSON.stringify(e)).join(', ')
        } else {
          errorMessage = JSON.stringify(err.response.data.detail)
        }
      } else if (err.message) {
        errorMessage = err.message
      }

      setError(errorMessage)
    } finally {
      setUploadingImage(false)
    }
  }

  if (loading && configs.length === 0) {
    return (
      <div className="visualization-config">
        <div className="loading">Loading visualization configs...</div>
      </div>
    )
  }

  return (
    <div className="visualization-config">
      <div className="page-header">
        <h1>Visualization Configuration</h1>
        <p className="page-description">
          Control how entity previews are generated. Configure composition, framing, lighting, and art styles.
        </p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Controls */}
      <div className="config-controls">
        <div className="filter-group">
          <label>Filter by Entity Type:</label>
          <select
            value={entityTypeFilter}
            onChange={(e) => setEntityTypeFilter(e.target.value)}
          >
            <option value="">All Types</option>
            <option value="character">Characters</option>
            <option value="clothing_item">Clothing Items</option>
            <option value="outfit">Outfits</option>
            <option value="expression">Expressions</option>
            <option value="makeup">Makeup</option>
            <option value="accessories">Accessories</option>
            <option value="art_style">Art Styles</option>
            <option value="visual_style">Visual Styles</option>
            <option value="hair_style">Hair Styles</option>
            <option value="hair_color">Hair Colors</option>
          </select>
        </div>

        <button
          className="primary-button"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Cancel' : '+ New Config'}
        </button>
      </div>

      {/* Create/Edit Form */}
      {showCreateForm && (
        <div className="config-form-container">
          <h2>{editingConfig ? 'Edit Configuration' : 'Create New Configuration'}</h2>
          <form onSubmit={editingConfig ? handleUpdate : handleCreate} className="config-form">
            <div className="form-row">
              <div className="form-group">
                <label>Entity Type *</label>
                <select
                  value={formData.entity_type}
                  onChange={(e) => setFormData({ ...formData, entity_type: e.target.value })}
                  required
                  disabled={editingConfig} // Can't change entity type when editing
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
              </div>

              <div className="form-group">
                <label>Display Name *</label>
                <input
                  type="text"
                  value={formData.display_name}
                  onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                  placeholder="e.g., Product Photography, Lifestyle Shot"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Composition Style (Optional)</label>
                <select
                  value={formData.composition_style}
                  onChange={(e) => setFormData({ ...formData, composition_style: e.target.value })}
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

              <div className="form-group">
                <label>Framing (Optional)</label>
                <select
                  value={formData.framing}
                  onChange={(e) => setFormData({ ...formData, framing: e.target.value })}
                >
                  <option value="">None</option>
                  <option value="extreme_closeup">Extreme Closeup</option>
                  <option value="closeup">Closeup</option>
                  <option value="medium">Medium</option>
                  <option value="full">Full</option>
                  <option value="wide">Wide</option>
                </select>
              </div>

              <div className="form-group">
                <label>Camera Angle (Optional)</label>
                <select
                  value={formData.angle}
                  onChange={(e) => setFormData({ ...formData, angle: e.target.value })}
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
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Background (Optional)</label>
                <select
                  value={formData.background}
                  onChange={(e) => setFormData({ ...formData, background: e.target.value })}
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

              <div className="form-group">
                <label>Lighting (Optional)</label>
                <select
                  value={formData.lighting}
                  onChange={(e) => setFormData({ ...formData, lighting: e.target.value })}
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

              <div className="form-group">
                <label>Art Style (Optional)</label>
                <select
                  value={formData.art_style_id}
                  onChange={(e) => setFormData({ ...formData, art_style_id: e.target.value })}
                >
                  <option value="">None</option>
                  {artStyles && artStyles.length > 0 ? (
                    artStyles.map(style => (
                      <option key={style.preset_id || style._id} value={style.preset_id || style._id}>
                        {style.display_name || style.preset_id || 'Unnamed Style'}
                      </option>
                    ))
                  ) : (
                    <option disabled>No art styles available</option>
                  )}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Reference Image (Optional)</label>
              <input
                type="file"
                accept="image/*"
                onChange={handleReferenceImageChange}
                disabled={uploadingImage}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'white',
                  border: '2px solid #ccc',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  cursor: 'pointer'
                }}
              />
              {referenceImageFile && (
                <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{ color: '#666', fontSize: '0.9rem', flex: 1 }}>
                    Selected: {referenceImageFile.name}
                  </span>
                  <button
                    type="button"
                    onClick={handleUploadReferenceImage}
                    disabled={uploadingImage}
                    className="secondary-button"
                    style={{ padding: '0.5rem 1rem' }}
                  >
                    {uploadingImage ? 'Uploading...' : 'Upload'}
                  </button>
                </div>
              )}
              {formData.reference_image_path && (
                <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: '#e8f5e9', borderRadius: '4px', border: '1px solid #4caf50' }}>
                  <span style={{ color: '#2e7d32', fontSize: '0.85rem' }}>
                    ✓ Reference image set: {formData.reference_image_path}
                  </span>
                </div>
              )}
              <small style={{ color: '#666', fontSize: '0.85rem', marginTop: '0.5rem', display: 'block' }}>
                Upload a reference image for Gemini image generation (optional). Gemini will use this as visual inspiration.
              </small>
            </div>

            <div className="form-group">
              <label>Additional Instructions</label>
              <textarea
                value={formData.additional_instructions}
                onChange={(e) => setFormData({ ...formData, additional_instructions: e.target.value })}
                placeholder="Optional free-form instructions for the visualizer..."
                rows={3}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Image Size</label>
                <select
                  value={formData.image_size}
                  onChange={(e) => setFormData({ ...formData, image_size: e.target.value })}
                >
                  <option value="1024x1024">1024x1024 (Square)</option>
                  <option value="1024x768">1024x768 (4:3)</option>
                  <option value="768x1024">768x1024 (3:4)</option>
                </select>
              </div>

              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.is_default}
                    onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                  />
                  {' '}Set as default for {formData.entity_type.replace('_', ' ')}
                </label>
              </div>
            </div>

            <div className="form-actions">
              <button type="button" onClick={handleCancelEdit} className="secondary-button">
                Cancel
              </button>
              <button type="submit" className="primary-button">
                {editingConfig ? 'Update Config' : 'Create Config'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Config List */}
      <div className="configs-list">
        <h2>Existing Configurations ({configs.length})</h2>
        {configs.length === 0 ? (
          <div className="empty-state">
            No visualization configs found. Create one to get started!
          </div>
        ) : (
          <div className="config-cards">
            {configs.map(config => (
              <div key={config.config_id} className={`config-card ${config.is_default ? 'default' : ''}`}>
                <div className="config-card-header">
                  <h3>{config.display_name}</h3>
                  {config.is_default && <span className="default-badge">DEFAULT</span>}
                </div>
                <div className="config-card-body">
                  <div className="config-detail">
                    <strong>Entity Type:</strong> {config.entity_type.replace('_', ' ')}
                  </div>
                  <div className="config-detail">
                    <strong>Style:</strong> {config.composition_style} / {config.framing} / {config.angle}
                  </div>
                  <div className="config-detail">
                    <strong>Environment:</strong> {config.background} background / {config.lighting} lighting
                  </div>
                  {config.art_style_id && (
                    <div className="config-detail">
                      <strong>Art Style:</strong> {config.art_style_id}
                    </div>
                  )}
                </div>
                <div className="config-card-actions">
                  <button onClick={() => handleEdit(config)} className="secondary-button">
                    Edit
                  </button>
                  <button onClick={() => handleDelete(config.config_id)} className="danger-button">
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default VisualizationConfig
