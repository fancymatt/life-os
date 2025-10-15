import { useState } from 'react'
import './OutfitAnalyzer.css' // Reuse the same styles

function ComprehensiveAnalyzer({ onClose }) {
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [error, setError] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [selectedAnalyses, setSelectedAnalyses] = useState({
    outfit: true,
    visual_style: true,
    hair_style: true,
    hair_color: true,
    makeup: true,
    accessories: true,
    art_style: false,      // Default unchecked
    expression: false      // Default unchecked
  })

  const analysisTypes = [
    { key: 'outfit', label: 'Outfit' },
    { key: 'visual_style', label: 'Photograph Composition' },
    { key: 'hair_style', label: 'Hair Style' },
    { key: 'hair_color', label: 'Hair Color' },
    { key: 'makeup', label: 'Makeup' },
    { key: 'accessories', label: 'Accessories' },
    { key: 'art_style', label: 'Art Style' },
    { key: 'expression', label: 'Expression' }
  ]

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    setImageFile(file)
    setError(null)

    const reader = new FileReader()
    reader.onloadend = () => {
      setImagePreview(reader.result)
    }
    reader.readAsDataURL(file)
  }

  const handleToggleAnalysis = (key) => {
    setSelectedAnalyses(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  const handleAnalyze = async () => {
    if (!imageFile) {
      setError('Please select an image')
      return
    }

    // Check if at least one analysis is selected
    const selectedCount = Object.values(selectedAnalyses).filter(Boolean).length
    if (selectedCount === 0) {
      setError('Please select at least one analysis type')
      return
    }

    setAnalyzing(true)
    setError(null)

    const reader = new FileReader()
    reader.onloadend = async () => {
      try {
        const base64Data = reader.result.split(',')[1]

        const response = await fetch('/api/analyze/comprehensive', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image: {
              image_data: base64Data
            },
            save_as_preset: true,
            selected_analyses: selectedAnalyses
          })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Analysis failed')
        }

        const data = await response.json()

        if (data.status === 'failed') {
          throw new Error(data.error || 'Analysis failed')
        }

        setAnalysisResult(data.result)
        setAnalyzing(false)
      } catch (err) {
        console.error('Analysis error:', err)
        setError(err.message)
        setAnalyzing(false)
      }
    }

    reader.onerror = () => {
      setError('Failed to read image file')
      setAnalyzing(false)
    }

    reader.readAsDataURL(imageFile)
  }

  const handleReset = () => {
    setImageFile(null)
    setImagePreview(null)
    setAnalysisResult(null)
    setError(null)
    setSelectedAnalyses({
      outfit: true,
      visual_style: true,
      hair_style: true,
      hair_color: true,
      makeup: true,
      accessories: true,
      art_style: false,
      expression: false
    })
  }

  if (analysisResult) {
    const createdPresets = analysisResult.created_presets || []

    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>Comprehensive Analysis Complete</h2>
            <button className="close-button" onClick={onClose}>×</button>
          </div>

          <div className="modal-body">
            <div className="success-message">
              <h3>{createdPresets.length} Preset{createdPresets.length !== 1 ? 's' : ''} Created Successfully!</h3>
              <p>All analyses have been saved with AI-generated names</p>
            </div>

            <div className="comprehensive-results">
              <h3>Presets Created:</h3>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {createdPresets.map((preset, idx) => (
                  <li key={idx}>✓ {preset.name} ({preset.type})</li>
                ))}
              </ul>
            </div>

            <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
              <button className="analyze-button" onClick={handleReset} style={{ flex: 1 }}>
                Analyze Another
              </button>
              <button className="done-button" onClick={onClose} style={{ flex: 1 }}>
                Done
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Comprehensive Analyzer</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <p style={{ marginBottom: '1.5rem', color: '#6b7280' }}>
            Select which analyses to run. Each will create a preset with an AI-generated name.
          </p>

          <div
            className={`drop-zone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {imagePreview ? (
              <div className="image-preview">
                <img src={imagePreview} alt="Preview" />
                <button
                  className="remove-image"
                  onClick={() => {
                    setImageFile(null)
                    setImagePreview(null)
                  }}
                >
                  Remove
                </button>
              </div>
            ) : (
              <div className="drop-zone-content">
                <p className="drop-zone-text">
                  Drag and drop an image here, or click to select
                </p>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileInput}
                  className="file-input"
                  id="file-input"
                />
                <label htmlFor="file-input" className="file-input-label">
                  Choose File
                </label>
              </div>
            )}
          </div>

          <div className="form-group">
            <label>Select Analyses to Run:</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '0.5rem' }}>
              {analysisTypes.map(({ key, label }) => (
                <label key={key} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={selectedAnalyses[key]}
                    onChange={() => handleToggleAnalysis(key)}
                    disabled={analyzing}
                    style={{ marginRight: '0.5rem' }}
                  />
                  <span>{label}</span>
                </label>
              ))}
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={analyzing || !imageFile}
            style={{ width: '100%' }}
          >
            {analyzing ? 'Analyzing (this may take a while)...' : 'Run Selected Analyses'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ComprehensiveAnalyzer
