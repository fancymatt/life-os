import api from '../../../api/client'
import { formatDate, getPreview } from './helpers'

/**
 * Board Games Entity Configuration
 */
export const boardGamesConfig = {
  entityType: 'board-game',
  title: 'Board Games',
  icon: '🎲',
  emptyMessage: 'No board games yet. Use the BGG Rulebook Fetcher tool to add games!',
  enableSearch: true,
  enableSort: true,
  enableEdit: true,
  showRefreshButton: true,
  defaultSort: 'alphabetical',
  searchFields: ['name', 'designer', 'publisher', 'description'],

  actions: [],

  fetchEntities: async () => {
    const response = await api.get('/board-games/')
    return (response.data.games || []).map(game => ({
      id: game.game_id,
      gameId: game.game_id,
      title: game.name,
      name: game.name,
      bggId: game.bgg_id,
      designer: game.designer,
      publisher: game.publisher,
      year: game.year,
      description: game.description,
      playerCountMin: game.player_count_min,
      playerCountMax: game.player_count_max,
      playtimeMin: game.playtime_min,
      playtimeMax: game.playtime_max,
      complexity: game.complexity,
      createdAt: game.created_at,
      metadata: game.metadata || {},
      archived: game.archived || false,
      archivedAt: game.archived_at,
      // Wrap editable fields in data property for EntityBrowser
      data: {
        name: game.name,
        designer: game.designer || '',
        publisher: game.publisher || '',
        year: game.year || null,
        description: game.description || '',
        player_count_min: game.player_count_min || null,
        player_count_max: game.player_count_max || null,
        playtime_min: game.playtime_min || null,
        playtime_max: game.playtime_max || null,
        complexity: game.complexity || null
      }
    }))
  },

  gridConfig: {
    columns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '1.5rem'
  },

  renderCard: (game) => (
    <div className="entity-card">
      <div className="entity-card-image" style={{
        height: '180px',
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(59, 130, 246, 0.2))',
        position: 'relative',
        opacity: game.archived ? 0.6 : 1
      }}>
        {game.archived && (
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
        <div className="entity-card-placeholder" style={{ fontSize: '5rem' }}>🎲</div>
      </div>
      <div className="entity-card-content">
        <h3 className="entity-card-title">{game.name}</h3>
        {game.year && (
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem', margin: '0 0 0.5rem 0' }}>
            ({game.year})
          </p>
        )}
        {game.designer && (
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem', margin: '0 0 0.5rem 0' }}>
            by {game.designer}
          </p>
        )}
        <div style={{ display: 'flex', gap: '1rem', marginTop: '0.75rem', fontSize: '0.85rem', color: 'rgba(255, 255, 255, 0.6)' }}>
          {game.playerCountMin && game.playerCountMax && (
            <span>
              👥 {game.playerCountMin === game.playerCountMax
                ? game.playerCountMin
                : `${game.playerCountMin}-${game.playerCountMax}`}
            </span>
          )}
          {game.complexity && (
            <span>🧩 {game.complexity.toFixed(1)}/5</span>
          )}
        </div>
      </div>
    </div>
  ),

  renderPreview: (game) => (
    <>
      <div style={{
        width: '100%',
        aspectRatio: '16/9',
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(59, 130, 246, 0.3))',
        borderRadius: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '8rem',
        marginBottom: '1.5rem'
      }}>
        🎲
      </div>
    </>
  ),

  renderDetail: (game, handleBackToList, onUpdate) => (
    <div style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ color: 'white', margin: '0 0 0.5rem 0' }}>{game.name}</h2>
        {game.year && (
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', margin: 0 }}>({game.year})</p>
        )}
      </div>

      {/* Designer & Publisher */}
      {(game.designer || game.publisher) && (
        <div style={{ marginBottom: '1.5rem' }}>
          {game.designer && (
            <p style={{ color: 'rgba(255, 255, 255, 0.8)', margin: '0 0 0.5rem 0' }}>
              <strong>Designer:</strong> {game.designer}
            </p>
          )}
          {game.publisher && (
            <p style={{ color: 'rgba(255, 255, 255, 0.8)', margin: 0 }}>
              <strong>Publisher:</strong> {game.publisher}
            </p>
          )}
        </div>
      )}

      {/* Game Stats */}
      <div style={{ marginBottom: '1.5rem', display: 'grid', gap: '0.75rem' }}>
        {game.playerCountMin && game.playerCountMax && (
          <div>
            <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Players:</strong>{' '}
            <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
              {game.playerCountMin === game.playerCountMax
                ? game.playerCountMin
                : `${game.playerCountMin}-${game.playerCountMax}`}
            </span>
          </div>
        )}
        {game.playtimeMin && game.playtimeMax && (
          <div>
            <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Playtime:</strong>{' '}
            <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
              {game.playtimeMin === game.playtimeMax
                ? `${game.playtimeMin} min`
                : `${game.playtimeMin}-${game.playtimeMax} min`}
            </span>
          </div>
        )}
        {game.complexity && (
          <div>
            <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>Complexity:</strong>{' '}
            <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{game.complexity.toFixed(1)}/5</span>
          </div>
        )}
        {game.bggId && (
          <div>
            <strong style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>BGG ID:</strong>{' '}
            <a
              href={`https://boardgamegeek.com/boardgame/${game.bggId}`}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'rgba(139, 92, 246, 0.9)', textDecoration: 'none' }}
            >
              {game.bggId} ↗
            </a>
          </div>
        )}
      </div>

      {/* Description */}
      {game.description && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '1rem', margin: '0 0 0.5rem 0' }}>
            Description
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', margin: 0 }}>
            {game.description}
          </p>
        </div>
      )}

      {formatDate(game.createdAt) && (
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem', margin: 0 }}>
            <strong>Added:</strong> {formatDate(game.createdAt)}
          </p>
        </div>
      )}
    </div>
  ),

  renderEdit: (game, editedData, editedTitle, handlers) => (
    <div>
      {/* Name Field */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Game Name
        </label>
        <input
          type="text"
          value={editedData.name || ''}
          onChange={(e) => handlers.updateField('name', e.target.value)}
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

      {/* Designer */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Designer
        </label>
        <input
          type="text"
          value={editedData.designer || ''}
          onChange={(e) => handlers.updateField('designer', e.target.value)}
          placeholder="Game designer(s)..."
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

      {/* Publisher */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Publisher
        </label>
        <input
          type="text"
          value={editedData.publisher || ''}
          onChange={(e) => handlers.updateField('publisher', e.target.value)}
          placeholder="Publisher..."
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

      {/* Year */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Year Published
        </label>
        <input
          type="number"
          value={editedData.year || ''}
          onChange={(e) => handlers.updateField('year', e.target.value ? parseInt(e.target.value) : null)}
          placeholder="2024"
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

      {/* Description */}
      <div style={{ marginBottom: '2rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Description
        </label>
        <textarea
          value={editedData.description || ''}
          onChange={(e) => handlers.updateField('description', e.target.value)}
          rows="4"
          placeholder="Game description..."
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

      {/* Player Count */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Player Count
        </label>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <input
            type="number"
            value={editedData.player_count_min || ''}
            onChange={(e) => handlers.updateField('player_count_min', e.target.value ? parseInt(e.target.value) : null)}
            placeholder="Min"
            style={{
              flex: 1,
              padding: '0.75rem',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '8px',
              color: 'white',
              fontSize: '0.95rem'
            }}
          />
          <input
            type="number"
            value={editedData.player_count_max || ''}
            onChange={(e) => handlers.updateField('player_count_max', e.target.value ? parseInt(e.target.value) : null)}
            placeholder="Max"
            style={{
              flex: 1,
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

      {/* Playtime */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Playtime (minutes)
        </label>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <input
            type="number"
            value={editedData.playtime_min || ''}
            onChange={(e) => handlers.updateField('playtime_min', e.target.value ? parseInt(e.target.value) : null)}
            placeholder="Min"
            style={{
              flex: 1,
              padding: '0.75rem',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '8px',
              color: 'white',
              fontSize: '0.95rem'
            }}
          />
          <input
            type="number"
            value={editedData.playtime_max || ''}
            onChange={(e) => handlers.updateField('playtime_max', e.target.value ? parseInt(e.target.value) : null)}
            placeholder="Max"
            style={{
              flex: 1,
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

      {/* Complexity */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', color: 'rgba(255, 255, 255, 0.9)', marginBottom: '0.5rem', fontWeight: 500 }}>
          Complexity (1-5)
        </label>
        <input
          type="number"
          step="0.1"
          min="0"
          max="5"
          value={editedData.complexity || ''}
          onChange={(e) => handlers.updateField('complexity', e.target.value ? parseFloat(e.target.value) : null)}
          placeholder="3.5"
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

  saveEntity: async (game, updates) => {
    const response = await api.put(
      `/board-games/${game.gameId}`,
      {
        name: updates.data.name,
        designer: updates.data.designer,
        publisher: updates.data.publisher,
        year: updates.data.year,
        description: updates.data.description,
        player_count_min: updates.data.player_count_min,
        player_count_max: updates.data.player_count_max,
        playtime_min: updates.data.playtime_min,
        playtime_max: updates.data.playtime_max,
        complexity: updates.data.complexity
      }
    )
    return response.data
  },

  deleteEntity: async (game) => {
    await api.post(`/board-games/${game.gameId}/archive`)
  },

  archiveEntity: async (game) => {
    await api.post(`/board-games/${game.gameId}/archive`)
  },

  unarchiveEntity: async (game) => {
    await api.post(`/board-games/${game.gameId}/unarchive`)
  }
}
