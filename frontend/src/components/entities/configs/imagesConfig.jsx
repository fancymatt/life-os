import api from '../../../api/client'
import { formatDate } from './helpers'
import EntityPreviewImage from '../EntityPreviewImage'
import RelatedEntityChip from '../RelatedEntityChip'

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
      // Use entity_previews path for optimized preview images
      imageUrl: `/entity_previews/images/${img.image_id}_preview.png`,
      originalImageUrl: img.file_path, // Keep original for download
      width: img.width,
      height: img.height,
      entities: img.entities || {},
      createdAt: img.created_at,
      metadata: img.generation_metadata || {},
      archived: img.archived || false,
      archivedAt: img.archived_at
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
        <div className="entity-card-image" style={{
          height: '280px',
          position: 'relative',
          opacity: image.archived ? 0.6 : 1
        }}>
          {image.archived && (
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
          <EntityPreviewImage
            entityType="images"
            entityId={image.imageId}
            previewImageUrl={image.imageUrl}
            standInIcon="🖼️"
            size="small"
            shape="preserve"
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
    <EntityPreviewImage
      entityType="images"
      entityId={image.imageId}
      previewImageUrl={image.imageUrl}
      standInIcon="🖼️"
      size="medium"
      shape="preserve"
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

    return (
      <div style={{ padding: '2rem' }}>
        <h2 style={{ color: 'white', margin: '0 0 1.5rem 0' }}>{image.filename}</h2>

        {/* Preview Image */}
        <div style={{ marginBottom: '2rem' }}>
          <EntityPreviewImage
            entityType="images"
            entityId={image.imageId}
            previewImageUrl={image.imageUrl}
            standInIcon="🖼️"
            size="large"
            shape="preserve"
          />
        </div>

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
                    <RelatedEntityChip
                      key={idx}
                      entity={{
                        ...entity,
                        entity_type: entityType
                      }}
                    />
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
          href={image.originalImageUrl || image.imageUrl}
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
          ⬇️ Download Full Resolution
        </a>
      </div>
    )
  },

  deleteEntity: async (image) => {
    await api.post(`/images/${image.imageId}/archive`)
  },

  archiveEntity: async (image) => {
    await api.post(`/images/${image.imageId}/archive`)
  },

  unarchiveEntity: async (image) => {
    await api.post(`/images/${image.imageId}/unarchive`)
  }
}
