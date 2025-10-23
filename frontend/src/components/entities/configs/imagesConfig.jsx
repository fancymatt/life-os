import api from '../../../api/client'
import { formatDate } from './helpers'
import LazyImage from '../LazyImage'
import { Link } from 'react-router-dom'

/**
 * Images Entity Configuration
 */
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
    // Note: images router is mounted without /api prefix
    const response = await api.get('/images/?limit=100')

    return (response.data.images || []).map(img => ({
      id: img.image_id,
      imageId: img.image_id,
      title: img.filename,
      filename: img.filename,
      imageUrl: img.file_path,
      width: img.width,
      height: img.height,
      entities: img.entities || {},
      createdAt: img.created_at,
      metadata: img.generation_metadata || {}
    }))
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (image) => {
    // Count entities
    const entityCounts = {}
    Object.keys(image.entities || {}).forEach(type => {
      entityCounts[type] = image.entities[type].length
    })

    return (
      <div className="entity-card">
        <div className="entity-card-image" style={{ height: '280px' }}>
          <LazyImage
            src={image.imageUrl}
            alt={image.title}
            onError={(e) => e.target.style.display = 'none'}
          />
        </div>
        <div className="entity-card-content">
          <h3 className="entity-card-title" style={{ fontSize: '1rem' }}>{image.filename}</h3>

          {/* Entity badges */}
          {Object.keys(entityCounts).length > 0 && (
            <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
              {entityCounts.character > 0 && (
                <span style={{
                  padding: '0.25rem 0.5rem',
                  background: 'rgba(99, 102, 241, 0.2)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  color: 'rgba(99, 102, 241, 1)'
                }}>
                  👤 {entityCounts.character}
                </span>
              )}
              {entityCounts.clothing_item > 0 && (
                <span style={{
                  padding: '0.25rem 0.5rem',
                  background: 'rgba(168, 85, 247, 0.2)',
                  border: '1px solid rgba(168, 85, 247, 0.3)',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  color: 'rgba(168, 85, 247, 1)'
                }}>
                  👕 {entityCounts.clothing_item}
                </span>
              )}
              {entityCounts.visual_style > 0 && (
                <span style={{
                  padding: '0.25rem 0.5rem',
                  background: 'rgba(245, 158, 11, 0.2)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  color: 'rgba(245, 158, 11, 1)'
                }}>
                  🎨 {entityCounts.visual_style}
                </span>
              )}
            </div>
          )}

          {formatDate(image.createdAt) && (
            <p className="entity-card-date">{formatDate(image.createdAt)}</p>
          )}
        </div>
      </div>
    )
  },

  renderPreview: (image) => (
    <img
      src={image.imageUrl}
      alt={image.filename}
      style={{ width: '100%', height: 'auto', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)' }}
    />
  ),

  renderDetail: (image) => {
    const getEntityIcon = (type) => {
      const icons = {
        'character': '👤',
        'clothing_item': '👕',
        'visual_style': '🎨',
        'preset': '⚙️',
        'story_theme': '📖'
      }
      return icons[type] || '📦'
    }

    const getEntityLabel = (type) => {
      const labels = {
        'character': 'Characters',
        'clothing_item': 'Clothing Items',
        'visual_style': 'Visual Style',
        'preset': 'Visual Style',
        'story_theme': 'Story Themes'
      }
      return labels[type] || type
    }

    const getEntityRoute = (type) => {
      const routes = {
        'character': '/entities/characters',
        'clothing_item': '/entities/clothing-items',
        'visual_style': '/entities/visual-styles',
        'preset': '/entities/visual-styles',
        'story_theme': '/entities/story-themes'
      }
      return routes[type] || '/entities'
    }

    return (
      <div style={{ padding: '2rem' }}>
        <h2 style={{ color: 'white', margin: '0 0 1.5rem 0' }}>{image.filename}</h2>

        {/* Image metadata */}
        {(image.width || image.height) && (
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>Dimensions</h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', margin: 0 }}>
              {image.width} × {image.height} pixels
            </p>
          </div>
        )}

        {/* Entity relationships */}
        {Object.keys(image.entities || {}).length > 0 && (
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.75rem 0' }}>
              Used Entities
            </h3>
            {Object.keys(image.entities).map(entityType => (
              <div key={entityType} style={{ marginBottom: '1rem' }}>
                <h4 style={{
                  color: 'rgba(255, 255, 255, 0.6)',
                  fontSize: '0.85rem',
                  margin: '0 0 0.5rem 0',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  {getEntityIcon(entityType)} {getEntityLabel(entityType)}
                </h4>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {image.entities[entityType].map((entity, idx) => (
                    <Link
                      key={idx}
                      to={getEntityRoute(entityType)}
                      style={{
                        padding: '0.5rem 0.75rem',
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: '6px',
                        fontSize: '0.85rem',
                        color: 'rgba(255, 255, 255, 0.9)',
                        textDecoration: 'none',
                        transition: 'all 0.2s',
                        display: 'inline-block'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)'
                        e.currentTarget.style.borderColor = 'rgba(102, 126, 234, 0.5)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'
                        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
                      }}
                    >
                      {entity.entity_name || entity.entity_id}
                      {entity.role && (
                        <span style={{ color: 'rgba(255, 255, 255, 0.5)', marginLeft: '0.5rem' }}>
                          ({entity.role})
                        </span>
                      )}
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {formatDate(image.createdAt) && (
          <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            <p style={{ margin: 0 }}><strong>Generated:</strong> {formatDate(image.createdAt)}</p>
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
}
