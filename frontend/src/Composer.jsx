import { useState, useEffect, useCallback, useMemo } from 'react'
import './Composer.css'
import api from './api/client'
import { useDebounce } from './hooks/useDebounce'
import { useLRUCache } from './hooks/useLRUCache'

// Category configurations (static, moved outside component)
const categoryConfig = [
  // Clothing item categories
  { key: 'headwear', label: 'Headwear', apiCategory: 'clothing_items', clothingCategory: 'headwear' },
  { key: 'eyewear', label: 'Eyewear', apiCategory: 'clothing_items', clothingCategory: 'eyewear' },
  { key: 'earrings', label: 'Earrings', apiCategory: 'clothing_items', clothingCategory: 'earrings' },
  { key: 'neckwear', label: 'Neckwear', apiCategory: 'clothing_items', clothingCategory: 'neckwear' },
  { key: 'tops', label: 'Tops', apiCategory: 'clothing_items', clothingCategory: 'tops' },
  { key: 'overtops', label: 'Overtops', apiCategory: 'clothing_items', clothingCategory: 'overtops' },
  { key: 'outerwear', label: 'Outerwear', apiCategory: 'clothing_items', clothingCategory: 'outerwear' },
  { key: 'one_piece', label: 'One-Piece', apiCategory: 'clothing_items', clothingCategory: 'one_piece' },
  { key: 'bottoms', label: 'Bottoms', apiCategory: 'clothing_items', clothingCategory: 'bottoms' },
  { key: 'belts', label: 'Belts', apiCategory: 'clothing_items', clothingCategory: 'belts' },
  { key: 'hosiery', label: 'Hosiery', apiCategory: 'clothing_items', clothingCategory: 'hosiery' },
  { key: 'footwear', label: 'Footwear', apiCategory: 'clothing_items', clothingCategory: 'footwear' },
  { key: 'bags', label: 'Bags', apiCategory: 'clothing_items', clothingCategory: 'bags' },
  { key: 'wristwear', label: 'Wristwear', apiCategory: 'clothing_items', clothingCategory: 'wristwear' },
  { key: 'handwear', label: 'Handwear', apiCategory: 'clothing_items', clothingCategory: 'handwear' },

  // Style presets
  { key: 'visual_style', label: 'Visual Style', apiCategory: 'visual_styles' },
  { key: 'art_style', label: 'Art Style', apiCategory: 'art_styles' },
  { key: 'hair_style', label: 'Hair Style', apiCategory: 'hair_styles' },
  { key: 'hair_color', label: 'Hair Color', apiCategory: 'hair_colors' },
  { key: 'makeup', label: 'Makeup', apiCategory: 'makeup' },
  { key: 'expression', label: 'Expression', apiCategory: 'expressions' },
  { key: 'accessories', label: 'Accessories', apiCategory: 'accessories' }
]

function Composer() {
  const [subject, setSubject] = useState(null) // Now stores character_id
  const [characters, setCharacters] = useState([])
  const [categories, setCategories] = useState([])
  const [presets, setPresets] = useState({})
  const [loading, setLoading] = useState(true)
  const [appliedPresets, setAppliedPresets] = useState([])
  const [generatedImage, setGeneratedImage] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [favorites, setFavorites] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)
  const [selectedPreset, setSelectedPreset] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [compositions, setCompositions] = useState([])

  // Debounce search query to avoid expensive filtering on every keystroke (300ms delay)
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  // LRU cache for generation results (max 50 items, auto-evicts least recently used)
  const generationCache = useLRUCache(50)

  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [compositionName, setCompositionName] = useState('')
  const [showCompositions, setShowCompositions] = useState(false)
  const [mobileTab, setMobileTab] = useState('canvas') // 'library', 'canvas', 'applied'

  useEffect(() => {
    loadPresets()
    fetchFavorites()
    fetchCharacters()
    fetchCompositions()
  }, [])

  const loadPresets = async () => {
    setLoading(true)

    try {
      const presetsData = {}

      // Load clothing items by category
      const clothingCategories = categoryConfig.filter(cat => cat.apiCategory === 'clothing_items')
      for (const cat of clothingCategories) {
        try {
          // CRITICAL: Must include trailing slash - FastAPI is strict about this
          const response = await api.get(`/clothing-items/?category=${cat.clothingCategory}`)
          // Map clothing items to preset-like format (using snake_case field names from API)
          presetsData[cat.key] = (response.data.items || []).map(item => ({
            preset_id: item.item_id,
            display_name: `${item.item} - ${item.color}`,
            category: item.category,
            data: item
          }))
        } catch (err) {
          console.error(`Failed to load ${cat.key} clothing items:`, err)
          presetsData[cat.key] = []
        }
      }

      // Load style presets via batch endpoint
      const styleCategories = categoryConfig.filter(cat => cat.apiCategory !== 'clothing_items')
      try {
        const response = await api.get('/presets/batch')
        for (const cat of styleCategories) {
          presetsData[cat.key] = response.data[cat.apiCategory] || []
        }
        console.log('✅ Loaded style presets in batch request')
      } catch (err) {
        console.error('Batch preset loading failed, falling back to individual requests:', err)
        // Fallback to individual requests
        for (const cat of styleCategories) {
          try {
            const response = await api.get(`/presets/${cat.apiCategory}`)
            presetsData[cat.key] = response.data.presets || []
          } catch (err) {
            console.error(`Failed to load ${cat.key}:`, err)
            presetsData[cat.key] = []
          }
        }
      }

      setPresets(presetsData)
      setCategories(categoryConfig)
      console.log('✅ Loaded all presets and clothing items')
    } catch (err) {
      console.error('Failed to load presets:', err)
    }

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

  const fetchCharacters = async () => {
    try {
      const response = await api.get('/characters/')
      setCharacters(response.data.characters || [])
      // Set first character as default if available
      if (response.data.characters && response.data.characters.length > 0 && !subject) {
        setSubject(response.data.characters[0].character_id)
      }
    } catch (err) {
      console.error('Failed to fetch characters:', err)
      setCharacters([])
    }
  }

  const handleSubjectChange = (newSubject) => {
    setSubject(newSubject)
    // Clear generation cache since it's subject-specific
    generationCache.clear()
    setGeneratedImage(null)
    // Optionally clear applied presets
    // setAppliedPresets([])
  }

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
  }, [])

  const handleDragStart = useCallback((e, preset, category) => {
    // For clothing items, preserve the original category (e.g., "outerwear")
    // For style presets, use the passed category (e.g., "visual_styles")
    const presetData = preset.category && preset.data ? preset : { ...preset, category }
    e.dataTransfer.setData('preset', JSON.stringify(presetData))
  }, [])

  const getCacheKey = useCallback((presetsToApply) => {
    // Create deterministic cache key from subject + sorted presets
    const presetIds = presetsToApply
      .map(p => `${p.category}:${p.preset_id}`)
      .sort()
      .join('|')

    return `${subject}|${presetIds}`
  }, [subject])

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

  const generateImage = useCallback(async (presetsToApply) => {
    if (presetsToApply.length === 0) return

    setGenerating(true)

    try {
      // Check LRU cache first
      const cacheKey = getCacheKey(presetsToApply)
      const cached = generationCache.get(cacheKey)

      if (cached) {
        console.log('✅ Using cached result:', cached)
        setGeneratedImage(cached)
        setGenerating(false)
        return
      }

      // Find the selected character to get its reference image path
      const selectedCharacter = characters.find(c => c.character_id === subject)
      if (!selectedCharacter) {
        alert('Please select a character')
        setGenerating(false)
        return
      }

      if (!selectedCharacter.reference_image_url) {
        alert('Selected character has no reference image')
        setGenerating(false)
        return
      }

      // Use the character's reference image path for generation
      // The backend stores character images as: data/characters/{character_id}_ref.png
      const characterImagePath = `data/characters/${selectedCharacter.character_id}_ref.png`

      // Build request payload
      const payload = {
        subject_image: characterImagePath,
        variations: 1
      }

      // Add presets and clothing items to payload
      presetsToApply.forEach(preset => {
        console.log('🔍 Processing preset:', {
          preset_id: preset.preset_id,
          category: preset.category,
          display_name: preset.display_name
        })

        // Find the category configuration
        const catConfig = categoryConfig.find(c => {
          // For clothing items, match by category field
          if (c.apiCategory === 'clothing_items') {
            const matches = preset.category === c.clothingCategory
            console.log(`  Checking clothing category: ${c.clothingCategory} === ${preset.category}? ${matches}`)
            return matches
          }
          // For style presets, match by apiCategory
          const matches = c.apiCategory === preset.category
          console.log(`  Checking style category: ${c.apiCategory} === ${preset.category}? ${matches}`)
          return matches
        })

        if (catConfig) {
          const categoryKey = catConfig.key
          console.log(`  ✓ Found category config: ${categoryKey}`)

          // Clothing items can be layered (multiple items per category)
          if (catConfig.apiCategory === 'clothing_items') {
            if (!payload[categoryKey]) {
              payload[categoryKey] = []
            }
            payload[categoryKey].push(preset.preset_id)
            console.log(`  ✓ Added clothing item to ${categoryKey}:`, preset.preset_id)
          } else {
            // Style presets replace (one per category)
            payload[categoryKey] = preset.preset_id
            console.log(`  ✓ Added style preset to ${categoryKey}:`, preset.preset_id)
          }
        } else {
          console.log(`  ✗ No category config found for:`, preset.category)
        }
      })

      console.log('🎨 Generating with payload:', JSON.stringify(payload, null, 2))

      const response = await api.post('/generate/modular', payload)
      const jobId = response.data.job_id

      // Poll for completion
      const imageUrl = await pollForCompletion(jobId)

      if (imageUrl) {
        console.log('✅ Generated image URL:', imageUrl)
        setGeneratedImage(imageUrl)

        // Cache the result in LRU cache
        generationCache.set(cacheKey, imageUrl)
      }
    } catch (err) {
      console.error('Generation failed:', err)
      alert('Failed to generate image: ' + (err.response?.data?.detail || err.message))
    } finally {
      setGenerating(false)
    }
  }, [subject, getCacheKey, generationCache, characters])

  const addPreset = useCallback(async (preset) => {
    let newAppliedPresets

    // Find category config to determine if items can be layered
    const catConfig = categoryConfig.find(c => {
      if (c.apiCategory === 'clothing_items') {
        return preset.category === c.clothingCategory
      }
      return c.apiCategory === preset.category
    })

    // Clothing items can be layered (multiple items per category)
    const canLayer = catConfig && catConfig.apiCategory === 'clothing_items'

    if (canLayer) {
      // Always add clothing items (they can layer/stack)
      newAppliedPresets = [...appliedPresets, preset]
    } else {
      // For style presets, check if preset of same category already exists
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
  }, [appliedPresets, generateImage])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    const presetData = e.dataTransfer.getData('preset')

    if (presetData) {
      const preset = JSON.parse(presetData)
      addPreset(preset)
    }
  }, [addPreset])

  const handlePresetClick = useCallback((preset, category) => {
    // For clothing items, preserve the original category (e.g., "outerwear")
    // For style presets, use the passed category (e.g., "visual_styles")
    const presetWithCategory = preset.category && preset.data ? preset : { ...preset, category }

    // If clicking the same preset, apply it
    if (selectedPreset?.preset_id === preset.preset_id) {
      addPreset(presetWithCategory)
    } else {
      // Otherwise, select it
      setSelectedPreset(presetWithCategory)
    }
  }, [selectedPreset, addPreset])

  const applySelectedPreset = useCallback(() => {
    if (selectedPreset) {
      addPreset(selectedPreset)
    }
  }, [selectedPreset, addPreset])

  const removePreset = useCallback(async (index) => {
    const newAppliedPresets = appliedPresets.filter((_, i) => i !== index)
    setAppliedPresets(newAppliedPresets)

    // Regenerate without removed preset
    if (newAppliedPresets.length > 0) {
      await generateImage(newAppliedPresets)
    } else {
      setGeneratedImage(null)
    }
  }, [appliedPresets, generateImage])

  const toggleFavorite = useCallback(async (preset, category) => {
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
  }, [favorites])

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

  const loadComposition = useCallback(async (composition) => {
    try {
      // Set subject
      setSubject(composition.subject)

      // Clear current presets
      setAppliedPresets([])

      // Apply composition presets
      setAppliedPresets(composition.presets)

      // Clear generation since we're starting fresh
      setGeneratedImage(null)
      generationCache.clear()

      // Generate with new presets
      await generateImage(composition.presets)

      alert(`Loaded composition: ${composition.name}`)
    } catch (err) {
      console.error('Failed to load composition:', err)
      alert('Failed to load composition')
    }
  }, [generateImage, generationCache])

  const deleteComposition = useCallback(async (compositionId) => {
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
  }, [])

  const downloadImage = useCallback(async () => {
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
      const characterName = characters.find(c => c.character_id === subject)?.name || 'unknown'
      const presetNames = appliedPresets.map(p => p.display_name || p.preset_id).join('_')
      const filename = `composition_${characterName}_${presetNames.substring(0, 50)}_${timestamp}.png`

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
  }, [generatedImage, appliedPresets, subject, characters])

  // Memoized filtered and sorted presets for the active category
  const filteredPresets = useMemo(() => {
    if (!activeCategory) return []

    return (presets[activeCategory] || [])
      .filter(preset => {
        // Filter by debounced search query (waits 300ms after typing stops)
        if (!debouncedSearchQuery) return true

        const searchLower = debouncedSearchQuery.toLowerCase()
        const displayName = (preset.display_name || preset.preset_id).toLowerCase()
        const presetId = preset.preset_id.toLowerCase()

        return displayName.includes(searchLower) || presetId.includes(searchLower)
      })
      .sort((a, b) => {
        const cat = categories.find(c => c.key === activeCategory)
        if (!cat) return 0

        const aKey = `${cat.apiCategory}:${a.preset_id}`
        const bKey = `${cat.apiCategory}:${b.preset_id}`
        const aFav = favorites.includes(aKey)
        const bFav = favorites.includes(bKey)

        // Favorites first
        if (aFav && !bFav) return -1
        if (!aFav && bFav) return 1
        return 0
      })
  }, [presets, activeCategory, debouncedSearchQuery, categories, favorites])

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
                {filteredPresets.map(preset => {
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
              <label htmlFor="subject-select">Character:</label>
              <select
                id="subject-select"
                value={subject || ''}
                onChange={(e) => handleSubjectChange(e.target.value)}
              >
                {characters.length === 0 ? (
                  <option value="">No characters available</option>
                ) : (
                  characters.map(char => (
                    <option key={char.character_id} value={char.character_id}>
                      {char.name}
                    </option>
                  ))
                )}
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
                  <p>Character: {characters.find(c => c.character_id === subject)?.name || 'None selected'}</p>
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

        {generationCache.size > 0 && (
          <div className="generation-cache-info">
            <p>💾 {generationCache.size} combination(s) cached (max 50)</p>
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
                        {comp.presets.length} preset(s) · {characters.find(c => c.character_id === comp.subject)?.name || comp.subject}
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
              // Find category config - handle both clothing items and style presets
              const catConfig = categoryConfig.find(c => {
                // For clothing items, match by clothingCategory field
                if (c.apiCategory === 'clothing_items') {
                  return preset.category === c.clothingCategory
                }
                // For style presets, match by apiCategory
                return c.apiCategory === preset.category
              })
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

  // For clothing items, use preview_image_path; for style presets, use API endpoint
  const isClothingItem = preset.data && preset.data.preview_image_path
  const previewUrl = isClothingItem
    ? preset.data.preview_image_path
    : `/api/presets/${category}/${preset.preset_id}/preview?t=${Date.now()}`

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
