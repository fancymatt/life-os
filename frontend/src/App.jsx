import { useState, useEffect } from 'react'
import './App.css'
import OutfitAnalyzer from './OutfitAnalyzer'
import GenericAnalyzer from './GenericAnalyzer'
import ModularGenerator from './ModularGenerator'
import ComprehensiveAnalyzer from './ComprehensiveAnalyzer'
import TaskManager from './TaskManager'

function App() {
  const [tools, setTools] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showOutfitAnalyzer, setShowOutfitAnalyzer] = useState(false)
  const [activeAnalyzer, setActiveAnalyzer] = useState(null)
  const [showModularGenerator, setShowModularGenerator] = useState(false)
  const [showComprehensiveAnalyzer, setShowComprehensiveAnalyzer] = useState(false)

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
          <h2>🎨 Generators ({generators.length + 1})</h2>
          <div className="tools-list">
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

      {/* Task Manager - Always visible */}
      <TaskManager />
    </>
  )
}

export default App
