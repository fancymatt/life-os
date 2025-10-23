import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../../api/client'
import { formatDate } from './configs/helpers'
import LazyImage from './LazyImage'
import './EntityGallery.css'

/**
 * Entity Gallery Component
 *
 * Displays all images that used a specific entity with full relationship details
 *
 * @param {string} entityType - Type of entity (e.g., "character", "clothing_item", "preset")
 * @param {string} entityId - ID of the entity
 */
function EntityGallery({ entityType, entityId }) {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [total, setTotal] = useState(0)
  const [selectedImage, setSelectedImage] = useState(null)

  useEffect(() => {
    if (!entityType || !entityId) {
      setLoading(false)
      return
    }

    const fetchImages = async () => {
      try {
        setLoading(true)
        setError(null)

        // Fetch images for this entity
        const response = await api.get(`/images/by-entity/${entityType}/${entityId}?limit=100`)
        const imageList = response.data.images || []
        setTotal(response.data.total || 0)

        // Fetch full details for each image to get entity relationships
        const imagesWithDetails = await Promise.all(
          imageList.map(async (img) => {
            try {
              const detailResponse = await api.get(`/images/${img.image_id}`)
              const imageData = detailResponse.data.image
              const relationships = detailResponse.data.relationships || []

              // Group relationships by entity type and fetch entity names
              const entitiesByType = {}
              for (const rel of relationships) {
                if (!entitiesByType[rel.entity_type]) {
                  entitiesByType[rel.entity_type] = []
                }

                // For now, use entity_id - we'll fetch names via the list endpoint
                entitiesByType[rel.entity_type].push({
                  entity_id: rel.entity_id,
                  entity_name: rel.entity_id, // Will be populated from list endpoint
                  role: rel.role
                })
              }

              return {
                id: imageData.image_id,
                imageId: imageData.image_id,
                title: imageData.filename,
                filename: imageData.filename,
                imageUrl: imageData.file_path,
                width: imageData.width,
                height: imageData.height,
                entities: entitiesByType,
                createdAt: imageData.created_at,
                metadata: imageData.generation_metadata || {}
              }
            } catch (err) {
              console.error(`Failed to fetch details for image ${img.image_id}:`, err)
              return {
                id: img.image_id,
                imageId: img.image_id,
                filename: img.filename,
                imageUrl: img.file_path,
                entities: {},
                createdAt: img.created_at
              }
            }
          })
        )

        // Now fetch the images from the list endpoint to get entity names
        try {
          const listResponse = await api.get('/images/?limit=100')
          const imagesWithNames = listResponse.data.images || []

          // Create a map of image_id to entities with names
          const entityNamesMap = {}
          imagesWithNames.forEach(img => {
            if (img.entities) {
              entityNamesMap[img.image_id] = img.entities
            }
          })

          // Merge entity names into our detailed images
          imagesWithDetails.forEach(img => {
            if (entityNamesMap[img.id]) {
              img.entities = entityNamesMap[img.id]
            }
          })
        } catch (err) {
          console.error('Failed to fetch entity names:', err)
        }

        setImages(imagesWithDetails)
      } catch (err) {
        console.error('Failed to fetch gallery images:', err)
        setError(err.response?.data?.detail || err.message || 'Failed to load images')
      } finally {
        setLoading(false)
      }
    }

    fetchImages()
  }, [entityType, entityId])

  const getEntityIcon = (type) => {
    const icons = {
      'character': '👤',
      'clothing_item': '👕',
      'visual_style': '🎨',
      'preset': '🎨',
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

  const renderImageCard = (image) => {
    const entityCounts = {}
    Object.keys(image.entities || {}).forEach(type => {
      entityCounts[type] = image.entities[type].length
    })

    return (
      <div
        key={image.id}
        className="gallery-card"
        onClick={() => setSelectedImage(image)}
      >
        <div className="gallery-card-image">
          <LazyImage
            src={image.imageUrl}
            alt={image.title}
            onError={(e) => e.target.style.display = 'none'}
          />
        </div>
        <div className="gallery-card-content">
          <h3 className="gallery-card-title">{image.filename}</h3>

          {Object.keys(entityCounts).length > 0 && (
            <div className="gallery-card-badges">
              {entityCounts.character > 0 && (
                <span className="entity-badge entity-badge-character">
                  👤 {entityCounts.character}
                </span>
              )}
              {entityCounts.clothing_item > 0 && (
                <span className="entity-badge entity-badge-clothing">
                  👕 {entityCounts.clothing_item}
                </span>
              )}
              {(entityCounts.visual_style > 0 || entityCounts.preset > 0) && (
                <span className="entity-badge entity-badge-style">
                  🎨 {(entityCounts.visual_style || 0) + (entityCounts.preset || 0)}
                </span>
              )}
            </div>
          )}

          {formatDate(image.createdAt) && (
            <p className="gallery-card-date">{formatDate(image.createdAt)}</p>
          )}
        </div>
      </div>
    )
  }

  const renderImageDetail = (image) => {
    return (
      <div className="gallery-detail-container">
        <div className="gallery-detail-left">
          <img
            src={image.imageUrl}
            alt={image.filename}
            className="gallery-detail-image"
          />
        </div>
        <div className="gallery-detail-right">
          <h2 className="gallery-detail-title">{image.filename}</h2>

          {(image.width || image.height) && (
            <div className="gallery-detail-section">
              <h3>Dimensions</h3>
              <p>{image.width} × {image.height} pixels</p>
            </div>
          )}

          {Object.keys(image.entities || {}).length > 0 && (
            <div className="gallery-detail-section">
              <h3>Used Entities</h3>
              {Object.keys(image.entities).map(entityType => (
                <div key={entityType} className="gallery-detail-entity-type">
                  <h4>{getEntityIcon(entityType)} {getEntityLabel(entityType)}</h4>
                  <div className="gallery-detail-entity-list">
                    {image.entities[entityType].map((entity, idx) => (
                      <Link
                        key={idx}
                        to={getEntityRoute(entityType)}
                        className="gallery-detail-entity-badge"
                      >
                        {entity.entity_name || entity.entity_id}
                        {entity.role && (
                          <span className="entity-role"> ({entity.role})</span>
                        )}
                      </Link>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {formatDate(image.createdAt) && (
            <div className="gallery-detail-section">
              <p><strong>Generated:</strong> {formatDate(image.createdAt)}</p>
            </div>
          )}

          <a
            href={image.imageUrl}
            download={image.filename}
            className="gallery-detail-download"
          >
            ⬇️ Download
          </a>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="entity-gallery-loading">
        <div className="spinner"></div>
        <p>Loading gallery...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="entity-gallery-error">
        <p>Error loading gallery: {error}</p>
      </div>
    )
  }

  if (images.length === 0) {
    return (
      <div className="entity-gallery-empty">
        <div className="empty-icon">🖼️</div>
        <h3>No images yet</h3>
        <p>Images generated with this {entityType.replace('_', ' ')} will appear here.</p>
      </div>
    )
  }

  return (
    <div className="entity-gallery">
      {!selectedImage ? (
        <>
          <div className="entity-gallery-header">
            <h3>📸 Gallery</h3>
            <p className="gallery-count">{total} {total === 1 ? 'image' : 'images'}</p>
          </div>

          <div className="entity-gallery-grid">
            {images.map(renderImageCard)}
          </div>
        </>
      ) : (
        <>
          <button
            className="gallery-back-button"
            onClick={() => setSelectedImage(null)}
          >
            ← Back to Gallery
          </button>
          {renderImageDetail(selectedImage)}
        </>
      )}
    </div>
  )
}

export default EntityGallery
