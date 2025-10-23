import { useState, useEffect } from 'react'
import api from '../../api/client'
import './EntityGallery.css'

/**
 * Entity Gallery Component
 *
 * Displays all images that used a specific entity (character, clothing item, preset, etc.)
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
        const response = await api.get(`/images/by-entity/${entityType}/${entityId}?limit=100`)
        setImages(response.data.images || [])
        setTotal(response.data.total || 0)
      } catch (err) {
        console.error('Failed to fetch gallery images:', err)
        setError(err.response?.data?.detail || err.message || 'Failed to load images')
      } finally {
        setLoading(false)
      }
    }

    fetchImages()
  }, [entityType, entityId])

  const handleImageClick = (image) => {
    setSelectedImage(image)
  }

  const closeModal = () => {
    setSelectedImage(null)
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
      <div className="entity-gallery-header">
        <h3>📸 Gallery</h3>
        <p className="gallery-count">{total} {total === 1 ? 'image' : 'images'}</p>
      </div>

      <div className="entity-gallery-grid">
        {images.map((image, idx) => (
          <div
            key={image.image_id || idx}
            className="gallery-image-card"
            onClick={() => handleImageClick(image)}
          >
            <div className="gallery-image-wrapper">
              <img
                src={image.file_path}
                alt={`Generated ${idx + 1}`}
                loading="lazy"
              />
              <div className="gallery-image-overlay">
                <span className="view-icon">🔍</span>
              </div>
            </div>
            <div className="gallery-image-info">
              <span className="gallery-image-date">
                {new Date(image.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div className="gallery-modal" onClick={closeModal}>
          <div className="gallery-modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="gallery-modal-close" onClick={closeModal}>×</button>
            <img
              src={selectedImage.file_path}
              alt="Full size"
            />
            <div className="gallery-modal-info">
              <p><strong>Created:</strong> {new Date(selectedImage.created_at).toLocaleString()}</p>
              {selectedImage.width && selectedImage.height && (
                <p><strong>Dimensions:</strong> {selectedImage.width} × {selectedImage.height}</p>
              )}
              <a
                href={selectedImage.file_path}
                download
                className="gallery-download-button"
                onClick={(e) => e.stopPropagation()}
              >
                ⬇️ Download
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default EntityGallery
