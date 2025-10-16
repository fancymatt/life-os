import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './OutfitAnalyzer.css' // Reuse the base modal styles
import './ModularGenerator.css' // Modular generator specific styles
import api from './api/client'

function ModularGenerator({ onClose }) {
  const navigate = useNavigate()
  const handleClose = onClose || (() => navigate(-1))
  // Subject selection
  const [subject, setSubject] = useState('jenny.png')
  const [characters, setCharacters] = useState([])
  const [subjects, setSubjects] = useState([])
  const [loadingSubjects, setLoadingSubjects] = useState(true)

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

  // State for each category: enabled, presets, selected preset(s)
  // Note: outfit category uses an array for multiple selection
  const [categoryStates, setCategoryStates] = useState({})
  const [iterations, setIterations] = useState(1)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [favorites, setFavorites] = useState([])

  // Initialize category states
  useEffect(() => {
    const initialState = {}
    categories.forEach(cat => {
      initialState[cat.key] = {
        enabled: false,
        presets: [],
        loadingPresets: false,
        // Outfit uses array for multi-select, others use single value
        selectedPreset: cat.key === 'outfit' ? [] : null
      }
    })
    setCategoryStates(initialState)

    // Fetch user favorites
    fetchFavorites()

    // Fetch characters and subjects
    fetchCharactersAndSubjects()
  }, [])

  const fetchCharactersAndSubjects = async () => {
    setLoadingSubjects(true)
    try {
      // Fetch characters
      const charsResponse = await api.get('/characters/')
      setCharacters(charsResponse.data.characters || [])

      // Fetch subjects
      const subsResponse = await api.get('/analyze/subjects')
      setSubjects(subsResponse.data || [])

      // Set default subject if available
      if (charsResponse.data.characters && charsResponse.data.characters.length > 0) {
        setSubject(`character:${charsResponse.data.characters[0].character_id}`)
      } else if (subsResponse.data && subsResponse.data.length > 0) {
        setSubject(subsResponse.data[0].filename)
      }
    } catch (err) {
      console.error('Failed to fetch characters/subjects:', err)
      setError('Failed to load characters and subjects')
    } finally {
      setLoadingSubjects(false)
    }
  }

  const fetchFavorites = async () => {
    try {
      const response = await api.get('/favorites')
      setFavorites(response.data)
    } catch (err) {
      console.error('Failed to fetch favorites:', err)
    }
  }

  const toggleFavorite = async (preset, category) => {
    try {
      const favoriteKey = `${category}:${preset.preset_id}`
      const isFavorite = favorites.includes(favoriteKey)

      if (isFavorite) {
        await api.post('/favorites/remove', {
          preset_id: preset.preset_id,
          category
        })
        setFavorites(prev => prev.filter(f => f !== favoriteKey))
      } else {
        await api.post('/favorites/add', {
          preset_id: preset.preset_id,
          category
        })
        setFavorites(prev => [...prev, favoriteKey])
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err)
    }
  }

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
        const response = await api.get(`/presets/${apiCategory}`)
        setCategoryStates(prev => ({
          ...prev,
          [categoryKey]: {
            ...prev[categoryKey],
            presets: response.data.presets || [],
            loadingPresets: false
          }
        }))
      } catch (err) {
        const errorMsg = err.response?.data?.detail || err.message
        setError(`Failed to load ${categoryKey} presets: ${errorMsg}`)
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
    setCategoryStates(prev => {
      const currentState = prev[categoryKey]

      // Outfit category: toggle multi-select
      if (categoryKey === 'outfit') {
        const currentSelected = currentState.selectedPreset || []
        const newSelected = currentSelected.includes(presetId)
          ? currentSelected.filter(id => id !== presetId)  // Remove if already selected
          : [...currentSelected, presetId]  // Add if not selected

        return {
          ...prev,
          [categoryKey]: {
            ...currentState,
            selectedPreset: newSelected
          }
        }
      }

      // Other categories: single select
      return {
        ...prev,
        [categoryKey]: {
          ...currentState,
          selectedPreset: presetId
        }
      }
    })
  }

  const handleGenerate = async () => {
    setError(null)
    setSuccess(null)

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
          // Outfit can be array (multiple) or single value
          if (cat.key === 'outfit' && Array.isArray(state.selectedPreset)) {
            // Only include if array has items
            if (state.selectedPreset.length > 0) {
              payload[cat.key] = state.selectedPreset
            }
          } else if (state.selectedPreset) {
            // Other categories: single value
            payload[cat.key] = state.selectedPreset
          }
        }
      })

      // Call the generation endpoint
      const response = await api.post('/generate/modular', payload)

      // Show success message
      setSuccess(`Generation started! Check the Task Manager (⚡) to track progress. Job ID: ${response.data.job_id}`)

      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    }
  }

  const canGenerate = subject

  return (
    <div className="analyzer-page">
      <div className="modal-header">
        <h2>Modular Generator</h2>
      </div>

      <div className="modal-body">
          {/* Subject Selection */}
          <div className="form-group">
            <label htmlFor="subject">Subject Image</label>
            {loadingSubjects ? (
              <div className="loading">Loading subjects...</div>
            ) : (
              <select
                id="subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              >
                {characters.length > 0 && (
                  <optgroup label="Characters">
                    {characters.map(char => (
                      <option key={char.character_id} value={`character:${char.character_id}`}>
                        {char.name}
                      </option>
                    ))}
                  </optgroup>
                )}
                {subjects.length > 0 && (
                  <optgroup label="Subjects">
                    {subjects.map(sub => (
                      <option key={sub.filename} value={sub.filename}>
                        {sub.filename}
                      </option>
                    ))}
                  </optgroup>
                )}
                {characters.length === 0 && subjects.length === 0 && (
                  <option value="">No subjects or characters available</option>
                )}
              </select>
            )}
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
                      style={{ marginRight: '0.5rem' }}
                    />
                    <label
                      htmlFor={`enable-${cat.key}`}
                      style={{ fontWeight: '500', cursor: 'pointer', margin: 0 }}
                    >
                      {cat.label}
                      {cat.key === 'outfit' && (
                        <span style={{ fontSize: '0.75rem', color: '#6b7280', marginLeft: '0.5rem' }}>
                          (multi-select)
                        </span>
                      )}
                    </label>
                  </div>

                  {state.enabled && (
                    <div style={{ marginLeft: '1.5rem' }}>
                      {state.loadingPresets ? (
                        <div className="loading">Loading presets...</div>
                      ) : state.presets.length === 0 ? (
                        <div className="preset-grid-empty">
                          No presets available
                        </div>
                      ) : (
                        <div className="preset-grid">
                          {state.presets.map(preset => {
                            // Check selection: array for outfit, single value for others
                            const isSelected = cat.key === 'outfit'
                              ? (state.selectedPreset || []).includes(preset.preset_id)
                              : state.selectedPreset === preset.preset_id

                            const favoriteKey = `${cat.apiCategory}:${preset.preset_id}`
                            const isFavorite = favorites.includes(favoriteKey)

                            return (
                              <PresetCard
                                key={preset.preset_id}
                                preset={preset}
                                category={cat.apiCategory}
                                selected={isSelected}
                                isFavorite={isFavorite}
                                onClick={() => handleSelectPreset(cat.key, preset.preset_id)}
                                onToggleFavorite={(e) => {
                                  e.stopPropagation()
                                  toggleFavorite(preset, cat.apiCategory)
                                }}
                              />
                            )
                          })}
                        </div>
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
              style={{ width: '100px' }}
            />
          </div>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message" style={{ marginTop: '1rem' }}>{success}</div>}

          {/* Generate Button */}
          <button
            className="analyze-button"
            onClick={handleGenerate}
            disabled={!canGenerate}
            style={{ marginTop: '1.5rem', width: '100%' }}
          >
            Generate
          </button>
        </div>
      </div>
  )
}

function PresetCard({ preset, category, selected, isFavorite, onClick, onToggleFavorite }) {
  const [imageLoaded, setImageLoaded] = useState(false)
  const [imageError, setImageError] = useState(false)

  const previewUrl = `/api/presets/${category}/${preset.preset_id}/preview?t=${Date.now()}`

  return (
    <div
      className={`preset-card ${selected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="preset-preview">
        {!imageLoaded && !imageError && (
          <div className="loading-spinner" />
        )}
        {!imageError ? (
          <img
            src={previewUrl}
            alt={preset.display_name || preset.preset_id}
            onLoad={() => setImageLoaded(true)}
            onError={() => {
              setImageError(true)
              setImageLoaded(true)
            }}
            style={{ display: imageLoaded ? 'block' : 'none' }}
          />
        ) : (
          <div className="no-image">🖼️</div>
        )}
        {selected && <div className="checkmark">✓</div>}
        <button
          className={`favorite-btn ${isFavorite ? 'favorited' : ''}`}
          onClick={onToggleFavorite}
          title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          {isFavorite ? '★' : '☆'}
        </button>
      </div>
      <div className="preset-name">
        {preset.display_name || preset.preset_id}
      </div>
    </div>
  )
}

export default ModularGenerator
