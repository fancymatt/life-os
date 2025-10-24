import { useState, useEffect, useRef } from 'react'
import api from '../../api/client'
import './TagManager.css'

/**
 * TagManager Component
 *
 * Reusable component for managing tags on entities.
 * Supports adding, removing, and autocomplete from existing tags.
 *
 * @param {Object} props
 * @param {string} props.entityType - Entity type (e.g., 'character', 'clothing_item')
 * @param {string} props.entityId - Entity ID
 * @param {Array} props.tags - Current tags (array of TagInfo objects)
 * @param {Function} props.onTagsChange - Callback when tags change
 * @param {boolean} props.readonly - If true, tags are display-only
 */
function TagManager({ entityType, entityId, tags = [], onTagsChange, readonly = false }) {
  const [inputValue, setInputValue] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [loading, setLoading] = useState(false)
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1)
  const inputRef = useRef(null)
  const suggestionsRef = useRef(null)

  // Fetch autocomplete suggestions when input changes
  useEffect(() => {
    if (!inputValue.trim() || readonly) {
      setSuggestions([])
      setShowSuggestions(false)
      return
    }

    const fetchSuggestions = async () => {
      try {
        const response = await api.get('/tags/autocomplete/search', {
          params: { query: inputValue }
        })
        setSuggestions(response.data.suggestions || [])
        setShowSuggestions(true)
        setSelectedSuggestionIndex(-1)
      } catch (error) {
        console.error('Failed to fetch tag suggestions:', error)
        setSuggestions([])
      }
    }

    // Debounce API calls
    const timeoutId = setTimeout(fetchSuggestions, 300)
    return () => clearTimeout(timeoutId)
  }, [inputValue, readonly])

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target) &&
        !inputRef.current.contains(event.target)
      ) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const addTag = async (tagName) => {
    if (!tagName.trim() || readonly) return

    try {
      setLoading(true)
      // Add tag to entity (API will create tag if it doesn't exist)
      await api.post(`/tags/entity/${entityType}/${entityId}`, {
        tag_names: [tagName.trim()],
        auto_create: true
      })

      // Fetch updated tags
      const response = await api.get(`/tags/entity/${entityType}/${entityId}`)
      onTagsChange(response.data.tags)
    } catch (error) {
      console.error('Failed to add tag:', error)
      alert(error.response?.data?.detail || 'Failed to add tag')
    } finally {
      setLoading(false)
      setInputValue('')
      setShowSuggestions(false)
    }
  }

  const removeTag = async (tagId) => {
    if (readonly) return

    try {
      setLoading(true)
      await api.delete(`/tags/entity/${entityType}/${entityId}/${tagId}`)

      // Fetch updated tags
      const response = await api.get(`/tags/entity/${entityType}/${entityId}`)
      onTagsChange(response.data.tags)
    } catch (error) {
      console.error('Failed to remove tag:', error)
      alert(error.response?.data?.detail || 'Failed to remove tag')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (readonly) return

    // Enter - Add tag or select suggestion
    if (e.key === 'Enter') {
      e.preventDefault()
      if (selectedSuggestionIndex >= 0 && suggestions[selectedSuggestionIndex]) {
        addTag(suggestions[selectedSuggestionIndex].name)
      } else if (inputValue.trim()) {
        addTag(inputValue)
      }
    }

    // Escape - Clear input and close suggestions
    if (e.key === 'Escape') {
      setInputValue('')
      setShowSuggestions(false)
      setSelectedSuggestionIndex(-1)
    }

    // Arrow keys - Navigate suggestions
    if (showSuggestions && suggestions.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedSuggestionIndex(prev =>
          prev < suggestions.length - 1 ? prev + 1 : 0
        )
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedSuggestionIndex(prev =>
          prev > 0 ? prev - 1 : suggestions.length - 1
        )
      }
    }
  }

  // Get color for category
  const getCategoryColor = (category) => {
    const colors = {
      material: '#9C27B0',
      style: '#2196F3',
      season: '#FF9800',
      genre: '#E91E63',
      color: '#4CAF50',
      mood: '#FF5722',
      setting: '#00BCD4',
      character: '#3F51B5',
      custom: '#607D8B'
    }
    return colors[category] || colors.custom
  }

  return (
    <div className="tag-manager">
      <div className="tag-manager-header">
        <label className="tag-manager-label">Tags</label>
        {tags.length > 0 && (
          <span className="tag-count">{tags.length}</span>
        )}
      </div>

      {/* Existing Tags */}
      <div className="tags-container">
        {tags.map((tag) => (
          <div
            key={tag.tag_id}
            className="tag-badge"
            style={{
              background: tag.color || getCategoryColor(tag.category),
              opacity: readonly ? 0.7 : 1
            }}
          >
            <span className="tag-name">{tag.name}</span>
            {!readonly && (
              <button
                className="tag-remove"
                onClick={() => removeTag(tag.tag_id)}
                disabled={loading}
                title="Remove tag"
              >
                ×
              </button>
            )}
          </div>
        ))}

        {/* Add Tag Input */}
        {!readonly && (
          <div className="tag-input-container">
            <input
              ref={inputRef}
              type="text"
              className="tag-input"
              placeholder="Add tag..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />

            {/* Autocomplete Suggestions */}
            {showSuggestions && suggestions.length > 0 && (
              <div ref={suggestionsRef} className="tag-suggestions">
                {suggestions.map((suggestion, index) => (
                  <div
                    key={suggestion.tag_id}
                    className={`tag-suggestion ${index === selectedSuggestionIndex ? 'selected' : ''}`}
                    onClick={() => addTag(suggestion.name)}
                  >
                    <div
                      className="tag-suggestion-color"
                      style={{ background: suggestion.color || getCategoryColor(suggestion.category) }}
                    />
                    <span className="tag-suggestion-name">{suggestion.name}</span>
                    {suggestion.category && (
                      <span className="tag-suggestion-category">{suggestion.category}</span>
                    )}
                    <span className="tag-suggestion-count">{suggestion.usage_count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {tags.length === 0 && readonly && (
        <p className="tag-empty-message">No tags</p>
      )}
    </div>
  )
}

export default TagManager
