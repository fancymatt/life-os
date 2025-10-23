import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'
import './ToolConfigPage.css'

/**
 * Tool Configuration Page
 *
 * Allows editing non-preset tools (analyzers, generators, agents):
 * - View and edit prompt templates
 * - Change model selection
 * - Adjust temperature
 * - Test with uploaded images
 */
function ToolConfigPage() {
  const { type } = useParams() // For tools like "character-appearance"
  const navigate = useNavigate()
  const location = window.location

  // Convert URL param to tool name (e.g., "character-appearance" -> "character_appearance_analyzer")
  // If no type param, extract from pathname
  let toolType = type
  if (!toolType) {
    const pathMatch = location.pathname.match(/\/analyzers\/([^/]+)/)
    if (pathMatch) {
      toolType = pathMatch[1]
    }
  }

  const toolName = toolType ? `${toolType.replace(/-/g, '_')}_analyzer` : null

  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  // Editable state
  const [editedTemplate, setEditedTemplate] = useState('')
  const [editedModel, setEditedModel] = useState('')
  const [editedTemperature, setEditedTemperature] = useState(0.7)

  // Run tool state
  const [testImage, setTestImage] = useState(null)
  const [testImagePreview, setTestImagePreview] = useState(null)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState(null)

  // Available models
  const [availableModels, setAvailableModels] = useState({})

  useEffect(() => {
    fetchConfig()
    fetchAvailableModels()
  }, [toolName])

  const fetchConfig = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get(`/tool-configs/tools/${toolName}`)
      setConfig(response.data)
      setEditedTemplate(response.data.template || '')
      setEditedModel(response.data.model || '')
      setEditedTemperature(response.data.temperature || 0.7)
    } catch (err) {
      console.error('Failed to fetch tool config:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load tool configuration')
    } finally {
      setLoading(false)
    }
  }

  const fetchAvailableModels = async () => {
    try {
      const response = await api.get('/tool-configs/models')
      setAvailableModels(response.data)
    } catch (err) {
      console.error('Failed to fetch available models:', err)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)

    try {
      // Use fixed temperature if model requires it, otherwise use edited value
      const finalTemperature = hasFixedTemperature
        ? temperatureRestrictions.fixed
        : editedTemperature

      await api.put(`/tool-configs/tools/${toolName}`, {
        model: editedModel,
        temperature: finalTemperature,
        template: editedTemplate
      })

      // Refresh config
      await fetchConfig()

      alert('Tool configuration saved successfully')
    } catch (err) {
      console.error('Failed to save config:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to save configuration')
    } finally {
      setSaving(false)
    }
  }

  // Check if selected model has temperature restrictions
  const selectedModelInfo = Object.values(availableModels)
    .flat()
    .find(m => m.id === editedModel)

  const temperatureRestrictions = selectedModelInfo?.temperature_restrictions
  const hasFixedTemperature = temperatureRestrictions?.fixed !== undefined

  const handleReset = () => {
    setEditedTemplate(config.template || '')
    setEditedModel(config.model || '')
    setEditedTemperature(config.temperature || 0.7)
    setError(null)
  }

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setTestImage(file)

      // Create preview URL
      const reader = new FileReader()
      reader.onloadend = () => {
        setTestImagePreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleTest = async () => {
    if (!testImage) {
      alert('Please select an image to test')
      return
    }

    setTesting(true)
    setTestResult(null)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('image', testImage)

      const response = await api.post(`/tool-configs/tools/${toolName}/test?async_mode=true`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      const data = response.data

      // Async mode: job queued, SSE will update task panel automatically
      if (data.job_id) {
        console.log('✅ Analysis queued:', data.job_id)
        setTesting(false)
        // Clear the test image to allow another test
        setTestImage(null)
        setTestImagePreview(null)
        setError(null)
        // SSE stream will automatically add job to task panel
        return
      }

      // Sync mode (fallback - shouldn't happen with async_mode=true)
      setTestResult(data.result)
      setTesting(false)
    } catch (err) {
      console.error('Test failed:', err)
      setError(err.response?.data?.detail || err.message || 'Test execution failed')
      setTesting(false)
    }
  }

  if (loading) {
    return (
      <div className="tool-config-page">
        <div className="loading">Loading tool configuration...</div>
      </div>
    )
  }

  if (!config) {
    return (
      <div className="tool-config-page">
        <div className="error">Tool not found</div>
      </div>
    )
  }

  const hasChanges =
    editedTemplate !== (config.template || '') ||
    editedModel !== (config.model || '') ||
    editedTemperature !== (config.temperature || 0.7)

  return (
    <div className="tool-config-page">
      {/* Header */}
      <div className="tool-config-header">
        <button className="back-button" onClick={() => navigate('/tools/analyzers')}>
          ← Back to Tools
        </button>
        <div>
          <h1>{config.display_name}</h1>
          {config.description && (
            <p className="tool-description">{config.description}</p>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Configuration Section */}
      <div className="tool-config-content">
        <div className="config-section">
          <h2>Configuration</h2>

          {/* Model Selection */}
          <div className="form-group">
            <label htmlFor="model">Model</label>
            <select
              id="model"
              value={editedModel}
              onChange={(e) => setEditedModel(e.target.value)}
              disabled={saving}
            >
              {Object.entries(availableModels).map(([provider, models]) => (
                <optgroup key={provider} label={provider.toUpperCase()}>
                  {models.map(model => (
                    <option key={model.id} value={model.id}>
                      {model.name}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          {/* Temperature */}
          <div className="form-group">
            <label htmlFor="temperature">
              Temperature: {hasFixedTemperature
                ? `${temperatureRestrictions.fixed.toFixed(2)} (fixed for ${selectedModelInfo?.name})`
                : editedTemperature.toFixed(2)
              }
            </label>
            <input
              type="range"
              id="temperature"
              min="0"
              max="1"
              step="0.1"
              value={hasFixedTemperature ? temperatureRestrictions.fixed : editedTemperature}
              onChange={(e) => setEditedTemperature(parseFloat(e.target.value))}
              disabled={saving || hasFixedTemperature}
            />
            <small>
              {hasFixedTemperature
                ? (temperatureRestrictions.note || 'This model requires a fixed temperature value')
                : 'Higher values = more creative/random, lower values = more deterministic'
              }
            </small>
          </div>

          {/* Prompt Template */}
          {config.has_template && (
            <div className="form-group template-group">
              <label htmlFor="template">Prompt Template</label>
              <textarea
                id="template"
                value={editedTemplate}
                onChange={(e) => setEditedTemplate(e.target.value)}
                disabled={saving}
                rows={20}
                spellCheck={false}
              />
            </div>
          )}

          {/* Action Buttons */}
          <div className="config-actions">
            <button
              onClick={handleReset}
              disabled={saving || !hasChanges}
              className="secondary-button"
            >
              Reset Changes
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !hasChanges}
              className="primary-button"
            >
              {saving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </div>

        {/* Run Tool Section */}
        <div className="test-section">
          <h2>Run Tool</h2>

          <div className="test-upload">
            <label htmlFor="test-image">Upload Image</label>
            <input
              type="file"
              id="test-image"
              accept="image/*"
              onChange={handleImageChange}
              disabled={testing}
            />

            {testImagePreview && (
              <div className="test-image-preview">
                <img src={testImagePreview} alt="Preview" />
              </div>
            )}

            <button
              onClick={handleTest}
              disabled={testing || !testImage}
              className="primary-button"
            >
              {testing ? 'Running...' : 'Run Analysis'}
            </button>
          </div>

          {testResult && (
            <div className="test-results">
              <h3>Results</h3>
              <pre>{JSON.stringify(testResult, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ToolConfigPage
