import { useState } from 'react'
import './StoryWorkflowPage.css'
import api from '../api/client'

function StoryWorkflowPage() {
  const [formData, setFormData] = useState({
    characterName: '',
    characterAppearance: '',
    characterPersonality: '',
    theme: 'adventure',
    targetScenes: 5,
    ageGroup: 'children',
    proseStyle: 'descriptive',
    artStyle: 'digital_art',
    maxIllustrations: 5
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    if (!formData.characterName) {
      setError('Character name is required')
      return
    }

    setSubmitting(true)

    try {
      const payload = {
        character: {
          name: formData.characterName,
          appearance: formData.characterAppearance || undefined,
          personality: formData.characterPersonality || undefined
        },
        theme: formData.theme,
        target_scenes: parseInt(formData.targetScenes),
        age_group: formData.ageGroup,
        prose_style: formData.proseStyle,
        art_style: formData.artStyle,
        max_illustrations: parseInt(formData.maxIllustrations)
      }

      const response = await api.post('/workflows/story-generation/execute', payload)

      setSuccess(`Story generation started! Job ID: ${response.data.workflow_execution_id || response.data.job_id}. Check the Task Manager (⚡) to track progress.`)

      // Reset form
      setFormData({
        characterName: '',
        characterAppearance: '',
        characterPersonality: '',
        theme: 'adventure',
        targetScenes: 5,
        ageGroup: 'children',
        proseStyle: 'descriptive',
        artStyle: 'digital_art',
        maxIllustrations: 5
      })

      setTimeout(() => setSuccess(null), 5000)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="story-workflow-page">
      <div className="story-header">
        <h2>📖 Story Generator</h2>
        <p className="story-subtitle">
          Create illustrated stories with AI-generated text and images
        </p>
      </div>

      <div className="story-info">
        <div className="info-box">
          <h3>How it works</h3>
          <ol>
            <li><strong>Story Planning:</strong> AI creates an outline based on your character and theme</li>
            <li><strong>Story Writing:</strong> AI writes the complete story with your chosen prose style</li>
            <li><strong>Illustration:</strong> AI generates images for key scenes in your chosen art style</li>
          </ol>
          <p className="info-note">⏱️ Generation typically takes 1-3 minutes</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="story-form">
        <div className="form-section">
          <h3>Character</h3>
          <div className="form-group">
            <label htmlFor="characterName">Character Name *</label>
            <input
              type="text"
              id="characterName"
              value={formData.characterName}
              onChange={(e) => handleChange('characterName', e.target.value)}
              placeholder="e.g., Luna, Milo, Detective Chen"
              disabled={submitting}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="characterAppearance">Appearance (optional)</label>
            <input
              type="text"
              id="characterAppearance"
              value={formData.characterAppearance}
              onChange={(e) => handleChange('characterAppearance', e.target.value)}
              placeholder="e.g., young girl with curly brown hair and green eyes"
              disabled={submitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="characterPersonality">Personality (optional)</label>
            <input
              type="text"
              id="characterPersonality"
              value={formData.characterPersonality}
              onChange={(e) => handleChange('characterPersonality', e.target.value)}
              placeholder="e.g., curious and brave"
              disabled={submitting}
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Story Settings</h3>
          <div className="form-group">
            <label htmlFor="theme">Theme</label>
            <select
              id="theme"
              value={formData.theme}
              onChange={(e) => handleChange('theme', e.target.value)}
              disabled={submitting}
            >
              <option value="adventure">Adventure</option>
              <option value="mystery">Mystery</option>
              <option value="friendship">Friendship</option>
              <option value="fantasy">Fantasy</option>
              <option value="science_fiction">Science Fiction</option>
              <option value="comedy">Comedy</option>
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="targetScenes">Number of Scenes</label>
              <input
                type="number"
                id="targetScenes"
                min="3"
                max="10"
                value={formData.targetScenes}
                onChange={(e) => handleChange('targetScenes', e.target.value)}
                disabled={submitting}
              />
            </div>

            <div className="form-group">
              <label htmlFor="ageGroup">Age Group</label>
              <select
                id="ageGroup"
                value={formData.ageGroup}
                onChange={(e) => handleChange('ageGroup', e.target.value)}
                disabled={submitting}
              >
                <option value="children">Children</option>
                <option value="young_adult">Young Adult</option>
                <option value="adult">Adult</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Style</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="proseStyle">Prose Style</label>
              <select
                id="proseStyle"
                value={formData.proseStyle}
                onChange={(e) => handleChange('proseStyle', e.target.value)}
                disabled={submitting}
              >
                <option value="descriptive">Descriptive</option>
                <option value="concise">Concise</option>
                <option value="poetic">Poetic</option>
                <option value="humorous">Humorous</option>
                <option value="simple">Simple</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="artStyle">Art Style</label>
              <select
                id="artStyle"
                value={formData.artStyle}
                onChange={(e) => handleChange('artStyle', e.target.value)}
                disabled={submitting}
              >
                <option value="digital_art">Digital Art</option>
                <option value="watercolor">Watercolor</option>
                <option value="cartoon">Cartoon</option>
                <option value="sketch">Sketch</option>
                <option value="realistic">Realistic</option>
                <option value="anime">Anime</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="maxIllustrations">Number of Illustrations</label>
            <input
              type="number"
              id="maxIllustrations"
              min="1"
              max="10"
              value={formData.maxIllustrations}
              onChange={(e) => handleChange('maxIllustrations', e.target.value)}
              disabled={submitting}
            />
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <button
          type="submit"
          className="generate-button"
          disabled={submitting || !formData.characterName}
        >
          {submitting ? 'Generating Story...' : 'Generate Story'}
        </button>
      </form>
    </div>
  )
}

export default StoryWorkflowPage
