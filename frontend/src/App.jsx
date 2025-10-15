import { useState, useEffect } from 'react'
import './App.css'
import OutfitAnalyzer from './OutfitAnalyzer'

function App() {
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showOutfitAnalyzer, setShowOutfitAnalyzer] = useState(false)

  useEffect(() => {
    fetch('/api/tools')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch tools')
        return res.json()
      })
      .then(data => {
        setTools(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

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

  return (
    <>
      <div className="container">
        <header>
          <h1>🎨 AI-Studio</h1>
          <p className="subtitle">Available Tools</p>
        </header>

        <section>
          <h2>📊 Analyzers ({analyzers.length})</h2>
          <div className="tools-list">
            {analyzers.map(tool => (
              <div
                key={tool.name}
                className={`tool-card ${tool.name === 'outfit' ? 'clickable' : ''}`}
                onClick={() => {
                  if (tool.name === 'outfit') {
                    setShowOutfitAnalyzer(true)
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
          <h2>🎨 Generators ({generators.length})</h2>
          <div className="tools-list">
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
    </>
  )
}

export default App
