import { NavLink } from 'react-router-dom'
import './Sidebar.css'

function Sidebar({ isOpen, onClose }) {
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
          <section className="nav-section">
            <h3>Main</h3>
            <NavLink to="/" className="nav-link" onClick={onClose}>
              <span className="nav-icon">🏠</span>
              <span className="nav-label">Dashboard</span>
            </NavLink>
            <NavLink to="/composer" className="nav-link" onClick={onClose}>
              <span className="nav-icon">🎭</span>
              <span className="nav-label">Composer</span>
            </NavLink>
            <NavLink to="/gallery" className="nav-link" onClick={onClose}>
              <span className="nav-icon">🖼️</span>
              <span className="nav-label">Gallery</span>
            </NavLink>
            <NavLink to="/jobs" className="nav-link" onClick={onClose}>
              <span className="nav-icon">📋</span>
              <span className="nav-label">Job History</span>
            </NavLink>
          </section>

          <section className="nav-section">
            <h3>Analyzers</h3>
            <NavLink to="/analyzers/outfit" className="nav-link" onClick={onClose}>
              <span className="nav-icon">👔</span>
              <span className="nav-label">Outfit</span>
            </NavLink>
            <NavLink to="/analyzers/comprehensive" className="nav-link" onClick={onClose}>
              <span className="nav-icon">📊</span>
              <span className="nav-label">Comprehensive</span>
            </NavLink>
            <NavLink to="/analyzers/visual-style" className="nav-link" onClick={onClose}>
              <span className="nav-icon">📸</span>
              <span className="nav-label">Photograph Style</span>
            </NavLink>
            <NavLink to="/analyzers/art-style" className="nav-link" onClick={onClose}>
              <span className="nav-icon">🎨</span>
              <span className="nav-label">Art Style</span>
            </NavLink>
            <NavLink to="/analyzers/hair-style" className="nav-link" onClick={onClose}>
              <span className="nav-icon">💇</span>
              <span className="nav-label">Hair Style</span>
            </NavLink>
            <NavLink to="/analyzers/hair-color" className="nav-link" onClick={onClose}>
              <span className="nav-icon">🎨</span>
              <span className="nav-label">Hair Color</span>
            </NavLink>
            <NavLink to="/analyzers/makeup" className="nav-link" onClick={onClose}>
              <span className="nav-icon">💄</span>
              <span className="nav-label">Makeup</span>
            </NavLink>
            <NavLink to="/analyzers/expression" className="nav-link" onClick={onClose}>
              <span className="nav-icon">😊</span>
              <span className="nav-label">Expression</span>
            </NavLink>
            <NavLink to="/analyzers/accessories" className="nav-link" onClick={onClose}>
              <span className="nav-icon">👓</span>
              <span className="nav-label">Accessories</span>
            </NavLink>
          </section>

          <section className="nav-section">
            <h3>Generators</h3>
            <NavLink to="/generators/modular" className="nav-link" onClick={onClose}>
              <span className="nav-icon">🎨</span>
              <span className="nav-label">Modular Generator</span>
            </NavLink>
          </section>

          <section className="nav-section">
            <h3>Workflows</h3>
            <NavLink to="/workflows/story" className="nav-link" onClick={onClose}>
              <span className="nav-icon">📖</span>
              <span className="nav-label">Story Generator</span>
            </NavLink>
          </section>
        </nav>
      </aside>
    </>
  )
}

export default Sidebar
