import api from '../../../api/client'
import { formatDate, getPreview } from './helpers'

/**
 * Q&As Entity Configuration
 */
export const qasConfig = {
  entityType: 'qa',
  title: 'Q&As',
  icon: '💬',
  emptyMessage: 'No Q&As yet. Use the Document Question Asker tool to ask questions!',
  enableSearch: true,
  enableSort: true,
  enableEdit: false,  // Q&As are read-only (generated content)
  showRefreshButton: true,
  defaultSort: 'newest',
  searchFields: ['question', 'answer'],

  actions: [],

  fetchEntities: async () => {
    const response = await api.get('/qa/')
    return (response.data.qas || []).map(qa => ({
      id: qa.qa_id,
      qaId: qa.qa_id,
      title: qa.question,  // Use question as title
      question: qa.question,
      answer: qa.answer,
      contextType: qa.context_type,
      gameId: qa.game_id,
      documentIds: qa.document_ids || [],
      imageUrl: qa.image_url,
      citations: qa.citations || [],
      confidence: qa.confidence || 0,
      isFavorite: qa.is_favorite || false,
      wasHelpful: qa.was_helpful,
      userNotes: qa.user_notes,
      customTags: qa.custom_tags || [],
      createdAt: qa.created_at,
      metadata: qa.metadata || {},
      // Wrap editable fields (minimal - mostly read-only)
      data: {
        is_favorite: qa.is_favorite || false,
        user_notes: qa.user_notes || ''
      }
    }))
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (qa) => {
    const getContextColor = (contextType) => {
      switch (contextType) {
        case 'document': return 'rgba(59, 130, 246, 0.9)'
        case 'general': return 'rgba(139, 92, 246, 0.9)'
        case 'image': return 'rgba(236, 72, 153, 0.9)'
        case 'comparison': return 'rgba(34, 197, 94, 0.9)'
        default: return 'rgba(156, 163, 175, 0.9)'
      }
    }

    return (
      <div className="entity-card">
        <div className="entity-card-content" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <span style={{
              background: `${getContextColor(qa.contextType)}33`,
              color: getContextColor(qa.contextType),
              padding: '0.25rem 0.75rem',
              borderRadius: '12px',
              fontSize: '0.75rem',
              fontWeight: 600,
              textTransform: 'uppercase'
            }}>
              {qa.contextType}
            </span>
            {qa.isFavorite && (
              <span style={{ fontSize: '1.2rem' }}>⭐</span>
            )}
          </div>

          <h3 className="entity-card-title" style={{ marginBottom: '0.75rem' }}>
            {getPreview(qa.question, 15)}
          </h3>

          <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem', lineHeight: '1.5', marginBottom: '0.75rem' }}>
            {getPreview(qa.answer, 25)}
          </p>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
            {qa.citations && qa.citations.length > 0 && (
              <span style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.8rem' }}>
                📖 {qa.citations.length} source{qa.citations.length !== 1 ? 's' : ''}
              </span>
            )}
            {qa.confidence > 0 && (
              <span style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.8rem' }}>
                {(qa.confidence * 100).toFixed(0)}% confidence
              </span>
            )}
          </div>

          {formatDate(qa.createdAt) && (
            <p className="entity-card-date" style={{ marginTop: '0.75rem' }}>{formatDate(qa.createdAt)}</p>
          )}
        </div>
      </div>
    )
  },

  renderPreview: (qa) => (
    <>
      <div style={{
        width: '100%',
        padding: '2rem',
        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(139, 92, 246, 0.3))',
        borderRadius: '12px',
        marginBottom: '1.5rem'
      }}>
        <div style={{ fontSize: '4rem', textAlign: 'center', marginBottom: '1rem' }}>💬</div>
      </div>
    </>
  ),

  renderDetail: (qa, handleBackToList, onUpdate) => {
    const getContextColor = (contextType) => {
      switch (contextType) {
        case 'document': return 'rgba(59, 130, 246, 0.9)'
        case 'general': return 'rgba(139, 92, 246, 0.9)'
        case 'image': return 'rgba(236, 72, 153, 0.9)'
        case 'comparison': return 'rgba(34, 197, 94, 0.9)'
        default: return 'rgba(156, 163, 175, 0.9)'
      }
    }

    return (
      <div style={{ padding: '2rem' }}>
        {/* Header */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
            <span style={{
              background: `${getContextColor(qa.contextType)}33`,
              color: getContextColor(qa.contextType),
              padding: '0.25rem 0.75rem',
              borderRadius: '12px',
              fontSize: '0.85rem',
              fontWeight: 600,
              textTransform: 'uppercase'
            }}>
              {qa.contextType}
            </span>
            {qa.confidence > 0 && (
              <span style={{
                background: 'rgba(255, 255, 255, 0.1)',
                color: 'rgba(255, 255, 255, 0.7)',
                padding: '0.25rem 0.75rem',
                borderRadius: '12px',
                fontSize: '0.85rem'
              }}>
                {(qa.confidence * 100).toFixed(0)}% confidence
              </span>
            )}
            {qa.isFavorite && (
              <span style={{ fontSize: '1.5rem' }}>⭐</span>
            )}
          </div>
        </div>

        {/* Question */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
            Question
          </h3>
          <p style={{ color: 'white', lineHeight: '1.6', margin: 0, fontSize: '1.1rem' }}>
            {qa.question}
          </p>
        </div>

        {/* Answer */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
            Answer
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.6', margin: 0 }}>
            {qa.answer}
          </p>
        </div>

        {/* Citations */}
        {qa.citations && qa.citations.length > 0 && (
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.75rem 0' }}>
              Sources ({qa.citations.length})
            </h3>
            <div style={{ display: 'grid', gap: '1rem' }}>
              {qa.citations.map((citation, idx) => (
                <div key={idx} style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  padding: '1rem',
                  borderRadius: '8px',
                  borderLeft: '3px solid rgba(59, 130, 246, 0.5)'
                }}>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                      {citation.document_id && `Document: ${citation.document_id}`}
                      {citation.page && ` | Page ${citation.page}`}
                    </strong>
                    {citation.section && (
                      <span style={{ color: 'rgba(255, 255, 255, 0.6)', marginLeft: '0.5rem', fontSize: '0.9rem' }}>
                        ({citation.section})
                      </span>
                    )}
                  </div>
                  {citation.text && (
                    <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem', fontStyle: 'italic', margin: 0 }}>
                      "{citation.text}"
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* User Notes */}
        {qa.userNotes && (
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
              Your Notes
            </h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>
              {qa.userNotes}
            </p>
          </div>
        )}

        {/* Tags */}
        {qa.customTags && qa.customTags.length > 0 && (
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {qa.customTags.map((tag, idx) => (
                <span key={idx} style={{
                  background: 'rgba(139, 92, 246, 0.2)',
                  color: 'rgba(139, 92, 246, 0.9)',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '12px',
                  fontSize: '0.85rem'
                }}>
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Feedback */}
        {qa.wasHelpful !== null && qa.wasHelpful !== undefined && (
          <div style={{ marginBottom: '1.5rem' }}>
            <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Helpful:</strong>{' '}
            <span style={{ fontSize: '1.2rem' }}>{qa.wasHelpful ? '👍' : '👎'}</span>
          </div>
        )}

        {formatDate(qa.createdAt) && (
          <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', margin: 0 }}>
              <strong>Created:</strong> {formatDate(qa.createdAt)}
            </p>
          </div>
        )}
      </div>
    )
  },

  renderEdit: null,  // Q&As are read-only

  saveEntity: null,  // Q&As are read-only

  deleteEntity: async (qa) => {
    await api.delete(`/qa/${qa.qaId}`)
  }
}
