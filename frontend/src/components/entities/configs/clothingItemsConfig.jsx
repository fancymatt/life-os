import { useState, useEffect } from 'react'
import api from '../../../api/client'
import { formatDate, getPreview } from './helpers'

/**
 * Preview component with job tracking
 */
function ClothingItemPreview({ item, onUpdate }) {
  const [generatingJobId, setGeneratingJobId] = useState(null)
  const [jobProgress, setJobProgress] = useState(null)

  // Poll for job status if we're tracking a job
  useEffect(() => {
    if (!generatingJobId) return

    const pollInterval = setInterval(async () => {
      try {
        const response = await api.get(`/jobs/${generatingJobId}`)
        const job = response.data

        setJobProgress(job.progress)

        if (job.status === 'completed') {
          console.log('✅ Preview generation completed, refreshing item data...')
          setGeneratingJobId(null)
          setJobProgress(null)
          // Refresh the item to get the new preview image
          if (onUpdate) onUpdate()
        } else if (job.status === 'failed') {
          console.error('❌ Preview generation failed')
          setGeneratingJobId(null)
          setJobProgress(null)
        }
      } catch (error) {
        console.error('Failed to poll job status:', error)
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

      const response = await api.post(`/clothing-items/${item.itemId}/generate-preview`)
      const jobId = response.data.job_id

      console.log(`✅ Preview generation queued (Job: ${jobId})`)
      button.textContent = '✅ Queued!'

      // Start tracking this job
      setTimeout(() => {
        setGeneratingJobId(jobId)
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

      const response = await api.post(`/clothing-items/${item.itemId}/generate-test-image`, {
        character_id: 'jenny',
        visual_style: 'b1ed9953-a91d-4257-98de-bf8b2f256293'
      })

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
        {item.previewImage ? (
          <div style={{
            borderRadius: '8px',
            overflow: 'hidden',
            background: 'rgba(0, 0, 0, 0.3)'
          }}>
            <img
              src={item.previewImage}
              alt={item.item}
              style={{
                width: '100%',
                height: 'auto',
                display: 'block'
              }}
            />
          </div>
        ) : (
          <div style={{
            padding: '3rem 1rem',
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2))',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '4rem'
          }}>
            {getCategoryIcon(item.category)}
          </div>
        )}

        {/* Loading overlay when generating */}
        {generatingJobId && (
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
            gap: '1rem'
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
        disabled={generatingJobId !== null}
        style={{
          width: '100%',
          padding: '0.75rem',
          marginBottom: '0.5rem',
          background: 'rgba(168, 85, 247, 0.2)',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          borderRadius: '8px',
          color: 'rgba(168, 85, 247, 1)',
          cursor: generatingJobId ? 'not-allowed' : 'pointer',
          fontSize: '0.95rem',
          fontWeight: '500',
          transition: 'all 0.2s',
          opacity: generatingJobId ? 0.5 : 1
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

/**
 * Detail component with job tracking
 */
function ClothingItemDetail({ item, onUpdate }) {
  const [generatingJobId, setGeneratingJobId] = useState(null)
  const [jobProgress, setJobProgress] = useState(null)

  // Poll for job status if we're tracking a job
  useEffect(() => {
    if (!generatingJobId) return

    const pollInterval = setInterval(async () => {
      try {
        const response = await api.get(`/jobs/${generatingJobId}`)
        const job = response.data

        setJobProgress(job.progress)

        if (job.status === 'completed') {
          console.log('✅ Preview generation completed, refreshing item data...')
          setGeneratingJobId(null)
          setJobProgress(null)
          // Refresh the item to get the new preview image
          if (onUpdate) onUpdate()
        } else if (job.status === 'failed') {
          console.error('❌ Preview generation failed')
          setGeneratingJobId(null)
          setJobProgress(null)
        }
      } catch (error) {
        console.error('Failed to poll job status:', error)
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

      const response = await api.post(`/clothing-items/${item.itemId}/generate-preview`)
      const jobId = response.data.job_id

      console.log(`✅ Preview generation queued (Job: ${jobId})`)
      button.textContent = '✅ Queued!'

      // Start tracking this job
      setTimeout(() => {
        setGeneratingJobId(jobId)
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

      const response = await api.post(`/clothing-items/${item.itemId}/generate-test-image`, {
        character_id: 'jenny',
        visual_style: 'b1ed9953-a91d-4257-98de-bf8b2f256293'
      })

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
    <div style={{ padding: '2rem' }}>
      {/* Preview Image with loading overlay */}
      {item.previewImage && (
        <div style={{ position: 'relative', marginBottom: '1rem' }}>
          <div style={{
            borderRadius: '8px',
            overflow: 'hidden',
            maxWidth: '400px'
          }}>
            <img
              src={item.previewImage}
              alt={item.item}
              style={{
                width: '100%',
                height: 'auto',
                display: 'block'
              }}
            />
          </div>

          {/* Loading overlay when generating */}
          {generatingJobId && (
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
              gap: '1rem'
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
      )}

      {/* Generate Preview Button */}
      <button
        onClick={handleGeneratePreview}
        disabled={generatingJobId !== null}
        style={{
          width: '100%',
          maxWidth: '400px',
          padding: '0.75rem',
          marginBottom: '0.5rem',
          background: 'rgba(168, 85, 247, 0.2)',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          borderRadius: '8px',
          color: 'rgba(168, 85, 247, 1)',
          cursor: generatingJobId ? 'not-allowed' : 'pointer',
          fontSize: '0.95rem',
          fontWeight: '500',
          transition: 'all 0.2s',
          opacity: generatingJobId ? 0.5 : 1
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
          maxWidth: '400px',
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

/**
 * Clothing Items Entity Configuration
 */
export const clothingItemsConfig = {
  entityType: 'clothing_item',
  title: 'Clothing Items',
  icon: '👕',
  emptyMessage: 'No clothing items yet. Analyze an outfit image to extract items!',
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  showRefreshButton: true,
  defaultSort: 'newest',
  searchFields: ['item', 'category', 'fabric', 'color', 'details'],

  actions: [],

  fetchEntities: async (filterCategory = null) => {
    const url = filterCategory ? `/clothing-items/?category=${filterCategory}` : '/clothing-items/'
    const response = await api.get(url)
    return (response.data.items || []).map(item => ({
      id: item.item_id,
      itemId: item.item_id,
      title: item.item,
      item: item.item,
      category: item.category,
      fabric: item.fabric,
      color: item.color,
      details: item.details,
      sourceImage: item.source_image,
      previewImage: item.preview_image_path,  // Add preview image path
      createdAt: item.created_at,
      // Wrap editable fields in data property for EntityBrowser
      data: {
        category: item.category,
        item: item.item,
        fabric: item.fabric,
        color: item.color,
        details: item.details
      }
    }))
  },

  fetchCategorySummary: async () => {
    const response = await api.get('/clothing-items/categories')
    return response.data
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(180px, 1fr))',
    gap: '1rem'
  },

  renderCard: (item) => (
    <div className="entity-card">
      {/* Square preview image */}
      <div style={{
        position: 'relative',
        width: '100%',
        paddingBottom: '100%', // Creates square aspect ratio
        background: item.previewImage
          ? `url(${item.previewImage}) center/cover`
          : 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2))',
        borderRadius: '8px 8px 0 0',
        overflow: 'hidden'
      }}>
        {!item.previewImage && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '4rem'
          }}>
            {getCategoryIcon(item.category)}
          </div>
        )}
      </div>
      {/* Just the item name */}
      <div className="entity-card-content">
        <h3 className="entity-card-title" style={{
          fontSize: '0.95rem',
          margin: '0',
          textAlign: 'center'
        }}>
          {item.item}
        </h3>
      </div>
    </div>
  ),

  renderPreview: (item, onUpdate) => <ClothingItemPreview item={item} onUpdate={onUpdate} />,

  renderDetail: (item, handleBackToList, onUpdate) => <ClothingItemDetail item={item} onUpdate={onUpdate} />,

  renderEdit: (item, editedData, editedTitle, handlers) => (
    <div>
      {/* Item Name */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Item Name
        </label>
        <input
          type="text"
          value={editedTitle}
          onChange={(e) => handlers.setEditedTitle(e.target.value)}
          placeholder="e.g., Ribbed tank top, High-waisted jeans..."
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

      {/* Category */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Category
        </label>
        <select
          value={editedData.category || ''}
          onChange={(e) => handlers.updateField('category', e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem',
            background: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            color: 'white',
            fontSize: '0.95rem'
          }}
        >
          <option value="headwear">Headwear</option>
          <option value="eyewear">Eyewear</option>
          <option value="earrings">Earrings</option>
          <option value="neckwear">Neckwear</option>
          <option value="tops">Tops</option>
          <option value="overtops">Overtops</option>
          <option value="outerwear">Outerwear</option>
          <option value="one_piece">One Piece</option>
          <option value="bottoms">Bottoms</option>
          <option value="belts">Belts</option>
          <option value="hosiery">Hosiery</option>
          <option value="footwear">Footwear</option>
          <option value="bags">Bags</option>
          <option value="wristwear">Wristwear</option>
          <option value="handwear">Handwear</option>
        </select>
      </div>

      {/* Color */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Color
        </label>
        <input
          type="text"
          value={editedData.color || ''}
          onChange={(e) => handlers.updateField('color', e.target.value)}
          placeholder="e.g., Navy blue, Charcoal grey..."
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
      </div>

      {/* Fabric */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Fabric
        </label>
        <input
          type="text"
          value={editedData.fabric || ''}
          onChange={(e) => handlers.updateField('fabric', e.target.value)}
          placeholder="e.g., Cotton jersey, Wool blend..."
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
      </div>

      {/* Details */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Construction & Details
        </label>
        <textarea
          value={editedData.details || ''}
          onChange={(e) => handlers.updateField('details', e.target.value)}
          rows="6"
          placeholder="Describe construction, fit, styling details..."
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
      </div>
    </div>
  ),

  saveEntity: async (item, updates) => {
    const response = await api.put(
      `/clothing-items/${item.itemId}`,
      {
        item: updates.title,
        category: updates.data.category,
        fabric: updates.data.fabric,
        color: updates.data.color,
        details: updates.data.details
      }
    )
    return response.data
  },

  deleteEntity: async (item) => {
    await api.delete(`/clothing-items/${item.itemId}`)
  }
}

// Helper function to get category icon
function getCategoryIcon(category) {
  const icons = {
    'headwear': '🎩',
    'eyewear': '👓',
    'earrings': '👂',
    'neckwear': '📿',
    'tops': '👚',
    'overtops': '🧥',
    'outerwear': '🧥',
    'one_piece': '👗',
    'bottoms': '👖',
    'belts': '👔',
    'hosiery': '🧦',
    'footwear': '👞',
    'bags': '👜',
    'wristwear': '⌚',
    'handwear': '🧤'
  }
  return icons[category] || '👕'
}
