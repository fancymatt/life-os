import { useState, useEffect } from 'react'
import './OutfitAnalyzer.css'

function GenericAnalyzer({ analyzerType, displayName, onClose }) {
  // Map analyzer types to API endpoints and categories
  const analyzerConfig = {
    'visual-style': { category: 'visual_styles', endpoint: '/api/analyze/visual-style', title: 'Photograph Composition' },
    'art-style': { category: 'art_styles', endpoint: '/api/analyze/art-style', title: 'Art Style' },
    'hair-style': { category: 'hair_styles', endpoint: '/api/analyze/hair-style', title: 'Hair Style' },
    'hair-color': { category: 'hair_colors', endpoint: '/api/analyze/hair-color', title: 'Hair Color' },
    'makeup': { category: 'makeup', endpoint: '/api/analyze/makeup', title: 'Makeup' },
    'expression': { category: 'expressions', endpoint: '/api/analyze/expression', title: 'Expression' },
    'accessories': { category: 'accessories', endpoint: '/api/analyze/accessories', title: 'Accessories' }
  }

  const config = analyzerConfig[analyzerType]
  const title = displayName || config.title

  // View state
  const [view, setView] = useState('list')
  const [presets, setPresets] = useState([])
  const [loadingPresets, setLoadingPresets] = useState(true)
  const [selectedPreset, setSelectedPreset] = useState(null)

  // Create view state
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [presetName, setPresetName] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [newPresetId, setNewPresetId] = useState(null)

  // Edit view state
  const [editedData, setEditedData] = useState(null)
  const [saving, setSaving] = useState(false)
  const [generating, setGenerating] = useState(false)

  // Shared state
  const [error, setError] = useState(null)
  const [dragActive, setDragActive] = useState(false)

  // Preview loading state
  const [loadingPreviews, setLoadingPreviews] = useState(new Set())

  // Fetch presets on mount
  useEffect(() => {
    fetchPresets()
  }, [])

  const fetchPresets = async () => {
    try {
      setLoadingPresets(true)
      const response = await fetch(`/api/presets/${config.category}`)
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
    setLoadingPreviews(prev => new Set([...prev, presetId]))

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await fetch(`/api/presets/${config.category}/${presetId}/preview`, {
          method: 'HEAD'
        })

        if (response.ok) {
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

      await new Promise(resolve => setTimeout(resolve, interval))
    }

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
    setPresetName('')
    setSelectedPreset(null)
    setEditedData(null)
    setAnalysisResult(null)
    setNewPresetId(null)
    fetchPresets()
  }

  const handleSelectPreset = async (preset) => {
    try {
      setError(null)
      const response = await fetch(`/api/presets/${config.category}/${preset.preset_id}`)
      if (!response.ok) throw new Error('Failed to load preset')

      const data = await response.json()
      setSelectedPreset(preset)
      setEditedData(JSON.parse(JSON.stringify(data)))
      setPresetName(preset.display_name || '')
      setView('edit')
    } catch (err) {
      setError(err.message)
    }
  }

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

    const reader = new FileReader()
    reader.onloadend = async () => {
      try {
        const base64Data = reader.result.split(',')[1]

        const response = await fetch(`${config.endpoint}?async_mode=true`, {
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

        // Async mode: close modal immediately, job appears in TaskManager
        if (data.job_id) {
          console.log('Analysis queued:', data.job_id)
          handleBackToList()  // Go back to list view
          onClose()  // Close modal
          return
        }

        // Sync mode (fallback - shouldn't happen with async_mode=true)
        if (data.status === 'failed') {
          throw new Error(data.error || 'Analysis failed')
        }

        setAnalysisResult(data.result)
        setNewPresetId(data.preset_id)
        setPresetName(data.preset_display_name || data.result?.suggested_name || 'Analysis')
        setAnalyzing(false)

        if (data.preset_id) {
          pollForPreview(data.preset_id)
        }
      } catch (err) {
        console.error('Analysis error:', err)
        setError(err.message)
        setAnalyzing(false)
      }
    }

    reader.onerror = () => {
      setError('Failed to read image file')
      setAnalyzing(false)
    }

    reader.readAsDataURL(imageFile)
  }

  const handleSave = async () => {
    if (!selectedPreset) {
      setError('No preset selected')
      return
    }

    setSaving(true)
    setError(null)

    try {
      const response = await fetch(`/api/presets/${config.category}/${selectedPreset.preset_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: editedData,
          display_name: presetName.trim() || undefined
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to save preset')
      }

      setSaving(false)

      if (selectedPreset?.preset_id) {
        pollForPreview(selectedPreset.preset_id)
      }

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
      const response = await fetch(`/api/presets/${config.category}/${selectedPreset.preset_id}`, {
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
      const response = await fetch(`/api/presets/${config.category}/${selectedPreset.preset_id}/generate-test`, {
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

  const updateField = (field, value) => {
    setEditedData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const renderListView = () => (
    <>
      <div className="preset-list-header">
        <h3>{title} Presets ({presets.length})</h3>
        <button className="add-new-button" onClick={handleCreateNew}>
          + Add New
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loadingPresets ? (
        <div className="loading">Loading presets...</div>
      ) : presets.length === 0 ? (
        <div className="empty-state">
          <p>No {title.toLowerCase()} presets yet</p>
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
                    src={`/api/presets/${config.category}/${preset.preset_id}/preview?t=${Date.now()}`}
                    alt={preset.display_name || `${title} preview`}
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
    if (analysisResult && newPresetId) {
      return (
        <>
          <button className="back-button" onClick={handleBackToList}>
            ← Back to List
          </button>

          <h3>Analysis Complete!</h3>

          <div className="success-message">
            {title} "{presetName}" has been analyzed and saved
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
                  src={`/api/presets/${config.category}/${newPresetId}/preview?t=${Date.now()}`}
                  alt={presetName || `${title} preview`}
                  className="preset-preview-large"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
              )}
            </div>
          )}

          <div className="results">
            <h3>{title} Details</h3>
            {Object.entries(analysisResult).map(([key, value]) => {
              if (key === '_metadata') return null
              return (
                <div key={key} className="result-item">
                  <strong>{key.replace(/_/g, ' ')}:</strong>{' '}
                  {Array.isArray(value) ? value.join(', ') : value}
                </div>
              )
            })}
          </div>

          <button className="done-button" onClick={handleBackToList}>
            Done
          </button>
        </>
      )
    }

    return (
      <>
        <button className="back-button" onClick={handleBackToList}>
          ← Back to List
        </button>

        <h3>Analyze New {title}</h3>

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
          {analyzing ? 'Analyzing...' : `Analyze ${title}`}
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
            <label htmlFor="edit-preset-name">Preset Name</label>
            <input
              type="text"
              id="edit-preset-name"
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
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
                src={`/api/presets/${config.category}/${selectedPreset.preset_id}/preview?t=${Date.now()}`}
                alt={selectedPreset.display_name || `${title} preview`}
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
          <h3>{title} Details</h3>
          {Object.entries(editedData).map(([key, value]) => {
            if (key === '_metadata') return null

            return (
              <div key={key} className="form-group">
                <label>{key.replace(/_/g, ' ')}</label>
                {Array.isArray(value) ? (
                  <input
                    type="text"
                    value={value.join(', ')}
                    onChange={(e) => updateField(key, e.target.value.split(',').map(v => v.trim()))}
                  />
                ) : (
                  <textarea
                    value={value || ''}
                    onChange={(e) => updateField(key, e.target.value)}
                    rows="3"
                  />
                )}
              </div>
            )
          })}
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
          <h2>{title} Analyzer</h2>
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

export default GenericAnalyzer
