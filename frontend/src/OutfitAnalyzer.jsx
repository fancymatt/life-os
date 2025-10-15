import { useState, useEffect } from 'react'
import './OutfitAnalyzer.css'

function OutfitAnalyzer({ onClose }) {
  // View state: 'list' | 'create' | 'edit'
  const [view, setView] = useState('list')
  const [presets, setPresets] = useState([])
  const [loadingPresets, setLoadingPresets] = useState(true)
  const [selectedPreset, setSelectedPreset] = useState(null)

  // Create view state
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [outfitName, setOutfitName] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [newPresetId, setNewPresetId] = useState(null)

  // Preview loading state
  const [loadingPreviews, setLoadingPreviews] = useState(new Set())

  // Edit view state
  const [editedData, setEditedData] = useState(null)
  const [expandedItems, setExpandedItems] = useState({})
  const [editingItems, setEditingItems] = useState({})
  const [saving, setSaving] = useState(false)
  const [generating, setGenerating] = useState(false)

  // Shared state
  const [error, setError] = useState(null)
  const [dragActive, setDragActive] = useState(false)

  // Fetch presets on mount
  useEffect(() => {
    fetchPresets()
  }, [])

  const fetchPresets = async () => {
    try {
      setLoadingPresets(true)
      const response = await fetch('/api/presets/outfits')
      if (!response.ok) throw new Error('Failed to fetch presets')

      const data = await response.json()
      setPresets(data.presets || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingPresets(false)
    }
  }

  const pollForPreview = async (presetId, maxAttempts = 20, interval = 1000) => {
    // Mark as loading
    setLoadingPreviews(prev => new Set([...prev, presetId]))

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await fetch(`/api/presets/outfits/${presetId}/preview`, {
          method: 'HEAD'
        })

        if (response.ok) {
          // Preview is available
          setLoadingPreviews(prev => {
            const newSet = new Set(prev)
            newSet.delete(presetId)
            return newSet
          })
          return true
        }
      } catch (err) {
        // Continue polling
      }

      // Wait before next attempt
      await new Promise(resolve => setTimeout(resolve, interval))
    }

    // Timeout - stop loading state
    setLoadingPreviews(prev => {
      const newSet = new Set(prev)
      newSet.delete(presetId)
      return newSet
    })
    return false
  }

  const handleCreateNew = () => {
    setView('create')
    setError(null)
  }

  const handleBackToList = () => {
    setView('list')
    setError(null)
    setImageFile(null)
    setImagePreview(null)
    setOutfitName('')
    setSelectedPreset(null)
    setEditedData(null)
    setAnalysisResult(null)
    setNewPresetId(null)
    fetchPresets() // Refresh list
  }

  const handleSelectPreset = async (preset) => {
    try {
      setError(null)
      // Fetch full preset data
      const response = await fetch(`/api/presets/outfits/${preset.preset_id}`)
      if (!response.ok) throw new Error('Failed to load preset')

      const data = await response.json()
      setSelectedPreset(preset)
      setEditedData(JSON.parse(JSON.stringify(data))) // Deep copy
      setOutfitName(preset.display_name || '')
      setView('edit')
    } catch (err) {
      setError(err.message)
    }
  }

  // Drag & drop handlers
  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    setImageFile(file)
    setError(null)

    const reader = new FileReader()
    reader.onloadend = () => {
      setImagePreview(reader.result)
    }
    reader.readAsDataURL(file)
  }

  const handleAnalyze = async () => {
    if (!imageFile) {
      setError('Please select an image')
      return
    }

    setAnalyzing(true)
    setError(null)

    try {
      const reader = new FileReader()
      reader.onloadend = async () => {
        const base64Data = reader.result.split(',')[1]

        const response = await fetch('/api/analyze/outfit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image: {
              image_data: base64Data
            },
            save_as_preset: true  // Auto-generate name
          })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Analysis failed')
        }

        const data = await response.json()

        if (data.status === 'failed') {
          throw new Error(data.error || 'Analysis failed')
        }

        // Store analysis result, preset ID, and AI-generated name
        setAnalysisResult(data.result)
        setNewPresetId(data.preset_id)
        setOutfitName(data.preset_display_name || data.result?.suggested_name || 'Outfit Analysis')
        setAnalyzing(false)

        // Start polling for preview image if we have a preset ID
        if (data.preset_id) {
          pollForPreview(data.preset_id)
        }
      }

      reader.readAsDataURL(imageFile)
    } catch (err) {
      setError(err.message)
      setAnalyzing(false)
    }
  }

  // Edit view handlers
  const toggleItem = (index) => {
    setExpandedItems(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const toggleEdit = (index) => {
    setEditingItems(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const updateItemField = (index, field, value) => {
    setEditedData(prev => {
      const newData = { ...prev }
      newData.clothing_items[index] = {
        ...newData.clothing_items[index],
        [field]: value
      }
      return newData
    })
  }

  const deleteItem = (index) => {
    setEditedData(prev => {
      const newData = { ...prev }
      newData.clothing_items = newData.clothing_items.filter((_, i) => i !== index)
      return newData
    })
  }

  const handleSave = async () => {
    if (!selectedPreset) {
      setError('No preset selected')
      return
    }

    setSaving(true)
    setError(null)

    try {
      const response = await fetch(`/api/presets/outfits/${selectedPreset.preset_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: editedData,
          display_name: outfitName.trim() || undefined
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to save preset')
      }

      // Clear editing states
      setEditingItems({})
      setSaving(false)

      // Start polling for updated preview image
      if (selectedPreset?.preset_id) {
        pollForPreview(selectedPreset.preset_id)
      }

      // Show success (could add a toast notification here)
      setTimeout(() => handleBackToList(), 1000)
    } catch (err) {
      setError(err.message)
      setSaving(false)
    }
  }

  const handleDeletePreset = async () => {
    if (!selectedPreset) return

    if (!confirm(`Are you sure you want to delete "${selectedPreset.display_name || 'this preset'}"?`)) {
      return
    }

    try {
      const response = await fetch(`/api/presets/outfits/${selectedPreset.preset_id}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to delete preset')
      }

      handleBackToList()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleGenerateTest = async () => {
    if (!selectedPreset) return

    setGenerating(true)
    setError(null)

    try {
      const response = await fetch(`/api/presets/outfits/${selectedPreset.preset_id}/generate-test`, {
        method: 'POST'
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to start test generation')
      }

      const data = await response.json()

      setGenerating(false)
    } catch (err) {
      setError(err.message)
      setGenerating(false)
    }
  }

  // Render views
  const renderListView = () => (
    <>
      <div className="preset-list-header">
        <h3>Outfit Presets ({presets.length})</h3>
        <button className="add-new-button" onClick={handleCreateNew}>
          + Add New
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loadingPresets ? (
        <div className="loading">Loading presets...</div>
      ) : presets.length === 0 ? (
        <div className="empty-state">
          <p>No outfit presets yet</p>
          <button className="add-new-button" onClick={handleCreateNew}>
            Create your first preset
          </button>
        </div>
      ) : (
        <div className="preset-list">
          {presets.map((preset) => (
            <div
              key={preset.preset_id}
              className="preset-card"
              onClick={() => handleSelectPreset(preset)}
            >
              <div className="preset-preview-image">
                {loadingPreviews.has(preset.preset_id) ? (
                  <div className="preview-loading">
                    <div className="loading-spinner"></div>
                    <span>Generating...</span>
                  </div>
                ) : (
                  <img
                    key={`preview-${preset.preset_id}-${loadingPreviews.size}`}
                    src={`/api/presets/outfits/${preset.preset_id}/preview?t=${Date.now()}`}
                    alt={preset.display_name || 'Outfit preview'}
                    onError={(e) => {
                      e.target.style.display = 'none'
                    }}
                  />
                )}
              </div>
              <div className="preset-card-content">
                <div className="preset-card-header">
                  <h4>{preset.display_name || 'Untitled'}</h4>
                </div>
                <div className="preset-card-meta">
                  {preset.created_at && (
                    <span className="preset-date">{new Date(preset.created_at).toLocaleDateString()}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  )

  const renderCreateView = () => {
    // Show results if analysis is complete
    if (analysisResult && newPresetId) {
      return (
        <>
          <button className="back-button" onClick={handleBackToList}>
            ← Back to List
          </button>

          <h3>Analysis Complete!</h3>

          <div className="success-message">
            Outfit "{outfitName}" has been analyzed and saved
          </div>

          {newPresetId && (
            <div className="preset-preview-container">
              {loadingPreviews.has(newPresetId) ? (
                <div className="preview-loading-large">
                  <div className="loading-spinner"></div>
                  <span>Generating preview...</span>
                </div>
              ) : (
                <img
                  key={`preview-${newPresetId}-${loadingPreviews.size}`}
                  src={`/api/presets/outfits/${newPresetId}/preview?t=${Date.now()}`}
                  alt={outfitName || 'Outfit preview'}
                  className="preset-preview-large"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
              )}
            </div>
          )}

          <div className="results">
            <h3>Outfit Details</h3>
            <div className="result-item">
              <strong>Style Genre:</strong> {analysisResult.style_genre || 'N/A'}
            </div>
            <div className="result-item">
              <strong>Formality:</strong> {analysisResult.formality || 'N/A'}
            </div>
            <div className="result-item">
              <strong>Aesthetic:</strong> {analysisResult.aesthetic || 'N/A'}
            </div>
          </div>

          <div className="clothing-items">
            <h3>Clothing Items ({analysisResult.clothing_items?.length || 0})</h3>
            {analysisResult.clothing_items?.map((item, index) => (
              <div key={index} className="result-item">
                <strong>{item.item}:</strong> {item.color} {item.fabric}
                {item.details && <div style={{ marginLeft: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>{item.details}</div>}
              </div>
            ))}
          </div>

          <button className="done-button" onClick={handleBackToList}>
            Done
          </button>
        </>
      )
    }

    // Show upload/analyze form
    return (
      <>
        <button className="back-button" onClick={handleBackToList}>
          ← Back to List
        </button>

        <h3>Analyze New Outfit</h3>

        <div
          className={`drop-zone ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {imagePreview ? (
            <div className="image-preview">
              <img src={imagePreview} alt="Preview" />
              <button
                className="remove-image"
                onClick={() => {
                  setImageFile(null)
                  setImagePreview(null)
                }}
              >
                Remove
              </button>
            </div>
          ) : (
            <div className="drop-zone-content">
              <p className="drop-zone-text">
                Drag and drop an image here, or click to select
              </p>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileInput}
                className="file-input"
                id="file-input"
              />
              <label htmlFor="file-input" className="file-input-label">
                Choose File
              </label>
            </div>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          className="analyze-button"
          onClick={handleAnalyze}
          disabled={analyzing || !imageFile}
        >
          {analyzing ? 'Analyzing...' : 'Analyze Outfit'}
        </button>
      </>
    )
  }

  const renderEditView = () => {
    if (!editedData) return <div className="loading">Loading...</div>

    return (
      <>
        <button className="back-button" onClick={handleBackToList}>
          ← Back to List
        </button>

        <div className="preset-edit-header">
          <div className="form-group">
            <label htmlFor="edit-outfit-name">Preset Name</label>
            <input
              type="text"
              id="edit-outfit-name"
              value={outfitName}
              onChange={(e) => setOutfitName(e.target.value)}
              placeholder="Preset name"
            />
          </div>
        </div>

        {selectedPreset && (
          <div className="preset-preview-container">
            {loadingPreviews.has(selectedPreset.preset_id) ? (
              <div className="preview-loading-large">
                <div className="loading-spinner"></div>
                <span>Generating preview...</span>
              </div>
            ) : (
              <img
                key={`preview-${selectedPreset.preset_id}-${loadingPreviews.size}`}
                src={`/api/presets/outfits/${selectedPreset.preset_id}/preview?t=${Date.now()}`}
                alt={selectedPreset.display_name || 'Outfit preview'}
                className="preset-preview-large"
                onError={(e) => {
                  e.target.style.display = 'none'
                }}
              />
            )}
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        <div className="results">
          <h3>Outfit Details</h3>
          <div className="result-item">
            <strong>Style Genre:</strong> {editedData.style_genre || 'N/A'}
          </div>
          <div className="result-item">
            <strong>Formality:</strong> {editedData.formality || 'N/A'}
          </div>
          <div className="result-item">
            <strong>Aesthetic:</strong> {editedData.aesthetic || 'N/A'}
          </div>
        </div>

        <div className="clothing-items">
          <h3>Clothing Items ({editedData.clothing_items?.length || 0})</h3>
          {editedData.clothing_items?.map((item, index) => (
            <div key={index} className="item-accordion">
              <div
                className="item-header"
                onClick={() => toggleItem(index)}
              >
                <span className="item-title">
                  {item.item || `Item ${index + 1}`}
                </span>
                <span className="accordion-icon">
                  {expandedItems[index] ? '▼' : '▶'}
                </span>
              </div>

              {expandedItems[index] && (
                <div className="item-content">
                  {editingItems[index] ? (
                    <>
                      <div className="form-group">
                        <label>Item Type</label>
                        <input
                          type="text"
                          value={item.item || ''}
                          onChange={(e) => updateItemField(index, 'item', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>Color</label>
                        <input
                          type="text"
                          value={item.color || ''}
                          onChange={(e) => updateItemField(index, 'color', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>Fabric</label>
                        <input
                          type="text"
                          value={item.fabric || ''}
                          onChange={(e) => updateItemField(index, 'fabric', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>Details</label>
                        <textarea
                          value={item.details || ''}
                          onChange={(e) => updateItemField(index, 'details', e.target.value)}
                          rows="3"
                        />
                      </div>
                      <div className="item-actions">
                        <button
                          className="edit-done-button"
                          onClick={() => toggleEdit(index)}
                        >
                          Done Editing
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="item-detail">
                        <strong>Item:</strong> {item.item || 'N/A'}
                      </div>
                      <div className="item-detail">
                        <strong>Color:</strong> {item.color || 'N/A'}
                      </div>
                      <div className="item-detail">
                        <strong>Fabric:</strong> {item.fabric || 'N/A'}
                      </div>
                      <div className="item-detail">
                        <strong>Details:</strong> {item.details || 'N/A'}
                      </div>
                      <div className="item-actions">
                        <button
                          className="edit-button"
                          onClick={() => toggleEdit(index)}
                        >
                          Edit
                        </button>
                        <button
                          className="delete-button"
                          onClick={() => deleteItem(index)}
                        >
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="button-group">
          <button
            className="save-button"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
          <button
            className="analyze-button"
            onClick={handleGenerateTest}
            disabled={generating}
          >
            {generating ? 'Generating...' : 'Generate Test Image'}
          </button>
          <button
            className="delete-preset-button"
            onClick={handleDeletePreset}
          >
            Delete Preset
          </button>
        </div>
      </>
    )
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Outfit Analyzer</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {view === 'list' && renderListView()}
          {view === 'create' && renderCreateView()}
          {view === 'edit' && renderEditView()}
        </div>
      </div>
    </div>
  )
}

export default OutfitAnalyzer
