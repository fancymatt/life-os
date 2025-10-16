import { Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import { useAuth } from './contexts/AuthContext'
import Login from './components/Login'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import JobsPage from './pages/JobsPage'

// Entity Pages
import StoriesEntity from './pages/entities/StoriesEntity'
import ImagesEntity from './pages/entities/ImagesEntity'
import CharactersEntity from './pages/entities/CharactersEntity'
import OutfitsEntity from './pages/entities/OutfitsEntity'
import ExpressionsEntity from './pages/entities/ExpressionsEntity'
import MakeupsEntity from './pages/entities/MakeupsEntity'
import HairStylesEntity from './pages/entities/HairStylesEntity'
import HairColorsEntity from './pages/entities/HairColorsEntity'
import VisualStylesEntity from './pages/entities/VisualStylesEntity'
import ArtStylesEntity from './pages/entities/ArtStylesEntity'
import AccessoriesEntity from './pages/entities/AccessoriesEntity'
import StoryThemesEntity from './pages/entities/StoryThemesEntity'
import StoryAudiencesEntity from './pages/entities/StoryAudiencesEntity'
import StoryProseStylesEntity from './pages/entities/StoryProseStylesEntity'
import StoryPlannerConfigsEntity from './pages/entities/StoryPlannerConfigsEntity'
import StoryWriterConfigsEntity from './pages/entities/StoryWriterConfigsEntity'
import StoryIllustratorConfigsEntity from './pages/entities/StoryIllustratorConfigsEntity'
import ToolConfigPage from './pages/ToolConfigPage'

// Tool Pages - Analyzers
import OutfitAnalyzer from './OutfitAnalyzer'
import ComprehensiveAnalyzer from './ComprehensiveAnalyzer'
import GenericAnalyzer from './GenericAnalyzer'

// Tool Pages - Story Tools
import StoryPlannerPage from './pages/StoryPlannerPage'
import StoryWriterPage from './pages/StoryWriterPage'
import StoryIllustratorPage from './pages/StoryIllustratorPage'

// Tool Pages - Generators
import ModularGenerator from './ModularGenerator'

// Workflow Pages
import StoryWorkflowPage from './pages/StoryWorkflowPage'

// Application Pages
import ComposerPage from './pages/ComposerPage'

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
        {/* Dashboard */}
        <Route index element={<Dashboard />} />

        {/* Entities */}
        <Route path="entities">
          <Route index element={<Navigate to="/entities/stories" replace />} />
          <Route path="stories" element={<StoriesEntity />} />
          <Route path="stories/:id" element={<StoriesEntity />} />
          <Route path="images" element={<ImagesEntity />} />
          <Route path="images/:id" element={<ImagesEntity />} />
          <Route path="characters" element={<CharactersEntity />} />
          <Route path="characters/:id" element={<CharactersEntity />} />
          <Route path="outfits" element={<OutfitsEntity />} />
          <Route path="outfits/:id" element={<OutfitsEntity />} />
          <Route path="expressions" element={<ExpressionsEntity />} />
          <Route path="expressions/:id" element={<ExpressionsEntity />} />
          <Route path="makeup" element={<MakeupsEntity />} />
          <Route path="makeup/:id" element={<MakeupsEntity />} />
          <Route path="hair-styles" element={<HairStylesEntity />} />
          <Route path="hair-styles/:id" element={<HairStylesEntity />} />
          <Route path="hair-colors" element={<HairColorsEntity />} />
          <Route path="hair-colors/:id" element={<HairColorsEntity />} />
          <Route path="visual-styles" element={<VisualStylesEntity />} />
          <Route path="visual-styles/:id" element={<VisualStylesEntity />} />
          <Route path="art-styles" element={<ArtStylesEntity />} />
          <Route path="art-styles/:id" element={<ArtStylesEntity />} />
          <Route path="accessories" element={<AccessoriesEntity />} />
          <Route path="accessories/:id" element={<AccessoriesEntity />} />
          <Route path="story-themes" element={<StoryThemesEntity />} />
          <Route path="story-themes/:id" element={<StoryThemesEntity />} />
          <Route path="story-audiences" element={<StoryAudiencesEntity />} />
          <Route path="story-audiences/:id" element={<StoryAudiencesEntity />} />
          <Route path="story-prose-styles" element={<StoryProseStylesEntity />} />
          <Route path="story-prose-styles/:id" element={<StoryProseStylesEntity />} />
          <Route path="story-planner-configs" element={<StoryPlannerConfigsEntity />} />
          <Route path="story-planner-configs/:id" element={<StoryPlannerConfigsEntity />} />
          <Route path="story-writer-configs" element={<StoryWriterConfigsEntity />} />
          <Route path="story-writer-configs/:id" element={<StoryWriterConfigsEntity />} />
          <Route path="story-illustrator-configs" element={<StoryIllustratorConfigsEntity />} />
          <Route path="story-illustrator-configs/:id" element={<StoryIllustratorConfigsEntity />} />
        </Route>

        {/* Tools */}
        <Route path="tools">
          <Route index element={<Dashboard />} />

          {/* Analyzers */}
          <Route path="analyzers">
            <Route index element={<Dashboard />} />
            <Route path="outfit" element={<OutfitAnalyzer />} />
            <Route path="comprehensive" element={<ComprehensiveAnalyzer />} />
            <Route path=":type" element={<GenericAnalyzer />} />
          </Route>

          {/* Story Tools */}
          <Route path="story">
            <Route index element={<Dashboard />} />
            <Route path="planner" element={<StoryPlannerPage />} />
            <Route path="writer" element={<StoryWriterPage />} />
            <Route path="illustrator" element={<StoryIllustratorPage />} />
          </Route>

          {/* Generators */}
          <Route path="generators">
            <Route index element={<Dashboard />} />
            <Route path="modular" element={<ModularGenerator />} />
          </Route>

          {/* Tool Configuration */}
          <Route path=":category/:toolName/config" element={<ToolConfigPage />} />
        </Route>

        {/* Workflows */}
        <Route path="workflows">
          <Route index element={<Dashboard />} />
          <Route path="story" element={<StoryWorkflowPage />} />
        </Route>

        {/* Applications */}
        <Route path="apps">
          <Route index element={<Dashboard />} />
          <Route path="composer" element={<ComposerPage />} />
        </Route>

        {/* System */}
        <Route path="jobs" element={<JobsPage />} />

        {/* Legacy routes for backwards compatibility */}
        <Route path="composer" element={<Navigate to="/apps/composer" replace />} />
        <Route path="gallery" element={<Navigate to="/entities/images" replace />} />
        <Route path="stories" element={<Navigate to="/entities/stories" replace />} />
        <Route path="analyzers/*" element={<Navigate to="/tools/analyzers" replace />} />
        <Route path="generators/*" element={<Navigate to="/tools/generators" replace />} />
        <Route path="story-tools/*" element={<Navigate to="/tools/story" replace />} />
      </Route>

      {/* Catch all - redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
