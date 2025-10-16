import { useState } from 'react'

/**
 * Outfit Editor Component
 *
 * Custom editor for outfit entities with accordion-style clothing item management
 */
function OutfitEditor({ editedData, editedTitle, handlers }) {
  const [expandedItems, setExpandedItems] = useState({})
  const [editingItems, setEditingItems] = useState({})

  // Handle loading state
  if (!editedData) {
    return (
      <div style={{ padding: '2rem', color: 'rgba(255, 255, 255, 0.7)' }}>
        Loading outfit data...
      </div>
    )
  }

  const toggleItem = (index) => {
    setExpandedItems(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const toggleEdit = (index) => {
    setEditingItems(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const updateItemField = (index, field, value) => {
    const newItems = [...(editedData.clothing_items || [])]
    newItems[index] = {
      ...newItems[index],
      [field]: value
    }
    handlers.updateField('clothing_items', newItems)
  }

  const deleteItem = (index) => {
    const newItems = (editedData.clothing_items || []).filter((_, i) => i !== index)
    handlers.updateField('clothing_items', newItems)
  }

  const addNewItem = () => {
    const newItems = [...(editedData.clothing_items || []), {
      item: '',
      fabric: '',
      color: '',
      details: ''
    }]
    handlers.updateField('clothing_items', newItems)
  }

  return (
    <div>
      {/* Name Field */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Outfit Name
        </label>
        <input
          type="text"
          value={editedTitle}
          onChange={(e) => handlers.setEditedTitle(e.target.value)}
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

      {/* Outfit Details */}
      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: 'white', marginBottom: '1rem' }}>Outfit Details</h3>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Style Genre
          </label>
          <input
            type="text"
            value={editedData.style_genre || ''}
            onChange={(e) => handlers.updateField('style_genre', e.target.value)}
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

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Formality
          </label>
          <input
            type="text"
            value={editedData.formality || ''}
            onChange={(e) => handlers.updateField('formality', e.target.value)}
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

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Aesthetic
          </label>
          <input
            type="text"
            value={editedData.aesthetic || ''}
            onChange={(e) => handlers.updateField('aesthetic', e.target.value)}
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
      </div>

      {/* Clothing Items */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ color: 'white', margin: 0 }}>
            Clothing Items ({(editedData.clothing_items || []).length})
          </h3>
          <button
            onClick={addNewItem}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(102, 126, 234, 0.2)',
              border: '1px solid rgba(102, 126, 234, 0.3)',
              borderRadius: '6px',
              color: '#667eea',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            + Add Item
          </button>
        </div>

        {(editedData.clothing_items || []).map((item, index) => (
          <div
            key={index}
            style={{
              marginBottom: '0.75rem',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              overflow: 'hidden'
            }}
          >
            {/* Item Header */}
            <div
              onClick={() => toggleItem(index)}
              style={{
                padding: '1rem',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                background: 'rgba(255, 255, 255, 0.02)'
              }}
            >
              <span style={{ color: 'white', fontWeight: 500 }}>
                {item.item || `Item ${index + 1}`}
              </span>
              <span style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                {expandedItems[index] ? '▼' : '▶'}
              </span>
            </div>

            {/* Item Content */}
            {expandedItems[index] && (
              <div style={{ padding: '1rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                {editingItems[index] ? (
                  // Edit Mode
                  <>
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        Item Type
                      </label>
                      <input
                        type="text"
                        value={item.item || ''}
                        onChange={(e) => updateItemField(index, 'item', e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          background: 'rgba(0, 0, 0, 0.3)',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                          borderRadius: '6px',
                          color: 'white',
                          fontSize: '0.9rem'
                        }}
                      />
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        Color
                      </label>
                      <input
                        type="text"
                        value={item.color || ''}
                        onChange={(e) => updateItemField(index, 'color', e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          background: 'rgba(0, 0, 0, 0.3)',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                          borderRadius: '6px',
                          color: 'white',
                          fontSize: '0.9rem'
                        }}
                      />
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        Fabric
                      </label>
                      <input
                        type="text"
                        value={item.fabric || ''}
                        onChange={(e) => updateItemField(index, 'fabric', e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          background: 'rgba(0, 0, 0, 0.3)',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                          borderRadius: '6px',
                          color: 'white',
                          fontSize: '0.9rem'
                        }}
                      />
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        Details
                      </label>
                      <textarea
                        value={item.details || ''}
                        onChange={(e) => updateItemField(index, 'details', e.target.value)}
                        rows="3"
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          background: 'rgba(0, 0, 0, 0.3)',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                          borderRadius: '6px',
                          color: 'white',
                          fontSize: '0.9rem',
                          resize: 'vertical',
                          fontFamily: 'inherit'
                        }}
                      />
                    </div>
                    <button
                      onClick={() => toggleEdit(index)}
                      style={{
                        padding: '0.5rem 1rem',
                        background: 'rgba(102, 126, 234, 0.2)',
                        border: '1px solid rgba(102, 126, 234, 0.3)',
                        borderRadius: '6px',
                        color: '#667eea',
                        cursor: 'pointer',
                        fontSize: '0.9rem'
                      }}
                    >
                      Done Editing
                    </button>
                  </>
                ) : (
                  // View Mode
                  <>
                    <div style={{ marginBottom: '0.5rem', color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
                      <strong>Item:</strong> {item.item || 'N/A'}
                    </div>
                    <div style={{ marginBottom: '0.5rem', color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
                      <strong>Color:</strong> {item.color || 'N/A'}
                    </div>
                    <div style={{ marginBottom: '0.5rem', color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
                      <strong>Fabric:</strong> {item.fabric || 'N/A'}
                    </div>
                    <div style={{ marginBottom: '1rem', color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
                      <strong>Details:</strong> {item.details || 'N/A'}
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={() => toggleEdit(index)}
                        style={{
                          padding: '0.5rem 1rem',
                          background: 'rgba(102, 126, 234, 0.2)',
                          border: '1px solid rgba(102, 126, 234, 0.3)',
                          borderRadius: '6px',
                          color: '#667eea',
                          cursor: 'pointer',
                          fontSize: '0.9rem'
                        }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteItem(index)}
                        style={{
                          padding: '0.5rem 1rem',
                          background: 'rgba(255, 100, 100, 0.2)',
                          border: '1px solid rgba(255, 100, 100, 0.3)',
                          borderRadius: '6px',
                          color: '#ff6b6b',
                          cursor: 'pointer',
                          fontSize: '0.9rem'
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default OutfitEditor
