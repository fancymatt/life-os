import { Link } from 'react-router-dom'

/**
 * RelatedEntityChip Component
 *
 * Displays a clickable chip for an entity reference (used in image detail views, etc.)
 * Handles routing, styling, and display for all entity types.
 *
 * @param {Object} entity - Entity data
 * @param {string} entity.entity_id - ID of the entity
 * @param {string} entity.entity_name - Display name of the entity
 * @param {string} entity.entity_type - Type of entity (character, clothing_item, visual_style, etc.)
 * @param {string} [entity.role] - Optional role/category (e.g., "subject", "outerwear", "visual_style")
 * @param {string} [entity.preset_category] - Optional preset category for routing presets
 */
function RelatedEntityChip({ entity }) {
  const getEntityRoute = (entity) => {
    // For presets, use the preset_category to determine the route
    if ((entity.entity_type === 'preset' || entity.entity_type === 'visual_style') && entity.preset_category) {
      const categoryRoutes = {
        'visual_styles': '/entities/visual-styles',
        'expressions': '/entities/expressions',
        'accessories': '/entities/accessories',
        'art_styles': '/entities/art-styles',
        'hair_colors': '/entities/hair-colors',
        'hair_styles': '/entities/hair-styles',
        'makeup': '/entities/makeup',
        'story_themes': '/entities/story-themes',
        'story_prose_styles': '/entities/story-prose-styles',
        'story_audiences': '/entities/story-audiences'
      }
      return categoryRoutes[entity.preset_category] || '/entities/visual-styles'
    }

    // Default routes for non-preset entities
    const routes = {
      'character': '/entities/characters',
      'clothing_item': '/entities/clothing-items',
      'visual_style': '/entities/visual-styles',
      'preset': '/entities/visual-styles',
      'story_theme': '/entities/story-themes'
    }
    return routes[entity.entity_type] || '/entities'
  }

  return (
    <Link
      to={`${getEntityRoute(entity)}/${entity.entity_id}`}
      style={{
        padding: '0.5rem 0.75rem',
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '6px',
        fontSize: '0.85rem',
        color: 'rgba(255, 255, 255, 0.9)',
        textDecoration: 'none',
        transition: 'all 0.2s',
        display: 'inline-block'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)'
        e.currentTarget.style.borderColor = 'rgba(102, 126, 234, 0.5)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'
        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
      }}
    >
      {entity.entity_name || entity.entity_id}
      {entity.role && (
        <span style={{ color: 'rgba(255, 255, 255, 0.5)', marginLeft: '0.5rem' }}>
          ({entity.role})
        </span>
      )}
    </Link>
  )
}

export default RelatedEntityChip
