import { useState } from 'react'
import api from '../../../api/client'
import { formatDate, getPreview } from './helpers'
import TagManager from '../../tags/TagManager'
import EntityPreviewImage from '../EntityPreviewImage'

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

/**
 * Card component for grid view - uses EntityPreviewImage for live updates
 */
function ClothingItemCard({ item }) {
  return (
    <div className="entity-card">
      {/* Square preview image with live job tracking */}
      <div style={{ position: 'relative' }}>
        <EntityPreviewImage
          entityType="clothing_item"
          entityId={item.itemId}
          previewImageUrl={item.previewImage}
          standInIcon={getCategoryIcon(item.category)}
          size="small"
          shape="square"
        />

        {/* Archived badge overlay */}
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
      </div>

      {/* Item name */}
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
  )
}

/**
 * Preview component - shows image and action buttons
 */
function ClothingItemPreview({ item, onUpdate }) {

  const handleGeneratePreview = async (e) => {
    const button = e.currentTarget
    const originalText = button.textContent

    try {
      button.disabled = true
      button.textContent = '⏳ Queueing...'

      await api.post(`/clothing-items/${item.itemId}/generate-preview`)

      button.textContent = '✅ Queued!'
      setTimeout(() => {
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
      {/* Preview Image (with automatic job tracking) */}
      <div style={{ marginBottom: '1rem' }}>
        <EntityPreviewImage
          entityType="clothing_item"
          entityId={item.itemId}
          previewImageUrl={item.previewImage}
          standInIcon={getCategoryIcon(item.category)}
          size="medium"
          onUpdate={onUpdate}
        />
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
 * Detail component - shows large preview and action buttons
 */
function ClothingItemDetail({ item, onUpdate }) {
  const handleGeneratePreview = async (e) => {
    const button = e.currentTarget
    const originalText = button.textContent

    try {
      button.disabled = true
      button.textContent = '⏳ Queueing...'

      await api.post(`/clothing-items/${item.itemId}/generate-preview`)

      button.textContent = '✅ Queued!'
      setTimeout(() => {
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
      {/* Preview Image (with automatic job tracking) */}
      <div style={{ marginBottom: '1rem', maxWidth: '400px' }}>
        <EntityPreviewImage
          entityType="clothing_item"
          entityId={item.itemId}
          previewImageUrl={item.previewImage}
          standInIcon={getCategoryIcon(item.category)}
          size="large"
          onUpdate={onUpdate}
        />
      </div>

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

  renderCard: (item) => <ClothingItemCard item={item} />,

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
