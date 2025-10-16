import { useState, useEffect } from 'react'
import './Composer.css'
import api from './api/client'

function Composer() {
  const [subject, setSubject] = useState('jenny.png')
  const [subjects, setSubjects] = useState([])
  const [categories, setCategories] = useState([])
  const [presets, setPresets] = useState({})
  const [loading, setLoading] = useState(true)
  const [appliedPresets, setAppliedPresets] = useState([])
  const [generatedImage, setGeneratedImage] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [favorites, setFavorites] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)
  const [generationHistory, setGenerationHistory] = useState([])
  const [selectedPreset, setSelectedPreset] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [compositions, setCompositions] = useState([])
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [compositionName, setCompositionName] = useState('')
  const [showCompositions, setShowCompositions] = useState(false)
  const [mobileTab, setMobileTab] = useState('canvas') // 'library', 'canvas', 'applied'

  // Category configurations
  const categoryConfig = [
    { key: 'outfit', label: 'Outfit', apiCategory: 'outfits' },
    { key: 'visual_style', label: 'Visual Style', apiCategory: 'visual_styles' },
    { key: 'art_style', label: 'Art Style', apiCategory: 'art_styles' },
    { key: 'hair_style', label: 'Hair Style', apiCategory: 'hair_styles' },
    { key: 'hair_color', label: 'Hair Color', apiCategory: 'hair_colors' },
    { key: 'makeup', label: 'Makeup', apiCategory: 'makeup' },
    { key: 'expression', label: 'Expression', apiCategory: 'expressions' },
    { key: 'accessories', label: 'Accessories', apiCategory: 'accessories' }
  ]

  useEffect(() => {
    loadPresets()
    fetchFavorites()
    fetchSubjects()
    fetchCompositions()
  }, [])

  const loadPresets = async () => {
    setLoading(true)
    const presetsData = {}

    for (const cat of categoryConfig) {
      try {
        const response = await api.get(`/presets/${cat.apiCategory}`)
        presetsData[cat.key] = response.data.presets || []
      } catch (err) {
        console.error(`Failed to load ${cat.key}:`, err)
        presetsData[cat.key] = []
      }
    }

    setPresets(presetsData)
    setCategories(categoryConfig)
    setLoading(false)
  }

  const fetchFavorites = async () => {
    try {
      const response = await api.get('/favorites')
      setFavorites(response.data)
    } catch (err) {
      console.error('Failed to fetch favorites:', err)
    }
  }

  const fetchSubjects = async () => {
    try {
      const response = await api.get('/analyze/subjects')
      setSubjects(response.data)
      // Set first subject as default if available
      if (response.data.length > 0 && !subject) {
        setSubject(response.data[0].filename)
      }
    } catch (err) {
      console.error('Failed to fetch subjects:', err)
    }
  }

  const handleSubjectChange = (newSubject) => {
    setSubject(newSubject)
    // Clear generation history since it's subject-specific
    setGenerationHistory([])
    setGeneratedImage(null)
    // Optionally clear applied presets
    // setAppliedPresets([])
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const presetData = e.dataTransfer.getData('preset')

    if (presetData) {
      const preset = JSON.parse(presetData)
      addPreset(preset)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const addPreset = async (preset) => {
    let newAppliedPresets

    // Outfits can be layered, other categories replace
    if (preset.category === 'outfits') {
      // Always add outfits (they stack)
      newAppliedPresets = [...appliedPresets, preset]
    } else {
      // For other categories, check if preset of same category already exists
      const existingIndex = appliedPresets.findIndex(
        p => p.category === preset.category
      )

      if (existingIndex >= 0) {
        // Replace preset in same category
        newAppliedPresets = [...appliedPresets]
        newAppliedPresets[existingIndex] = preset
      } else {
        // Add new preset
        newAppliedPresets = [...appliedPresets, preset]
      }
    }

    setAppliedPresets(newAppliedPresets)

    // Clear selected preset after applying
    setSelectedPreset(null)

    // On mobile, switch to canvas tab when generating
    if (window.innerWidth < 768) {
      setMobileTab('canvas')
    }

    // Auto-generate with new preset combination
    await generateImage(newAppliedPresets)
  }

  const handlePresetClick = (preset, category) => {
    const presetWithCategory = { ...preset, category }

    // If clicking the same preset, apply it
    if (selectedPreset?.preset_id === preset.preset_id) {
      addPreset(presetWithCategory)
    } else {
      // Otherwise, select it
      setSelectedPreset(presetWithCategory)
    }
  }

  const applySelectedPreset = () => {
    if (selectedPreset) {
      addPreset(selectedPreset)
    }
  }

  const removePreset = async (index) => {
    const newAppliedPresets = appliedPresets.filter((_, i) => i !== index)
    setAppliedPresets(newAppliedPresets)

    // Regenerate without removed preset
    if (newAppliedPresets.length > 0) {
      await generateImage(newAppliedPresets)
    } else {
      setGeneratedImage(null)
    }
  }

  const generateImage = async (presetsToApply) => {
    if (presetsToApply.length === 0) return

    setGenerating(true)

    try {
      // Check cache first
      const cacheKey = getCacheKey(presetsToApply)
      const cached = generationHistory.find(h => h.cacheKey === cacheKey)

      if (cached) {
        console.log('✅ Using cached result:', cached.imageUrl)
        setGeneratedImage(cached.imageUrl)
        setGenerating(false)
        return
      }

      // Build request payload
      const payload = {
        subject_image: subject,
        variations: 1
      }

      // Add presets to payload
      presetsToApply.forEach(preset => {
        const categoryKey = categoryConfig.find(c => c.apiCategory === preset.category)?.key
        if (categoryKey) {
          // For outfit, support multiple presets
          if (categoryKey === 'outfit') {
            if (!payload[categoryKey]) {
              payload[categoryKey] = []
            }
            payload[categoryKey].push(preset.preset_id)
          } else {
            payload[categoryKey] = preset.preset_id
          }
        }
      })

      console.log('🎨 Generating with presets:', payload)

      const response = await api.post('/generate/modular', payload)
      const jobId = response.data.job_id

      // Poll for completion
      const imageUrl = await pollForCompletion(jobId)

      if (imageUrl) {
        console.log('✅ Generated image URL:', imageUrl)
        setGeneratedImage(imageUrl)

        // Cache the result
        setGenerationHistory(prev => [
          ...prev,
          { cacheKey, imageUrl, presets: presetsToApply, timestamp: Date.now() }
        ])
      }
    } catch (err) {
      console.error('Generation failed:', err)
      alert('Failed to generate image: ' + (err.response?.data?.detail || err.message))
    } finally {
      setGenerating(false)
    }
  }

  const pollForCompletion = async (jobId) => {
    const maxAttempts = 60
    const pollInterval = 2000

    for (let i = 0; i < maxAttempts; i++) {
      await new Promise(resolve => setTimeout(resolve, pollInterval))

      try {
        const jobResponse = await api.get(`/jobs/${jobId}`)
        const job = jobResponse.data

        if (job.status === 'completed') {
          if (job.result?.file_paths && job.result.file_paths.length > 0) {
            // Convert file path to URL
            const filePath = job.result.file_paths[0]
            // Ensure URL starts with /
            let imageUrl = filePath.replace('/app', '')
            if (!imageUrl.startsWith('/')) {
              imageUrl = '/' + imageUrl
            }
            console.log('📸 Job completed, file path:', filePath)
            console.log('📸 Converted to URL:', imageUrl)
            return imageUrl
          } else {
            console.log('⚠️ Job completed but no file_paths in result:', job.result)
          }
        } else if (job.status === 'failed') {
          throw new Error(job.error || 'Generation failed')
        }

        console.log(`⏳ Job status: ${job.status}, progress: ${job.progress}`)

      } catch (err) {
        console.error('Polling error:', err)
      }
    }

    throw new Error('Generation timed out')
  }

  const getCacheKey = (presetsToApply) => {
    // Create deterministic cache key from subject + sorted presets
    const presetIds = presetsToApply
      .map(p => `${p.category}:${p.preset_id}`)
      .sort()
      .join('|')

    return `${subject}|${presetIds}`
  }

  const handleDragStart = (e, preset, category) => {
    e.dataTransfer.setData('preset', JSON.stringify({
      ...preset,
      category
    }))
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

  // Composition Management
  const fetchCompositions = async () => {
    try {
      const response = await api.get('/compositions/list')
      setCompositions(response.data)
    } catch (err) {
      console.error('Failed to fetch compositions:', err)
    }
  }

  const handleSaveComposition = async () => {
    if (!compositionName.trim()) {
      alert('Please enter a name for this composition')
      return
    }

    if (appliedPresets.length === 0) {
      alert('No presets to save')
      return
    }

    try {
      await api.post('/compositions/save', {
        name: compositionName,
        subject: subject,
        presets: appliedPresets
      })

      // Refresh compositions list
      await fetchCompositions()

      // Close dialog and reset
      setShowSaveDialog(false)
      setCompositionName('')

      alert('Composition saved successfully!')
    } catch (err) {
      console.error('Failed to save composition:', err)
      alert('Failed to save composition: ' + (err.response?.data?.detail || err.message))
    }
  }

  const loadComposition = async (composition) => {
    try {
      // Set subject
      setSubject(composition.subject)

      // Clear current presets
      setAppliedPresets([])

      // Apply composition presets
      setAppliedPresets(composition.presets)

      // Clear generation since we're starting fresh
      setGeneratedImage(null)
      setGenerationHistory([])

      // Generate with new presets
      await generateImage(composition.presets)

      alert(`Loaded composition: ${composition.name}`)
    } catch (err) {
      console.error('Failed to load composition:', err)
      alert('Failed to load composition')
    }
  }

  const deleteComposition = async (compositionId) => {
    if (!confirm('Are you sure you want to delete this composition?')) {
      return
    }

    try {
      await api.delete(`/compositions/${compositionId}`)
      await fetchCompositions()
      alert('Composition deleted')
    } catch (err) {
      console.error('Failed to delete composition:', err)
      alert('Failed to delete composition')
    }
  }

  const downloadImage = async () => {
    if (!generatedImage) return

    try {
      // Fetch the image
      const response = await fetch(generatedImage)
      const blob = await response.blob()

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      // Generate filename with timestamp and preset info
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
      const presetNames = appliedPresets.map(p => p.display_name || p.preset_id).join('_')
      const filename = `composition_${subject}_${presetNames.substring(0, 50)}_${timestamp}.png`

      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      // Cleanup
      window.URL.revokeObjectURL(url)

      console.log('✅ Downloaded image:', filename)
    } catch (err) {
      console.error('Failed to download image:', err)
      alert('Failed to download image')
    }
  }

  if (loading) {
    return (
      <div className="composer-loading">
        <p>Loading presets...</p>
      </div>
    )
  }

  return (
    <div className="composer">
      {/* Mobile Tab Navigation */}
      <div className="mobile-tabs">
        <button
          className={`mobile-tab ${mobileTab === 'library' ? 'active' : ''}`}
          onClick={() => setMobileTab('library')}
        >
          <span className="tab-icon">📚</span>
          <span className="tab-label">Library</span>
        </button>
        <button
          className={`mobile-tab ${mobileTab === 'canvas' ? 'active' : ''}`}
          onClick={() => setMobileTab('canvas')}
        >
          <span className="tab-icon">🎨</span>
          <span className="tab-label">Canvas</span>
          {generating && <span className="tab-badge">⚡</span>}
        </button>
        <button
          className={`mobile-tab ${mobileTab === 'applied' ? 'active' : ''}`}
          onClick={() => setMobileTab('applied')}
        >
          <span className="tab-icon">📋</span>
          <span className="tab-label">Applied</span>
          {appliedPresets.length > 0 && (
            <span className="tab-badge">{appliedPresets.length}</span>
          )}
        </button>
      </div>

      {/* Left Panel - Preset Library */}
      <div className={`composer-sidebar left ${mobileTab === 'library' ? 'mobile-active' : ''}`}>
        <h2>Preset Library</h2>
        <div className="category-tabs">
          {categories.map(cat => (
            <button
              key={cat.key}
              className={`category-tab ${activeCategory === cat.key ? 'active' : ''}`}
              onClick={() => setActiveCategory(activeCategory === cat.key ? null : cat.key)}
            >
              {cat.label}
              <span className="preset-count">{presets[cat.key]?.length || 0}</span>
            </button>
          ))}
        </div>

        <div className="presets-container">
          {activeCategory ? (
            <div className="preset-category-section">
              <h3>{categories.find(c => c.key === activeCategory)?.label}</h3>

              {/* Search Input */}
              <div className="preset-search">
                <input
                  type="text"
                  placeholder="Search presets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                />
                {searchQuery && (
                  <button
                    className="clear-search-btn"
                    onClick={() => setSearchQuery('')}
                    title="Clear search"
                  >
                    ×
                  </button>
                )}
              </div>

              <div className="preset-library-grid">
                {(presets[activeCategory] || [])
                  .filter(preset => {
                    // Filter by search query
                    if (!searchQuery) return true

                    const searchLower = searchQuery.toLowerCase()
                    const displayName = (preset.display_name || preset.preset_id).toLowerCase()
                    const presetId = preset.preset_id.toLowerCase()

                    return displayName.includes(searchLower) || presetId.includes(searchLower)
                  })
                  .sort((a, b) => {
                    const cat = categories.find(c => c.key === activeCategory)
                    const aKey = `${cat.apiCategory}:${a.preset_id}`
                    const bKey = `${cat.apiCategory}:${b.preset_id}`
                    const aFav = favorites.includes(aKey)
                    const bFav = favorites.includes(bKey)

                    // Favorites first
                    if (aFav && !bFav) return -1
                    if (!aFav && bFav) return 1
                    return 0
                  })
                  .map(preset => {
                    const cat = categories.find(c => c.key === activeCategory)
                    const favoriteKey = `${cat.apiCategory}:${preset.preset_id}`
                    const isFavorite = favorites.includes(favoriteKey)
                    const isSelected = selectedPreset?.preset_id === preset.preset_id

                    return (
                      <PresetThumbnail
                        key={preset.preset_id}
                        preset={preset}
                        category={cat.apiCategory}
                        isFavorite={isFavorite}
                        isSelected={isSelected}
                        onDragStart={(e) => handleDragStart(e, preset, cat.apiCategory)}
                        onClick={() => handlePresetClick(preset, cat.apiCategory)}
                        onToggleFavorite={() => toggleFavorite(preset, cat.apiCategory)}
                      />
                    )
                  })}
              </div>
            </div>
          ) : (
            <div className="no-category-selected">
              <p>Select a category to view presets</p>
            </div>
          )}
        </div>

        {selectedPreset && (
          <div className="apply-preset-bar">
            <div className="apply-preset-info">
              <span className="apply-preset-name">{selectedPreset.display_name || selectedPreset.preset_id}</span>
              <span className="apply-preset-hint">Click again or use button to apply</span>
            </div>
            <button className="apply-preset-btn" onClick={applySelectedPreset}>
              Apply Preset
            </button>
          </div>
        )}
      </div>

      {/* Center Panel - Canvas */}
      <div className={`composer-canvas ${mobileTab === 'canvas' ? 'mobile-active' : ''}`}>
        <div className="canvas-header">
          <div className="canvas-header-top">
            <div>
              <h2>Composition Canvas</h2>
              <p className="canvas-hint">Drag presets here to build your image</p>
            </div>
            <div className="subject-selector">
              <label htmlFor="subject-select">Subject:</label>
              <select
                id="subject-select"
                value={subject}
                onChange={(e) => handleSubjectChange(e.target.value)}
              >
                {subjects.map(subj => (
                  <option key={subj.filename} value={subj.filename}>
                    {subj.filename} {subj.source === 'uploaded' ? '(uploaded)' : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div
          className="drop-zone"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {generatedImage ? (
            <>
              <img
                src={generatedImage}
                alt="Generated composition"
                className="generated-preview"
                onLoad={() => console.log('✅ Image loaded successfully:', generatedImage)}
                onError={(e) => {
                  console.error('❌ Image failed to load:', generatedImage)
                  console.error('Error event:', e)
                }}
              />
              {generating && (
                <div className="generating-badge">
                  <div className="spinner-small"></div>
                  <span>Generating...</span>
                </div>
              )}
              {!generating && (
                <button
                  className="download-image-btn"
                  onClick={downloadImage}
                  title="Download image"
                >
                  ⬇ Download
                </button>
              )}
            </>
          ) : (
            <>
              <div className="empty-canvas">
                <div className="subject-placeholder">
                  <p>Subject: {subject}</p>
                  <p className="canvas-instruction">Drop presets to start composing</p>
                </div>
              </div>
              {generating && (
                <div className="generating-overlay">
                  <div className="spinner"></div>
                  <p>Generating...</p>
                </div>
              )}
            </>
          )}
        </div>

        {generationHistory.length > 0 && (
          <div className="generation-cache-info">
            <p>💾 {generationHistory.length} combination(s) cached</p>
          </div>
        )}
      </div>

      {/* Right Panel - Applied Presets Stack */}
      <div className={`composer-sidebar right ${mobileTab === 'applied' ? 'mobile-active' : ''}`}>
        {/* Saved Compositions Section */}
        <div className="compositions-section">
          <button
            className="compositions-toggle-btn"
            onClick={() => setShowCompositions(!showCompositions)}
          >
            <span>💾 Saved Compositions ({compositions.length})</span>
            <span>{showCompositions ? '▼' : '▶'}</span>
          </button>

          {showCompositions && (
            <div className="compositions-list">
              {compositions.length === 0 ? (
                <p className="no-compositions">No saved compositions yet</p>
              ) : (
                compositions.map(comp => (
                  <div key={comp.composition_id} className="composition-item">
                    <div className="composition-info">
                      <span className="composition-name">{comp.name}</span>
                      <span className="composition-meta">
                        {comp.presets.length} preset(s) · {comp.subject}
                      </span>
                    </div>
                    <div className="composition-actions">
                      <button
                        className="load-comp-btn"
                        onClick={() => loadComposition(comp)}
                        title="Load composition"
                      >
                        ↻
                      </button>
                      <button
                        className="delete-comp-btn"
                        onClick={() => deleteComposition(comp.composition_id)}
                        title="Delete composition"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <h2>Applied Presets</h2>
        <p className="stack-count">{appliedPresets.length} preset(s)</p>

        {appliedPresets.length === 0 ? (
          <div className="no-presets">
            <p>No presets applied yet</p>
            <p className="hint">Drag presets from the left to start</p>
          </div>
        ) : (
          <div className="applied-presets-list">
            {appliedPresets.map((preset, index) => {
              const catConfig = categoryConfig.find(c => c.apiCategory === preset.category)
              return (
                <div key={index} className="applied-preset-item">
                  <div className="applied-preset-info">
                    <span className="preset-category-badge">{catConfig?.label}</span>
                    <span className="preset-name">{preset.display_name || preset.preset_id}</span>
                  </div>
                  <button
                    className="remove-preset-btn"
                    onClick={() => removePreset(index)}
                    title="Remove preset"
                  >
                    ×
                  </button>
                </div>
              )
            })}
          </div>
        )}

        {appliedPresets.length > 0 && (
          <>
            <button
              className="save-composition-btn"
              onClick={() => setShowSaveDialog(true)}
            >
              💾 Save Composition
            </button>
            <button
              className="clear-all-btn"
              onClick={() => {
                setAppliedPresets([])
                setGeneratedImage(null)
              }}
            >
              Clear All
            </button>
          </>
        )}
      </div>

      {/* Save Composition Dialog */}
      {showSaveDialog && (
        <div className="modal-overlay" onClick={() => setShowSaveDialog(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <h3>Save Composition</h3>
            <p className="modal-hint">Give your composition a name</p>
            <input
              type="text"
              placeholder="e.g., Summer Beach Look"
              value={compositionName}
              onChange={(e) => setCompositionName(e.target.value)}
              className="composition-name-input"
              autoFocus
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSaveComposition()
                }
              }}
            />
            <div className="modal-actions">
              <button
                className="modal-btn cancel"
                onClick={() => {
                  setShowSaveDialog(false)
                  setCompositionName('')
                }}
              >
                Cancel
              </button>
              <button
                className="modal-btn save"
                onClick={handleSaveComposition}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function PresetThumbnail({ preset, category, isFavorite, isSelected, onDragStart, onClick, onToggleFavorite }) {
  const [imageLoaded, setImageLoaded] = useState(false)
  const [imageError, setImageError] = useState(false)

  const previewUrl = `/api/presets/${category}/${preset.preset_id}/preview?t=${Date.now()}`

  return (
    <div
      className={`preset-thumbnail ${isSelected ? 'selected' : ''}`}
      draggable
      onDragStart={onDragStart}
      onClick={onClick}
    >
      <div className="preset-thumbnail-preview">
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
        <button
          className={`favorite-btn-small ${isFavorite ? 'favorited' : ''}`}
          onClick={(e) => {
            e.stopPropagation()
            onToggleFavorite()
          }}
          title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          {isFavorite ? '★' : '☆'}
        </button>
      </div>
      <div className="preset-thumbnail-name">
        {preset.display_name || preset.preset_id}
      </div>
    </div>
  )
}

export default Composer
