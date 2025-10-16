import api from '../../../api/client'
import { formatDate, getPreview } from './helpers'

/**
 * Characters Entity Configuration
 */
export const charactersConfig = {
  entityType: 'character',
  title: 'Characters',
  icon: '👤',
  emptyMessage: 'No characters yet. Create your first character!',
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  defaultSort: 'newest',
  searchFields: ['name', 'visual_description', 'personality'],

  actions: [
    {
      label: 'New Character',
      icon: '+',
      primary: true,
      onClick: () => {
        // TODO: Open character creation modal/form
        alert('Character creation UI coming soon!')
      }
    }
  ],

  fetchEntities: async () => {
    const response = await api.get('/characters')
    return (response.data.characters || []).map(char => ({
      id: char.character_id,
      characterId: char.character_id,
      title: char.name,
      name: char.name,
      visualDescription: char.visual_description,
      personality: char.personality,
      referenceImageUrl: char.reference_image_url,
      tags: char.tags || [],
      createdAt: char.created_at,
      metadata: char.metadata || {}
    }))
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (character) => (
    <div className="entity-card">
      <div className="entity-card-image" style={{ height: '280px' }}>
        {character.referenceImageUrl ? (
          <img
            src={character.referenceImageUrl}
            alt={character.name}
            onError={(e) => {
              e.target.style.display = 'none'
              e.target.parentElement.innerHTML = '<div class="entity-card-placeholder">👤</div>'
            }}
          />
        ) : (
          <div className="entity-card-placeholder">👤</div>
        )}
      </div>
      <div className="entity-card-content">
        <h3 className="entity-card-title">{character.name}</h3>
        <p className="entity-card-description">
          {getPreview(character.visualDescription || character.personality || 'No description', 20)}
        </p>
        {character.tags.length > 0 && (
          <div className="entity-card-meta">
            {character.tags.slice(0, 3).map((tag, idx) => (
              <span key={idx} className="entity-card-meta-item">
                {tag}
              </span>
            ))}
          </div>
        )}
        {formatDate(character.createdAt) && (
          <p className="entity-card-date">{formatDate(character.createdAt)}</p>
        )}
      </div>
    </div>
  ),

  renderPreview: (character) => (
    <>
      {character.referenceImageUrl ? (
        <img
          src={character.referenceImageUrl}
          alt={character.name}
          style={{ width: '100%', height: 'auto', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)' }}
          onError={(e) => e.target.style.display = 'none'}
        />
      ) : (
        <div style={{
          width: '100%',
          aspectRatio: '3/4',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '8rem',
          opacity: 0.3
        }}>
          👤
        </div>
      )}
    </>
  ),

  renderDetail: (character) => (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ color: 'white', margin: '0 0 1.5rem 0' }}>{character.name}</h2>

      {character.visualDescription && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
            Visual Description
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>
            {character.visualDescription}
          </p>
        </div>
      )}

      {character.personality && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
            Personality
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>
            {character.personality}
          </p>
        </div>
      )}

      {character.tags.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
            Tags
          </h3>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {character.tags.map((tag, idx) => (
              <span
                key={idx}
                style={{
                  padding: '0.25rem 0.75rem',
                  background: 'rgba(102, 126, 234, 0.2)',
                  border: '1px solid rgba(102, 126, 234, 0.3)',
                  borderRadius: '12px',
                  color: '#667eea',
                  fontSize: '0.85rem'
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {formatDate(character.createdAt) && (
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', margin: 0 }}>
            <strong>Created:</strong> {formatDate(character.createdAt)}
          </p>
        </div>
      )}
    </div>
  ),

  renderEdit: (character, editedData, editedTitle, handlers) => (
    <div>
      {/* Name Field */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Character Name
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

      {/* Visual Description */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Visual Description
        </label>
        <textarea
          value={editedData.visual_description || ''}
          onChange={(e) => handlers.updateField('visual_description', e.target.value)}
          rows="4"
          placeholder="Describe the character's physical appearance..."
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

      {/* Personality */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Personality
        </label>
        <textarea
          value={editedData.personality || ''}
          onChange={(e) => handlers.updateField('personality', e.target.value)}
          rows="4"
          placeholder="Describe the character's personality traits..."
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

      {/* Tags */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Tags (comma-separated)
        </label>
        <input
          type="text"
          value={(editedData.tags || []).join(', ')}
          onChange={(e) => handlers.updateField('tags', e.target.value.split(',').map(t => t.trim()).filter(t => t))}
          placeholder="protagonist, hero, adventure..."
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
  ),

  saveEntity: async (character, updates) => {
    const response = await api.put(
      `/characters/${character.characterId}`,
      {
        name: updates.title,
        visual_description: updates.data.visual_description,
        personality: updates.data.personality,
        tags: updates.data.tags
      }
    )
    return response.data
  },

  deleteEntity: async (character) => {
    await api.delete(`/characters/${character.characterId}`)
  }
}
