import { useState, useEffect } from 'react'
import './OutfitAnalyzer.css' // Reuse the same styles

function ModularGenerator({ onClose }) {
  // Subject selection
  const [subject, setSubject] = useState('jenny.png')

  // Category configurations
  const categories = [
    { key: 'outfit', label: 'Outfit', apiCategory: 'outfits' },
    { key: 'visual_style', label: 'Photograph Composition', apiCategory: 'visual_styles' },
    { key: 'art_style', label: 'Art Style', apiCategory: 'art_styles' },
    { key: 'hair_style', label: 'Hair Style', apiCategory: 'hair_styles' },
    { key: 'hair_color', label: 'Hair Color', apiCategory: 'hair_colors' },
    { key: 'makeup', label: 'Makeup', apiCategory: 'makeup' },
    { key: 'expression', label: 'Expression', apiCategory: 'expressions' },
    { key: 'accessories', label: 'Accessories', apiCategory: 'accessories' }
  ]

  // State for each category: enabled, presets, selected preset
  const [categoryStates, setCategoryStates] = useState({})
  const [iterations, setIterations] = useState(1)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [taskId, setTaskId] = useState(null)
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState('')

  // Initialize category states
  useEffect(() => {
    const initialState = {}
    categories.forEach(cat => {
      initialState[cat.key] = {
        enabled: false,
        presets: [],
        loadingPresets: false,
        selectedPreset: null
      }
    })
    setCategoryStates(initialState)
  }, [])

  // Fetch presets when a category is enabled
  const handleToggleCategory = async (categoryKey, apiCategory) => {
    const currentEnabled = categoryStates[categoryKey]?.enabled || false
    const newEnabled = !currentEnabled

    setCategoryStates(prev => ({
      ...prev,
      [categoryKey]: {
        ...prev[categoryKey],
        enabled: newEnabled,
        loadingPresets: newEnabled
      }
    }))

    if (newEnabled) {
      // Fetch presets for this category
      try {
        const response = await fetch(`/api/presets/${apiCategory}`)
        if (!response.ok) throw new Error('Failed to fetch presets')

        const data = await response.json()
        setCategoryStates(prev => ({
          ...prev,
          [categoryKey]: {
            ...prev[categoryKey],
            presets: data.presets || [],
            loadingPresets: false
          }
        }))
      } catch (err) {
        setError(`Failed to load ${categoryKey} presets: ${err.message}`)
        setCategoryStates(prev => ({
          ...prev,
          [categoryKey]: {
            ...prev[categoryKey],
            enabled: false,
            loadingPresets: false
          }
        }))
      }
    } else {
      // Clear selection when disabled
      setCategoryStates(prev => ({
        ...prev,
        [categoryKey]: {
          ...prev[categoryKey],
          selectedPreset: null
        }
      }))
    }
  }

  const handleSelectPreset = (categoryKey, presetId) => {
    setCategoryStates(prev => ({
      ...prev,
      [categoryKey]: {
        ...prev[categoryKey],
        selectedPreset: presetId
      }
    }))
  }

  const pollStatus = async (taskId) => {
    try {
      const response = await fetch(`/api/generate/modular/status/${taskId}`)
      if (!response.ok) {
        throw new Error('Failed to fetch status')
      }

      const status = await response.json()
      setProgress(status.progress || 0)
      setProgressMessage(status.message || '')

      if (status.status === 'completed') {
        setResult(status.result)
        setGenerating(false)
        setTaskId(null)
      } else if (status.status === 'failed') {
        setError(status.error || 'Generation failed')
        setGenerating(false)
        setTaskId(null)
      } else {
        // Still in progress, poll again in 1 second
        setTimeout(() => pollStatus(taskId), 1000)
      }
    } catch (err) {
      setError(err.message)
      setGenerating(false)
      setTaskId(null)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    setError(null)
    setResult(null)
    setProgress(0)
    setProgressMessage('Starting generation...')

    try {
      // Build the request payload
      const payload = {
        subject_image: subject,
        variations: parseInt(iterations) || 1
      }

      // Add selected presets
      categories.forEach(cat => {
        const state = categoryStates[cat.key]
        if (state?.enabled && state?.selectedPreset) {
          payload[cat.key] = state.selectedPreset
        }
      })

      // Call the generation endpoint
      const response = await fetch('/api/generate/modular', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Generation failed')
      }

      const data = await response.json()
      setTaskId(data.task_id)

      // Start polling for status
      setTimeout(() => pollStatus(data.task_id), 1000)
    } catch (err) {
      setError(err.message)
      setGenerating(false)
    }
  }

  const canGenerate = subject && !generating

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Modular Generator</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {/* Subject Selection */}
          <div className="form-group">
            <label htmlFor="subject">Subject Image</label>
            <select
              id="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              disabled={generating}
            >
              <option value="jenny.png">jenny.png</option>
            </select>
          </div>

          {/* Category Selections */}
          <div className="categories-section">
            <h3>Select Components</h3>
            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '1rem' }}>
              Enable categories to apply specific presets. Unchecked categories will use the subject's original properties.
            </p>

            {categories.map(cat => {
              const state = categoryStates[cat.key] || {}
              return (
                <div key={cat.key} className="category-section" style={{ marginBottom: '1.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <input
                      type="checkbox"
                      id={`enable-${cat.key}`}
                      checked={state.enabled || false}
                      onChange={() => handleToggleCategory(cat.key, cat.apiCategory)}
                      disabled={generating}
                      style={{ marginRight: '0.5rem' }}
                    />
                    <label
                      htmlFor={`enable-${cat.key}`}
                      style={{ fontWeight: '500', cursor: 'pointer', margin: 0 }}
                    >
                      {cat.label}
                    </label>
                  </div>

                  {state.enabled && (
                    <div style={{ marginLeft: '1.5rem' }}>
                      {state.loadingPresets ? (
                        <div className="loading">Loading presets...</div>
                      ) : state.presets.length === 0 ? (
                        <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>
                          No presets available
                        </div>
                      ) : (
                        <select
                          value={state.selectedPreset || ''}
                          onChange={(e) => handleSelectPreset(cat.key, e.target.value)}
                          disabled={generating}
                          style={{ width: '100%', padding: '0.5rem' }}
                        >
                          <option value="">Select a preset...</option>
                          {state.presets.map(preset => (
                            <option key={preset.preset_id} value={preset.preset_id}>
                              {preset.display_name || preset.preset_id}
                            </option>
                          ))}
                        </select>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Generation Options */}
          <div className="form-group" style={{ marginTop: '2rem' }}>
            <label htmlFor="iterations">Number of Variations</label>
            <input
              type="number"
              id="iterations"
              min="1"
              max="10"
              value={iterations}
              onChange={(e) => setIterations(e.target.value)}
              disabled={generating}
              style={{ width: '100px' }}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          {generating && (
            <div style={{ marginTop: '1rem' }}>
              <div style={{ marginBottom: '0.5rem', fontSize: '0.875rem', color: '#6b7280' }}>
                {progressMessage}
              </div>
              <div style={{
                width: '100%',
                height: '8px',
                backgroundColor: '#e5e7eb',
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${progress}%`,
                  height: '100%',
                  backgroundColor: '#3b82f6',
                  transition: 'width 0.3s ease'
                }} />
              </div>
              <div style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: '#9ca3af', textAlign: 'right' }}>
                {Math.round(progress)}%
              </div>
            </div>
          )}

          {result && (
            <div className="success-message" style={{ marginTop: '1rem' }}>
              <h4>Generation Complete!</h4>
              <p>Generated {iterations} image(s)</p>
              <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                Check output/generated/ directory for results
              </p>
              {result.file_paths && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                  {result.file_paths.map((path, idx) => (
                    <div key={idx} style={{ fontFamily: 'monospace' }}>{path}</div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Generate Button */}
          <button
            className="analyze-button"
            onClick={handleGenerate}
            disabled={!canGenerate}
            style={{ marginTop: '1.5rem', width: '100%' }}
          >
            {generating ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ModularGenerator
