import { Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import { useAuth } from './contexts/AuthContext'
import Login from './components/Login'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import ComposerPage from './pages/ComposerPage'
import GalleryPage from './pages/GalleryPage'
import JobsPage from './pages/JobsPage'
import StoryWorkflowPage from './pages/StoryWorkflowPage'
import OutfitAnalyzer from './OutfitAnalyzer'
import GenericAnalyzer from './GenericAnalyzer'
import ModularGenerator from './ModularGenerator'
import ComprehensiveAnalyzer from './ComprehensiveAnalyzer'

function App() {
  const { loading: authLoading, isAuthenticated } = useAuth()

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div className="container">
        <h1>Life-OS</h1>
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/login"
        element={!isAuthenticated ? <Login /> : <Navigate to="/" replace />}
      />

      {/* Protected routes */}
      <Route
        path="/"
        element={isAuthenticated ? <Layout /> : <Navigate to="/login" replace />}
      >
        <Route index element={<Dashboard />} />
        <Route path="composer" element={<ComposerPage />} />
        <Route path="gallery" element={<GalleryPage />} />

        {/* Analyzer routes */}
        <Route path="analyzers">
          <Route index element={<Dashboard />} />
          <Route path="outfit" element={<OutfitAnalyzer />} />
          <Route path="comprehensive" element={<ComprehensiveAnalyzer />} />
          <Route path=":type" element={<GenericAnalyzer />} />
        </Route>

        {/* Generator routes */}
        <Route path="generators">
          <Route index element={<Dashboard />} />
          <Route path="modular" element={<ModularGenerator />} />
        </Route>

        {/* Workflow routes */}
        <Route path="workflows">
          <Route index element={<Dashboard />} />
          <Route path="story" element={<StoryWorkflowPage />} />
        </Route>

        {/* Job history */}
        <Route path="jobs" element={<JobsPage />} />
      </Route>

      {/* Catch all - redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
