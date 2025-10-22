import { useState, useMemo, useEffect } from 'react'
import EntityBrowser from '../../components/entities/EntityBrowser'
import { clothingItemsConfig } from '../../components/entities/configs/clothingItemsConfig'
import api from '../../api/client'

function ClothingItemsEntity() {
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [categorySummary, setCategorySummary] = useState(null)

  // Fetch category summary
  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get('/clothing-items/categories')
        setCategorySummary(response.data)
      } catch (error) {
        console.error('Failed to fetch category summary:', error)
      }
    }
    fetchSummary()
  }, [refreshTrigger])

  // Create a modified config with category filtering
  const config = useMemo(() => ({
    ...clothingItemsConfig,
    fetchEntities: () => clothingItemsConfig.fetchEntities(selectedCategory),
    actions: []
  }), [selectedCategory])

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
      {/* Category Filter */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        flexWrap: 'wrap',
        padding: '1rem 1.5rem',
        background: 'rgba(0, 0, 0, 0.2)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        overflowX: 'auto'
      }}>
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
      <EntityBrowser key={refreshTrigger} config={config} />
    </div>
  )
}

export default ClothingItemsEntity
