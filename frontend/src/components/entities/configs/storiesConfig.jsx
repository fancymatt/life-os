import api from '../../../api/client'
import { formatDate, getWordCount, getPreview } from './helpers'
import LazyImage from '../LazyImage'

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
  fullWidthDetail: true,  // Show stories in full-width layout, not sidebar

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
          <LazyImage
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

  renderDetail: (story) => {
    // Parse story text and replace image markers with actual images
    const renderStoryWithImages = () => {
      // Create a map of scene_number to illustration
      const illustrationMap = {}
      story.illustrations.forEach(ill => {
        illustrationMap[ill.scene_number] = ill
      })

      // Split story by paragraphs
      const paragraphs = story.story.split('\n\n')
      const elements = []

      paragraphs.forEach((paragraph, idx) => {
        // Check if paragraph is an image marker like {image_01}
        const imageMatch = paragraph.match(/^\{image_(\d+)\}$/)

        // Check if paragraph contains markdown image syntax like ![alt text](url)
        const markdownImageMatch = paragraph.match(/^!\[([^\]]*)\]\(([^\)]+)\)$/)

        if (imageMatch) {
          // This is an image marker
          const imageNumber = parseInt(imageMatch[1], 10)
          const illustration = illustrationMap[imageNumber]

          if (illustration) {
            // Render the image
            elements.push(
              <div
                key={`img-${idx}`}
                style={{
                  margin: '2rem 0',
                  borderRadius: '12px',
                  overflow: 'hidden',
                  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)',
                  background: 'rgba(255, 255, 255, 0.05)'
                }}
              >
                <img
                  src={illustration.image_url}
                  alt={`Scene ${illustration.scene_number}`}
                  style={{ width: '100%', height: 'auto', display: 'block' }}
                />
              </div>
            )
          }
        } else if (markdownImageMatch) {
          // This is a markdown image ![alt](url)
          const [, altText, imageUrl] = markdownImageMatch
          elements.push(
            <div
              key={`md-img-${idx}`}
              style={{
                margin: '2rem 0',
                borderRadius: '12px',
                overflow: 'hidden',
                boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)',
                background: 'rgba(255, 255, 255, 0.05)'
              }}
            >
              <img
                src={imageUrl}
                alt={altText}
                style={{ width: '100%', height: 'auto', display: 'block' }}
                onError={(e) => e.target.style.display = 'none'}
              />
            </div>
          )
        } else if (paragraph.trim()) {
          // Regular text paragraph
          elements.push(
            <p key={`p-${idx}`} style={{ margin: '0 0 1.5rem 0' }}>
              {paragraph}
            </p>
          )
        }
      })

      return elements
    }

    return (
      <div style={{ padding: '0', maxWidth: '1000px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '2.5rem', margin: '0 0 3rem 0', color: 'white', textAlign: 'center' }}>
          {story.title}
        </h1>

        <div style={{ lineHeight: '1.8', fontSize: '1.1rem', color: 'rgba(255, 255, 255, 0.9)' }}>
          {renderStoryWithImages()}
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
}
