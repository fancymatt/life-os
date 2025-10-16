import React, { useState } from 'react'
import api from '../../api/client'

/**
 * Entity Configurations
 *
 * Define how each entity type should be fetched, displayed, and interacted with
 */

// Outfit Editor Component (needs to be a separate component to use hooks)
function OutfitEditor({ editedData, editedTitle, handlers }) {
  const [expandedItems, setExpandedItems] = useState({})
  const [editingItems, setEditingItems] = useState({})

  // Handle loading state
  if (!editedData) {
    return (
      <div style={{ padding: '2rem', color: 'rgba(255, 255, 255, 0.7)' }}>
        Loading outfit data...
      </div>
    )
  }

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
    const newItems = [...(editedData.clothing_items || [])]
    newItems[index] = {
      ...newItems[index],
      [field]: value
    }
    handlers.updateField('clothing_items', newItems)
  }

  const deleteItem = (index) => {
    const newItems = (editedData.clothing_items || []).filter((_, i) => i !== index)
    handlers.updateField('clothing_items', newItems)
  }

  const addNewItem = () => {
    const newItems = [...(editedData.clothing_items || []), {
      item: '',
      fabric: '',
      color: '',
      details: ''
    }]
    handlers.updateField('clothing_items', newItems)
  }

  return (
    <div>
      {/* Name Field */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Outfit Name
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

      {/* Outfit Details */}
      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: 'white', marginBottom: '1rem' }}>Outfit Details</h3>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Style Genre
          </label>
          <input
            type="text"
            value={editedData.style_genre || ''}
            onChange={(e) => handlers.updateField('style_genre', e.target.value)}
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

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Formality
          </label>
          <input
            type="text"
            value={editedData.formality || ''}
            onChange={(e) => handlers.updateField('formality', e.target.value)}
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

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Aesthetic
          </label>
          <input
            type="text"
            value={editedData.aesthetic || ''}
            onChange={(e) => handlers.updateField('aesthetic', e.target.value)}
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
      </div>

      {/* Clothing Items */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ color: 'white', margin: 0 }}>
            Clothing Items ({(editedData.clothing_items || []).length})
          </h3>
          <button
            onClick={addNewItem}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(102, 126, 234, 0.2)',
              border: '1px solid rgba(102, 126, 234, 0.3)',
              borderRadius: '6px',
              color: '#667eea',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            + Add Item
          </button>
        </div>

        {(editedData.clothing_items || []).map((item, index) => (
          <div
            key={index}
            style={{
              marginBottom: '0.75rem',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              overflow: 'hidden'
            }}
          >
            {/* Item Header */}
            <div
              onClick={() => toggleItem(index)}
              style={{
                padding: '1rem',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                background: 'rgba(255, 255, 255, 0.02)'
              }}
            >
              <span style={{ color: 'white', fontWeight: 500 }}>
                {item.item || `Item ${index + 1}`}
              </span>
              <span style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                {expandedItems[index] ? '▼' : '▶'}
              </span>
            </div>

            {/* Item Content */}
            {expandedItems[index] && (
              <div style={{ padding: '1rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                {editingItems[index] ? (
                  // Edit Mode
                  <>
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        Item Type
                      </label>
                      <input
                        type="text"
                        value={item.item || ''}
                        onChange={(e) => updateItemField(index, 'item', e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          background: 'rgba(0, 0, 0, 0.3)',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                          borderRadius: '6px',
                          color: 'white',
                          fontSize: '0.9rem'
                        }}
                      />
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        Color
                      </label>
                      <input
                        type="text"
                        value={item.color || ''}
                        onChange={(e) => updateItemField(index, 'color', e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          background: 'rgba(0, 0, 0, 0.3)',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                          borderRadius: '6px',
                          color: 'white',
                          fontSize: '0.9rem'
                        }}
                      />
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        Fabric
                      </label>
                      <input
                        type="text"
                        value={item.fabric || ''}
                        onChange={(e) => updateItemField(index, 'fabric', e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          background: 'rgba(0, 0, 0, 0.3)',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                          borderRadius: '6px',
                          color: 'white',
                          fontSize: '0.9rem'
                        }}
                      />
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        Details
                      </label>
                      <textarea
                        value={item.details || ''}
                        onChange={(e) => updateItemField(index, 'details', e.target.value)}
                        rows="3"
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          background: 'rgba(0, 0, 0, 0.3)',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                          borderRadius: '6px',
                          color: 'white',
                          fontSize: '0.9rem',
                          resize: 'vertical',
                          fontFamily: 'inherit'
                        }}
                      />
                    </div>
                    <button
                      onClick={() => toggleEdit(index)}
                      style={{
                        padding: '0.5rem 1rem',
                        background: 'rgba(102, 126, 234, 0.2)',
                        border: '1px solid rgba(102, 126, 234, 0.3)',
                        borderRadius: '6px',
                        color: '#667eea',
                        cursor: 'pointer',
                        fontSize: '0.9rem'
                      }}
                    >
                      Done Editing
                    </button>
                  </>
                ) : (
                  // View Mode
                  <>
                    <div style={{ marginBottom: '0.5rem', color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
                      <strong>Item:</strong> {item.item || 'N/A'}
                    </div>
                    <div style={{ marginBottom: '0.5rem', color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
                      <strong>Color:</strong> {item.color || 'N/A'}
                    </div>
                    <div style={{ marginBottom: '0.5rem', color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
                      <strong>Fabric:</strong> {item.fabric || 'N/A'}
                    </div>
                    <div style={{ marginBottom: '1rem', color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
                      <strong>Details:</strong> {item.details || 'N/A'}
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={() => toggleEdit(index)}
                        style={{
                          padding: '0.5rem 1rem',
                          background: 'rgba(102, 126, 234, 0.2)',
                          border: '1px solid rgba(102, 126, 234, 0.3)',
                          borderRadius: '6px',
                          color: '#667eea',
                          cursor: 'pointer',
                          fontSize: '0.9rem'
                        }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteItem(index)}
                        style={{
                          padding: '0.5rem 1rem',
                          background: 'rgba(255, 100, 100, 0.2)',
                          border: '1px solid rgba(255, 100, 100, 0.3)',
                          borderRadius: '6px',
                          color: '#ff6b6b',
                          cursor: 'pointer',
                          fontSize: '0.9rem'
                        }}
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
    </div>
  )
}

// Helper functions
const formatDate = (dateString) => {
  if (!dateString) return null
  const date = new Date(dateString)
  // Check if date is invalid or is Unix epoch (Jan 1, 1970 or earlier)
  if (isNaN(date.getTime()) || date.getFullYear() < 1971) {
    return null
  }
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getWordCount = (text) => {
  return text?.split(/\s+/).filter(word => word.length > 0).length || 0
}

const getPreview = (text, maxWords = 30) => {
  if (!text) return ''
  const words = text.split(/\s+/)
  if (words.length <= maxWords) return text
  return words.slice(0, maxWords).join(' ') + '...'
}

// =============================================================================
// STORIES
// =============================================================================

export const storiesConfig = {
  entityType: 'story',
  title: 'Stories',
  icon: '📚',
  emptyMessage: 'No stories yet. Generate your first story!',
  enableSearch: true,
  enableSort: true,
  defaultSort: 'newest',
  searchFields: ['title', 'story'],

  actions: [
    {
      label: 'New Story',
      icon: '+',
      primary: true,
      path: '/workflows/story'
    }
  ],

  fetchEntities: async () => {
    const response = await api.get('/jobs?limit=100')
    return response.data
      .filter(job => job.type === 'workflow' && job.status === 'completed' && job.result?.illustrated_story)
      .map(job => ({
        id: job.job_id,
        title: job.result.illustrated_story.title,
        story: job.result.illustrated_story.story,
        illustrations: job.result.illustrated_story.illustrations || [],
        metadata: job.result.illustrated_story.metadata || {},
        createdAt: job.created_at,
        completedAt: job.completed_at,
        jobTitle: job.title
      }))
  },

  renderCard: (story) => (
    <div className="entity-card">
      {story.illustrations.length > 0 && (
        <div className="entity-card-image">
          <img
            src={story.illustrations[0].image_url}
            alt={story.title}
            onError={(e) => e.target.style.display = 'none'}
          />
        </div>
      )}
      <div className="entity-card-content">
        <h3 className="entity-card-title">{story.title}</h3>
        <p className="entity-card-description">{getPreview(story.story)}</p>
        <div className="entity-card-meta">
          <span className="entity-card-meta-item">
            {getWordCount(story.story)} words
          </span>
          <span className="entity-card-meta-item">
            {story.illustrations.length} {story.illustrations.length === 1 ? 'illustration' : 'illustrations'}
          </span>
        </div>
        {formatDate(story.completedAt) && (
          <p className="entity-card-date">{formatDate(story.completedAt)}</p>
        )}
      </div>
    </div>
  ),

  renderDetail: (story) => (
    <div style={{ padding: '3rem' }}>
      <h1 style={{ fontSize: '2.5rem', margin: '0 0 2rem 0', color: 'white', textAlign: 'center' }}>
        {story.title}
      </h1>

      {story.illustrations.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
          {story.illustrations.map((ill, idx) => (
            <div key={idx} style={{ borderRadius: '8px', overflow: 'hidden', background: 'rgba(255, 255, 255, 0.05)' }}>
              <img src={ill.image_url} alt={`Scene ${ill.scene_number}`} style={{ width: '100%', height: 'auto', display: 'block' }} />
            </div>
          ))}
        </div>
      )}

      <div style={{ lineHeight: '1.8', fontSize: '1.1rem', color: 'rgba(255, 255, 255, 0.9)' }}>
        {story.story.split('\n\n').map((paragraph, idx) => (
          <p key={idx} style={{ margin: '0 0 1.5rem 0' }}>{paragraph}</p>
        ))}
      </div>

      <div style={{ marginTop: '3rem', paddingTop: '2rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap', fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.6)' }}>
          <p style={{ margin: 0 }}><strong style={{ color: 'rgba(255, 255, 255, 0.8)' }}>Word Count:</strong> {getWordCount(story.story)}</p>
          <p style={{ margin: 0 }}><strong style={{ color: 'rgba(255, 255, 255, 0.8)' }}>Illustrations:</strong> {story.illustrations.length}</p>
          <p style={{ margin: 0 }}><strong style={{ color: 'rgba(255, 255, 255, 0.8)' }}>Generated:</strong> {formatDate(story.completedAt)}</p>
        </div>
      </div>
    </div>
  )
}

// =============================================================================
// IMAGES (Gallery)
// =============================================================================

export const imagesConfig = {
  entityType: 'image',
  title: 'Images',
  icon: '🖼️',
  emptyMessage: 'No images yet. Generate your first image!',
  enableSearch: true,
  enableSort: true,
  defaultSort: 'newest',
  searchFields: ['filename', 'title'],

  actions: [
    {
      label: 'Generate Image',
      icon: '+',
      primary: true,
      path: '/tools/generators/modular'
    }
  ],

  fetchEntities: async () => {
    const response = await api.get('/jobs?limit=100')
    const imageList = []

    response.data.forEach(job => {
      if (job.status === 'completed' && job.result?.file_paths) {
        job.result.file_paths.forEach(filePath => {
          // Ensure absolute path by removing /app prefix and ensuring it starts with /
          let url = filePath.replace('/app', '')
          if (!url.startsWith('/')) {
            url = '/' + url
          }
          const filename = filePath.split('/').pop()

          imageList.push({
            id: `${job.job_id}_${filename}`,
            title: job.title || 'Generated Image',
            filename,
            imageUrl: url,
            jobId: job.job_id,
            createdAt: job.created_at,
            completedAt: job.completed_at
          })
        })
      }
    })

    return imageList
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (image) => (
    <div className="entity-card">
      <div className="entity-card-image" style={{ height: '280px' }}>
        <img
          src={image.imageUrl}
          alt={image.title}
          loading="lazy"
          onError={(e) => e.target.style.display = 'none'}
        />
      </div>
      <div className="entity-card-content">
        <h3 className="entity-card-title" style={{ fontSize: '1rem' }}>{image.filename}</h3>
        <p className="entity-card-description" style={{ fontSize: '0.85rem' }}>
          {image.title}
        </p>
        {formatDate(image.completedAt) && (
          <p className="entity-card-date">{formatDate(image.completedAt)}</p>
        )}
      </div>
    </div>
  ),

  renderPreview: (image) => (
    <img
      src={image.imageUrl}
      alt={image.filename}
      style={{ width: '100%', height: 'auto', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)' }}
    />
  ),

  renderDetail: (image) => (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ color: 'white', margin: '0 0 1.5rem 0' }}>{image.filename}</h2>
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>Job</h3>
        <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>{image.title}</p>
      </div>
      {formatDate(image.completedAt) && (
        <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
          <p style={{ margin: 0 }}><strong>Generated:</strong> {formatDate(image.completedAt)}</p>
        </div>
      )}
      <a
        href={image.imageUrl}
        download={image.filename}
        style={{
          display: 'inline-block',
          padding: '0.75rem 1.5rem',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '8px',
          fontWeight: 500
        }}
      >
        ⬇️ Download
      </a>
    </div>
  )
}

// =============================================================================
// HELPER: Create Preset Entity Config
// =============================================================================

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
        <img
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
    const response = await api.put(
      `/presets/${options.category}/${entity.presetId}`,
      {
        data: updates.data,
        display_name: updates.title
      }
    )
    return response.data
  },

  deleteEntity: async (entity) => {
    await api.delete(`/presets/${options.category}/${entity.presetId}`)
  }
})

// =============================================================================
// ALL PRESET-BASED ENTITIES
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

export const expressionsConfig = createPresetConfig({
  entityType: 'expression',
  title: 'Expressions',
  icon: '😊',
  category: 'expressions',
  analyzerPath: 'expression'
})

export const makeupsConfig = createPresetConfig({
  entityType: 'makeup',
  title: 'Makeup',
  icon: '💄',
  category: 'makeup',
  analyzerPath: 'makeup'
})

export const hairStylesConfig = createPresetConfig({
  entityType: 'hair style',
  title: 'Hair Styles',
  icon: '💇',
  category: 'hair_styles',
  analyzerPath: 'hair-style'
})

export const hairColorsConfig = createPresetConfig({
  entityType: 'hair color',
  title: 'Hair Colors',
  icon: '🎨',
  category: 'hair_colors',
  analyzerPath: 'hair-color'
})

export const visualStylesConfig = createPresetConfig({
  entityType: 'visual style',
  title: 'Visual Styles',
  icon: '📸',
  category: 'visual_styles',
  analyzerPath: 'visual-style'
})

export const artStylesConfig = createPresetConfig({
  entityType: 'art style',
  title: 'Art Styles',
  icon: '🎨',
  category: 'art_styles',
  analyzerPath: 'art-style'
})

export const accessoriesConfig = createPresetConfig({
  entityType: 'accessory',
  title: 'Accessories',
  icon: '👓',
  category: 'accessories',
  analyzerPath: 'accessories'
})

// =============================================================================
// CHARACTERS
// =============================================================================

export const charactersConfig = {
  entityType: 'character',
  title: 'Characters',
  icon: '👤',
  emptyMessage: 'No characters yet. Create your first character!',
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  defaultSort: 'newest',
  searchFields: ['name', 'visual_description', 'personality'],

  actions: [
    {
      label: 'New Character',
      icon: '+',
      primary: true,
      onClick: () => {
        // TODO: Open character creation modal/form
        alert('Character creation UI coming soon!')
      }
    }
  ],

  fetchEntities: async () => {
    const response = await api.get('/characters')
    return (response.data.characters || []).map(char => ({
      id: char.character_id,
      characterId: char.character_id,
      title: char.name,
      name: char.name,
      visualDescription: char.visual_description,
      personality: char.personality,
      referenceImageUrl: char.reference_image_url,
      tags: char.tags || [],
      createdAt: char.created_at,
      metadata: char.metadata || {}
    }))
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (character) => (
    <div className="entity-card">
      <div className="entity-card-image" style={{ height: '280px' }}>
        {character.referenceImageUrl ? (
          <img
            src={character.referenceImageUrl}
            alt={character.name}
            onError={(e) => {
              e.target.style.display = 'none'
              e.target.parentElement.innerHTML = '<div class="entity-card-placeholder">👤</div>'
            }}
          />
        ) : (
          <div className="entity-card-placeholder">👤</div>
        )}
      </div>
      <div className="entity-card-content">
        <h3 className="entity-card-title">{character.name}</h3>
        <p className="entity-card-description">
          {getPreview(character.visualDescription || character.personality || 'No description', 20)}
        </p>
        {character.tags.length > 0 && (
          <div className="entity-card-meta">
            {character.tags.slice(0, 3).map((tag, idx) => (
              <span key={idx} className="entity-card-meta-item">
                {tag}
              </span>
            ))}
          </div>
        )}
        {formatDate(character.createdAt) && (
          <p className="entity-card-date">{formatDate(character.createdAt)}</p>
        )}
      </div>
    </div>
  ),

  renderPreview: (character) => (
    <>
      {character.referenceImageUrl ? (
        <img
          src={character.referenceImageUrl}
          alt={character.name}
          style={{ width: '100%', height: 'auto', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)' }}
          onError={(e) => e.target.style.display = 'none'}
        />
      ) : (
        <div style={{
          width: '100%',
          aspectRatio: '3/4',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '8rem',
          opacity: 0.3
        }}>
          👤
        </div>
      )}
    </>
  ),

  renderDetail: (character) => (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ color: 'white', margin: '0 0 1.5rem 0' }}>{character.name}</h2>

      {character.visualDescription && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
            Visual Description
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>
            {character.visualDescription}
          </p>
        </div>
      )}

      {character.personality && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
            Personality
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>
            {character.personality}
          </p>
        </div>
      )}

      {character.tags.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
            Tags
          </h3>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {character.tags.map((tag, idx) => (
              <span
                key={idx}
                style={{
                  padding: '0.25rem 0.75rem',
                  background: 'rgba(102, 126, 234, 0.2)',
                  border: '1px solid rgba(102, 126, 234, 0.3)',
                  borderRadius: '12px',
                  color: '#667eea',
                  fontSize: '0.85rem'
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {formatDate(character.createdAt) && (
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', margin: 0 }}>
            <strong>Created:</strong> {formatDate(character.createdAt)}
          </p>
        </div>
      )}
    </div>
  ),

  renderEdit: (character, editedData, editedTitle, handlers) => (
    <div>
      {/* Name Field */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Character Name
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

      {/* Visual Description */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Visual Description
        </label>
        <textarea
          value={editedData.visual_description || ''}
          onChange={(e) => handlers.updateField('visual_description', e.target.value)}
          rows="4"
          placeholder="Describe the character's physical appearance..."
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

      {/* Personality */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Personality
        </label>
        <textarea
          value={editedData.personality || ''}
          onChange={(e) => handlers.updateField('personality', e.target.value)}
          rows="4"
          placeholder="Describe the character's personality traits..."
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
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Tags (comma-separated)
        </label>
        <input
          type="text"
          value={(editedData.tags || []).join(', ')}
          onChange={(e) => handlers.updateField('tags', e.target.value.split(',').map(t => t.trim()).filter(t => t))}
          placeholder="protagonist, hero, adventure..."
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
    </div>
  ),

  saveEntity: async (character, updates) => {
    const response = await api.put(
      `/characters/${character.characterId}`,
      {
        name: updates.title,
        visual_description: updates.data.visual_description,
        personality: updates.data.personality,
        tags: updates.data.tags
      }
    )
    return response.data
  },

  deleteEntity: async (character) => {
    await api.delete(`/characters/${character.characterId}`)
  }
}
