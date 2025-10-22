import api from '../../../api/client'
import { formatDate, getPreview } from './helpers'

/**
 * Clothing Items Entity Configuration
 */
export const clothingItemsConfig = {
  entityType: 'clothing_item',
  title: 'Clothing Items',
  icon: '👕',
  emptyMessage: 'No clothing items yet. Analyze an outfit image to extract items!',
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  showRefreshButton: true,
  defaultSort: 'newest',
  searchFields: ['item', 'category', 'fabric', 'color', 'details'],

  actions: [],

  fetchEntities: async (filterCategory = null) => {
    const url = filterCategory ? `/clothing-items/?category=${filterCategory}` : '/clothing-items/'
    const response = await api.get(url)
    return (response.data.items || []).map(item => ({
      id: item.item_id,
      itemId: item.item_id,
      title: item.item,
      item: item.item,
      category: item.category,
      fabric: item.fabric,
      color: item.color,
      details: item.details,
      sourceImage: item.source_image,
      createdAt: item.created_at,
      // Wrap editable fields in data property for EntityBrowser
      data: {
        category: item.category,
        item: item.item,
        fabric: item.fabric,
        color: item.color,
        details: item.details
      }
    }))
  },

  fetchCategorySummary: async () => {
    const response = await api.get('/clothing-items/categories')
    return response.data
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(260px, 1fr))',
    gap: '1.25rem'
  },

  renderCard: (item) => (
    <div className="entity-card">
      <div className="entity-card-image" style={{ height: '160px', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2))' }}>
        <div className="entity-card-placeholder" style={{ fontSize: '4rem' }}>
          {getCategoryIcon(item.category)}
        </div>
      </div>
      <div className="entity-card-content">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span style={{
            padding: '0.25rem 0.5rem',
            background: 'rgba(99, 102, 241, 0.2)',
            borderRadius: '4px',
            fontSize: '0.75rem',
            color: 'rgba(99, 102, 241, 1)',
            fontWeight: '500',
            textTransform: 'capitalize'
          }}>
            {item.category.replace('_', ' ')}
          </span>
        </div>
        <h3 className="entity-card-title" style={{ fontSize: '1rem' }}>{item.item}</h3>
        <p className="entity-card-description" style={{ fontSize: '0.85rem' }}>
          {item.color} • {getPreview(item.fabric, 15)}
        </p>
        {formatDate(item.createdAt) && (
          <p className="entity-card-date" style={{ fontSize: '0.75rem' }}>{formatDate(item.createdAt)}</p>
        )}
      </div>
    </div>
  ),

  renderPreview: (item) => (
    <div style={{ padding: '1rem' }}>
      <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span style={{ fontSize: '2.5rem' }}>{getCategoryIcon(item.category)}</span>
        <span style={{
          padding: '0.5rem 0.75rem',
          background: 'rgba(99, 102, 241, 0.2)',
          borderRadius: '6px',
          fontSize: '0.85rem',
          color: 'rgba(99, 102, 241, 1)',
          fontWeight: '500',
          textTransform: 'capitalize'
        }}>
          {item.category.replace('_', ' ')}
        </span>
      </div>
      <h3 style={{ color: 'white', margin: '0 0 0.75rem 0', fontSize: '1.1rem' }}>{item.item}</h3>
      <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.8)', marginBottom: '0.5rem' }}>
        <strong>Color:</strong> {item.color}
      </div>
      <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.8)', marginBottom: '0.75rem' }}>
        <strong>Fabric:</strong> {item.fabric}
      </div>
      <div style={{ fontSize: '0.85rem', color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.4' }}>
        {getPreview(item.details, 40)}
      </div>
    </div>
  ),

  renderDetail: (item, handleBackToList, onUpdate) => (
    <div style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <span style={{ fontSize: '3rem' }}>{getCategoryIcon(item.category)}</span>
        <div>
          <h2 style={{ color: 'white', margin: '0 0 0.5rem 0' }}>{item.item}</h2>
          <span style={{
            padding: '0.5rem 0.75rem',
            background: 'rgba(99, 102, 241, 0.2)',
            borderRadius: '6px',
            fontSize: '0.9rem',
            color: 'rgba(99, 102, 241, 1)',
            fontWeight: '500',
            textTransform: 'capitalize'
          }}>
            {item.category.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Color */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
          Color
        </h3>
        <p style={{ color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.6', margin: 0 }}>
          {item.color}
        </p>
      </div>

      {/* Fabric */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
          Fabric
        </h3>
        <p style={{ color: 'rgba(255, 255, 255, 0.9)', lineHeight: '1.6', margin: 0 }}>
          {item.fabric}
        </p>
      </div>

      {/* Construction Details */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
          Construction & Details
        </h3>
        <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>
          {item.details}
        </p>
      </div>

      {formatDate(item.createdAt) && (
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', margin: 0 }}>
            <strong>Created:</strong> {formatDate(item.createdAt)}
          </p>
        </div>
      )}
    </div>
  ),

  renderEdit: (item, editedData, editedTitle, handlers) => (
    <div>
      {/* Item Name */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Item Name
        </label>
        <input
          type="text"
          value={editedTitle}
          onChange={(e) => handlers.setEditedTitle(e.target.value)}
          placeholder="e.g., Ribbed tank top, High-waisted jeans..."
          style={{
            width: '100%',
            padding: '0.75rem',
            background: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            color: 'white',
            fontSize: '1rem'
          }}
        />
      </div>

      {/* Category */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Category
        </label>
        <select
          value={editedData.category || ''}
          onChange={(e) => handlers.updateField('category', e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem',
            background: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            color: 'white',
            fontSize: '0.95rem'
          }}
        >
          <option value="headwear">Headwear</option>
          <option value="eyewear">Eyewear</option>
          <option value="earrings">Earrings</option>
          <option value="neckwear">Neckwear</option>
          <option value="tops">Tops</option>
          <option value="overtops">Overtops</option>
          <option value="outerwear">Outerwear</option>
          <option value="one_piece">One Piece</option>
          <option value="bottoms">Bottoms</option>
          <option value="belts">Belts</option>
          <option value="hosiery">Hosiery</option>
          <option value="footwear">Footwear</option>
          <option value="bags">Bags</option>
          <option value="wristwear">Wristwear</option>
          <option value="handwear">Handwear</option>
        </select>
      </div>

      {/* Color */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Color
        </label>
        <input
          type="text"
          value={editedData.color || ''}
          onChange={(e) => handlers.updateField('color', e.target.value)}
          placeholder="e.g., Navy blue, Charcoal grey..."
          style={{
            width: '100%',
            padding: '0.75rem',
            background: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            color: 'white',
            fontSize: '0.95rem'
          }}
        />
      </div>

      {/* Fabric */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Fabric
        </label>
        <input
          type="text"
          value={editedData.fabric || ''}
          onChange={(e) => handlers.updateField('fabric', e.target.value)}
          placeholder="e.g., Cotton jersey, Wool blend..."
          style={{
            width: '100%',
            padding: '0.75rem',
            background: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            color: 'white',
            fontSize: '0.95rem'
          }}
        />
      </div>

      {/* Details */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Construction & Details
        </label>
        <textarea
          value={editedData.details || ''}
          onChange={(e) => handlers.updateField('details', e.target.value)}
          rows="6"
          placeholder="Describe construction, fit, styling details..."
          style={{
            width: '100%',
            padding: '0.75rem',
            background: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            color: 'white',
            fontSize: '0.95rem',
            resize: 'vertical',
            fontFamily: 'inherit'
          }}
        />
      </div>
    </div>
  ),

  saveEntity: async (item, updates) => {
    const response = await api.put(
      `/clothing-items/${item.itemId}`,
      {
        item: updates.title,
        category: updates.data.category,
        fabric: updates.data.fabric,
        color: updates.data.color,
        details: updates.data.details
      }
    )
    return response.data
  },

  deleteEntity: async (item) => {
    await api.delete(`/clothing-items/${item.itemId}`)
  }
}

// Helper function to get category icon
function getCategoryIcon(category) {
  const icons = {
    'headwear': '🎩',
    'eyewear': '👓',
    'earrings': '👂',
    'neckwear': '📿',
    'tops': '👚',
    'overtops': '🧥',
    'outerwear': '🧥',
    'one_piece': '👗',
    'bottoms': '👖',
    'belts': '👔',
    'hosiery': '🧦',
    'footwear': '👞',
    'bags': '👜',
    'wristwear': '⌚',
    'handwear': '🧤'
  }
  return icons[category] || '👕'
}
