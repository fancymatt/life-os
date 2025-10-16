import api from '../../../api/client'
import { formatDate, getWordCount, getPreview } from './helpers'

/**
 * Stories Entity Configuration
 */
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
