import { useState, useEffect } from 'react'
import './StoryWorkflowPage.css'
import api from '../api/client'

function StoryWorkflowPage() {
  const [formData, setFormData] = useState({
    characterName: '',
    characterAppearance: '',
    characterPersonality: '',
    storyType: 'transformation',  // 'normal' or 'transformation'
    // Story parameter preset IDs
    themeId: 'modern_magic',
    audienceId: 'adult',
    proseStyleId: 'humorous',
    // Agent configuration IDs
    plannerConfigId: 'default',
    writerConfigId: 'default',
    illustratorConfigId: 'default',
    // Story settings
    targetScenes: 5,
    artStyle: 'realistic',
    maxIllustrations: 5,
    // Transformation-specific fields
    transformationType: 'creature',  // 'alteration' or 'creature'
    transformationTarget: ''  // Description of alteration or creature name
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [characters, setCharacters] = useState([])
  const [selectedCharacterId, setSelectedCharacterId] = useState('')
  const [artStyles, setArtStyles] = useState([])
  const [selectedArtStyleId, setSelectedArtStyleId] = useState('realistic')
  const [outfits, setOutfits] = useState([])
  const [selectedOutfitId, setSelectedOutfitId] = useState('')
  const [hairStyles, setHairStyles] = useState([])
  const [selectedHairStyleId, setSelectedHairStyleId] = useState('')
  const [hairColors, setHairColors] = useState([])
  const [selectedHairColorId, setSelectedHairColorId] = useState('')
  // Story parameter presets
  const [themes, setThemes] = useState([])
  const [audiences, setAudiences] = useState([])
  const [proseStyles, setProseStyles] = useState([])
  // Agent configurations
  const [plannerConfigs, setPlannerConfigs] = useState([])
  const [writerConfigs, setWriterConfigs] = useState([])
  const [illustratorConfigs, setIllustratorConfigs] = useState([])

  // Fetch characters and presets on mount
  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const response = await api.get('/characters/')
        setCharacters(response.data.characters || [])
      } catch (err) {
        console.error('Failed to fetch characters:', err)
      }
    }

    const fetchArtStyles = async () => {
      try {
        const response = await api.get('/presets/art_styles')
        setArtStyles(response.data.presets || [])
      } catch (err) {
        console.error('Failed to fetch art styles:', err)
      }
    }

    const fetchOutfits = async () => {
      try {
        const response = await api.get('/presets/outfits')
        setOutfits(response.data.presets || [])
      } catch (err) {
        console.error('Failed to fetch outfits:', err)
      }
    }

    const fetchHairStyles = async () => {
      try {
        const response = await api.get('/presets/hair_styles')
        setHairStyles(response.data.presets || [])
      } catch (err) {
        console.error('Failed to fetch hair styles:', err)
      }
    }

    const fetchHairColors = async () => {
      try {
        const response = await api.get('/presets/hair_colors')
        setHairColors(response.data.presets || [])
      } catch (err) {
        console.error('Failed to fetch hair colors:', err)
      }
    }

    const fetchThemes = async () => {
      try {
        const response = await api.get('/presets/story_themes')
        setThemes(response.data.presets || [])
      } catch (err) {
        console.error('Failed to fetch themes:', err)
      }
    }

    const fetchAudiences = async () => {
      try {
        const response = await api.get('/presets/story_audiences')
        setAudiences(response.data.presets || [])
      } catch (err) {
        console.error('Failed to fetch audiences:', err)
      }
    }

    const fetchProseStyles = async () => {
      try {
        const response = await api.get('/presets/story_prose_styles')
        setProseStyles(response.data.presets || [])
      } catch (err) {
        console.error('Failed to fetch prose styles:', err)
      }
    }

    const fetchPlannerConfigs = async () => {
      try {
        const response = await api.get('/configs/agent_configs/story_planner')
        setPlannerConfigs(response.data.configs || [])
      } catch (err) {
        console.error('Failed to fetch planner configs:', err)
      }
    }

    const fetchWriterConfigs = async () => {
      try {
        const response = await api.get('/configs/agent_configs/story_writer')
        setWriterConfigs(response.data.configs || [])
      } catch (err) {
        console.error('Failed to fetch writer configs:', err)
      }
    }

    const fetchIllustratorConfigs = async () => {
      try {
        const response = await api.get('/configs/agent_configs/story_illustrator')
        setIllustratorConfigs(response.data.configs || [])
      } catch (err) {
        console.error('Failed to fetch illustrator configs:', err)
      }
    }

    fetchCharacters()
    fetchArtStyles()
    fetchOutfits()
    fetchHairStyles()
    fetchHairColors()
    fetchThemes()
    fetchAudiences()
    fetchProseStyles()
    fetchPlannerConfigs()
    fetchWriterConfigs()
    fetchIllustratorConfigs()
  }, [])

  // Handle character selection
  const handleCharacterSelect = (characterId) => {
    setSelectedCharacterId(characterId)

    if (!characterId) {
      setFormData(prev => ({
        ...prev,
        characterName: '',
        characterAppearance: '',
        characterPersonality: ''
      }))
      return
    }

    const character = characters.find(c => c.character_id === characterId)
    if (character) {
      setFormData(prev => ({
        ...prev,
        characterName: character.name,
        characterAppearance: character.visual_description || '',
        characterPersonality: character.personality || ''
      }))
    }
  }

  // Handle art style selection
  const handleArtStyleSelect = (presetId) => {
    setSelectedArtStyleId(presetId)

    if (!presetId) {
      setFormData(prev => ({
        ...prev,
        artStyle: ''
      }))
      return
    }

    // Handle "realistic" special case
    if (presetId === 'realistic') {
      setFormData(prev => ({
        ...prev,
        artStyle: 'realistic'
      }))
      return
    }

    const artStyle = artStyles.find(a => a.preset_id === presetId)
    if (artStyle) {
      // Store the preset name/description for the workflow
      setFormData(prev => ({
        ...prev,
        artStyle: artStyle.display_name || artStyle.name || presetId
      }))
    }
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    if (!selectedCharacterId || !formData.characterName) {
      setError('Please select a character')
      return
    }

    if (!selectedArtStyleId || !formData.artStyle) {
      setError('Please select an art style')
      return
    }

    if (formData.storyType === 'transformation' && !formData.transformationTarget) {
      setError('Please enter a transformation target')
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
        character_id: selectedCharacterId || undefined,  // Pass character ID for reference image
        story_type: formData.storyType,
        // Story parameter preset IDs
        theme_id: formData.themeId,
        audience_id: formData.audienceId,
        prose_style_id: formData.proseStyleId,
        // Agent configuration IDs
        planner_config_id: formData.plannerConfigId,
        writer_config_id: formData.writerConfigId,
        illustrator_config_id: formData.illustratorConfigId,
        // Story settings
        target_scenes: parseInt(formData.targetScenes),
        art_style: formData.artStyle,
        max_illustrations: parseInt(formData.maxIllustrations),
        // Appearance overrides
        outfit_id: selectedOutfitId || undefined,
        hair_style_id: selectedHairStyleId || undefined,
        hair_color_id: selectedHairColorId || undefined
      }

      // Add transformation parameters if transformation story
      if (formData.storyType === 'transformation') {
        payload.transformation = {
          type: formData.transformationType,
          target: formData.transformationTarget
        }
      }

      const response = await api.post('/workflows/story-generation/execute', payload)

      setSuccess(`Story generation started! Check Job History to track progress and view the completed story.`)

      // Keep all form settings for easy re-submission with similar parameters
      // Only clear the success message after a delay
      setTimeout(() => setSuccess(null), 8000)
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
            <label htmlFor="character-select">Select Character *</label>
            <select
              id="character-select"
              value={selectedCharacterId}
              onChange={(e) => handleCharacterSelect(e.target.value)}
              disabled={submitting}
              required
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

          {formData.characterName && (
            <>
              <div className="form-group">
                <label>Character Name</label>
                <input
                  type="text"
                  value={formData.characterName}
                  disabled
                  style={{ opacity: 0.7, cursor: 'not-allowed' }}
                />
              </div>

              {formData.characterAppearance && (
                <div className="form-group">
                  <label>Appearance</label>
                  <input
                    type="text"
                    value={formData.characterAppearance}
                    disabled
                    style={{ opacity: 0.7, cursor: 'not-allowed' }}
                  />
                </div>
              )}

              {formData.characterPersonality && (
                <div className="form-group">
                  <label>Personality</label>
                  <input
                    type="text"
                    value={formData.characterPersonality}
                    disabled
                    style={{ opacity: 0.7, cursor: 'not-allowed' }}
                  />
                </div>
              )}
            </>
          )}
        </div>

        <div className="form-section">
          <h3>Appearance Overrides</h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            Optional: Select specific outfit, hair style, or hair color to override the character's default appearance
          </p>

          <div className="form-group">
            <label htmlFor="outfit-select">Outfit</label>
            <select
              id="outfit-select"
              value={selectedOutfitId}
              onChange={(e) => setSelectedOutfitId(e.target.value)}
              disabled={submitting}
            >
              <option value="">-- Use character's default --</option>
              {outfits.map(outfit => (
                <option key={outfit.preset_id} value={outfit.preset_id}>
                  {outfit.display_name || outfit.name || outfit.preset_id}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="hair-style-select">Hair Style</label>
              <select
                id="hair-style-select"
                value={selectedHairStyleId}
                onChange={(e) => setSelectedHairStyleId(e.target.value)}
                disabled={submitting}
              >
                <option value="">-- Use character's default --</option>
                {hairStyles.map(style => (
                  <option key={style.preset_id} value={style.preset_id}>
                    {style.display_name || style.name || style.preset_id}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="hair-color-select">Hair Color</label>
              <select
                id="hair-color-select"
                value={selectedHairColorId}
                onChange={(e) => setSelectedHairColorId(e.target.value)}
                disabled={submitting}
              >
                <option value="">-- Use character's default --</option>
                {hairColors.map(color => (
                  <option key={color.preset_id} value={color.preset_id}>
                    {color.display_name || color.name || color.preset_id}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Story Type</h3>
          <div className="form-group">
            <label htmlFor="storyType">Story Type</label>
            <select
              id="storyType"
              value={formData.storyType}
              onChange={(e) => handleChange('storyType', e.target.value)}
              disabled={submitting}
            >
              <option value="normal">Normal Story</option>
              <option value="transformation">Transformation Story</option>
            </select>
          </div>

          {formData.storyType === 'transformation' && (
            <>
              <div className="form-group">
                <label htmlFor="transformationType">Transformation Type</label>
                <select
                  id="transformationType"
                  value={formData.transformationType}
                  onChange={(e) => handleChange('transformationType', e.target.value)}
                  disabled={submitting}
                >
                  <option value="creature">Creature (e.g., panda, dragon)</option>
                  <option value="alteration">Alteration (e.g., dragon scales, big feet)</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="transformationTarget">
                  {formData.transformationType === 'creature'
                    ? 'Creature Name'
                    : 'Alteration Description'}
                </label>
                <input
                  type="text"
                  id="transformationTarget"
                  value={formData.transformationTarget}
                  onChange={(e) => handleChange('transformationTarget', e.target.value)}
                  placeholder={formData.transformationType === 'creature'
                    ? 'e.g., panda, dragon, wolf'
                    : 'e.g., dragon scales and wings, big paws and tail'}
                  disabled={submitting}
                  required={formData.storyType === 'transformation'}
                />
              </div>
            </>
          )}
        </div>

        <div className="form-section">
          <h3>Story Settings</h3>
          <div className="form-group">
            <label htmlFor="theme">Theme</label>
            <select
              id="theme"
              value={formData.themeId}
              onChange={(e) => handleChange('themeId', e.target.value)}
              disabled={submitting}
            >
              {themes.map(theme => (
                <option key={theme.preset_id} value={theme.preset_id}>
                  {theme.display_name || theme.suggested_name || theme.preset_id}
                </option>
              ))}
            </select>
            {themes.length === 0 && (
              <small style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                Loading themes...
              </small>
            )}
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
              <label htmlFor="ageGroup">Target Audience</label>
              <select
                id="ageGroup"
                value={formData.audienceId}
                onChange={(e) => handleChange('audienceId', e.target.value)}
                disabled={submitting}
              >
                {audiences.map(audience => (
                  <option key={audience.preset_id} value={audience.preset_id}>
                    {audience.display_name || audience.suggested_name || audience.preset_id}
                  </option>
                ))}
              </select>
              {audiences.length === 0 && (
                <small style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                  Loading audiences...
                </small>
              )}
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
                value={formData.proseStyleId}
                onChange={(e) => handleChange('proseStyleId', e.target.value)}
                disabled={submitting}
              >
                {proseStyles.map(style => (
                  <option key={style.preset_id} value={style.preset_id}>
                    {style.display_name || style.suggested_name || style.preset_id}
                  </option>
                ))}
              </select>
              {proseStyles.length === 0 && (
                <small style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                  Loading prose styles...
                </small>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="artStyle">Visual Style (Rendering) *</label>
              <select
                id="artStyle"
                value={selectedArtStyleId}
                onChange={(e) => handleArtStyleSelect(e.target.value)}
                disabled={submitting}
                required
              >
                <option value="">-- Select a visual style --</option>
                <option value="realistic">Realistic (Photographic)</option>
                {artStyles.map(style => (
                  <option key={style.preset_id} value={style.preset_id}>
                    {style.display_name || style.name || style.preset_id}
                  </option>
                ))}
              </select>
              {artStyles.length === 0 ? (
                <small style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                  No art styles available. Create one in the Art Styles section first.
                </small>
              ) : (
                <small style={{ color: 'rgba(255, 255, 255, 0.7)', display: 'block', marginTop: '0.25rem' }}>
                  How images are rendered (cartoon, watercolor, realistic, etc.)
                </small>
              )}
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

        <div className="form-section">
          <h3>Agent Configurations</h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            Control HOW the AI creates your story - choose different approaches for planning, writing, and illustration
          </p>

          <div className="form-group">
            <label htmlFor="plannerConfig">Story Planning Approach</label>
            <select
              id="plannerConfig"
              value={formData.plannerConfigId}
              onChange={(e) => handleChange('plannerConfigId', e.target.value)}
              disabled={submitting}
            >
              {plannerConfigs.map(config => (
                <option key={config.config_id} value={config.config_id}>
                  {config.display_name || config.config_id}
                </option>
              ))}
            </select>
            {plannerConfigs.length === 0 && (
              <small style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                Loading planner configurations...
              </small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="writerConfig">Writing Style Engine</label>
            <select
              id="writerConfig"
              value={formData.writerConfigId}
              onChange={(e) => handleChange('writerConfigId', e.target.value)}
              disabled={submitting}
            >
              {writerConfigs.map(config => (
                <option key={config.config_id} value={config.config_id}>
                  {config.display_name || config.config_id}
                </option>
              ))}
            </select>
            {writerConfigs.length === 0 && (
              <small style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                Loading writer configurations...
              </small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="illustratorConfig">Cinematography (Framing & Lighting)</label>
            <select
              id="illustratorConfig"
              value={formData.illustratorConfigId}
              onChange={(e) => handleChange('illustratorConfigId', e.target.value)}
              disabled={submitting}
            >
              {illustratorConfigs.map(config => (
                <option key={config.config_id} value={config.config_id}>
                  {config.display_name || config.config_id}
                </option>
              ))}
            </select>
            {illustratorConfigs.length === 0 ? (
              <small style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                Loading illustrator configurations...
              </small>
            ) : (
              <small style={{ color: 'rgba(255, 255, 255, 0.7)', display: 'block', marginTop: '0.25rem' }}>
                How scenes are composed and lit (cinematic, storybook, etc.)
              </small>
            )}
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <button
          type="submit"
          className="generate-button"
          disabled={submitting || !selectedCharacterId || !selectedArtStyleId}
        >
          {submitting ? 'Generating Story...' : 'Generate Story'}
        </button>
      </form>
    </div>
  )
}

export default StoryWorkflowPage
