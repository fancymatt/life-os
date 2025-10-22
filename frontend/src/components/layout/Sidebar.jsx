import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import './Sidebar.css'

const SIDEBAR_STORAGE_KEY = 'lifeos_sidebar_collapsed'

function Sidebar({ isOpen, onClose }) {
  // Load collapse state from localStorage or use defaults
  const [collapsed, setCollapsed] = useState(() => {
    try {
      const saved = localStorage.getItem(SIDEBAR_STORAGE_KEY)
      if (saved) {
        return JSON.parse(saved)
      }
    } catch (error) {
      console.error('Failed to load sidebar state:', error)
    }
    // Default state - all sections expanded
    return {
      entities: false,
      tools: false,
      applications: false,
      system: false
    }
  })

  // Save collapse state to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(SIDEBAR_STORAGE_KEY, JSON.stringify(collapsed))
    } catch (error) {
      console.error('Failed to save sidebar state:', error)
    }
  }, [collapsed])

  const toggleSection = (section) => {
    setCollapsed(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>🎨 Life-OS</h2>
          <button className="sidebar-close" onClick={onClose}>×</button>
        </div>

        <nav className="sidebar-nav">
          {/* ENTITIES SECTION */}
          <section className="nav-section">
            <button
              className="nav-section-header"
              onClick={() => toggleSection('entities')}
            >
              <span className="nav-section-title">
                <span className="nav-section-icon">📦</span>
                Entities
              </span>
              <span className={`nav-section-toggle ${collapsed.entities ? 'collapsed' : ''}`}>
                ▼
              </span>
            </button>
            {!collapsed.entities && (
              <div className="nav-section-content">
                <NavLink to="/entities/accessories" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">👓</span>
                  <span className="nav-label">Accessories</span>
                </NavLink>
                <NavLink to="/entities/art-styles" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🎨</span>
                  <span className="nav-label">Art Styles</span>
                </NavLink>
                <NavLink to="/entities/board-games" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🎲</span>
                  <span className="nav-label">Board Games</span>
                </NavLink>
                <NavLink to="/entities/characters" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">👤</span>
                  <span className="nav-label">Characters</span>
                </NavLink>
                <NavLink to="/entities/clothing-items" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">👕</span>
                  <span className="nav-label">Clothing Items</span>
                </NavLink>
                <NavLink to="/entities/documents" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📄</span>
                  <span className="nav-label">Documents</span>
                </NavLink>
                <NavLink to="/entities/expressions" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">😊</span>
                  <span className="nav-label">Expressions</span>
                </NavLink>
                <NavLink to="/entities/hair-colors" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🎨</span>
                  <span className="nav-label">Hair Colors</span>
                </NavLink>
                <NavLink to="/entities/hair-styles" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">💇</span>
                  <span className="nav-label">Hair Styles</span>
                </NavLink>
                <NavLink to="/entities/story-illustrator-configs" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🎨</span>
                  <span className="nav-label">Illustrator Configs</span>
                </NavLink>
                <NavLink to="/entities/images" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🖼️</span>
                  <span className="nav-label">Images</span>
                </NavLink>
                <NavLink to="/entities/makeup" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">💄</span>
                  <span className="nav-label">Makeup</span>
                </NavLink>
                <NavLink to="/entities/outfits" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">👔</span>
                  <span className="nav-label">Outfits</span>
                </NavLink>
                <NavLink to="/entities/qas" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">💬</span>
                  <span className="nav-label">Q&As</span>
                </NavLink>
                <NavLink to="/entities/story-planner-configs" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📋</span>
                  <span className="nav-label">Planner Configs</span>
                </NavLink>
                <NavLink to="/entities/story-prose-styles" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">✍️</span>
                  <span className="nav-label">Prose Styles</span>
                </NavLink>
                <NavLink to="/entities/stories" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📚</span>
                  <span className="nav-label">Stories</span>
                </NavLink>
                <NavLink to="/entities/story-audiences" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">👥</span>
                  <span className="nav-label">Story Audiences</span>
                </NavLink>
                <NavLink to="/entities/story-themes" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📚</span>
                  <span className="nav-label">Story Themes</span>
                </NavLink>
                <NavLink to="/entities/visual-styles" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📸</span>
                  <span className="nav-label">Visual Styles</span>
                </NavLink>
                <NavLink to="/entities/story-writer-configs" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📝</span>
                  <span className="nav-label">Writer Configs</span>
                </NavLink>
              </div>
            )}
          </section>

          {/* TOOLS SECTION */}
          <section className="nav-section">
            <button
              className="nav-section-header"
              onClick={() => toggleSection('tools')}
            >
              <span className="nav-section-title">
                <span className="nav-section-icon">🔧</span>
                Tools
              </span>
              <span className={`nav-section-toggle ${collapsed.tools ? 'collapsed' : ''}`}>
                ▼
              </span>
            </button>
            {!collapsed.tools && (
              <div className="nav-section-content">
                <NavLink to="/tools/analyzers/accessories" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">👓</span>
                  <span className="nav-label">Accessories Analyzer</span>
                </NavLink>
                <NavLink to="/tools/analyzers/art-style" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🎨</span>
                  <span className="nav-label">Art Style Analyzer</span>
                </NavLink>
                <NavLink to="/tools/bgg-rulebook-fetcher" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🎲</span>
                  <span className="nav-label">BGG Rulebook Fetcher</span>
                </NavLink>
                <NavLink to="/tools/analyzers/character-appearance" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">👤</span>
                  <span className="nav-label">Character Appearance Analyzer</span>
                </NavLink>
                <NavLink to="/tools/analyzers/comprehensive" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📊</span>
                  <span className="nav-label">Comprehensive Analyzer</span>
                </NavLink>
                <NavLink to="/tools/document-processor" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📄</span>
                  <span className="nav-label">Document Processor</span>
                </NavLink>
                <NavLink to="/tools/document-question-asker" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">💬</span>
                  <span className="nav-label">Document Question Asker</span>
                </NavLink>
                <NavLink to="/tools/analyzers/expression" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">😊</span>
                  <span className="nav-label">Expression Analyzer</span>
                </NavLink>
                <NavLink to="/tools/analyzers/hair-color" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🎨</span>
                  <span className="nav-label">Hair Color Analyzer</span>
                </NavLink>
                <NavLink to="/tools/analyzers/hair-style" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">💇</span>
                  <span className="nav-label">Hair Style Analyzer</span>
                </NavLink>
                <NavLink to="/tools/analyzers/makeup" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">💄</span>
                  <span className="nav-label">Makeup Analyzer</span>
                </NavLink>
                <NavLink to="/tools/generators/modular" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🖼️</span>
                  <span className="nav-label">Modular Image Generator</span>
                </NavLink>
                <NavLink to="/tools/analyzers/outfit" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">👔</span>
                  <span className="nav-label">Outfit Analyzer</span>
                </NavLink>
                <NavLink to="/tools/story/illustrator" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🎨</span>
                  <span className="nav-label">Story Illustrator</span>
                </NavLink>
                <NavLink to="/tools/story/planner" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📝</span>
                  <span className="nav-label">Story Planner</span>
                </NavLink>
                <NavLink to="/tools/story/writer" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">✍️</span>
                  <span className="nav-label">Story Writer</span>
                </NavLink>
                <NavLink to="/tools/analyzers/visual-style" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📸</span>
                  <span className="nav-label">Visual Style Analyzer</span>
                </NavLink>
                <NavLink to="/tools/visualization-config" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🎨</span>
                  <span className="nav-label">Visualization Config</span>
                </NavLink>
              </div>
            )}
          </section>

          {/* APPLICATIONS SECTION */}
          <section className="nav-section">
            <button
              className="nav-section-header"
              onClick={() => toggleSection('applications')}
            >
              <span className="nav-section-title">
                <span className="nav-section-icon">🎯</span>
                Applications
              </span>
              <span className={`nav-section-toggle ${collapsed.applications ? 'collapsed' : ''}`}>
                ▼
              </span>
            </button>
            {!collapsed.applications && (
              <div className="nav-section-content">
                <NavLink to="/apps/composer" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">🎭</span>
                  <span className="nav-label">Image Composer</span>
                </NavLink>
                <NavLink to="/apps/outfit-composer" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">👗</span>
                  <span className="nav-label">Outfit Composer</span>
                </NavLink>
                <NavLink to="/workflows/story" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📖</span>
                  <span className="nav-label">Story Generator</span>
                </NavLink>
              </div>
            )}
          </section>

          {/* SYSTEM SECTION */}
          <section className="nav-section">
            <button
              className="nav-section-header"
              onClick={() => toggleSection('system')}
            >
              <span className="nav-section-title">
                <span className="nav-section-icon">⚙️</span>
                System
              </span>
              <span className={`nav-section-toggle ${collapsed.system ? 'collapsed' : ''}`}>
                ▼
              </span>
            </button>
            {!collapsed.system && (
              <div className="nav-section-content">
                <NavLink to="/jobs" className="nav-link" onClick={onClose}>
                  <span className="nav-icon">📋</span>
                  <span className="nav-label">Job History</span>
                </NavLink>
              </div>
            )}
          </section>
        </nav>
      </aside>
    </>
  )
}

export default Sidebar
