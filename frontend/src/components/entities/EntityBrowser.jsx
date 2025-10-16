import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import './EntityBrowser.css'

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

  // Keyboard shortcuts for list and detail views
  useEffect(() => {
    const handleKeyPress = (e) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
      const modKey = isMac ? e.metaKey : e.ctrlKey
      const isInputFocused = e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA'

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

    // If the last segment looks like an ID (contains hyphens/long string), remove it
    // Otherwise keep the full path
    let basePath
    if (pathSegments.length > 0 && (pathSegments[pathSegments.length - 1].includes('-') || pathSegments[pathSegments.length - 1].length > 20)) {
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

  const handleAction = (action) => {
    if (action.onClick) {
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
                {filteredEntities.length} {filteredEntities.length === 1 ? config.entityType : `${config.entityType}s`}
                {searchTerm && ` (filtered from ${entities.length})`}
              </p>
            </div>
            <div className="entity-header-right">
              <button className="refresh-button" onClick={handleRefresh} disabled={loading}>
                🔄 Refresh
              </button>
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
        <div
          className="entity-grid"
          style={{
            gridTemplateColumns: config.gridConfig?.columns || 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: config.gridConfig?.gap || '1.5rem'
          }}
        >
          {sortedEntities.map((entity, idx) => (
            <div key={entity.id || idx} onClick={() => handleEntityClick(entity)}>
              {config.renderCard(entity)}
            </div>
          ))}
        </div>
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

            {/* Two Column Layout */}
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
                      <button
                        onClick={handleDelete}
                        disabled={saving}
                        className="delete-button"
                      >
                        Delete
                      </button>
                      <div style={{ marginLeft: 'auto', display: 'flex', gap: '1rem' }}>
                        <button
                          onClick={handleResetChanges}
                          disabled={saving}
                          className="cancel-button"
                        >
                          Reset Changes
                        </button>
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
          </div>
        </>
      )}
    </div>
  )
}

export default EntityBrowser
