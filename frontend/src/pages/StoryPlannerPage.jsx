import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './StoryToolsPage.css'
import api from '../api/client'

function StoryPlannerPage() {
  const navigate = useNavigate()
  const [useExistingCharacter, setUseExistingCharacter] = useState(false)
  const [characters, setCharacters] = useState([])
  const [selectedCharacterId, setSelectedCharacterId] = useState('')
  const [characterName, setCharacterName] = useState('')
  const [characterTraits, setCharacterTraits] = useState('')
  const [theme, setTheme] = useState('adventure')
  const [targetWordCount, setTargetWordCount] = useState(500)
  const [maxScenes, setMaxScenes] = useState(5)
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

  // Fetch characters on mount
  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const response = await api.get('/characters/')
        setCharacters(response.data.characters || [])
      } catch (err) {
        console.error('Failed to fetch characters:', err)
      }
    }
    fetchCharacters()
  }, [])

  // Handle character selection
  const handleCharacterSelect = (characterId) => {
    setSelectedCharacterId(characterId)

    if (!characterId) {
      setCharacterName('')
      setCharacterTraits('')
      return
    }

    const character = characters.find(c => c.character_id === characterId)
    if (character) {
      setCharacterName(character.name)

      // Build traits from visual description and personality
      const traits = []
      if (character.personality) {
        traits.push(character.personality)
      }
      if (character.visual_description) {
        traits.push(character.visual_description)
      }
      setCharacterTraits(traits.join('. '))
    }
  }

  const handleExecute = async () => {
    if (!characterName.trim()) {
      setError('Please enter a character name')
      return
    }

    setRunning(true)
    setError(null)
    setResult(null)

    try {
      const character = {
        name: characterName.trim(),
        traits: characterTraits.trim() || 'curious and brave'
      }

      const response = await api.post('/story-tools/story-planner?async_mode=true', {
        character,
        theme,
        target_word_count: targetWordCount,
        max_scenes: maxScenes
      })

      // Async mode: job is queued
      if (response.data.job_id) {
        console.log('Story planning job queued:', response.data.job_id)
        // Navigate to jobs page to see progress
        navigate('/jobs')
        return
      }

      // Sync mode (fallback): display result
      if (response.data.status === 'completed') {
        setResult(response.data.result)
      } else {
        throw new Error(response.data.error || 'Planning failed')
      }
    } catch (err) {
      console.error('Planning error:', err)
      setError(err.response?.data?.detail || err.message)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="story-tool-page">
      <div className="page-header">
        <h2>📝 Story Planner</h2>
        <p className="page-subtitle">Create a structured story outline with scenes and illustration prompts</p>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="tool-form">
        <div className="form-section">
          <h3>Character</h3>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={useExistingCharacter}
                onChange={(e) => {
                  setUseExistingCharacter(e.target.checked)
                  if (!e.target.checked) {
                    setSelectedCharacterId('')
                    setCharacterName('')
                    setCharacterTraits('')
                  }
                }}
                disabled={running}
              />
              <span>Use existing character</span>
            </label>
          </div>

          {useExistingCharacter && (
            <div className="form-group">
              <label htmlFor="character-select">Select Character *</label>
              <select
                id="character-select"
                value={selectedCharacterId}
                onChange={(e) => handleCharacterSelect(e.target.value)}
                disabled={running}
              >
                <option value="">-- Select a character --</option>
                {characters.map(char => (
                  <option key={char.character_id} value={char.character_id}>
                    {char.name}
                  </option>
                ))}
              </select>
              {characters.length === 0 && (
                <small style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                  No characters available. Create one in the Characters section first.
                </small>
              )}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="character-name">Character Name *</label>
            <input
              type="text"
              id="character-name"
              value={characterName}
              onChange={(e) => setCharacterName(e.target.value)}
              placeholder="e.g., Luna, Max, Zara"
              disabled={running || useExistingCharacter}
            />
          </div>

          <div className="form-group">
            <label htmlFor="character-traits">Character Traits</label>
            <textarea
              id="character-traits"
              value={characterTraits}
              onChange={(e) => setCharacterTraits(e.target.value)}
              placeholder="e.g., curious, brave, loves adventure"
              rows="3"
              disabled={running || useExistingCharacter}
            />
            <small>Optional - describes your character's personality</small>
          </div>
        </div>

        <div className="form-section">
          <h3>Story Settings</h3>

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

          <div className="form-group">
            <label htmlFor="word-count">
              Target Word Count: {targetWordCount}
            </label>
            <input
              type="range"
              id="word-count"
              min="300"
              max="2000"
              step="100"
              value={targetWordCount}
              onChange={(e) => setTargetWordCount(parseInt(e.target.value))}
              disabled={running}
            />
            <div className="range-labels">
              <span>300</span>
              <span>2000</span>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="max-scenes">
              Number of Scenes: {maxScenes}
            </label>
            <input
              type="range"
              id="max-scenes"
              min="3"
              max="10"
              step="1"
              value={maxScenes}
              onChange={(e) => setMaxScenes(parseInt(e.target.value))}
              disabled={running}
            />
            <div className="range-labels">
              <span>3</span>
              <span>10</span>
            </div>
          </div>
        </div>

        <button
          className="execute-button"
          onClick={handleExecute}
          disabled={running || !characterName.trim()}
        >
          {running ? 'Planning Story...' : 'Create Story Outline'}
        </button>
      </div>

      {result && (
        <div className="tool-result">
          <h3>Story Outline</h3>

          <div className="result-section">
            <h4>Title</h4>
            <p className="story-title">{result.story_outline?.title || 'Untitled'}</p>
          </div>

          <div className="result-section">
            <h4>Scenes ({result.story_outline?.scenes?.length || 0})</h4>
            <div className="scenes-list">
              {result.story_outline?.scenes?.map((scene, idx) => (
                <div key={idx} className="scene-card">
                  <h5>Scene {scene.scene_number}</h5>
                  <p><strong>Description:</strong> {scene.description}</p>
                  <p><strong>Illustration Prompt:</strong> {scene.illustration_prompt}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="result-actions">
            <button
              className="secondary-button"
              onClick={() => navigate('/story-tools/story-writer', {
                state: { outline: result.story_outline, character: { name: characterName, traits: characterTraits }, theme }
              })}
            >
              Continue to Story Writer →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default StoryPlannerPage
