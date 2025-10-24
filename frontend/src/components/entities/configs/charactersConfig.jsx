import api from '../../../api/client'
import { formatDate, getPreview } from './helpers'
import LazyImage from '../LazyImage'
import ReAnalyzeButton from '../ReAnalyzeButton'
import TagManager from '../../tags/TagManager'

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
  enableGallery: true,
  showRefreshButton: false,  // Characters auto-refresh on creation
  defaultSort: 'newest',
  searchFields: ['name', 'visual_description', 'physical_description', 'personality', 'age', 'skin_tone', 'face_description', 'hair_description', 'body_description'],

  // actions will be overridden by CharactersEntity page to provide modal handler
  actions: [],

  fetchEntities: async () => {
    const response = await api.get('/characters/')
    return (response.data.characters || []).map(char => ({
      id: char.character_id,
      characterId: char.character_id,
      title: char.name,
      name: char.name,
      visualDescription: char.visual_description,
      physicalDescription: char.physical_description,
      personality: char.personality,
      referenceImageUrl: char.reference_image_url,
      tags: char.tags || [],
      createdAt: char.created_at,
      archived: char.archived || false,
      archivedAt: char.archived_at,
      metadata: char.metadata || {},
      // Detailed appearance fields
      age: char.age,
      skinTone: char.skin_tone,
      faceDescription: char.face_description,
      hairDescription: char.hair_description,
      bodyDescription: char.body_description,
      // Wrap editable fields in data property for EntityBrowser
      data: {
        personality: char.personality,
        age: char.age || '',
        skin_tone: char.skin_tone || '',
        face_description: char.face_description || '',
        hair_description: char.hair_description || '',
        body_description: char.body_description || ''
      }
    }))
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (character) => (
    <div className="entity-card" style={{ position: 'relative' }}>
      {character.archived && (
        <div style={{
          position: 'absolute',
          top: '0.5rem',
          right: '0.5rem',
          background: 'rgba(255, 152, 0, 0.9)',
          color: 'white',
          padding: '0.25rem 0.5rem',
          borderRadius: '4px',
          fontSize: '0.75rem',
          fontWeight: 'bold',
          zIndex: 10,
          boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
        }}>
          📦 ARCHIVED
        </div>
      )}
      <div className="entity-card-image" style={{ height: '280px', opacity: character.archived ? 0.6 : 1 }}>
        {character.referenceImageUrl ? (
          <LazyImage
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
          {getPreview(character.visualDescription || character.physicalDescription || character.personality || 'No description', 20)}
        </p>
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

  renderDetail: (character, handleBackToList, onUpdate) => (
    <div style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
        <h2 style={{ color: 'white', margin: 0 }}>{character.name}</h2>
        <ReAnalyzeButton character={character} onUpdate={onUpdate} variant="compact" />
      </div>

      {/* Tags (readonly) */}
      {character.tags && character.tags.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <TagManager
            entityType="character"
            entityId={character.characterId}
            tags={character.tags}
            readonly={true}
          />
        </div>
      )}

        {/* Overall Description */}
        {character.physicalDescription && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
            Overall Appearance
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>
            {character.physicalDescription}
          </p>
        </div>
      )}

      {/* Detailed Appearance Fields */}
      {(character.age || character.skinTone || character.faceDescription || character.hairDescription || character.bodyDescription) && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.75rem 0' }}>
            Appearance Details
          </h3>
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            {character.age && (
              <div>
                <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Age:</strong>{' '}
                <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{character.age}</span>
              </div>
            )}
            {character.skinTone && (
              <div>
                <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Skin Tone:</strong>{' '}
                <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{character.skinTone}</span>
              </div>
            )}
            {character.faceDescription && (
              <div>
                <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Face:</strong>{' '}
                <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{character.faceDescription}</span>
              </div>
            )}
            {character.hairDescription && (
              <div>
                <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Hair:</strong>{' '}
                <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{character.hairDescription}</span>
              </div>
            )}
            {character.bodyDescription && (
              <div>
                <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Build:</strong>{' '}
                <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{character.bodyDescription}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Personality */}
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
      {/* Re-Analyze Button */}
      <ReAnalyzeButton
        character={character}
        variant="edit"
        onUpdate={(data) => {
          // Update the edited data with new appearance fields
          if (handlers.updateField) {
            handlers.updateField('age', data.age || '')
            handlers.updateField('skin_tone', data.skin_tone || '')
            handlers.updateField('face_description', data.face_description || '')
            handlers.updateField('hair_description', data.hair_description || '')
            handlers.updateField('body_description', data.body_description || '')
          }
        }}
      />

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

      {/* Tags */}
      <TagManager
        entityType="character"
        entityId={character.characterId}
        tags={character.tags || []}
        onTagsChange={(newTags) => {
          // Trigger entity refresh to show updated tags
          if (handleEntityUpdate) {
            handleEntityUpdate()
          }
        }}
      />

      {/* Appearance Details Section */}
      <div style={{ marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem', margin: '0 0 1rem 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Appearance Details
        </h3>

        {/* Age */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Age
          </label>
          <input
            type="text"
            value={editedData.age || ''}
            onChange={(e) => handlers.updateField('age', e.target.value)}
            placeholder="e.g., young adult, middle-aged..."
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

        {/* Skin Tone */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Skin Tone
          </label>
          <input
            type="text"
            value={editedData.skin_tone || ''}
            onChange={(e) => handlers.updateField('skin_tone', e.target.value)}
            placeholder="e.g., fair, olive, brown..."
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

        {/* Face Description */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Face Description
          </label>
          <textarea
            value={editedData.face_description || ''}
            onChange={(e) => handlers.updateField('face_description', e.target.value)}
            rows="2"
            placeholder="Face shape, eyes, features, gender presentation, ethnicity..."
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

        {/* Hair Description */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Hair Description
          </label>
          <textarea
            value={editedData.hair_description || ''}
            onChange={(e) => handlers.updateField('hair_description', e.target.value)}
            rows="2"
            placeholder="Color, style, length, texture..."
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

        {/* Body Description */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
            Body Description
          </label>
          <textarea
            value={editedData.body_description || ''}
            onChange={(e) => handlers.updateField('body_description', e.target.value)}
            rows="2"
            placeholder="Build, height, physique..."
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
    </div>
  ),

  saveEntity: async (character, updates) => {
    const response = await api.put(
      `/characters/${character.characterId}`,
      {
        name: updates.title,
        personality: updates.data.personality,
        age: updates.data.age,
        skin_tone: updates.data.skin_tone,
        face_description: updates.data.face_description,
        hair_description: updates.data.hair_description,
        body_description: updates.data.body_description
      }
    )
    return response.data
  },

  deleteEntity: async (character) => {
    // Use archive endpoint instead of delete (soft delete)
    await api.post(`/characters/${character.characterId}/archive`)
  },

  archiveEntity: async (character) => {
    await api.post(`/characters/${character.characterId}/archive`)
  },

  unarchiveEntity: async (character) => {
    await api.post(`/characters/${character.characterId}/unarchive`)
  }
}
