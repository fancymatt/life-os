import { useState, useEffect } from 'react'
import './Gallery.css'
import api from './api/client'

function Gallery({ onClose }) {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedImage, setSelectedImage] = useState(null)
  const [comparisonMode, setComparisonMode] = useState(false)
  const [selectedImages, setSelectedImages] = useState([])

  useEffect(() => {
    fetchGeneratedImages()
  }, [])

  const fetchGeneratedImages = async () => {
    try {
      setLoading(true)
      // Fetch completed generation jobs
      const response = await api.get('/jobs?limit=100')

      // Extract images from job results
      const imageList = []
      response.data.forEach(job => {
        if (job.status === 'completed' && job.result?.file_paths) {
          job.result.file_paths.forEach(filePath => {
            // Convert absolute path to relative URL
            // /app/output/generated/filename.png -> /output/generated/filename.png
            const url = filePath.replace('/app', '')
            const filename = filePath.split('/').pop()

            imageList.push({
              url,
              filename,
              jobId: job.job_id,
              title: job.title,
              createdAt: job.created_at,
              completedAt: job.completed_at
            })
          })
        }
      })

      // Sort by newest first
      imageList.sort((a, b) => new Date(b.completedAt) - new Date(a.completedAt))

      setImages(imageList)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleImageClick = (image) => {
    if (comparisonMode) {
      // Toggle selection in comparison mode
      setSelectedImages(prev => {
        const isSelected = prev.find(img => img.url === image.url)
        if (isSelected) {
          return prev.filter(img => img.url !== image.url)
        } else {
          // Limit to 4 images for comparison
          if (prev.length >= 4) {
            return [...prev.slice(1), image]
          }
          return [...prev, image]
        }
      })
    } else {
      // Open preview in normal mode
      setSelectedImage(image)
    }
  }

  const toggleComparisonMode = () => {
    setComparisonMode(!comparisonMode)
    setSelectedImages([])
    setSelectedImage(null)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="gallery-modal" onClick={(e) => e.stopPropagation()}>
        <div className="gallery-header">
          <div>
            <h2>🖼️ Image Gallery</h2>
            <p className="gallery-subtitle">{images.length} generated images</p>
          </div>
          <div className="gallery-actions">
            <button
              className={`comparison-toggle ${comparisonMode ? 'active' : ''}`}
              onClick={toggleComparisonMode}
            >
              {comparisonMode ? '📊 Exit Compare' : '📊 Compare'}
            </button>
            <button className="refresh-button" onClick={fetchGeneratedImages}>
              🔄 Refresh
            </button>
            <button className="close-button" onClick={onClose}>×</button>
          </div>
        </div>

        {loading ? (
          <div className="gallery-loading">Loading images...</div>
        ) : error ? (
          <div className="gallery-error">Error: {error}</div>
        ) : images.length === 0 ? (
          <div className="gallery-empty">
            <p>No generated images yet</p>
            <p className="gallery-empty-hint">Generate some images to see them here!</p>
          </div>
        ) : (
          <>
            {comparisonMode && selectedImages.length > 0 && (
              <div className="comparison-view">
                <h3>Comparing {selectedImages.length} images</h3>
                <div className="comparison-grid">
                  {selectedImages.map((image, idx) => (
                    <div key={idx} className="comparison-item">
                      <img src={image.url} alt={image.filename} />
                      <div className="comparison-info">
                        <p className="comparison-filename">{image.filename}</p>
                        <p className="comparison-date">{formatDate(image.completedAt)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="gallery-grid">
              {images.map((image, idx) => {
                const isSelected = selectedImages.find(img => img.url === image.url)
                return (
                  <div
                    key={idx}
                    className={`gallery-item ${isSelected ? 'selected' : ''} ${comparisonMode ? 'comparison-mode' : ''}`}
                    onClick={() => handleImageClick(image)}
                  >
                    <div className="gallery-image-container">
                      <img src={image.url} alt={image.filename} loading="lazy" />
                      {isSelected && <div className="selection-badge">✓</div>}
                    </div>
                    <div className="gallery-item-info">
                      <p className="gallery-item-title">{image.title}</p>
                      <p className="gallery-item-date">{formatDate(image.completedAt)}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </>
        )}

        {/* Image Preview Modal */}
        {selectedImage && !comparisonMode && (
          <div className="preview-overlay" onClick={() => setSelectedImage(null)}>
            <div className="preview-container" onClick={(e) => e.stopPropagation()}>
              <button className="preview-close" onClick={() => setSelectedImage(null)}>×</button>
              <img src={selectedImage.url} alt={selectedImage.filename} />
              <div className="preview-info">
                <h3>{selectedImage.filename}</h3>
                <p>{selectedImage.title}</p>
                <p className="preview-date">{formatDate(selectedImage.completedAt)}</p>
                <a
                  href={selectedImage.url}
                  download={selectedImage.filename}
                  className="download-button"
                  onClick={(e) => e.stopPropagation()}
                >
                  ⬇️ Download
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Gallery
