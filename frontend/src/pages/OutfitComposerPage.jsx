import { useState, useEffect } from 'react'
import api from '../api/client'
import './OutfitComposerPage.css'

function OutfitComposerPage() {
  const [clothingItems, setClothingItems] = useState([])
  const [selectedItems, setSelectedItems] = useState({})
  const [activeCategory, setActiveCategory] = useState('tops')
  const [outfitName, setOutfitName] = useState('')
  const [outfitNotes, setOutfitNotes] = useState('')
  const [savedOutfits, setSavedOutfits] = useState([])
  const [editingOutfitId, setEditingOutfitId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)

  // Categories with icons
  const categories = [
    { value: 'headwear', label: 'Headwear', icon: '🎩' },
    { value: 'eyewear', label: 'Eyewear', icon: '👓' },
    { value: 'earrings', label: 'Earrings', icon: '👂' },
    { value: 'neckwear', label: 'Neckwear', icon: '📿' },
    { value: 'tops', label: 'Tops', icon: '👚' },
    { value: 'overtops', label: 'Overtops', icon: '🧥' },
    { value: 'outerwear', label: 'Outerwear', icon: '🧥' },
    { value: 'one_piece', label: 'One Piece', icon: '👗' },
    { value: 'bottoms', label: 'Bottoms', icon: '👖' },
    { value: 'belts', label: 'Belts', icon: '👔' },
    { value: 'hosiery', label: 'Hosiery', icon: '🧦' },
    { value: 'footwear', label: 'Footwear', icon: '👞' },
    { value: 'bags', label: 'Bags', icon: '👜' },
    { value: 'wristwear', label: 'Wristwear', icon: '⌚' },
    { value: 'handwear', label: 'Handwear', icon: '🧤' }
  ]

  // Fetch all clothing items
  useEffect(() => {
    fetchClothingItems()
    fetchSavedOutfits()
  }, [])

  const fetchClothingItems = async () => {
    try {
      const response = await api.get('/clothing-items/')
      setClothingItems(response.data.items || [])
    } catch (error) {
      console.error('Failed to fetch clothing items:', error)
      showMessage('Failed to load clothing items', 'error')
    }
  }

  const fetchSavedOutfits = async () => {
    try {
      const response = await api.get('/outfits/')
      setSavedOutfits(response.data.outfits || [])
    } catch (error) {
      console.error('Failed to fetch outfits:', error)
    }
  }

  // Get items for a specific category
  const getItemsForCategory = (category) => {
    return clothingItems.filter(item => item.category === category)
  }

  // Toggle item selection
  const toggleItemSelection = (item) => {
    setSelectedItems(prev => {
      const newSelected = { ...prev }
      if (newSelected[item.category] === item.item_id) {
        delete newSelected[item.category]
      } else {
        newSelected[item.category] = item.item_id
      }
      return newSelected
    })
  }

  // Check if item is selected
  const isItemSelected = (item) => {
    return selectedItems[item.category] === item.item_id
  }

  // Get selected item details
  const getSelectedItemDetails = (category) => {
    const itemId = selectedItems[category]
    if (!itemId) return null
    return clothingItems.find(item => item.item_id === itemId)
  }

  // Save outfit
  const saveOutfit = async () => {
    if (!outfitName.trim()) {
      showMessage('Please enter an outfit name', 'error')
      return
    }

    const itemIds = Object.values(selectedItems)
    if (itemIds.length === 0) {
      showMessage('Please select at least one clothing item', 'error')
      return
    }

    setLoading(true)
    try {
      if (editingOutfitId) {
        // Update existing outfit
        await api.put(`/outfits/${editingOutfitId}`, {
          name: outfitName,
          clothing_item_ids: itemIds,
          notes: outfitNotes || null
        })
        showMessage('Outfit updated successfully', 'success')
      } else {
        // Create new outfit
        await api.post('/outfits/', {
          name: outfitName,
          clothing_item_ids: itemIds,
          notes: outfitNotes || null
        })
        showMessage('Outfit saved successfully', 'success')
      }

      // Refresh outfits list
      await fetchSavedOutfits()

      // Reset form
      setOutfitName('')
      setOutfitNotes('')
      setSelectedItems({})
      setEditingOutfitId(null)
    } catch (error) {
      console.error('Failed to save outfit:', error)
      showMessage('Failed to save outfit', 'error')
    } finally {
      setLoading(false)
    }
  }

  // Load outfit for editing
  const loadOutfit = async (outfitId) => {
    try {
      const response = await api.get(`/outfits/${outfitId}`)
      const outfit = response.data

      setOutfitName(outfit.name)
      setOutfitNotes(outfit.notes || '')
      setEditingOutfitId(outfitId)

      // Map item IDs to categories
      const newSelectedItems = {}
      for (const itemId of outfit.clothing_item_ids) {
        const item = clothingItems.find(i => i.item_id === itemId)
        if (item) {
          newSelectedItems[item.category] = itemId
        }
      }
      setSelectedItems(newSelectedItems)

      showMessage('Outfit loaded for editing', 'success')
    } catch (error) {
      console.error('Failed to load outfit:', error)
      showMessage('Failed to load outfit', 'error')
    }
  }

  // Delete outfit
  const deleteOutfit = async (outfitId) => {
    if (!confirm('Are you sure you want to delete this outfit?')) return

    try {
      await api.delete(`/outfits/${outfitId}`)
      showMessage('Outfit deleted successfully', 'success')
      await fetchSavedOutfits()

      // Clear form if editing this outfit
      if (editingOutfitId === outfitId) {
        setOutfitName('')
        setOutfitNotes('')
        setSelectedItems({})
        setEditingOutfitId(null)
      }
    } catch (error) {
      console.error('Failed to delete outfit:', error)
      showMessage('Failed to delete outfit', 'error')
    }
  }

  // Clear selection
  const clearSelection = () => {
    setSelectedItems({})
    setOutfitName('')
    setOutfitNotes('')
    setEditingOutfitId(null)
  }

  // Show message
  const showMessage = (text, type = 'info') => {
    setMessage({ text, type })
    setTimeout(() => setMessage(null), 3000)
  }

  return (
    <div className="outfit-composer-page">
      {message && (
        <div className={`message message-${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="composer-header">
        <h1>Outfit Composer</h1>
        <p>Select clothing items from each category to create your outfit</p>
      </div>

      <div className="composer-layout">
        {/* Left Panel - Item Selection */}
        <div className="composer-left">
          {/* Category Tabs */}
          <div className="category-tabs">
            {categories.map(cat => {
              const itemCount = getItemsForCategory(cat.value).length
              const hasSelection = !!selectedItems[cat.value]

              return (
                <button
                  key={cat.value}
                  className={`category-tab ${activeCategory === cat.value ? 'active' : ''} ${hasSelection ? 'has-selection' : ''}`}
                  onClick={() => setActiveCategory(cat.value)}
                >
                  <span className="category-icon">{cat.icon}</span>
                  <span className="category-label">{cat.label}</span>
                  {itemCount > 0 && (
                    <span className="category-count">{itemCount}</span>
                  )}
                  {hasSelection && <span className="selection-indicator">✓</span>}
                </button>
              )
            })}
          </div>

          {/* Items Grid */}
          <div className="items-grid">
            <h3>{categories.find(c => c.value === activeCategory)?.label || 'Items'}</h3>
            {getItemsForCategory(activeCategory).length === 0 ? (
              <div className="empty-category">
                <p>No items in this category yet</p>
                <p className="empty-hint">Analyze an outfit image to extract items</p>
              </div>
            ) : (
              <div className="item-cards">
                {getItemsForCategory(activeCategory).map(item => (
                  <div
                    key={item.item_id}
                    className={`item-card ${isItemSelected(item) ? 'selected' : ''}`}
                    onClick={() => toggleItemSelection(item)}
                  >
                    {isItemSelected(item) && (
                      <div className="selected-badge">✓</div>
                    )}
                    <div className="item-card-icon">
                      {categories.find(c => c.value === item.category)?.icon || '👕'}
                    </div>
                    <div className="item-card-content">
                      <h4>{item.item}</h4>
                      <p className="item-color">{item.color}</p>
                      <p className="item-fabric">{item.fabric.substring(0, 40)}...</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Outfit Preview & Save */}
        <div className="composer-right">
          {/* Outfit Preview */}
          <div className="outfit-preview">
            <h3>Selected Outfit</h3>
            {Object.keys(selectedItems).length === 0 ? (
              <div className="empty-outfit">
                <p>No items selected yet</p>
                <p className="empty-hint">Click items from the categories to build your outfit</p>
              </div>
            ) : (
              <div className="selected-items-list">
                {categories.map(cat => {
                  const item = getSelectedItemDetails(cat.value)
                  if (!item) return null

                  return (
                    <div key={cat.value} className="selected-item-row">
                      <span className="item-icon">{cat.icon}</span>
                      <div className="item-info">
                        <strong>{item.item}</strong>
                        <span className="item-color-small">{item.color}</span>
                      </div>
                      <button
                        className="remove-button"
                        onClick={() => toggleItemSelection(item)}
                        title="Remove item"
                      >
                        ×
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Outfit Form */}
          <div className="outfit-form">
            <h3>{editingOutfitId ? 'Edit Outfit' : 'Save Outfit'}</h3>

            <div className="form-group">
              <label>Outfit Name *</label>
              <input
                type="text"
                value={outfitName}
                onChange={(e) => setOutfitName(e.target.value)}
                placeholder="e.g., Casual Weekend Look"
              />
            </div>

            <div className="form-group">
              <label>Notes (Optional)</label>
              <textarea
                value={outfitNotes}
                onChange={(e) => setOutfitNotes(e.target.value)}
                placeholder="Add any notes about this outfit..."
                rows="3"
              />
            </div>

            <div className="form-actions">
              <button
                className="btn btn-primary"
                onClick={saveOutfit}
                disabled={loading || Object.keys(selectedItems).length === 0}
              >
                {loading ? 'Saving...' : (editingOutfitId ? 'Update Outfit' : 'Save Outfit')}
              </button>
              <button
                className="btn btn-secondary"
                onClick={clearSelection}
                disabled={loading}
              >
                Clear
              </button>
            </div>
          </div>

          {/* Saved Outfits */}
          <div className="saved-outfits">
            <h3>Saved Outfits ({savedOutfits.length})</h3>
            {savedOutfits.length === 0 ? (
              <p className="empty-hint">No saved outfits yet</p>
            ) : (
              <div className="saved-outfits-list">
                {savedOutfits.map(outfit => (
                  <div
                    key={outfit.outfit_id}
                    className={`saved-outfit-card ${editingOutfitId === outfit.outfit_id ? 'editing' : ''}`}
                  >
                    <div className="saved-outfit-header">
                      <h4>{outfit.name}</h4>
                      <div className="saved-outfit-actions">
                        <button
                          className="btn-icon"
                          onClick={() => loadOutfit(outfit.outfit_id)}
                          title="Edit"
                        >
                          ✏️
                        </button>
                        <button
                          className="btn-icon"
                          onClick={() => deleteOutfit(outfit.outfit_id)}
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                    <p className="saved-outfit-count">
                      {outfit.clothing_item_ids.length} items
                    </p>
                    {outfit.notes && (
                      <p className="saved-outfit-notes">{outfit.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default OutfitComposerPage
