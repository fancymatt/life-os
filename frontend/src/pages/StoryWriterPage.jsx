import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import './StoryToolsPage.css'
import api from '../api/client'

function StoryWriterPage() {
  const navigate = useNavigate()
  const location = useLocation()

  const [outlineJson, setOutlineJson] = useState('')
  const [characterName, setCharacterName] = useState('')
  const [characterTraits, setCharacterTraits] = useState('')
  const [theme, setTheme] = useState('adventure')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const themes = [
    'adventure',
    'mystery',
    'fantasy',
    'science_fiction',
    'comedy',
    'friendship',
    'courage',
    'discovery'
  ]

  // Check if we have outline passed from planner
  useEffect(() => {
    if (location.state?.outline) {
      setOutlineJson(JSON.stringify(location.state.outline, null, 2))
      setCharacterName(location.state.character?.name || '')
      setCharacterTraits(location.state.character?.traits || '')
      setTheme(location.state.theme || 'adventure')
    }
  }, [location.state])

  const handleExecute = async () => {
    if (!outlineJson.trim()) {
      setError('Please provide a story outline')
      return
    }

    setRunning(true)
    setError(null)
    setResult(null)

    try {
      // Parse the outline JSON
      const outline = JSON.parse(outlineJson)

      const character = {
        name: characterName.trim() || 'Character',
        traits: characterTraits.trim() || 'curious and brave'
      }

      const response = await api.post('/story-tools/story-writer?async_mode=true', {
        outline,
        character,
        theme
      })

      // Async mode: job is queued
      if (response.data.job_id) {
        console.log('Story writing job queued:', response.data.job_id)
        // Navigate to jobs page to see progress
        navigate('/jobs')
        return
      }

      // Sync mode (fallback): display result
      if (response.data.status === 'completed') {
        setResult(response.data.result)
      } else {
        throw new Error(response.data.error || 'Writing failed')
      }
    } catch (err) {
      console.error('Writing error:', err)
      if (err instanceof SyntaxError) {
        setError('Invalid JSON in outline. Please check the format.')
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
        <h2>✍️ Story Writer</h2>
        <p className="page-subtitle">Transform a story outline into a complete narrative</p>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="tool-form">
        <div className="form-section">
          <h3>Story Outline</h3>

          <div className="form-group">
            <label htmlFor="outline">Story Outline (JSON) *</label>
            <textarea
              id="outline"
              className="json-input"
              value={outlineJson}
              onChange={(e) => setOutlineJson(e.target.value)}
              placeholder={`{
  "title": "Story Title",
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
            <small>Paste the outline JSON from Story Planner or create your own</small>
          </div>
        </div>

        <div className="form-section">
          <h3>Character & Theme</h3>

          <div className="form-group">
            <label htmlFor="character-name">Character Name</label>
            <input
              type="text"
              id="character-name"
              value={characterName}
              onChange={(e) => setCharacterName(e.target.value)}
              placeholder="e.g., Luna, Max, Zara"
              disabled={running}
            />
          </div>

          <div className="form-group">
            <label htmlFor="character-traits">Character Traits</label>
            <input
              type="text"
              id="character-traits"
              value={characterTraits}
              onChange={(e) => setCharacterTraits(e.target.value)}
              placeholder="e.g., curious, brave, loves adventure"
              disabled={running}
            />
          </div>

          <div className="form-group">
            <label htmlFor="theme">Theme</label>
            <select
              id="theme"
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              disabled={running}
            >
              {themes.map(t => (
                <option key={t} value={t}>
                  {t.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          className="execute-button"
          onClick={handleExecute}
          disabled={running || !outlineJson.trim()}
        >
          {running ? 'Writing Story...' : 'Write Complete Story'}
        </button>
      </div>

      {result && (
        <div className="tool-result">
          <h3>Written Story</h3>

          <div className="result-section">
            <h4>{result.written_story?.title || 'Untitled'}</h4>
            <div className="story-text">
              {result.written_story?.story?.split('\n\n').map((paragraph, idx) => (
                <p key={idx}>{paragraph}</p>
              ))}
            </div>
          </div>

          <div className="result-section">
            <h4>Story Metadata</h4>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Word Count: {result.written_story?.story?.split(/\s+/).filter(w => w.length > 0).length || 0}<br/>
              Scenes: {result.written_story?.scenes?.length || 0}
            </p>
          </div>

          <div className="result-actions">
            <button
              className="secondary-button"
              onClick={() => navigate('/story-tools/story-illustrator', {
                state: {
                  writtenStory: result.written_story,
                  character: { name: characterName, traits: characterTraits }
                }
              })}
            >
              Continue to Story Illustrator →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default StoryWriterPage
