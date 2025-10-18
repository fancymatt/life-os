import api from '../../../api/client'
import { formatDate, getPreview } from './helpers'

/**
 * Documents Entity Configuration
 */
export const documentsConfig = {
  entityType: 'document',
  title: 'Documents',
  icon: '📄',
  emptyMessage: 'No documents yet. Use the BGG Rulebook Fetcher or upload documents!',
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  showRefreshButton: true,
  defaultSort: 'newest',
  searchFields: ['title', 'source_type', 'source_url'],

  actions: [],

  fetchEntities: async () => {
    const response = await api.get('/documents/')
    return (response.data.documents || []).map(doc => ({
      id: doc.document_id,
      documentId: doc.document_id,
      title: doc.title,
      gameId: doc.game_id,
      sourceType: doc.source_type,
      sourceUrl: doc.source_url,
      filePath: doc.file_path,
      pageCount: doc.page_count,
      fileSizeBytes: doc.file_size_bytes,
      processed: doc.processed,
      processedAt: doc.processed_at,
      markdownPath: doc.markdown_path,
      vectorIds: doc.vector_ids || [],
      createdAt: doc.created_at,
      metadata: doc.metadata || {},
      // Wrap editable fields in data property for EntityBrowser
      data: {
        title: doc.title
      }
    }))
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (doc) => {
    const getSourceIcon = (sourceType) => {
      switch (sourceType) {
        case 'pdf': return '📕'
        case 'url': return '🔗'
        case 'text': return '📝'
        default: return '📄'
      }
    }

    return (
      <div className="entity-card">
        <div className="entity-card-image" style={{ height: '200px', background: 'linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(202, 138, 4, 0.2))' }}>
          <div className="entity-card-placeholder" style={{ fontSize: '5rem' }}>
            {getSourceIcon(doc.sourceType)}
          </div>
          {doc.processed && (
            <div style={{
              position: 'absolute',
              top: '0.75rem',
              right: '0.75rem',
              background: 'rgba(34, 197, 94, 0.9)',
              color: 'white',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              fontWeight: 600
            }}>
              ✓ Processed
            </div>
          )}
        </div>
        <div className="entity-card-content">
          <h3 className="entity-card-title">{doc.title}</h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem', margin: '0 0 0.5rem 0' }}>
            {doc.sourceType.toUpperCase()}
            {doc.pageCount && ` • ${doc.pageCount} pages`}
          </p>
          {doc.fileSizeBytes && (
            <p style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.8rem', margin: '0 0 0.5rem 0' }}>
              {(doc.fileSizeBytes / 1024 / 1024).toFixed(2)} MB
            </p>
          )}
          {formatDate(doc.createdAt) && (
            <p className="entity-card-date">{formatDate(doc.createdAt)}</p>
          )}
        </div>
      </div>
    )
  },

  renderPreview: (doc) => {
    const getSourceIcon = (sourceType) => {
      switch (sourceType) {
        case 'pdf': return '📕'
        case 'url': return '🔗'
        case 'text': return '📝'
        default: return '📄'
      }
    }

    return (
      <>
        <div style={{
          width: '100%',
          aspectRatio: '4/5',
          background: 'linear-gradient(135deg, rgba(234, 179, 8, 0.3), rgba(202, 138, 4, 0.3))',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '8rem',
          marginBottom: '1.5rem'
        }}>
          {getSourceIcon(doc.sourceType)}
        </div>
      </>
    )
  },

  renderDetail: (doc, handleBackToList, onUpdate) => (
    <div style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ color: 'white', margin: '0 0 0.5rem 0' }}>{doc.title}</h2>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span style={{
            background: doc.processed ? 'rgba(34, 197, 94, 0.2)' : 'rgba(156, 163, 175, 0.2)',
            color: doc.processed ? 'rgba(34, 197, 94, 0.9)' : 'rgba(156, 163, 175, 0.9)',
            padding: '0.25rem 0.75rem',
            borderRadius: '12px',
            fontSize: '0.85rem',
            fontWeight: 600
          }}>
            {doc.processed ? '✓ Processed' : '○ Not Processed'}
          </span>
          <span style={{
            background: 'rgba(234, 179, 8, 0.2)',
            color: 'rgba(234, 179, 8, 0.9)',
            padding: '0.25rem 0.75rem',
            borderRadius: '12px',
            fontSize: '0.85rem',
            fontWeight: 600
          }}>
            {doc.sourceType.toUpperCase()}
          </span>
        </div>
      </div>

      {/* File Info */}
      <div style={{ marginBottom: '1.5rem', display: 'grid', gap: '0.75rem' }}>
        {doc.pageCount && (
          <div>
            <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Pages:</strong>{' '}
            <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{doc.pageCount}</span>
          </div>
        )}
        {doc.fileSizeBytes && (
          <div>
            <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>File Size:</strong>{' '}
            <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
              {(doc.fileSizeBytes / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>
        )}
        {doc.sourceUrl && (
          <div>
            <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Source:</strong>{' '}
            <a
              href={doc.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'rgba(234, 179, 8, 0.9)', textDecoration: 'none', wordBreak: 'break-all' }}
            >
              {doc.sourceUrl} ↗
            </a>
          </div>
        )}
        {doc.filePath && (
          <div>
            <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>File Path:</strong>{' '}
            <span style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.85rem', fontFamily: 'monospace' }}>
              {doc.filePath}
            </span>
          </div>
        )}
      </div>

      {/* Processing Info */}
      {doc.processed && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.75rem 0' }}>
            Processing Info
          </h3>
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            {doc.processedAt && (
              <div>
                <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Processed At:</strong>{' '}
                <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{formatDate(doc.processedAt)}</span>
              </div>
            )}
            {doc.markdownPath && (
              <div>
                <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Markdown:</strong>{' '}
                <span style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.85rem', fontFamily: 'monospace' }}>
                  {doc.markdownPath}
                </span>
              </div>
            )}
            {doc.vectorIds && doc.vectorIds.length > 0 && (
              <div>
                <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Vector Count:</strong>{' '}
                <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{doc.vectorIds.length} chunks</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Associated Game */}
      {doc.gameId && (
        <div style={{ marginBottom: '1.5rem' }}>
          <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Associated Game:</strong>{' '}
          <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{doc.gameId}</span>
        </div>
      )}

      {formatDate(doc.createdAt) && (
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', margin: 0 }}>
            <strong>Created:</strong> {formatDate(doc.createdAt)}
          </p>
        </div>
      )}
    </div>
  ),

  renderEdit: (doc, editedData, editedTitle, handlers) => (
    <div>
      {/* Title Field */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Document Title
        </label>
        <input
          type="text"
          value={editedData.title || ''}
          onChange={(e) => handlers.updateField('title', e.target.value)}
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

      {/* Read-only info */}
      <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px' }}>
        <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem', margin: '0 0 0.5rem 0' }}>
          <strong>Source Type:</strong> {doc.sourceType}
        </p>
        {doc.filePath && (
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem', margin: '0 0 0.5rem 0' }}>
            <strong>File:</strong> {doc.filePath}
          </p>
        )}
        {doc.processed && (
          <p style={{ color: 'rgba(34, 197, 94, 0.9)', fontSize: '0.9rem', margin: 0 }}>
            ✓ Document has been processed
          </p>
        )}
      </div>
    </div>
  ),

  saveEntity: async (doc, updates) => {
    const response = await api.put(
      `/documents/${doc.documentId}`,
      {
        title: updates.data.title
      }
    )
    return response.data
  },

  deleteEntity: async (doc) => {
    await api.delete(`/documents/${doc.documentId}`)
  }
}
