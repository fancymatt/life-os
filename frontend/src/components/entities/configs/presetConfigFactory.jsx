import api from '../../../api/client'
import { formatDate } from './helpers'
import EntityPreviewImage from '../EntityPreviewImage'

/**
 * Factory function to create entity configs for preset-based entities
 *
 * All preset-based entities share the same API structure via /presets/{category}
 * and have consistent JSON structure with _metadata.preset_id and _metadata.display_name
 */
export function createPresetConfig({
  category,           // API category name (e.g., 'hair_styles')
  title,              // Display title (e.g., 'Hair Styles')
  icon,               // Emoji icon (e.g., '💇')
  emptyMessage,       // Message when no entities exist
  descriptionField,   // Field to use for card description (optional)
  detailFields = []   // Array of {key, label} objects for detail view
}) {
  return {
    entityType: category.replace(/_/g, ' '),
    title,
    icon,
    emptyMessage: emptyMessage || `No ${title.toLowerCase()} yet. Create your first one!`,
    enableSearch: true,
    enableSort: true,
    enableEdit: false,  // Presets are typically not editable via UI
    defaultSort: 'newest',
    searchFields: ['display_name'],

    fetchEntities: async () => {
      const response = await api.get(`/presets/${category}`)
      const presets = response.data.presets || response.data || []

      return presets.map(preset => ({
        id: preset._metadata?.preset_id || preset.preset_id,
        presetId: preset._metadata?.preset_id || preset.preset_id,
        title: preset._metadata?.display_name || preset.display_name || preset.suggested_name || 'Unnamed',
        displayName: preset._metadata?.display_name || preset.display_name || preset.suggested_name,
        previewImageUrl: `/presets/${category}/${preset._metadata?.preset_id || preset.preset_id}_preview.png`,
        createdAt: preset._metadata?.created_at || preset.created_at,
        data: preset  // Store full preset data
      }))
    },

    gridConfig: {
      columns: 'repeat(auto-fill, minmax(280px, 1fr))',
      gap: '1.5rem'
    },

    renderCard: (entity) => (
      <div className="entity-card">
        <div className="entity-card-image" style={{ height: '280px' }}>
          <EntityPreviewImage
            entityType={category}
            entityId={entity.presetId}
            previewImageUrl={entity.previewImageUrl}
            standInIcon={icon}
            size="small"
            shape="square"
          />
        </div>
        <div className="entity-card-content">
          <h3 className="entity-card-title">{entity.displayName}</h3>
          {descriptionField && entity.data[descriptionField] && (
            <p className="entity-card-description" style={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical'
            }}>
              {entity.data[descriptionField]}
            </p>
          )}
          {formatDate(entity.createdAt) && (
            <p className="entity-card-date">{formatDate(entity.createdAt)}</p>
          )}
        </div>
      </div>
    ),

    renderPreview: (entity) => (
      <EntityPreviewImage
        entityType={category}
        entityId={entity.presetId}
        previewImageUrl={entity.previewImageUrl}
        standInIcon={icon}
        size="medium"
        shape="square"
      />
    ),

    renderDetail: (entity) => (
      <div style={{ padding: '2rem' }}>
        <h2 style={{ color: 'white', margin: '0 0 1.5rem 0' }}>{entity.displayName}</h2>

        {/* Preview Image */}
        <div style={{ marginBottom: '2rem' }}>
          <EntityPreviewImage
            entityType={category}
            entityId={entity.presetId}
            previewImageUrl={entity.previewImageUrl}
            standInIcon={icon}
            size="large"
            shape="square"
          />
        </div>

        {/* Detail Fields */}
        {detailFields.map(({ key, label }) => {
          const value = entity.data[key]
          if (!value) return null

          return (
            <div key={key} style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
                {label}
              </h3>
              {Array.isArray(value) ? (
                <ul style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0, paddingLeft: '1.5rem' }}>
                  {value.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>
                  {value}
                </p>
              )}
            </div>
          )
        })}

        {formatDate(entity.createdAt) && (
          <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', margin: 0 }}>
              <strong>Created:</strong> {formatDate(entity.createdAt)}
            </p>
          </div>
        )}
      </div>
    ),

    deleteEntity: async (entity) => {
      await api.delete(`/presets/${category}/${entity.presetId}`)
    }
  }
}
