import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './StoriesPage.css'
import api from '../api/client'

function StoriesPage() {
  const navigate = useNavigate()
  const [stories, setStories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedStory, setSelectedStory] = useState(null)

  useEffect(() => {
    fetchStories()
  }, [])

  const fetchStories = async () => {
    try {
      setLoading(true)
      // Fetch all jobs
      const response = await api.get('/jobs?limit=100')

      // Filter for completed workflow jobs
      const storyList = response.data
        .filter(job => job.type === 'workflow' && job.status === 'completed' && job.result?.illustrated_story)
        .map(job => ({
          jobId: job.job_id,
          title: job.result.illustrated_story.title,
          story: job.result.illustrated_story.story,
          illustrations: job.result.illustrated_story.illustrations || [],
          metadata: job.result.illustrated_story.metadata || {},
          createdAt: job.created_at,
          completedAt: job.completed_at,
          jobTitle: job.title
        }))

      // Sort by newest first
      storyList.sort((a, b) => new Date(b.completedAt) - new Date(a.completedAt))

      setStories(storyList)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getWordCount = (text) => {
    return text.split(/\s+/).filter(word => word.length > 0).length
  }

  const getPreview = (text, maxWords = 30) => {
    const words = text.split(/\s+/)
    if (words.length <= maxWords) return text
    return words.slice(0, maxWords).join(' ') + '...'
  }

  return (
    <div className="stories-page">
      <div className="stories-header">
        <div>
          <h2>📚 Story Library</h2>
          <p className="stories-subtitle">{stories.length} generated {stories.length === 1 ? 'story' : 'stories'}</p>
        </div>
        <div className="stories-actions">
          <button className="refresh-button" onClick={fetchStories}>
            🔄 Refresh
          </button>
          <button className="new-story-button" onClick={() => navigate('/workflows/story')}>
            + New Story
          </button>
        </div>
      </div>

      {loading ? (
        <div className="stories-loading">Loading stories...</div>
      ) : error ? (
        <div className="stories-error">Error: {error}</div>
      ) : stories.length === 0 ? (
        <div className="stories-empty">
          <p>No stories yet</p>
          <p className="stories-empty-hint">Generate your first story to see it here!</p>
          <button className="new-story-button" onClick={() => navigate('/workflows/story')}>
            Generate Story
          </button>
        </div>
      ) : (
        <div className="stories-grid">
          {stories.map((story, idx) => (
            <div
              key={idx}
              className="story-card"
              onClick={() => setSelectedStory(story)}
            >
              {story.illustrations.length > 0 && (
                <div className="story-cover">
                  <img
                    src={story.illustrations[0].image_url}
                    alt={story.title}
                    onError={(e) => {
                      e.target.style.display = 'none'
                    }}
                  />
                </div>
              )}
              <div className="story-card-content">
                <h3 className="story-card-title">{story.title}</h3>
                <p className="story-card-preview">{getPreview(story.story)}</p>
                <div className="story-card-meta">
                  <span className="story-word-count">{getWordCount(story.story)} words</span>
                  <span className="story-illustration-count">
                    {story.illustrations.length} {story.illustrations.length === 1 ? 'illustration' : 'illustrations'}
                  </span>
                </div>
                <p className="story-card-date">{formatDate(story.completedAt)}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Story Reader Modal */}
      {selectedStory && (
        <div className="story-reader-overlay" onClick={() => setSelectedStory(null)}>
          <div className="story-reader" onClick={(e) => e.stopPropagation()}>
            <button className="story-reader-close" onClick={() => setSelectedStory(null)}>×</button>

            <div className="story-reader-content">
              <h1 className="story-reader-title">{selectedStory.title}</h1>

              {selectedStory.illustrations.length > 0 && (
                <div className="story-illustrations">
                  {selectedStory.illustrations.map((ill, idx) => (
                    <div key={idx} className="story-illustration">
                      <img
                        src={ill.image_url}
                        alt={`Scene ${ill.scene_number}`}
                        onError={(e) => {
                          e.target.style.display = 'none'
                        }}
                      />
                    </div>
                  ))}
                </div>
              )}

              <div className="story-reader-text">
                {selectedStory.story.split('\n\n').map((paragraph, idx) => (
                  <p key={idx}>{paragraph}</p>
                ))}
              </div>

              <div className="story-reader-footer">
                <div className="story-reader-meta">
                  <p><strong>Word Count:</strong> {getWordCount(selectedStory.story)}</p>
                  <p><strong>Illustrations:</strong> {selectedStory.illustrations.length}</p>
                  <p><strong>Generated:</strong> {formatDate(selectedStory.completedAt)}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default StoriesPage
