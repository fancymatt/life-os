import api from '../../../api/client'
import { formatDate } from './helpers'
import OutfitEditor from './OutfitEditor'
import EntityPreviewImage from '../EntityPreviewImage'

/**
 * Preset Entity Configurations
 *
 * Factory function and configurations for all preset-based entities
 * (outfits, expressions, makeup, hair styles, hair colors, visual styles, art styles, accessories)
 */

/**
 * Create a preset-based entity configuration
 * @param {Object} options - Configuration options
 * @returns {Object} Entity configuration object
 */
const createPresetConfig = (options) => ({
  entityType: options.entityType,
  title: options.title,
  icon: options.icon,
  emptyMessage: `No ${options.title.toLowerCase()} yet. Analyze your first ${options.entityType}!`,
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  defaultSort: 'newest',
  searchFields: ['display_name'],
  category: options.category,

  actions: [
    {
      label: `Analyze ${options.title}`,
      icon: '+',
      primary: true,
      path: `/tools/analyzers/${options.analyzerPath}`
    }
  ],

  fetchEntities: async () => {
    const response = await api.get(`/presets/${options.category}`)
    return (response.data.presets || []).map(preset => ({
      id: preset.preset_id,
      title: preset.display_name || `Untitled ${options.title}`,
      presetId: preset.preset_id,
      category: preset.category,
      createdAt: preset.created_at,
      data: {} // Empty initially, will be loaded on-demand in edit mode
    }))
  },

  loadFullData: async (entity) => {
    // Fetch the full preset data from the individual endpoint
    const response = await api.get(`/presets/${options.category}/${entity.presetId}`)
    return response.data
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (entity) => (
    <div className="entity-card">
      <div className="entity-card-image" style={{ height: '280px' }}>
        <EntityPreviewImage
          entityType={options.category}
          entityId={entity.presetId}
          previewImageUrl={`/api/presets/${options.category}/${entity.presetId}/preview`}
          standInIcon={options.icon}
          size="small"
          shape="square"
        />
      </div>
      <div className="entity-card-content">
        <h3 className="entity-card-title">{entity.title}</h3>
        {formatDate(entity.createdAt) && (
          <p className="entity-card-date">{formatDate(entity.createdAt)}</p>
        )}
      </div>
    </div>
  ),

  renderPreview: (entity, onUpdate) => {
    const handleGeneratePreview = async () => {
      await api.post(`/presets/${options.category}/${entity.presetId}/generate-preview`)
    }

    return (
      <div style={{ padding: '1rem' }}>
        <EntityPreviewImage
          entityType={options.category}
          entityId={entity.presetId}
          previewImageUrl={`/api/presets/${options.category}/${entity.presetId}/preview`}
          standInIcon={options.icon}
          size="medium"
          shape="square"
          onUpdate={onUpdate}
        />

        <button
          onClick={handleGeneratePreview}
          style={{
            width: '100%',
            marginTop: '1rem',
            padding: '0.75rem',
            background: 'rgba(168, 85, 247, 0.2)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            borderRadius: '8px',
            color: 'rgba(168, 85, 247, 1)',
            cursor: 'pointer',
            fontSize: '0.95rem',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(168, 85, 247, 0.3)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(168, 85, 247, 0.2)'
          }}
        >
          🎨 Generate Preview
        </button>
      </div>
    )
  },

  renderDetail: (entity) => (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ color: 'white', margin: '0 0 1.5rem 0' }}>{entity.title}</h2>
      <div style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
        {Object.entries(entity.data || {}).map(([key, value]) => {
          if (key === '_metadata') return null
          return (
            <div key={key} style={{ marginBottom: '1rem' }}>
              <strong style={{ color: 'rgba(255, 255, 255, 0.9)', textTransform: 'capitalize' }}>
                {key.replace(/_/g, ' ')}:
              </strong>{' '}
              {Array.isArray(value) ? value.join(', ') : value}
            </div>
          )
        })}
      </div>
      {formatDate(entity.createdAt) && (
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', margin: 0 }}>
            <strong>Created:</strong> {formatDate(entity.createdAt)}
          </p>
        </div>
      )}
    </div>
  ),

  renderEdit: (entity, editedData, editedTitle, handlers) => (
    <div style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Name
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

      <div style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
        {Object.entries(editedData || {}).map(([key, value]) => {
          if (key === '_metadata') return null

          // Check if value is array of objects (complex structure)
          const isComplexArray = Array.isArray(value) && value.length > 0 && typeof value[0] === 'object'

          return (
            <div key={key} style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', textTransform: 'capitalize', fontWeight: 500 }}>
                {key.replace(/_/g, ' ')}
              </label>
              {isComplexArray ? (
                // Handle arrays of objects as JSON
                <textarea
                  value={JSON.stringify(value, null, 2)}
                  onChange={(e) => {
                    try {
                      const parsed = JSON.parse(e.target.value)
                      handlers.updateField(key, parsed)
                    } catch (err) {
                      // Invalid JSON, update the raw string so user can continue editing
                      // We'll use a temporary marker to indicate this is unparsed JSON
                      handlers.updateField(key + '_temp', e.target.value)
                    }
                  }}
                  rows="10"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '0.85rem',
                    resize: 'vertical',
                    fontFamily: 'monospace'
                  }}
                />
              ) : Array.isArray(value) ? (
                // Handle simple arrays as comma-separated values
                <input
                  type="text"
                  value={value.join(', ')}
                  onChange={(e) => handlers.updateField(key, e.target.value.split(',').map(v => v.trim()))}
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
              ) : (
                // Handle simple string/number values
                <textarea
                  value={value || ''}
                  onChange={(e) => handlers.updateField(key, e.target.value)}
                  rows="3"
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
              )}
            </div>
          )
        })}
      </div>
    </div>
  ),

  saveEntity: async (entity, updates) => {
    // Save the preset
    await api.put(
      `/presets/${options.category}/${entity.presetId}`,
      {
        data: updates.data,
        display_name: updates.title
      }
    )

    // Reload the full preset data after save (PUT only returns success message)
    const response = await api.get(`/presets/${options.category}/${entity.presetId}`)
    return response.data
  },

  deleteEntity: async (entity) => {
    await api.delete(`/presets/${options.category}/${entity.presetId}`)
  }
})

// =============================================================================
// OUTFITS (with custom editor)
// =============================================================================

export const outfitsConfig = {
  ...createPresetConfig({
    entityType: 'outfit',
    title: 'Outfits',
    icon: '👔',
    category: 'outfits',
    analyzerPath: 'outfit'
  }),
  // Override renderEdit with custom outfit editor
  renderEdit: (entity, editedData, editedTitle, handlers) => (
    <OutfitEditor editedData={editedData} editedTitle={editedTitle} handlers={handlers} />
  )
}

// =============================================================================
// ALL OTHER PRESET-BASED ENTITIES
// =============================================================================

export const hairStylesConfig = {
  ...createPresetConfig({
    entityType: 'hair style',
    title: 'Hair Styles',
    icon: '💇',
    category: 'hair_styles',
    analyzerPath: 'hair-style'
  }),
  enableGallery: true
}

export const hairColorsConfig = {
  ...createPresetConfig({
    entityType: 'hair color',
    title: 'Hair Colors',
    icon: '🎨',
    category: 'hair_colors',
    analyzerPath: 'hair-color'
  }),
  enableGallery: true
}

export const visualStylesConfig = {
  ...createPresetConfig({
    entityType: 'visual style',
    title: 'Visual Styles',
    icon: '📸',
    category: 'visual_styles',
    analyzerPath: 'visual-style'
  }),
  enableGallery: true
}

export const artStylesConfig = {
  ...createPresetConfig({
    entityType: 'art style',
    title: 'Art Styles',
    icon: '🎨',
    category: 'art_styles',
    analyzerPath: 'art-style'
  }),
  enableGallery: true
}

export const accessoriesConfig = {
  ...createPresetConfig({
    entityType: 'accessory',
    title: 'Accessories',
    icon: '👓',
    category: 'accessories',
    analyzerPath: 'accessories'
  }),
  enableGallery: true
}

export const expressionsConfig = {
  ...createPresetConfig({
    entityType: 'expression',
    title: 'Expressions',
    icon: '😊',
    category: 'expressions',
    analyzerPath: 'expression'
  }),
  enableGallery: true
}

export const makeupsConfig = {
  ...createPresetConfig({
    entityType: 'makeup',
    title: 'Makeup',
    icon: '💄',
    category: 'makeup',
    analyzerPath: 'makeup'
  }),
  enableGallery: true
}
