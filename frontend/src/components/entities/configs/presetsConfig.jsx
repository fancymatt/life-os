import { useState, useEffect } from 'react'
import api from '../../../api/client'
import { formatDate } from './helpers'
import OutfitEditor from './OutfitEditor'
import LazyImage from '../LazyImage'

/**
 * Preset Entity Configurations
 *
 * Factory function and configurations for all preset-based entities
 * (outfits, expressions, makeup, hair styles, hair colors, visual styles, art styles, accessories)
 */

/**
 * Create a preset-based entity configuration
 * @param {Object} options - Configuration options
 * @returns {Object} Entity configuration object
 */
const createPresetConfig = (options) => ({
  entityType: options.entityType,
  title: options.title,
  icon: options.icon,
  emptyMessage: `No ${options.title.toLowerCase()} yet. Analyze your first ${options.entityType}!`,
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  defaultSort: 'newest',
  searchFields: ['display_name'],
  category: options.category,

  actions: [
    {
      label: `Analyze ${options.title}`,
      icon: '+',
      primary: true,
      path: `/tools/analyzers/${options.analyzerPath}`
    }
  ],

  fetchEntities: async () => {
    const response = await api.get(`/presets/${options.category}`)
    return (response.data.presets || []).map(preset => ({
      id: preset.preset_id,
      title: preset.display_name || `Untitled ${options.title}`,
      presetId: preset.preset_id,
      category: preset.category,
      createdAt: preset.created_at,
      data: {} // Empty initially, will be loaded on-demand in edit mode
    }))
  },

  loadFullData: async (entity) => {
    // Fetch the full preset data from the individual endpoint
    const response = await api.get(`/presets/${options.category}/${entity.presetId}`)
    return response.data
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (entity) => (
    <div className="entity-card">
      <div className="entity-card-image" style={{ height: '280px' }}>
        <LazyImage
          src={`/api/presets/${options.category}/${entity.presetId}/preview?t=${Date.now()}`}
          alt={entity.title}
          onError={(e) => {
            e.target.style.display = 'none'
            e.target.parentElement.innerHTML = `<div class="entity-card-placeholder">${options.icon}</div>`
          }}
        />
      </div>
      <div className="entity-card-content">
        <h3 className="entity-card-title">{entity.title}</h3>
        {formatDate(entity.createdAt) && (
          <p className="entity-card-date">{formatDate(entity.createdAt)}</p>
        )}
      </div>
    </div>
  ),

  renderPreview: (entity) => (
    <img
      src={`/api/presets/${options.category}/${entity.presetId}/preview?t=${Date.now()}`}
      alt={entity.title}
      style={{ width: '100%', height: 'auto', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)' }}
      onError={(e) => e.target.style.display = 'none'}
    />
  ),

  renderDetail: (entity) => (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ color: 'white', margin: '0 0 1.5rem 0' }}>{entity.title}</h2>
      <div style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
        {Object.entries(entity.data || {}).map(([key, value]) => {
          if (key === '_metadata') return null
          return (
            <div key={key} style={{ marginBottom: '1rem' }}>
              <strong style={{ color: 'rgba(255, 255, 255, 0.9)', textTransform: 'capitalize' }}>
                {key.replace(/_/g, ' ')}:
              </strong>{' '}
              {Array.isArray(value) ? value.join(', ') : value}
            </div>
          )
        })}
      </div>
      {formatDate(entity.createdAt) && (
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', margin: 0 }}>
            <strong>Created:</strong> {formatDate(entity.createdAt)}
          </p>
        </div>
      )}
    </div>
  ),

  renderEdit: (entity, editedData, editedTitle, handlers) => (
    <div style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Name
        </label>
        <input
          type="text"
          value={editedTitle}
          onChange={(e) => handlers.setEditedTitle(e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem',
            background: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            color: 'white',
            fontSize: '1rem'
          }}
        />
      </div>

      <div style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
        {Object.entries(editedData || {}).map(([key, value]) => {
          if (key === '_metadata') return null

          // Check if value is array of objects (complex structure)
          const isComplexArray = Array.isArray(value) && value.length > 0 && typeof value[0] === 'object'

          return (
            <div key={key} style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', textTransform: 'capitalize', fontWeight: 500 }}>
                {key.replace(/_/g, ' ')}
              </label>
              {isComplexArray ? (
                // Handle arrays of objects as JSON
                <textarea
                  value={JSON.stringify(value, null, 2)}
                  onChange={(e) => {
                    try {
                      const parsed = JSON.parse(e.target.value)
                      handlers.updateField(key, parsed)
                    } catch (err) {
                      // Invalid JSON, update the raw string so user can continue editing
                      // We'll use a temporary marker to indicate this is unparsed JSON
                      handlers.updateField(key + '_temp', e.target.value)
                    }
                  }}
                  rows="10"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '0.85rem',
                    resize: 'vertical',
                    fontFamily: 'monospace'
                  }}
                />
              ) : Array.isArray(value) ? (
                // Handle simple arrays as comma-separated values
                <input
                  type="text"
                  value={value.join(', ')}
                  onChange={(e) => handlers.updateField(key, e.target.value.split(',').map(v => v.trim()))}
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
              ) : (
                // Handle simple string/number values
                <textarea
                  value={value || ''}
                  onChange={(e) => handlers.updateField(key, e.target.value)}
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
                    fontFamily: 'inherit'
                  }}
                />
              )}
            </div>
          )
        })}
      </div>
    </div>
  ),

  saveEntity: async (entity, updates) => {
    // Save the preset
    await api.put(
      `/presets/${options.category}/${entity.presetId}`,
      {
        data: updates.data,
        display_name: updates.title
      }
    )

    // Reload the full preset data after save (PUT only returns success message)
    const response = await api.get(`/presets/${options.category}/${entity.presetId}`)
    return response.data
  },

  deleteEntity: async (entity) => {
    await api.delete(`/presets/${options.category}/${entity.presetId}`)
  }
})

// =============================================================================
// OUTFITS (with custom editor)
// =============================================================================

export const outfitsConfig = {
  ...createPresetConfig({
    entityType: 'outfit',
    title: 'Outfits',
    icon: '👔',
    category: 'outfits',
    analyzerPath: 'outfit'
  }),
  // Preview renderer for left column
  renderPreview: (entity) => (
    <img
      src={`/api/presets/outfits/${entity.presetId}/preview?t=${Date.now()}`}
      alt={entity.title}
      style={{ width: '100%', height: 'auto', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)' }}
      onError={(e) => e.target.style.display = 'none'}
    />
  ),
  // Override renderEdit with custom outfit editor
  renderEdit: (entity, editedData, editedTitle, handlers) => (
    <OutfitEditor editedData={editedData} editedTitle={editedTitle} handlers={handlers} />
  )
}

// =============================================================================
// ALL OTHER PRESET-BASED ENTITIES
// =============================================================================

// Note: expressionsConfig and makeupsConfig are defined later with preview components

/**
 * Hair Style Preview Component (matches clothing items layout)
 */
function HairStylePreview({ entity, onUpdate }) {
  const [generatingJobId, setGeneratingJobId] = useState(null)
  const [jobProgress, setJobProgress] = useState(null)
  const [trackingPresetId, setTrackingPresetId] = useState(null)

  // Reset state if entity changes (to prevent showing overlay on wrong entity after refresh)
  useEffect(() => {
    if (trackingPresetId && trackingPresetId !== entity.presetId) {
      console.log(`Entity changed from ${trackingPresetId} to ${entity.presetId}, resetting state`)
      setGeneratingJobId(null)
      setJobProgress(null)
      setTrackingPresetId(null)
    }
  }, [entity.presetId, trackingPresetId])

  // Poll for job status if we're tracking a job
  useEffect(() => {
    if (!generatingJobId) return

    const pollInterval = setInterval(async () => {
      try {
        const response = await api.get(`/jobs/${generatingJobId}`)
        const job = response.data

        setJobProgress(job.progress)

        if (job.status === 'completed') {
          console.log('✅ Preview generation completed, refreshing preview...')
          setGeneratingJobId(null)
          setJobProgress(null)
          setTrackingPresetId(null)
          // Refresh the preview to get the new image
          if (onUpdate) onUpdate()
        } else if (job.status === 'failed') {
          console.error('❌ Preview generation failed')
          setGeneratingJobId(null)
          setJobProgress(null)
          setTrackingPresetId(null)
        }
      } catch (error) {
        console.error('Failed to poll job status:', error)
        // If job not found (404) or other error, stop polling
        if (error.response?.status === 404) {
          console.warn('Job not found, stopping polling')
        }
        setGeneratingJobId(null)
        setJobProgress(null)
        setTrackingPresetId(null)
      }
    }, 1000) // Poll every second

    return () => clearInterval(pollInterval)
  }, [generatingJobId, onUpdate])

  const handleGeneratePreview = async (e) => {
    const button = e.currentTarget
    const originalText = button.textContent

    try {
      button.disabled = true
      button.textContent = '⏳ Queueing...'

      const response = await api.post(`/presets/hair_styles/${entity.presetId}/generate-preview`)
      const jobId = response.data.job_id

      console.log(`✅ Preview generation queued (Job: ${jobId}) for preset ${entity.presetId}`)
      button.textContent = '✅ Queued!'

      // Start tracking this job for THIS specific entity
      setTimeout(() => {
        setGeneratingJobId(jobId)
        setTrackingPresetId(entity.presetId)
        button.textContent = originalText
        button.disabled = false
      }, 500)
    } catch (error) {
      console.error('Failed to queue preview generation:', error)
      button.textContent = '❌ Failed'
      setTimeout(() => {
        button.textContent = originalText
        button.disabled = false
      }, 2000)
    }
  }

  const handleCreateTestImage = async (e) => {
    const button = e.currentTarget
    const originalText = button.textContent

    try {
      button.disabled = true
      button.textContent = '⏳ Queueing...'

      const response = await api.post(`/presets/hair_styles/${entity.presetId}/generate-test-image`)

      console.log(`✅ Test image generation queued (Job: ${response.data.job_id})`)
      button.textContent = '✅ Queued!'
      setTimeout(() => {
        button.textContent = originalText
        button.disabled = false
      }, 2000)
    } catch (error) {
      console.error('Failed to generate test image:', error)
      button.textContent = '❌ Failed'
      setTimeout(() => {
        button.textContent = originalText
        button.disabled = false
      }, 2000)
    }
  }

  return (
    <div style={{ padding: '1rem' }}>
      {/* Preview Image with loading overlay */}
      <div style={{ position: 'relative', marginBottom: '1rem' }}>
        <div style={{
          borderRadius: '8px',
          overflow: 'hidden',
          background: 'rgba(0, 0, 0, 0.3)',
          minHeight: '300px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <LazyImage
            src={`/api/presets/hair_styles/${entity.presetId}/preview?t=${Date.now()}`}
            alt={entity.title}
            style={{
              width: '100%',
              height: 'auto',
              display: 'block'
            }}
            onError={(e) => {
              // Show placeholder icon when no preview exists
              e.target.style.display = 'none'
              const placeholder = document.createElement('div')
              placeholder.style.cssText = 'font-size: 4rem; color: rgba(255, 255, 255, 0.3);'
              placeholder.textContent = '💇'
              e.target.parentElement.appendChild(placeholder)
            }}
          />
        </div>

        {/* Loading overlay when generating (only show for this specific entity) */}
        {generatingJobId && trackingPresetId === entity.presetId && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            borderRadius: '8px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            minHeight: '300px'
          }}>
            <div style={{
              fontSize: '3rem',
              animation: 'spin 2s linear infinite'
            }}>
              🎨
            </div>
            <div style={{ color: 'white', fontSize: '0.95rem' }}>
              Generating preview...
            </div>
            {jobProgress !== null && (
              <div style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.85rem' }}>
                {Math.round(jobProgress)}%
              </div>
            )}
          </div>
        )}
      </div>

      {/* Generate Preview Button */}
      <button
        onClick={handleGeneratePreview}
        style={{
          width: '100%',
          padding: '0.75rem',
          marginBottom: '0.5rem',
          background: 'rgba(168, 85, 247, 0.2)',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          borderRadius: '8px',
          color: 'rgba(168, 85, 247, 1)',
          cursor: 'pointer',
          fontSize: '0.95rem',
          fontWeight: '500',
          transition: 'all 0.2s'
        }}
        onMouseEnter={(e) => {
          if (!e.currentTarget.disabled) {
            e.currentTarget.style.background = 'rgba(168, 85, 247, 0.3)'
          }
        }}
        onMouseLeave={(e) => {
          if (!e.currentTarget.disabled) {
            e.currentTarget.style.background = 'rgba(168, 85, 247, 0.2)'
          }
        }}
      >
        🎨 Generate Preview
      </button>

      {/* Create Test Image Button */}
      <button
        onClick={handleCreateTestImage}
        style={{
          width: '100%',
          padding: '0.75rem',
          background: 'rgba(99, 102, 241, 0.2)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: '8px',
          color: 'rgba(99, 102, 241, 1)',
          cursor: 'pointer',
          fontSize: '0.95rem',
          fontWeight: '500',
          transition: 'all 0.2s'
        }}
        onMouseEnter={(e) => {
          if (!e.currentTarget.disabled) {
            e.currentTarget.style.background = 'rgba(99, 102, 241, 0.3)'
          }
        }}
        onMouseLeave={(e) => {
          if (!e.currentTarget.disabled) {
            e.currentTarget.style.background = 'rgba(99, 102, 241, 0.2)'
          }
        }}
      >
        🎨 Create Test Image
      </button>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export const hairStylesConfig = {
  ...createPresetConfig({
    entityType: 'hair style',
    title: 'Hair Styles',
    icon: '💇',
    category: 'hair_styles',
    analyzerPath: 'hair-style'
  }),
  enableGallery: true,
  renderPreview: (entity, onUpdate) => <HairStylePreview entity={entity} onUpdate={onUpdate} />
}

/**
 * Generic Preset Preview Component Factory
 * Creates a preview component for any preset category
 */
function createPresetPreview(category, icon) {
  return function PresetPreview({ entity, onUpdate }) {
    const [generatingJobId, setGeneratingJobId] = useState(null)
    const [jobProgress, setJobProgress] = useState(null)
    const [trackingPresetId, setTrackingPresetId] = useState(null)

    // Reset state if entity changes
    useEffect(() => {
      if (trackingPresetId && trackingPresetId !== entity.presetId) {
        setGeneratingJobId(null)
        setJobProgress(null)
        setTrackingPresetId(null)
      }
    }, [entity.presetId, trackingPresetId])

    // Poll for job status
    useEffect(() => {
      if (!generatingJobId) return

      const pollInterval = setInterval(async () => {
        try {
          const response = await api.get(`/jobs/${generatingJobId}`)
          const job = response.data

          setJobProgress(job.progress)

          if (job.status === 'completed') {
            setGeneratingJobId(null)
            setJobProgress(null)
            setTrackingPresetId(null)
            if (onUpdate) onUpdate()
          } else if (job.status === 'failed') {
            setGeneratingJobId(null)
            setJobProgress(null)
            setTrackingPresetId(null)
          }
        } catch (error) {
          if (error.response?.status === 404) {
            console.warn('Job not found, stopping polling')
          }
          setGeneratingJobId(null)
          setJobProgress(null)
          setTrackingPresetId(null)
        }
      }, 1000)

      return () => clearInterval(pollInterval)
    }, [generatingJobId, onUpdate])

    const handleGeneratePreview = async (e) => {
      const button = e.currentTarget
      const originalText = button.textContent

      try {
        button.disabled = true
        button.textContent = '⏳ Queueing...'

        const response = await api.post(`/presets/${category}/${entity.presetId}/generate-preview`)
        const jobId = response.data.job_id

        button.textContent = '✅ Queued!'

        setTimeout(() => {
          setGeneratingJobId(jobId)
          setTrackingPresetId(entity.presetId)
          button.textContent = originalText
          button.disabled = false
        }, 500)
      } catch (error) {
        console.error('Failed to queue preview generation:', error)
        button.textContent = '❌ Failed'
        setTimeout(() => {
          button.textContent = originalText
          button.disabled = false
        }, 2000)
      }
    }

    const handleCreateTestImage = async (e) => {
      const button = e.currentTarget
      const originalText = button.textContent

      try {
        button.disabled = true
        button.textContent = '⏳ Queueing...'

        const response = await api.post(`/presets/${category}/${entity.presetId}/generate-test-image`)

        button.textContent = '✅ Queued!'
        setTimeout(() => {
          button.textContent = originalText
          button.disabled = false
        }, 2000)
      } catch (error) {
        console.error('Failed to generate test image:', error)
        button.textContent = '❌ Failed'
        setTimeout(() => {
          button.textContent = originalText
          button.disabled = false
        }, 2000)
      }
    }

    return (
      <div style={{ padding: '1rem' }}>
        {/* Preview Image with loading overlay */}
        <div style={{ position: 'relative', marginBottom: '1rem' }}>
          <div style={{
            borderRadius: '8px',
            overflow: 'hidden',
            background: 'rgba(0, 0, 0, 0.3)',
            minHeight: '300px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <LazyImage
              src={`/api/presets/${category}/${entity.presetId}/preview?t=${Date.now()}`}
              alt={entity.title}
              style={{
                width: '100%',
                height: 'auto',
                display: 'block'
              }}
              onError={(e) => {
                e.target.style.display = 'none'
                const placeholder = document.createElement('div')
                placeholder.style.cssText = 'font-size: 4rem; color: rgba(255, 255, 255, 0.3);'
                placeholder.textContent = icon
                e.target.parentElement.appendChild(placeholder)
              }}
            />
          </div>

          {/* Loading overlay when generating */}
          {generatingJobId && trackingPresetId === entity.presetId && (
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.7)',
              borderRadius: '8px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '1rem',
              minHeight: '300px'
            }}>
              <div style={{
                fontSize: '3rem',
                animation: 'spin 2s linear infinite'
              }}>
                🎨
              </div>
              <div style={{ color: 'white', fontSize: '0.95rem' }}>
                Generating preview...
              </div>
              {jobProgress !== null && (
                <div style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.85rem' }}>
                  {Math.round(jobProgress)}%
                </div>
              )}
            </div>
          )}
        </div>

        {/* Generate Preview Button */}
        <button
          onClick={handleGeneratePreview}
          style={{
            width: '100%',
            padding: '0.75rem',
            marginBottom: '0.5rem',
            background: 'rgba(168, 85, 247, 0.2)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            borderRadius: '8px',
            color: 'rgba(168, 85, 247, 1)',
            cursor: 'pointer',
            fontSize: '0.95rem',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            if (!e.currentTarget.disabled) {
              e.currentTarget.style.background = 'rgba(168, 85, 247, 0.3)'
            }
          }}
          onMouseLeave={(e) => {
            if (!e.currentTarget.disabled) {
              e.currentTarget.style.background = 'rgba(168, 85, 247, 0.2)'
            }
          }}
        >
          🎨 Generate Preview
        </button>

        {/* Create Test Image Button */}
        <button
          onClick={handleCreateTestImage}
          style={{
            width: '100%',
            padding: '0.75rem',
            background: 'rgba(99, 102, 241, 0.2)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            borderRadius: '8px',
            color: 'rgba(99, 102, 241, 1)',
            cursor: 'pointer',
            fontSize: '0.95rem',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            if (!e.currentTarget.disabled) {
              e.currentTarget.style.background = 'rgba(99, 102, 241, 0.3)'
            }
          }}
          onMouseLeave={(e) => {
            if (!e.currentTarget.disabled) {
              e.currentTarget.style.background = 'rgba(99, 102, 241, 0.2)'
            }
          }}
        >
          🎨 Create Test Image
        </button>

        <style>{`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    )
  }
}

// Create preview components for each category
const HairColorsPreview = createPresetPreview('hair_colors', '🎨')
const VisualStylesPreview = createPresetPreview('visual_styles', '📸')
const ArtStylesPreview = createPresetPreview('art_styles', '🎨')
const AccessoriesPreview = createPresetPreview('accessories', '👓')
const ExpressionsPreview = createPresetPreview('expressions', '😊')
const MakeupsPreview = createPresetPreview('makeup', '💄')

export const hairColorsConfig = {
  ...createPresetConfig({
    entityType: 'hair color',
    title: 'Hair Colors',
    icon: '🎨',
    category: 'hair_colors',
    analyzerPath: 'hair-color'
  }),
  enableGallery: true,
  renderPreview: (entity, onUpdate) => <HairColorsPreview entity={entity} onUpdate={onUpdate} />
}

export const visualStylesConfig = {
  ...createPresetConfig({
    entityType: 'visual style',
    title: 'Visual Styles',
    icon: '📸',
    category: 'visual_styles',
    analyzerPath: 'visual-style'
  }),
  enableGallery: true,
  renderPreview: (entity, onUpdate) => <VisualStylesPreview entity={entity} onUpdate={onUpdate} />
}

export const artStylesConfig = {
  ...createPresetConfig({
    entityType: 'art style',
    title: 'Art Styles',
    icon: '🎨',
    category: 'art_styles',
    analyzerPath: 'art-style'
  }),
  enableGallery: true,
  renderPreview: (entity, onUpdate) => <ArtStylesPreview entity={entity} onUpdate={onUpdate} />
}

export const accessoriesConfig = {
  ...createPresetConfig({
    entityType: 'accessory',
    title: 'Accessories',
    icon: '👓',
    category: 'accessories',
    analyzerPath: 'accessories'
  }),
  enableGallery: true,
  renderPreview: (entity, onUpdate) => <AccessoriesPreview entity={entity} onUpdate={onUpdate} />
}

export const expressionsConfig = {
  ...createPresetConfig({
    entityType: 'expression',
    title: 'Expressions',
    icon: '😊',
    category: 'expressions',
    analyzerPath: 'expression'
  }),
  enableGallery: true,
  renderPreview: (entity, onUpdate) => <ExpressionsPreview entity={entity} onUpdate={onUpdate} />
}

export const makeupsConfig = {
  ...createPresetConfig({
    entityType: 'makeup',
    title: 'Makeup',
    icon: '💄',
    category: 'makeup',
    analyzerPath: 'makeup'
  }),
  enableGallery: true,
  renderPreview: (entity, onUpdate) => <MakeupsPreview entity={entity} onUpdate={onUpdate} />
}
