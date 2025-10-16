import api from '../../../api/client'
import { formatDate } from './helpers'
import LazyImage from '../LazyImage'

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
        <LazyImage
          src={image.imageUrl}
          alt={image.title}
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
