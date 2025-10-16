import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import './Dashboard.css'

function Dashboard() {
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/tools')
      .then(res => {
        setTools(res.data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="dashboard">
        <h1>Dashboard</h1>
        <p>Loading tools...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard">
        <h1>Dashboard</h1>
        <p className="error">Error: {error}</p>
      </div>
    )
  }

  // Group tools by category
  const analyzers = tools.filter(t => t.category === 'analyzer')
  const generators = tools.filter(t => t.category === 'generator')

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🎨 Dashboard</h1>
        <p className="subtitle">Welcome to Life-OS AI Studio</p>
      </header>

      {/* Featured Tools */}
      <section className="featured-section">
        <h2>✨ Featured</h2>
        <div className="featured-grid">
          <div
            className="featured-card composer"
            onClick={() => navigate('/composer')}
          >
            <div className="featured-icon">🎭</div>
            <h3>Preset Composer</h3>
            <p>Drag and drop presets to build stunning compositions</p>
            <span className="featured-badge">Most Popular</span>
          </div>

          <div
            className="featured-card workflow"
            onClick={() => navigate('/workflows/story')}
          >
            <div className="featured-icon">📖</div>
            <h3>Story Generator</h3>
            <p>Create illustrated stories with AI workflows</p>
            <span className="featured-badge new">New</span>
          </div>

          <div
            className="featured-card generator"
            onClick={() => navigate('/generators/modular')}
          >
            <div className="featured-icon">🎨</div>
            <h3>Modular Generator</h3>
            <p>Mix and match presets for custom images</p>
          </div>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="stats-section">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>{analyzers.length}</h3>
            <p>Analyzers</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✨</div>
          <div className="stat-content">
            <h3>{generators.length + 2}</h3>
            <p>Generators</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚙️</div>
          <div className="stat-content">
            <h3>1</h3>
            <p>Workflows</p>
          </div>
        </div>
      </section>

      {/* Analyzers */}
      <section className="tools-section">
        <h2>📊 Analyzers</h2>
        <div className="tools-grid">
          {analyzers.map(tool => (
            <div
              key={tool.name}
              className="tool-card"
              onClick={() => {
                if (tool.name === 'outfit') {
                  navigate('/analyzers/outfit')
                } else if (tool.name === 'comprehensive') {
                  navigate('/analyzers/comprehensive')
                } else {
                  navigate(`/analyzers/${tool.name}`)
                }
              }}
            >
              <h3>{tool.name}</h3>
              <p>{tool.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Generators */}
      <section className="tools-section">
        <h2>🎨 Generators</h2>
        <div className="tools-grid">
          {generators.map(tool => (
            <div
              key={tool.name}
              className="tool-card"
              onClick={() => navigate(`/generators/${tool.name}`)}
            >
              <h3>{tool.name}</h3>
              <p>{tool.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default Dashboard
