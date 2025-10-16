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
              <span className="nav-badge">Featured</span>
            </NavLink>
            <NavLink to="/gallery" className="nav-link" onClick={onClose}>
              <span className="nav-icon">🖼️</span>
              <span className="nav-label">Gallery</span>
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
            <NavLink to="/analyzers" className="nav-link" onClick={onClose}>
              <span className="nav-icon">🔍</span>
              <span className="nav-label">All Analyzers</span>
            </NavLink>
          </section>

          <section className="nav-section">
            <h3>Generators</h3>
            <NavLink to="/generators/modular" className="nav-link" onClick={onClose}>
              <span className="nav-icon">🎨</span>
              <span className="nav-label">Modular</span>
            </NavLink>
            <NavLink to="/generators" className="nav-link" onClick={onClose}>
              <span className="nav-icon">✨</span>
              <span className="nav-label">All Generators</span>
            </NavLink>
          </section>

          <section className="nav-section">
            <h3>Workflows</h3>
            <NavLink to="/workflows" className="nav-link" onClick={onClose}>
              <span className="nav-icon">⚙️</span>
              <span className="nav-label">All Workflows</span>
            </NavLink>
            <NavLink to="/workflows/story" className="nav-link" onClick={onClose}>
              <span className="nav-icon">📖</span>
              <span className="nav-label">Story Generator</span>
              <span className="nav-badge new">New</span>
            </NavLink>
          </section>

          <section className="nav-section">
            <h3>System</h3>
            <NavLink to="/jobs" className="nav-link" onClick={onClose}>
              <span className="nav-icon">📋</span>
              <span className="nav-label">Job History</span>
            </NavLink>
          </section>
        </nav>
      </aside>
    </>
  )
}

export default Sidebar
