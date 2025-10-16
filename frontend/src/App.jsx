import { useState, useEffect } from 'react'
import './App.css'
import { useAuth } from './contexts/AuthContext'
import Login from './components/Login'
import OutfitAnalyzer from './OutfitAnalyzer'
import GenericAnalyzer from './GenericAnalyzer'
import ModularGenerator from './ModularGenerator'
import ComprehensiveAnalyzer from './ComprehensiveAnalyzer'
import TaskManager from './TaskManager'
import Gallery from './Gallery'
import Composer from './Composer'
import api from './api/client'

function App() {
  const { user, loading: authLoading, logout, isAuthenticated } = useAuth()
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showOutfitAnalyzer, setShowOutfitAnalyzer] = useState(false)
  const [activeAnalyzer, setActiveAnalyzer] = useState(null)
  const [showModularGenerator, setShowModularGenerator] = useState(false)
  const [showComprehensiveAnalyzer, setShowComprehensiveAnalyzer] = useState(false)
  const [showGallery, setShowGallery] = useState(false)
  const [showComposer, setShowComposer] = useState(false)

  useEffect(() => {
    // Only fetch tools if authenticated
    if (!isAuthenticated) {
      setLoading(false)
      return
    }

    api.get('/tools')
      .then(res => {
        setTools(res.data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message)
        setLoading(false)
      })
  }, [isAuthenticated])

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div className="container">
        <h1>AI-Studio Tools</h1>
        <p>Loading...</p>
      </div>
    )
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <Login />
  }

  // Show loading while fetching tools
  if (loading) {
    return (
      <div className="container">
        <h1>AI-Studio Tools</h1>
        <p>Loading...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container">
        <h1>AI-Studio Tools</h1>
        <p className="error">Error: {error}</p>
      </div>
    )
  }

  // Group tools by category
  const analyzers = tools.filter(t => t.category === 'analyzer')
  const generators = tools.filter(t => t.category === 'generator')

  // If Composer is active, show it full-screen
  if (showComposer) {
    return (
      <>
        <Composer />
        <button
          className="composer-back-button"
          onClick={() => setShowComposer(false)}
        >
          ← Back to Tools
        </button>
        <TaskManager />
      </>
    )
  }

  return (
    <>
      <div className="container">
        <header>
          <div className="header-content">
            <div>
              <h1>🎨 AI-Studio</h1>
              <p className="subtitle">Available Tools</p>
            </div>
            <div className="header-actions">
              <button className="gallery-button" onClick={() => setShowGallery(true)}>
                🖼️ Gallery
              </button>
              <span className="user-info">👤 {user?.username}</span>
              <button className="logout-button" onClick={logout}>
                Logout
              </button>
            </div>
          </div>
        </header>

        <section>
          <h2>📊 Analyzers ({analyzers.length})</h2>
          <div className="tools-list">
            {analyzers.map(tool => (
              <div
                key={tool.name}
                className="tool-card clickable"
                onClick={() => {
                  if (tool.name === 'outfit') {
                    setShowOutfitAnalyzer(true)
                  } else if (tool.name === 'comprehensive') {
                    setShowComprehensiveAnalyzer(true)
                  } else {
                    setActiveAnalyzer(tool.name)
                  }
                }}
              >
                <h3>{tool.name}</h3>
                <p className="description">{tool.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2>🎨 Generators ({generators.length + 2})</h2>
          <div className="tools-list">
            {/* Preset Composer - NEW drag-and-drop interface */}
            <div
              className="tool-card clickable featured"
              onClick={() => setShowComposer(true)}
            >
              <h3>🎭 Preset Composer</h3>
              <p className="description">Drag and drop presets to build stunning compositions. Stack presets, see live previews, and cache your favorite combinations.</p>
              <span className="new-badge">NEW</span>
            </div>

            {/* Modular Generator - Frontend Workflow */}
            <div
              className="tool-card clickable"
              onClick={() => setShowModularGenerator(true)}
            >
              <h3>Modular</h3>
              <p className="description">Mix and match presets from different categories to generate custom images</p>
            </div>
            {generators.map(tool => (
              <div key={tool.name} className="tool-card">
                <h3>{tool.name}</h3>
                <p className="description">{tool.description}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
      {showOutfitAnalyzer && <OutfitAnalyzer onClose={() => setShowOutfitAnalyzer(false)} />}
      {activeAnalyzer && (
        <GenericAnalyzer
          analyzerType={activeAnalyzer}
          onClose={() => setActiveAnalyzer(null)}
        />
      )}
      {showModularGenerator && <ModularGenerator onClose={() => setShowModularGenerator(false)} />}
      {showComprehensiveAnalyzer && <ComprehensiveAnalyzer onClose={() => setShowComprehensiveAnalyzer(false)} />}
      {showGallery && <Gallery onClose={() => setShowGallery(false)} />}

      {/* Task Manager - Always visible */}
      <TaskManager />
    </>
  )
}

export default App
