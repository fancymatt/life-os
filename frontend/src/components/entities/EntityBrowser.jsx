import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import './EntityBrowser.css'
import KeyboardShortcutsModal from './KeyboardShortcutsModal'

/**
 * Generic Entity Browser Component
 *
 * Configuration-driven browser for any entity type (stories, images, outfits, etc.)
 *
 * @param {Object} config - Entity configuration object
 * @param {string} config.entityType - Type identifier (e.g., 'story', 'image', 'outfit')
 * @param {string} config.title - Display title (e.g., 'Stories', 'Images')
 * @param {string} config.icon - Emoji icon for the entity type
 * @param {string} config.emptyMessage - Message when no entities exist
 * @param {Function} config.fetchEntities - Async function to fetch entities
 * @param {Function} config.renderCard - Function to render entity card
 * @param {Function} config.renderDetail - Function to render detail view
 * @param {Array} config.actions - Action buttons for header
 * @param {Object} config.gridConfig - Grid layout configuration
 */
function EntityBrowser({ config }) {
  const navigate = useNavigate()
  const { id } = useParams()
  const location = useLocation()
  const [entities, setEntities] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [view, setView] = useState('list') // 'list' or 'detail'
  const [selectedEntity, setSelectedEntity] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState(config.defaultSort || 'newest')

  // Edit state (always in edit mode when viewing an entity)
  const [editedData, setEditedData] = useState(null)
  const [editedTitle, setEditedTitle] = useState('')
  const [saving, setSaving] = useState(false)
  const [urlEntityLoaded, setUrlEntityLoaded] = useState(false)

  // Pagination state
  const [displayedCount, setDisplayedCount] = useState(50)
  const ITEMS_PER_PAGE = 50

  // Keyboard shortcuts help modal
  const [showShortcutsModal, setShowShortcutsModal] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  // Open entity from URL parameter (only once when entities load)
  useEffect(() => {
    if (id && entities.length > 0 && !urlEntityLoaded) {
      const entity = entities.find(e => e.id === id || e.presetId === id || e.characterId === id)
      if (entity && !selectedEntity) {
        setUrlEntityLoaded(true)
        handleEntityClick(entity)
      }
    }
  }, [id, entities, urlEntityLoaded, selectedEntity])

  // Handle browser back/forward navigation
  useEffect(() => {
    if (!id && view === 'detail') {
      // URL changed to list view (no ID), but we're still showing detail view
      // This happens when user clicks browser back button
      setView('list')
      setSelectedEntity(null)
      setEditedData(null)
      setEditedTitle('')
      setUrlEntityLoaded(false)
    } else if (id && view === 'list' && entities.length > 0) {
      // URL has an ID but we're showing list view
      // This happens when user clicks browser forward button or navigates directly to detail URL
      const entity = entities.find(e => e.id === id || e.presetId === id || e.characterId === id)
      if (entity) {
        handleEntityClick(entity)
      }
    }
  }, [id, view, entities])

  // Filter entities based on search (memoized)
  const filteredEntities = useMemo(() => {
    return entities.filter(entity => {
      if (!searchTerm) return true
      const searchLower = searchTerm.toLowerCase()

      // Search in title/name
      if (entity.title?.toLowerCase().includes(searchLower)) return true
      if (entity.name?.toLowerCase().includes(searchLower)) return true

      // Search in metadata
      if (config.searchFields) {
        return config.searchFields.some(field => {
          const value = entity[field]
          return value?.toString().toLowerCase().includes(searchLower)
        })
      }

      return false
    })
  }, [entities, searchTerm, config.searchFields])

  // Sort entities (memoized)
  const sortedEntities = useMemo(() => {
    return [...filteredEntities].sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.createdAt || b.completedAt || 0) - new Date(a.createdAt || a.completedAt || 0)
        case 'oldest':
          return new Date(a.createdAt || a.completedAt || 0) - new Date(b.createdAt || b.completedAt || 0)
        case 'name':
          return (a.title || a.name || '').localeCompare(b.title || b.name || '')
        default:
          if (config.customSort) {
            return config.customSort(a, b, sortBy)
          }
          return 0
      }
    })
  }, [filteredEntities, sortBy, config.customSort])

  // Paginated entities for display
  const displayedEntities = useMemo(() => {
    return sortedEntities.slice(0, displayedCount)
  }, [sortedEntities, displayedCount])

  // Reset pagination when search or sort changes
  useEffect(() => {
    setDisplayedCount(ITEMS_PER_PAGE)
  }, [searchTerm, sortBy])

  const loadMore = () => {
    setDisplayedCount(prev => prev + ITEMS_PER_PAGE)
  }

  const hasMore = displayedCount < sortedEntities.length

  // Keyboard shortcuts for list and detail views
  useEffect(() => {
    const handleKeyPress = (e) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
      const modKey = isMac ? e.metaKey : e.ctrlKey
      const isInputFocused = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA'

      // ? key - Show keyboard shortcuts help (when not typing in input)
      if (e.key === '?' && !isInputFocused && !e.shiftKey) {
        e.preventDefault()
        setShowShortcutsModal(prev => !prev)
        return
      }

      // Global shortcuts (work in both list and detail view)
      // Ctrl/Cmd + K - Focus search (only in list view)
      if (modKey && e.key === 'k' && view === 'list' && config.enableSearch) {
        e.preventDefault()
        const searchInput = document.querySelector('.search-box input')
        if (searchInput) {
          searchInput.focus()
        }
        return
      }

      // Detail view shortcuts
      if (view === 'detail' && selectedEntity) {
        // Escape - Go back to list
        if (e.key === 'Escape' && !saving) {
          e.preventDefault()
          handleBackToList()
          return
        }

        // Ctrl/Cmd + S - Save changes
        if (modKey && e.key === 's' && config.enableEdit) {
          e.preventDefault()
          if (!saving) {
            handleSave()
          }
          return
        }

        // Ctrl/Cmd + Enter - Save and close
        if (modKey && e.key === 'Enter' && config.enableEdit) {
          e.preventDefault()
          if (!saving) {
            handleSave()
            // Wait for save to complete, then go back
            setTimeout(() => handleBackToList(), 500)
          }
          return
        }

        // Delete key - Delete current entity (with confirmation)
        if (e.key === 'Delete' && config.enableEdit && !isInputFocused) {
          e.preventDefault()
          if (!saving) {
            handleDelete()
          }
          return
        }

        // Arrow key navigation (only when not in input/textarea)
        if (!isInputFocused && sortedEntities.length > 0 && !saving) {
          const currentEntityId = selectedEntity.presetId || selectedEntity.characterId || selectedEntity.id

          const currentIndex = sortedEntities.findIndex(
            entity => {
              const entityId = entity.presetId || entity.characterId || entity.id
              return entityId === currentEntityId
            }
          )

          if (currentIndex === -1) {
            console.warn('Current entity not found in sorted list')
            return
          }

          if (e.key === 'ArrowRight') {
            e.preventDefault()
            // Navigate to next entity (loop to first if at end)
            const nextIndex = (currentIndex + 1) % sortedEntities.length
            handleEntityClick(sortedEntities[nextIndex])
          } else if (e.key === 'ArrowLeft') {
            e.preventDefault()
            // Navigate to previous entity (loop to last if at start)
            const prevIndex = currentIndex === 0 ? sortedEntities.length - 1 : currentIndex - 1
            handleEntityClick(sortedEntities[prevIndex])
          }
        }
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [view, selectedEntity, sortedEntities, saving, config.enableEdit, config.enableSearch])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await config.fetchEntities()
      setEntities(data)
    } catch (err) {
      console.error(`Error fetching ${config.entityType}s:`, err)
      setError(err.message || `Failed to load ${config.entityType}s`)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = () => {
    fetchData()
  }

  const handleEntityClick = async (entity) => {
    setSelectedEntity(entity)
    setView('detail')
    setError(null)
    setSaving(true)

    // Update URL to include entity ID
    const entityId = entity.presetId || entity.characterId || entity.id
    const pathSegments = location.pathname.split('/').filter(s => s)

    // If the last segment looks like an entity ID (UUID format or matches known ID patterns), remove it
    // UUIDs have 4+ hyphens (e.g., "d7db2bd4-47bd-4125-a47c-749e172eaa17")
    // Route names like "story-themes" only have 1-2 hyphens
    let basePath
    const lastSegment = pathSegments[pathSegments.length - 1] || ''
    const isUUID = (lastSegment.match(/-/g) || []).length >= 4
    const looksLikeId = isUUID || (lastSegment.length > 30 && !lastSegment.includes('-'))

    if (pathSegments.length > 0 && looksLikeId) {
      basePath = '/' + pathSegments.slice(0, -1).join('/')
    } else {
      basePath = '/' + pathSegments.join('/')
    }

    if (!location.pathname.endsWith(`/${entityId}`)) {
      navigate(`${basePath}/${entityId}`, { replace: false })
    }

    // For preset-based entities, load full data and set up for editing
    if (config.loadFullData && (!entity.data || Object.keys(entity.data).length === 0)) {
      try {
        const fullData = await config.loadFullData(entity)
        const updatedEntity = { ...entity, data: fullData }
        setSelectedEntity(updatedEntity)

        // Set up edit data immediately
        setEditedData(JSON.parse(JSON.stringify(fullData || {})))
        setEditedTitle(updatedEntity.title || '')

        // Also update in the entities list for future access
        setEntities(prev => prev.map(e =>
          e.id === entity.id ? updatedEntity : e
        ))
        setSaving(false)
      } catch (err) {
        console.error('Failed to load full data:', err)
        setError(err.response?.data?.detail || err.message || 'Failed to load entity data')
        setSaving(false)
      }
    } else {
      // Data already loaded, use it directly
      setEditedData(JSON.parse(JSON.stringify(entity.data || {})))
      setEditedTitle(entity.title || '')
      setSaving(false)
    }
  }

  const handleBackToList = () => {
    setView('list')
    setSelectedEntity(null)
    setEditedData(null)
    setEditedTitle('')
    setUrlEntityLoaded(false) // Reset so URL-based navigation works again

    // Remove ID from URL
    const basePath = location.pathname.split('/').filter(seg => seg).slice(0, 2).join('/')
    navigate(`/${basePath}`, { replace: false })
  }

  const handleResetChanges = () => {
    // Reset to original entity data
    if (selectedEntity) {
      setEditedData(JSON.parse(JSON.stringify(selectedEntity.data || {})))
      setEditedTitle(selectedEntity.title || '')
      setError(null)
    }
  }

  const handleSave = async () => {
    if (!selectedEntity || !config.enableEdit) return

    setSaving(true)
    setError(null)

    try {
      const response = await config.saveEntity(selectedEntity, {
        data: editedData,
        title: editedTitle
      })

      // Update entity in list
      setEntities(prev => prev.map(e =>
        e.id === selectedEntity.id ? { ...e, title: editedTitle, data: editedData } : e
      ))

      // Update selected entity
      setSelectedEntity(prev => ({ ...prev, title: editedTitle, data: editedData }))

      setSaving(false)

      // Refresh data to get updated preview
      setTimeout(() => fetchData(), 1000)
    } catch (err) {
      console.error('Save failed:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to save')
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!selectedEntity || !config.enableEdit) return

    if (!window.confirm(`Are you sure you want to delete "${selectedEntity.title}"?`)) {
      return
    }

    // Find current position in sorted list before deletion
    const currentEntityId = selectedEntity.presetId || selectedEntity.characterId || selectedEntity.id
    const currentIndex = sortedEntities.findIndex(
      entity => {
        const entityId = entity.presetId || entity.characterId || entity.id
        return entityId === currentEntityId
      }
    )

    // Determine next entity to navigate to
    let nextEntity = null
    if (sortedEntities.length > 1) {
      // If not the last item, go to next; otherwise go to previous
      const nextIndex = currentIndex < sortedEntities.length - 1 ? currentIndex + 1 : currentIndex - 1
      nextEntity = sortedEntities[nextIndex]
    }

    setSaving(true)
    setError(null)

    try {
      await config.deleteEntity(selectedEntity)

      // Remove from list
      setEntities(prev => prev.filter(e => e.id !== selectedEntity.id))

      if (nextEntity) {
        // Navigate to next entity
        handleEntityClick(nextEntity)
      } else {
        // No entities left, go back to list view
        setView('list')
        setSelectedEntity(null)
        setEditedData(null)
        setEditedTitle('')
        setUrlEntityLoaded(false)
        const basePath = location.pathname.split('/').filter(seg => seg).slice(0, 2).join('/')
        navigate(`/${basePath}`, { replace: false })
        setSaving(false)
      }
    } catch (err) {
      console.error('Delete failed:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to delete')
      setSaving(false)
    }
  }

  const updateField = (field, value) => {
    setEditedData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleAction = async (action, entity = null) => {
    if (action.handler) {
      // Handler-based action (async function)
      setSaving(true)
      setError(null)
      try {
        await action.handler(entity || selectedEntity)
        // Refresh data after action
        fetchData()
      } catch (err) {
        console.error('Action failed:', err)
        setError(err.response?.data?.detail || err.message || 'Action failed')
      } finally {
        setSaving(false)
      }
    } else if (action.onClick) {
      action.onClick()
    } else if (action.path) {
      navigate(action.path)
    }
  }

  return (
    <div className="entity-browser">
      {view === 'list' ? (
        <>
          {/* List View Header */}
          <div className="entity-header">
            <div className="entity-header-left">
              <h2>
                {config.icon} {config.title}
              </h2>
              <p className="entity-count">
                {sortedEntities.length > 0 && displayedCount < sortedEntities.length ? (
                  <>
                    Showing {displayedCount} of {sortedEntities.length} {sortedEntities.length === 1 ? config.entityType : `${config.entityType}s`}
                    {searchTerm && ` (filtered from ${entities.length})`}
                  </>
                ) : (
                  <>
                    {filteredEntities.length} {filteredEntities.length === 1 ? config.entityType : `${config.entityType}s`}
                    {searchTerm && ` (filtered from ${entities.length})`}
                  </>
                )}
              </p>
            </div>
            <div className="entity-header-right">
              {(config.showRefreshButton !== false) && (
                <button className="refresh-button" onClick={handleRefresh} disabled={loading}>
                  🔄 Refresh
                </button>
              )}
              {config.actions?.map((action, idx) => (
                <button
                  key={idx}
                  className={action.primary ? 'primary-action-button' : 'secondary-action-button'}
                  onClick={() => handleAction(action)}
                >
                  {action.icon} {action.label}
                </button>
              ))}
            </div>
          </div>

      {/* Search and filters */}
      {(config.enableSearch || config.enableSort) && (
        <div className="entity-controls">
          {config.enableSearch && (
            <div className="search-box">
              <input
                type="text"
                placeholder={`Search ${config.entityType}s...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          )}
          {config.enableSort && (
            <div className="sort-box">
              <label>Sort by:</label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="name">Name</option>
                {config.customSortOptions?.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="entity-loading">Loading {config.entityType}s...</div>
      ) : error ? (
        <div className="entity-error">Error: {error}</div>
      ) : sortedEntities.length === 0 ? (
        <div className="entity-empty">
          <p>{config.emptyMessage || `No ${config.entityType}s found`}</p>
          {config.actions?.[0] && (
            <button
              className="primary-action-button"
              onClick={() => handleAction(config.actions[0])}
            >
              {config.actions[0].icon} {config.actions[0].label}
            </button>
          )}
        </div>
      ) : (
        <>
          <div
            className="entity-grid"
            style={{
              gridTemplateColumns: config.gridConfig?.columns || 'repeat(auto-fill, minmax(320px, 1fr))',
              gap: config.gridConfig?.gap || '1.5rem'
            }}
          >
            {displayedEntities.map((entity, idx) => (
              <div key={entity.id || idx} onClick={() => handleEntityClick(entity)}>
                {config.renderCard(entity)}
              </div>
            ))}
          </div>

          {/* Load More Button */}
          {hasMore && (
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              marginTop: '2rem',
              paddingBottom: '2rem'
            }}>
              <button
                onClick={loadMore}
                style={{
                  padding: '0.75rem 2rem',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)'
                  e.currentTarget.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.4)'
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)'
                }}
              >
                Load More ({sortedEntities.length - displayedCount} remaining)
              </button>
            </div>
          )}
        </>
      )}
        </>
      ) : (
        <>
          {/* Detail View */}
          <div className="entity-detail-view">
            {/* Breadcrumb / Back Button */}
            <div className="entity-breadcrumb">
              <button className="back-button" onClick={handleBackToList}>
                ← Back to {config.title}
              </button>
            </div>

            {error && (
              <div style={{
                margin: '1rem 0',
                padding: '1rem',
                background: 'rgba(255, 100, 100, 0.1)',
                border: '1px solid rgba(255, 100, 100, 0.3)',
                borderRadius: '8px',
                color: '#ff6b6b'
              }}>
                {error}
              </div>
            )}

            {config.fullWidthDetail ? (
              /* Full Width Layout - for entities like stories */
              <div className="entity-detail-full-width">
                {config.enableEdit && config.renderEdit ? (
                  // Always in edit mode for editable entities
                  <>
                    {config.renderEdit(selectedEntity, editedData, editedTitle, {
                      updateField,
                      setEditedTitle
                    })}

                    <div className="entity-detail-actions">
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {config.actions?.map((action, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleAction(action, selectedEntity)}
                            disabled={saving}
                            className="secondary-action-button"
                          >
                            {action.icon} {action.label}
                          </button>
                        ))}
                        <button
                          onClick={handleDelete}
                          disabled={saving}
                          className="delete-button"
                        >
                          Delete
                        </button>
                      </div>
                      <div style={{ marginLeft: 'auto', display: 'flex', gap: '1rem' }}>
                        <button
                          onClick={handleSave}
                          disabled={saving}
                          className="save-button"
                        >
                          {saving ? 'Saving...' : 'Save Changes'}
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  // For entities without edit capability, just show renderDetail
                  config.renderDetail(selectedEntity, handleBackToList)
                )}
              </div>
            ) : (
              /* Two Column Layout - for entities with preview */
              <div className="entity-detail-columns">
                {/* Left Column - Preview */}
                <div className="entity-detail-preview">
                  {config.renderPreview ? (
                    config.renderPreview(selectedEntity)
                  ) : (
                    <div style={{ background: 'rgba(0, 0, 0, 0.3)', borderRadius: '8px', padding: '2rem', textAlign: 'center', color: 'rgba(255, 255, 255, 0.5)' }}>
                      Preview not available
                    </div>
                  )}
                </div>

                {/* Right Column - Details/Edit */}
                <div className="entity-detail-content">
                  {config.enableEdit && config.renderEdit ? (
                    // Always in edit mode for editable entities
                    <>
                      {config.renderEdit(selectedEntity, editedData, editedTitle, {
                        updateField,
                        setEditedTitle
                      })}

                      <div className="entity-detail-actions">
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          {config.actions?.map((action, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleAction(action, selectedEntity)}
                              disabled={saving}
                              className="secondary-action-button"
                            >
                              {action.icon} {action.label}
                            </button>
                          ))}
                          <button
                            onClick={handleDelete}
                            disabled={saving}
                            className="delete-button"
                          >
                            Delete
                          </button>
                        </div>
                        <div style={{ marginLeft: 'auto', display: 'flex', gap: '1rem' }}>
                          <button
                            onClick={handleSave}
                            disabled={saving}
                            className="save-button"
                          >
                            {saving ? 'Saving...' : 'Save Changes'}
                          </button>
                        </div>
                      </div>
                    </>
                  ) : (
                    // For entities without edit capability, just show renderDetail
                    config.renderDetail(selectedEntity, handleBackToList)
                  )}
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* Keyboard Shortcuts Help Modal */}
      <KeyboardShortcutsModal
        isOpen={showShortcutsModal}
        onClose={() => setShowShortcutsModal(false)}
      />
    </div>
  )
}

export default EntityBrowser
