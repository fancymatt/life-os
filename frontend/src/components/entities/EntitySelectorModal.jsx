import React, { useState, useMemo } from 'react'
import './EntitySelectorModal.css'

/**
 * EntitySelectorModal - Modal for selecting an entity from a list
 *
 * Used for merge operations to pick which entity to merge with
 */
function EntitySelectorModal({
  entities,
  currentEntity,
  entityType,
  onSelect,
  onClose,
  title = 'Select Entity'
}) {
  const [searchTerm, setSearchTerm] = useState('')

  // Filter out current entity and filter by search
  const filteredEntities = useMemo(() => {
    return entities.filter(entity => {
      // Don't show current entity
      if (entity.id === currentEntity.id) return false

      // Don't show archived entities
      if (entity.archived) return false

      // Search filter
      if (!searchTerm) return true

      const searchLower = searchTerm.toLowerCase()
      const name = entity.title || entity.name || ''

      return name.toLowerCase().includes(searchLower)
    })
  }, [entities, currentEntity, searchTerm])

  return (
    <div className="entity-selector-overlay" onClick={onClose}>
      <div className="entity-selector-modal" onClick={(e) => e.stopPropagation()}>
        <div className="entity-selector-header">
          <h2>{title}</h2>
          <button className="entity-selector-close" onClick={onClose}>×</button>
        </div>

        <div className="entity-selector-body">
          {/* Search */}
          <div className="entity-selector-search">
            <input
              type="text"
              placeholder={`Search ${entityType}s...`}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              autoFocus
            />
          </div>

          {/* Entity List */}
          <div className="entity-selector-list">
            {filteredEntities.length === 0 ? (
              <div className="entity-selector-empty">
                No {entityType}s found
                {searchTerm && ` matching "${searchTerm}"`}
              </div>
            ) : (
              filteredEntities.map(entity => (
                <div
                  key={entity.id}
                  className="entity-selector-item"
                  onClick={() => onSelect(entity)}
                >
                  <div className="entity-selector-item-name">
                    {entity.title || entity.name}
                  </div>
                  {entity.id && (
                    <div className="entity-selector-item-id">
                      {entity.id.substring(0, 8)}...
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default EntitySelectorModal
