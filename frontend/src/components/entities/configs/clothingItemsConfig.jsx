import { useState, useEffect } from 'react'
import api from '../../../api/client'
import { formatDate, getPreview } from './helpers'
import TagManager from '../../tags/TagManager'

/**
 * Preview component with job tracking
 */
function ClothingItemPreview({ item, onUpdate }) {
  const [generatingJobId, setGeneratingJobId] = useState(null)
  const [jobProgress, setJobProgress] = useState(null)
  const [previewImageUrl, setPreviewImageUrl] = useState(item.previewImage)

  // Always listen to SSE job updates (even if job triggered externally)
  useEffect(() => {
    const eventSource = new EventSource('/api/jobs/stream')

    eventSource.onmessage = (event) => {
      try {
        const job = JSON.parse(event.data)

        // Check if this job is for OUR item
        const isOurJob = generatingJobId && job.job_id === generatingJobId
        const isOurItem = job.result && job.result.item_id === item.itemId

        if (!isOurJob && !isOurItem) return

        // If we weren't tracking this job, start tracking it
        if (!generatingJobId && isOurItem && job.status === 'running') {
          console.log('🎨 Detected preview generation for this item:', item.itemId)
          setGeneratingJobId(job.job_id)
        }

        setJobProgress(job.progress)

        if (job.status === 'completed') {
          console.log('✅ Preview generation completed, updating image...')

          // Update the preview image immediately from job result
          if (job.result && job.result.preview_image_path) {
            const imageUrl = `${job.result.preview_image_path}?t=${Date.now()}`
            setPreviewImageUrl(imageUrl)
            console.log('Updated preview image:', imageUrl)
          }

          setGeneratingJobId(null)
          setJobProgress(null)

          // Also trigger entity refresh for consistency
          if (onUpdate) onUpdate()
        } else if (job.status === 'failed') {
          console.error('❌ Preview generation failed:', job.error)
          setGeneratingJobId(null)
          setJobProgress(null)
        }
      } catch (error) {
        console.error('Error processing SSE message:', error)
      }
    }

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error)
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [generatingJobId, item.itemId, onUpdate])

  // Update preview image when item prop changes
  useEffect(() => {
    setPreviewImageUrl(item.previewImage)
  }, [item.previewImage])

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
        character_id: 'e1f4fe53',  // Jenny's character ID
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
        {previewImageUrl ? (
          <div style={{
            borderRadius: '8px',
            overflow: 'hidden',
            background: 'rgba(0, 0, 0, 0.3)'
          }}>
            <img
              src={previewImageUrl}
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

/**
 * Detail component with job tracking
 */
function ClothingItemDetail({ item, onUpdate }) {
  const [generatingJobId, setGeneratingJobId] = useState(null)
  const [jobProgress, setJobProgress] = useState(null)
  const [previewImageUrl, setPreviewImageUrl] = useState(item.previewImage)

  // Always listen to SSE job updates (even if job triggered externally)
  useEffect(() => {
    const eventSource = new EventSource('/api/jobs/stream')

    eventSource.onmessage = (event) => {
      try {
        const job = JSON.parse(event.data)

        // Check if this job is for OUR item
        const isOurJob = generatingJobId && job.job_id === generatingJobId
        const isOurItem = job.result && job.result.item_id === item.itemId

        if (!isOurJob && !isOurItem) return

        // If we weren't tracking this job, start tracking it
        if (!generatingJobId && isOurItem && job.status === 'running') {
          console.log('🎨 Detected preview generation for this item:', item.itemId)
          setGeneratingJobId(job.job_id)
        }

        setJobProgress(job.progress)

        if (job.status === 'completed') {
          console.log('✅ Preview generation completed, updating image...')

          // Update the preview image immediately from job result
          if (job.result && job.result.preview_image_path) {
            const imageUrl = `${job.result.preview_image_path}?t=${Date.now()}`
            setPreviewImageUrl(imageUrl)
            console.log('Updated preview image:', imageUrl)
          }

          setGeneratingJobId(null)
          setJobProgress(null)

          // Also trigger entity refresh for consistency
          if (onUpdate) onUpdate()
        } else if (job.status === 'failed') {
          console.error('❌ Preview generation failed:', job.error)
          setGeneratingJobId(null)
          setJobProgress(null)
        }
      } catch (error) {
        console.error('Error processing SSE message:', error)
      }
    }

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error)
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [generatingJobId, item.itemId, onUpdate])

  // Update preview image when item prop changes
  useEffect(() => {
    setPreviewImageUrl(item.previewImage)
  }, [item.previewImage])

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
        character_id: 'e1f4fe53',  // Jenny's character ID
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
      {previewImageUrl && (
        <div style={{ position: 'relative', marginBottom: '1rem' }}>
          <div style={{
            borderRadius: '8px',
            overflow: 'hidden',
            maxWidth: '400px'
          }}>
            <img
              src={previewImageUrl}
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
        style={{
          width: '100%',
          maxWidth: '400px',
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
  enableGallery: true,
  showRefreshButton: true,
  defaultSort: 'newest',
  searchFields: ['item', 'category', 'fabric', 'color', 'details'],

  actions: [
    {
      label: '✏️ Modify Item',
      handler: async (item, onUpdate) => {
        const instruction = prompt('How would you like to modify this item?\n\nExamples:\n• "Make these shoulder-length"\n• "Change the color to red"\n• "Add lace trim"\n• "Make this more formal"')

        if (!instruction || !instruction.trim()) {
          return // User cancelled
        }

        try {
          console.log(`Modifying item ${item.itemId} with instruction: ${instruction}`)
          const response = await api.post(`/clothing-items/${item.itemId}/modify`, {
            instruction: instruction.trim()
          })

          const modifiedItem = response.data
          console.log('✅ Item modified successfully:', modifiedItem)

          // Show what changed
          alert(`✅ Item modified successfully!\n\n📝 Changes:\n• Color: ${modifiedItem.color}\n• Fabric: ${modifiedItem.fabric}\n• Details: ${modifiedItem.details.substring(0, 100)}...\n\n🔄 Close and reopen this item to see all changes.`)

          // Trigger refresh
          if (onUpdate) onUpdate()
        } catch (error) {
          console.error('Failed to modify item:', error)
          alert(`❌ Failed to modify item: ${error.response?.data?.detail || error.message}`)
        }
      },
      color: 'rgba(99, 102, 241, 1)',
      background: 'rgba(99, 102, 241, 0.2)',
      hoverBackground: 'rgba(99, 102, 241, 0.3)'
    },
    {
      label: '🔀 Create Variant',
      handler: async (item, onUpdate) => {
        const instruction = prompt('How should the variant differ from the original?\n\nExamples:\n• "What would this look like in red?"\n• "Summer version with lighter fabric"\n• "More formal version"\n• "Ankle-length version"')

        if (!instruction || !instruction.trim()) {
          return // User cancelled
        }

        try {
          console.log(`Creating variant of ${item.itemId} with instruction: ${instruction}`)
          const response = await api.post(`/clothing-items/${item.itemId}/create-variant`, {
            instruction: instruction.trim()
          })

          console.log('✅ Variant created successfully:', response.data.item_id)
          alert(`✅ Variant created successfully! New item: "${response.data.item}"`)

          // Trigger refresh to show new variant in list
          if (onUpdate) onUpdate()
        } catch (error) {
          console.error('Failed to create variant:', error)
          alert(`❌ Failed to create variant: ${error.response?.data?.detail || error.message}`)
        }
      },
      color: 'rgba(168, 85, 247, 1)',
      background: 'rgba(168, 85, 247, 0.2)',
      hoverBackground: 'rgba(168, 85, 247, 0.3)'
    }
  ],

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
      tags: item.tags || [],
      createdAt: item.created_at,
      archived: item.archived || false,
      archivedAt: item.archived_at,
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
        overflow: 'hidden',
        opacity: item.archived ? 0.6 : 1
      }}>
        {item.archived && (
          <div style={{
            position: 'absolute',
            top: '0.5rem',
            right: '0.5rem',
            background: 'rgba(255, 152, 0, 0.9)',
            color: 'white',
            padding: '0.25rem 0.5rem',
            borderRadius: '4px',
            fontSize: '0.75rem',
            fontWeight: 'bold',
            zIndex: 10,
            boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
          }}>
            📦 ARCHIVED
          </div>
        )}
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

      {/* Tags */}
      <TagManager
        entityType="clothing_item"
        entityId={item.itemId}
        tags={item.tags || []}
        onTagsChange={(newTags) => {
          // Trigger entity refresh to show updated tags
          if (handlers.handleEntityUpdate) {
            handlers.handleEntityUpdate()
          }
        }}
      />
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
    await api.post(`/clothing-items/${item.itemId}/archive`)
  },

  archiveEntity: async (item) => {
    await api.post(`/clothing-items/${item.itemId}/archive`)
  },

  unarchiveEntity: async (item) => {
    await api.post(`/clothing-items/${item.itemId}/unarchive`)
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
