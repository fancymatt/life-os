import api from '../../../api/client'
import { formatDate } from './helpers'

/**
 * Story Tools Entity Configurations
 *
 * Configurations for story parameter presets and agent configurations
 */

// =============================================================================
// STORY PARAMETER PRESETS (themes, audiences, prose styles)
// =============================================================================

/**
 * Create a story preset configuration
 * @param {Object} options - Configuration options
 * @returns {Object} Entity configuration object
 */
const createStoryPresetConfig = (options) => ({
  entityType: options.entityType,
  title: options.title,
  icon: options.icon,
  emptyMessage: `No ${options.title.toLowerCase()} yet. Create your first ${options.entityType}!`,
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  defaultSort: 'name',
  searchFields: ['display_name'],
  category: options.category,

  actions: [
    {
      label: `New ${options.entityType.charAt(0).toUpperCase() + options.entityType.slice(1)}`,
      icon: '+',
      primary: true,
      onClick: async () => {
        const name = prompt(`Enter a name for the new ${options.entityType}:`)
        if (!name) return

        try {
          // Create a minimal preset structure based on type
          let defaultData = {
            description: `A ${options.entityType} preset`
          }

          // Add type-specific default fields
          if (options.category === 'story_themes') {
            defaultData.keywords = []
            defaultData.atmosphere = ''
          } else if (options.category === 'story_audiences') {
            defaultData.age_range = ''
            defaultData.reading_level = ''
          } else if (options.category === 'story_prose_styles') {
            defaultData.tone = ''
            defaultData.pacing = ''
            defaultData.vocabulary_level = ''
          }

          const response = await api.post(`/presets/${options.category}`, {
            name: name.toLowerCase().replace(/\s+/g, '_'),
            data: defaultData,
            notes: `Created via entity browser`
          })

          // Refresh the page to show the new entity
          window.location.reload()
        } catch (err) {
          alert(`Failed to create ${options.entityType}: ${err.response?.data?.detail || err.message}`)
        }
      }
    }
  ],

  fetchEntities: async () => {
    const response = await api.get(`/presets/${options.category}`)
    return (response.data.presets || []).map(preset => ({
      id: preset.preset_id,
      title: preset.display_name || preset.suggested_name || `Untitled ${options.title}`,
      presetId: preset.preset_id,
      category: preset.category,
      createdAt: preset.created_at,
      data: {} // Empty initially, will be loaded on-demand in edit mode
    }))
  },

  loadFullData: async (entity) => {
    const response = await api.get(`/presets/${options.category}/${entity.presetId}`)
    return response.data
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (entity) => (
    <div className="entity-card">
      <div className="entity-card-content" style={{ padding: '1.5rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem', textAlign: 'center' }}>
          {options.icon}
        </div>
        <h3 className="entity-card-title" style={{ textAlign: 'center' }}>{entity.title}</h3>
        {entity.data?.description && (
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', marginTop: '0.5rem', textAlign: 'center' }}>
            {entity.data.description}
          </p>
        )}
      </div>
    </div>
  ),

  renderPreview: (entity) => (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>{options.icon}</div>
      <h2 style={{ color: 'white', margin: 0 }}>{entity.title}</h2>
    </div>
  ),

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
              {Array.isArray(value) ? (
                <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
                  {value.map((item, idx) => <li key={idx}>{item}</li>)}
                </ul>
              ) : typeof value === 'object' ? (
                <pre style={{
                  background: 'rgba(0, 0, 0, 0.3)',
                  padding: '0.5rem',
                  borderRadius: '4px',
                  overflowX: 'auto',
                  fontSize: '0.85rem'
                }}>
                  {JSON.stringify(value, null, 2)}
                </pre>
              ) : (
                value
              )}
            </div>
          )
        })}
      </div>
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
          const isObject = typeof value === 'object' && !Array.isArray(value)

          return (
            <div key={key} style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', textTransform: 'capitalize', fontWeight: 500 }}>
                {key.replace(/_/g, ' ')}
              </label>
              {isComplexArray || isObject ? (
                // Handle objects and arrays of objects as JSON
                <textarea
                  value={JSON.stringify(value, null, 2)}
                  onChange={(e) => {
                    try {
                      const parsed = JSON.parse(e.target.value)
                      handlers.updateField(key, parsed)
                    } catch (err) {
                      // Invalid JSON, allow user to continue editing
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
    const response = await api.put(
      `/presets/${options.category}/${entity.presetId}`,
      {
        data: updates.data,
        display_name: updates.title
      }
    )
    return response.data
  },

  deleteEntity: async (entity) => {
    await api.delete(`/presets/${options.category}/${entity.presetId}`)
  }
})

// =============================================================================
// AGENT CONFIGURATIONS (planner, writer, illustrator)
// =============================================================================

/**
 * Create an agent config configuration
 * @param {Object} options - Configuration options
 * @returns {Object} Entity configuration object
 */
const createAgentConfigConfig = (options) => ({
  entityType: options.entityType,
  title: options.title,
  icon: options.icon,
  emptyMessage: `No ${options.title.toLowerCase()} yet. Create your first ${options.entityType}!`,
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  defaultSort: 'name',
  searchFields: ['display_name'],
  agentType: options.agentType, // story_planner, story_writer, story_illustrator

  actions: [
    {
      label: `New ${options.entityType.charAt(0).toUpperCase() + options.entityType.slice(1)}`,
      icon: '+',
      primary: true,
      onClick: async () => {
        const name = prompt(`Enter a name for the new ${options.entityType} (use lowercase with underscores):`)
        if (!name) return

        const configId = name.toLowerCase().replace(/\s+/g, '_')
        const displayName = prompt(`Enter a display name:`) || name

        try {
          // Load the default config to use as a template
          const defaultConfig = await api.get(`/configs/agent_configs/${options.agentType}/default`)

          // Create new config based on default, but with new ID and display name
          const newConfig = {
            ...defaultConfig.data,
            config_id: configId,
            display_name: displayName,
            description: `Custom ${options.entityType} configuration`
          }

          const response = await api.post(`/configs/agent_configs/${options.agentType}`, newConfig)

          // Refresh the page to show the new entity
          window.location.reload()
        } catch (err) {
          alert(`Failed to create ${options.entityType}: ${err.response?.data?.detail || err.message}`)
        }
      }
    }
  ],

  fetchEntities: async () => {
    const response = await api.get(`/configs/agent_configs/${options.agentType}`)
    return (response.data.configs || []).map(config => ({
      id: config.config_id,
      title: config.display_name || config.config_id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      configId: config.config_id,
      description: config.description || '',
      data: {} // Empty initially, will be loaded on-demand in edit mode
    }))
  },

  loadFullData: async (entity) => {
    const response = await api.get(`/configs/agent_configs/${options.agentType}/${entity.configId}`)
    return response.data
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (entity) => (
    <div className="entity-card">
      <div className="entity-card-content" style={{ padding: '1.5rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem', textAlign: 'center' }}>
          {options.icon}
        </div>
        <h3 className="entity-card-title" style={{ textAlign: 'center' }}>{entity.title}</h3>
        {entity.description && (
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', marginTop: '0.5rem', textAlign: 'center' }}>
            {entity.description}
          </p>
        )}
      </div>
    </div>
  ),

  renderPreview: (entity) => (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>{options.icon}</div>
      <h2 style={{ color: 'white', margin: 0 }}>{entity.title}</h2>
      {entity.description && (
        <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginTop: '1rem' }}>{entity.description}</p>
      )}
    </div>
  ),

  renderDetail: (entity) => (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ color: 'white', margin: '0 0 1.5rem 0' }}>{entity.title}</h2>
      {entity.data?.description && (
        <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '1.5rem' }}>{entity.data.description}</p>
      )}
      <div style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
        <pre style={{
          background: 'rgba(0, 0, 0, 0.3)',
          padding: '1rem',
          borderRadius: '8px',
          overflowX: 'auto',
          fontSize: '0.85rem',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word'
        }}>
          {JSON.stringify(entity.data, null, 2)}
        </pre>
      </div>
    </div>
  ),

  renderEdit: (entity, editedData, editedTitle, handlers) => (
    <div style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Display Name
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

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Full Configuration (JSON)
        </label>
        <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
          Edit the full configuration as JSON. Includes prompt templates, parameters, and all settings.
        </p>
        <textarea
          value={JSON.stringify(editedData, null, 2)}
          onChange={(e) => {
            try {
              const parsed = JSON.parse(e.target.value)
              // Update all fields at once
              Object.keys(parsed).forEach(key => {
                if (key !== 'config_id') { // Preserve config_id
                  handlers.updateField(key, parsed[key])
                }
              })
            } catch (err) {
              // Invalid JSON, allow user to continue editing
            }
          }}
          rows="25"
          style={{
            width: '100%',
            padding: '1rem',
            background: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            color: 'white',
            fontSize: '0.85rem',
            resize: 'vertical',
            fontFamily: 'monospace',
            lineHeight: '1.5'
          }}
        />
      </div>
    </div>
  ),

  saveEntity: async (entity, updates) => {
    const response = await api.put(
      `/configs/agent_configs/${options.agentType}/${entity.configId}`,
      updates.data
    )
    return response.data
  },

  deleteEntity: async (entity) => {
    if (entity.configId === 'default') {
      throw new Error('Cannot delete the default configuration')
    }
    await api.delete(`/configs/agent_configs/${options.agentType}/${entity.configId}`)
  }
})

// =============================================================================
// EXPORT ALL STORY TOOL CONFIGURATIONS
// =============================================================================

export const storyThemesConfig = createStoryPresetConfig({
  entityType: 'story theme',
  title: 'Story Themes',
  icon: '📚',
  category: 'story_themes'
})

export const storyAudiencesConfig = createStoryPresetConfig({
  entityType: 'story audience',
  title: 'Story Audiences',
  icon: '👥',
  category: 'story_audiences'
})

export const storyProseStylesConfig = createStoryPresetConfig({
  entityType: 'prose style',
  title: 'Prose Styles',
  icon: '✍️',
  category: 'story_prose_styles'
})

export const storyPlannerConfigsConfig = createAgentConfigConfig({
  entityType: 'planner configuration',
  title: 'Story Planner Configs',
  icon: '📋',
  agentType: 'story_planner'
})

export const storyWriterConfigsConfig = createAgentConfigConfig({
  entityType: 'writer configuration',
  title: 'Story Writer Configs',
  icon: '📝',
  agentType: 'story_writer'
})

export const storyIllustratorConfigsConfig = createAgentConfigConfig({
  entityType: 'cinematography configuration',
  title: 'Cinematography',
  icon: '🎬',
  agentType: 'story_illustrator'
})
