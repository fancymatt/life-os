import './Dashboard.css'

function Dashboard() {
  return (
    <div className="dashboard">
      <div className="dashboard-welcome">
        <h1>Welcome to Life-OS</h1>
        <p className="welcome-subtitle">AI-Powered Image Generation & Analysis Platform</p>

        <div className="welcome-content">
          <div className="welcome-card">
            <div className="welcome-icon">🎨</div>
            <h2>Create</h2>
            <p>Generate stunning images with AI using preset combinations and modular generation</p>
          </div>

          <div className="welcome-card">
            <div className="welcome-icon">📊</div>
            <h2>Analyze</h2>
            <p>Extract detailed information from images including outfits, styles, and visual elements</p>
          </div>

          <div className="welcome-card">
            <div className="welcome-icon">⚡</div>
            <h2>Automate</h2>
            <p>Build AI workflows that combine multiple tools for complex creative tasks</p>
          </div>
        </div>

        <div className="welcome-cta">
          <p>Use the sidebar to access all tools and features</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
