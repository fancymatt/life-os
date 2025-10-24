import { useState, useMemo, useEffect } from 'react'
import EntityBrowser from '../../components/entities/EntityBrowser'
import { clothingItemsConfig } from '../../components/entities/configs/clothingItemsConfig'
import EntityMergeModal from '../../components/entities/EntityMergeModal'
import api from '../../api/client'

function ClothingItemsEntity() {
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [categorySummary, setCategorySummary] = useState(null)

  // Merge state
  const [showMergeModal, setShowMergeModal] = useState(false)
  const [mergeSource, setMergeSource] = useState(null)
  const [mergeTarget, setMergeTarget] = useState(null)

  // Selection mode state
  const [selectionMode, setSelectionMode] = useState(false)
  const [selectedItems, setSelectedItems] = useState([])

  // Fetch category summary
  useEffect(() => {
    fetchSummary()
  }, [refreshTrigger])

  const fetchSummary = async () => {
    try {
      const response = await api.get('/clothing-items/categories')
      setCategorySummary(response.data)
    } catch (error) {
      console.error('Failed to fetch category summary:', error)
    }
  }

  const toggleSelectionMode = () => {
    setSelectionMode(!selectionMode)
    setSelectedItems([]) // Clear selection when toggling mode
  }

  const handleItemSelect = (item) => {
    if (!selectionMode) return

    setSelectedItems(prev => {
      const isSelected = prev.some(i => i.id === item.id)
      if (isSelected) {
        // Deselect
        return prev.filter(i => i.id !== item.id)
      } else {
        // Select (max 2)
        if (prev.length >= 2) {
          // Replace oldest selection
          return [prev[1], item]
        }
        return [...prev, item]
      }
    })
  }

  const handleMergeSelected = () => {
    if (selectedItems.length === 2) {
      setMergeSource(selectedItems[0])
      setMergeTarget(selectedItems[1])
      setShowMergeModal(true)
    }
  }

  const handleMergeComplete = () => {
    setShowMergeModal(false)
    setMergeSource(null)
    setMergeTarget(null)
    setSelectionMode(false)
    setSelectedItems([])
    setRefreshTrigger(prev => prev + 1)
  }

  const handleMergeModalClose = () => {
    setShowMergeModal(false)
    setMergeSource(null)
    setMergeTarget(null)
  }

  // Create a modified config with category filtering and selection mode
  const config = useMemo(() => ({
    ...clothingItemsConfig,
    fetchEntities: () => clothingItemsConfig.fetchEntities(selectedCategory),
    selectionMode: selectionMode,
    selectedItems: selectedItems,
    onItemSelect: handleItemSelect,
    actions: clothingItemsConfig.actions || []
  }), [selectedCategory, selectionMode, selectedItems])

  // Categories for filtering
  const categories = [
    { value: null, label: 'All Items', icon: '👕' },
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

  return (
    <div>
      {/* Selection Mode / Merge Controls */}
      {(selectionMode || selectedItems.length > 0) && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1rem 1.5rem',
          background: 'rgba(99, 102, 241, 0.15)',
          borderBottom: '1px solid rgba(99, 102, 241, 0.3)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ color: 'white', fontWeight: '500' }}>
              {selectedItems.length === 0 && 'Select 2 items to merge'}
              {selectedItems.length === 1 && '1 item selected - select 1 more'}
              {selectedItems.length === 2 && '2 items selected'}
            </span>
            {selectedItems.length > 0 && (
              <button
                onClick={() => setSelectedItems([])}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '0.9rem'
                }}
              >
                Clear Selection
              </button>
            )}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={handleMergeSelected}
              disabled={selectedItems.length !== 2}
              style={{
                padding: '0.75rem 1.5rem',
                background: selectedItems.length === 2
                  ? 'linear-gradient(135deg, #8b5cf6, #3b82f6)'
                  : 'rgba(139, 92, 246, 0.3)',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                cursor: selectedItems.length === 2 ? 'pointer' : 'not-allowed',
                fontSize: '1rem',
                fontWeight: '600',
                opacity: selectedItems.length === 2 ? 1 : 0.5,
                transition: 'all 0.2s'
              }}
            >
              🔀 Merge
            </button>
            <button
              onClick={toggleSelectionMode}
              style={{
                padding: '0.75rem 1.5rem',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '500'
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Category Filter */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        flexWrap: 'wrap',
        padding: '1rem 1.5rem',
        background: 'rgba(0, 0, 0, 0.2)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        overflowX: 'auto',
        alignItems: 'center'
      }}>
        {/* Selection Mode Toggle Button */}
        {!selectionMode && (
          <button
            onClick={toggleSelectionMode}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(139, 92, 246, 0.2)',
              border: '1px solid rgba(139, 92, 246, 0.4)',
              borderRadius: '8px',
              color: 'rgba(139, 92, 246, 1)',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: '500',
              whiteSpace: 'nowrap',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s',
              marginRight: '0.5rem'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(139, 92, 246, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(139, 92, 246, 0.2)'
            }}
          >
            <span>☑️</span>
            <span>Select...</span>
          </button>
        )}
        {categories.map(cat => {
          const count = categorySummary?.categories?.[cat.value] || (cat.value === null ? categorySummary?.total_items : 0)
          return (
            <button
              key={cat.value || 'all'}
              onClick={() => {
                setSelectedCategory(cat.value)
                setRefreshTrigger(prev => prev + 1)
              }}
              style={{
                padding: '0.5rem 1rem',
                background: selectedCategory === cat.value
                  ? 'rgba(99, 102, 241, 0.3)'
                  : 'rgba(255, 255, 255, 0.05)',
                border: selectedCategory === cat.value
                  ? '1px solid rgba(99, 102, 241, 0.5)'
                  : '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: selectedCategory === cat.value
                  ? 'rgba(99, 102, 241, 1)'
                  : 'rgba(255, 255, 255, 0.8)',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: selectedCategory === cat.value ? '600' : '400',
                whiteSpace: 'nowrap',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                if (selectedCategory !== cat.value) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'
                }
              }}
              onMouseLeave={(e) => {
                if (selectedCategory !== cat.value) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'
                }
              }}
            >
              <span>{cat.icon}</span>
              <span>{cat.label}</span>
              {count !== undefined && count > 0 && (
                <span style={{
                  padding: '0.125rem 0.375rem',
                  background: selectedCategory === cat.value
                    ? 'rgba(99, 102, 241, 0.4)'
                    : 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                  fontWeight: '600'
                }}>
                  {count}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Entity Browser */}
      <EntityBrowser key={`${refreshTrigger}-${selectionMode}`} config={config} />

      {/* Merge Modal */}
      {showMergeModal && mergeSource && mergeTarget && (
        <EntityMergeModal
          entityType="clothing_item"
          sourceEntity={mergeSource}
          targetEntity={mergeTarget}
          onClose={handleMergeModalClose}
          onMergeComplete={handleMergeComplete}
        />
      )}
    </div>
  )
}

export default ClothingItemsEntity
