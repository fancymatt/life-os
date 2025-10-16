import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import './StoryToolsPage.css'
import api from '../api/client'

function StoryIllustratorPage() {
  const navigate = useNavigate()
  const location = useLocation()

  const [storyJson, setStoryJson] = useState('')
  const [characterAppearance, setCharacterAppearance] = useState('')
  const [artStyle, setArtStyle] = useState('digital_art')
  const [maxIllustrations, setMaxIllustrations] = useState(5)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const artStyles = [
    { value: 'watercolor', label: 'Watercolor' },
    { value: 'digital_art', label: 'Digital Art' },
    { value: 'sketch', label: 'Pencil Sketch' },
    { value: 'cartoon', label: 'Cartoon' },
    { value: 'realistic', label: 'Realistic' },
    { value: 'oil_painting', label: 'Oil Painting' },
    { value: 'anime', label: 'Anime' }
  ]

  // Check if we have written story passed from writer
  useEffect(() => {
    if (location.state?.writtenStory) {
      setStoryJson(JSON.stringify(location.state.writtenStory, null, 2))
      setCharacterAppearance(location.state.character?.traits || '')
    }
  }, [location.state])

  const handleExecute = async () => {
    if (!storyJson.trim()) {
      setError('Please provide a written story')
      return
    }

    setRunning(true)
    setError(null)
    setResult(null)

    try {
      // Parse the story JSON
      const writtenStory = JSON.parse(storyJson)

      const response = await api.post('/story-tools/story-illustrator?async_mode=true', {
        written_story: writtenStory,
        character_appearance: characterAppearance.trim(),
        art_style: artStyle,
        max_illustrations: maxIllustrations
      })

      // Async mode: job is queued
      if (response.data.job_id) {
        console.log('Story illustration job queued:', response.data.job_id)
        // Navigate to jobs page to see progress
        navigate('/jobs')
        return
      }

      // Sync mode (fallback): display result
      if (response.data.status === 'completed') {
        setResult(response.data.result)
      } else {
        throw new Error(response.data.error || 'Illustration failed')
      }
    } catch (err) {
      console.error('Illustration error:', err)
      if (err instanceof SyntaxError) {
        setError('Invalid JSON in story. Please check the format.')
      } else {
        setError(err.response?.data?.detail || err.message)
      }
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="story-tool-page">
      <div className="page-header">
        <h2>🎨 Story Illustrator</h2>
        <p className="page-subtitle">Generate illustrations for your story scenes using DALL-E 3</p>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="tool-form">
        <div className="form-section">
          <h3>Written Story</h3>

          <div className="form-group">
            <label htmlFor="story">Written Story (JSON) *</label>
            <textarea
              id="story"
              className="json-input"
              value={storyJson}
              onChange={(e) => setStoryJson(e.target.value)}
              placeholder={`{
  "title": "Story Title",
  "story": "Full story text...",
  "scenes": [
    {
      "scene_number": 1,
      "description": "Scene description",
      "illustration_prompt": "Illustration description"
    }
  ]
}`}
              rows="12"
              disabled={running}
            />
            <small>Paste the written story JSON from Story Writer or create your own</small>
          </div>
        </div>

        <div className="form-section">
          <h3>Illustration Settings</h3>

          <div className="form-group">
            <label htmlFor="character-appearance">Character Appearance</label>
            <textarea
              id="character-appearance"
              value={characterAppearance}
              onChange={(e) => setCharacterAppearance(e.target.value)}
              placeholder="e.g., a young girl with curly brown hair, wearing a blue dress"
              rows="3"
              disabled={running}
            />
            <small>Optional - visual description of your main character</small>
          </div>

          <div className="form-group">
            <label htmlFor="art-style">Art Style</label>
            <select
              id="art-style"
              value={artStyle}
              onChange={(e) => setArtStyle(e.target.value)}
              disabled={running}
            >
              {artStyles.map(style => (
                <option key={style.value} value={style.value}>
                  {style.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="max-illustrations">
              Maximum Illustrations: {maxIllustrations}
            </label>
            <input
              type="range"
              id="max-illustrations"
              min="1"
              max="10"
              step="1"
              value={maxIllustrations}
              onChange={(e) => setMaxIllustrations(parseInt(e.target.value))}
              disabled={running}
            />
            <div className="range-labels">
              <span>1</span>
              <span>10</span>
            </div>
            <small>Note: Each illustration costs ~$0.04 using DALL-E 3</small>
          </div>
        </div>

        <button
          className="execute-button"
          onClick={handleExecute}
          disabled={running || !storyJson.trim()}
        >
          {running ? 'Generating Illustrations...' : 'Generate Illustrations'}
        </button>
      </div>

      {result && (
        <div className="tool-result">
          <h3>Illustrated Story</h3>

          <div className="result-section">
            <h4>{result.illustrated_story?.title || 'Untitled'}</h4>

            {result.illustrated_story?.illustrations?.length > 0 && (
              <div className="illustrations-grid">
                {result.illustrated_story.illustrations.map((ill, idx) => (
                  <div key={idx} className="illustration-card">
                    <div className="illustration-image">
                      <img
                        src={ill.image_url}
                        alt={`Scene ${ill.scene_number}`}
                        onError={(e) => {
                          e.target.style.display = 'none'
                        }}
                      />
                    </div>
                    <div className="illustration-info">
                      <h5>Scene {ill.scene_number}</h5>
                      <p>{ill.prompt_used}</p>
                      <p style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.4)' }}>
                        Generated in {ill.generation_time?.toFixed(1)}s
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="result-section">
            <h4>Story Text</h4>
            <div className="story-text">
              {result.illustrated_story?.story?.split('\n\n').map((paragraph, idx) => (
                <p key={idx}>{paragraph}</p>
              ))}
            </div>
          </div>

          <div className="result-section">
            <h4>Generation Statistics</h4>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Illustrations Generated: {result.illustrated_story?.illustrations?.length || 0}<br/>
              Total Generation Time: {result.illustrated_story?.total_generation_time?.toFixed(1)}s<br/>
              Estimated Cost: ${((result.illustrated_story?.illustrations?.length || 0) * 0.04).toFixed(2)}
            </p>
          </div>

          <div className="result-actions">
            <button
              className="secondary-button"
              onClick={() => navigate('/stories')}
            >
              View in Story Library →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default StoryIllustratorPage
