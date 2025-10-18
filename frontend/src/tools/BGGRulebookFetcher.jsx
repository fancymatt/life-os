import { useState, useEffect } from 'react'
import api from '../api/client'
import './BGGRulebookFetcher.css'

/**
 * BGG Rulebook Fetcher Tool
 *
 * Standalone tool for searching BoardGameGeek and downloading rulebooks.
 * Creates board game and document entities automatically.
 */
function BGGRulebookFetcher() {
  const [view, setView] = useState('existing') // 'existing' or 'search'
  const [existingGames, setExistingGames] = useState([])
  const [gamesWithDocs, setGamesWithDocs] = useState({})
  const [loadingGames, setLoadingGames] = useState(true)
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [gathering, setGathering] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  useEffect(() => {
    loadExistingGames()
  }, [])

  const loadExistingGames = async () => {
    try {
      setLoadingGames(true)

      // Load board games
      const gamesResponse = await api.get('/board-games/')
      const games = gamesResponse.data.games || []
      setExistingGames(games)

      // For each game, check if it has documents
      const docsMap = {}
      for (const game of games) {
        try {
          const docsResponse = await api.get(`/board-games/${game.game_id}/documents`)
          docsMap[game.game_id] = docsResponse.data.documents || []
        } catch (err) {
          docsMap[game.game_id] = []
        }
      }
      setGamesWithDocs(docsMap)
    } catch (err) {
      console.error('Failed to load games:', err)
      setError('Failed to load existing games')
    } finally {
      setLoadingGames(false)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    try {
      setSearching(true)
      setError(null)
      setResult(null)
      const response = await api.post('/board-games/search', null, {
        params: { query: query.trim() }
      })
      setSearchResults(response.data.results || [])
      if (response.data.results.length === 0) {
        setError('No games found. Try a different search.')
      }
    } catch (err) {
      console.error('Search failed:', err)
      setError('Search failed. Please try again.')
    } finally {
      setSearching(false)
    }
  }

  const handleDownloadRulebook = async (game) => {
    // For existing games, download rulebook using their BGG ID
    if (!game.bgg_id) {
      setError('This game does not have a BoardGameGeek ID')
      return
    }

    try {
      setGathering(true)
      setError(null)
      setResult(null)

      const response = await api.post('/board-games/gather', null, {
        params: {
          bgg_id: game.bgg_id,
          create_entities: true
        }
      })

      if (response.data.status === 'completed') {
        setResult({
          ...response.data,
          gameName: game.name,
          isExisting: true
        })
        // Reload games to update document status
        await loadExistingGames()
      } else if (response.data.status === 'failed') {
        setError(response.data.error || 'Failed to fetch rulebook')
      }
    } catch (err) {
      console.error('Failed to download rulebook:', err)
      setError(err.response?.data?.detail || 'Failed to download rulebook')
    } finally {
      setGathering(false)
    }
  }

  const handleGatherNewGame = async (searchResult) => {
    // For new games from search, create game + download rulebook
    try {
      setGathering(true)
      setError(null)
      setResult(null)

      const response = await api.post('/board-games/gather', null, {
        params: {
          bgg_id: searchResult.bgg_id,
          create_entities: true
        }
      })

      if (response.data.status === 'completed') {
        setResult({
          ...response.data,
          gameName: searchResult.name,
          isExisting: false
        })
        setSearchResults([])  // Clear search results
        setQuery('')  // Clear search query
        // Reload games to show the new one
        await loadExistingGames()
      } else if (response.data.status === 'failed') {
        setError(response.data.error || 'Failed to add game')
      }
    } catch (err) {
      console.error('Failed to add game:', err)
      setError(err.response?.data?.detail || 'Failed to add game')
    } finally {
      setGathering(false)
    }
  }

  const handleReset = () => {
    setQuery('')
    setSearchResults([])
    setError(null)
    setResult(null)
    setView('existing')
  }

  return (
    <div className="bgg-fetcher-page">
      <div className="tool-header">
        <h1>🎲 BGG Rulebook Fetcher</h1>
        <p>Download rulebooks for your board games from BoardGameGeek</p>
      </div>

      {/* View Tabs */}
      {!result && (
        <div className="view-tabs">
          <button
            className={`tab-button ${view === 'existing' ? 'active' : ''}`}
            onClick={() => setView('existing')}
          >
            Your Games ({existingGames.length})
          </button>
          <button
            className={`tab-button ${view === 'search' ? 'active' : ''}`}
            onClick={() => setView('search')}
          >
            Add New Game
          </button>
        </div>
      )}

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {gathering && (
        <div className="gathering-progress">
          <div className="spinner"></div>
          <p>Downloading from BoardGameGeek...</p>
        </div>
      )}

      {/* Existing Games View */}
      {view === 'existing' && !result && !gathering && (
        <>
          {loadingGames ? (
            <div className="loading">Loading your games...</div>
          ) : existingGames.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🎲</div>
              <h3>No Board Games Yet</h3>
              <p>Add your first game using the "Add New Game" tab above.</p>
            </div>
          ) : (
            <div className="existing-games">
              <h3>Your Board Games</h3>
              <div className="games-grid">
                {existingGames.map(game => {
                  const docs = gamesWithDocs[game.game_id] || []
                  const hasRulebook = docs.length > 0

                  return (
                    <div key={game.game_id} className={`game-card ${hasRulebook ? 'has-rulebook' : 'needs-rulebook'}`}>
                      <div className="game-info">
                        <h4>{game.name}</h4>
                        {game.year && <p className="game-year">({game.year})</p>}
                        {game.designer && <p className="game-designer">by {game.designer}</p>}

                        <div className="game-meta">
                          {game.player_count_min && game.player_count_max && (
                            <span>👥 {game.player_count_min}-{game.player_count_max}</span>
                          )}
                          {game.complexity && (
                            <span>🧩 {game.complexity.toFixed(1)}/5</span>
                          )}
                        </div>
                      </div>

                      <div className="game-status">
                        {hasRulebook ? (
                          <>
                            <div className="status-badge success">
                              ✓ {docs.length} Rulebook{docs.length !== 1 ? 's' : ''}
                            </div>
                            <div className="document-list">
                              {docs.map(doc => (
                                <div key={doc.document_id} className="document-item">
                                  <span>📄 {doc.title}</span>
                                  {doc.processed && <span className="processed-badge">✓ Processed</span>}
                                </div>
                              ))}
                            </div>
                          </>
                        ) : game.bgg_id ? (
                          <>
                            <div className="status-badge warning">⚠ No Rulebook</div>
                            <button
                              onClick={() => handleDownloadRulebook(game)}
                              disabled={gathering}
                              className="download-button"
                            >
                              {gathering ? 'Downloading...' : 'Download Rulebook'}
                            </button>
                          </>
                        ) : (
                          <div className="status-badge error">
                            ⚠ No BGG ID - Cannot download
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </>
      )}

      {/* Search View */}
      {view === 'search' && !result && !gathering && (
        <>
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              placeholder="Search for a board game..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={searching}
              autoFocus
            />
            <button type="submit" disabled={searching || !query.trim()}>
              {searching ? 'Searching...' : 'Search BoardGameGeek'}
            </button>
          </form>
        </>
      )}

      {/* Search Results */}
      {view === 'search' && searchResults.length > 0 && !result && (
        <div className="search-results">
          <h3>Search Results ({searchResults.length})</h3>
          <div className="results-grid">
            {searchResults.map(game => (
              <div key={game.bgg_id} className="result-card">
                <div className="result-info">
                  <h4>{game.name}</h4>
                  {game.year && (
                    <p className="result-year">({game.year})</p>
                  )}
                  <p className="result-type">{game.type.replace('boardgame', 'Game').replace('boardgameexpansion', 'Expansion')}</p>
                  <p className="result-id">BGG ID: {game.bgg_id}</p>
                </div>
                <button
                  onClick={() => handleGatherNewGame(game)}
                  disabled={gathering}
                  className="gather-button"
                >
                  {gathering ? 'Adding...' : 'Add Game + Download Rulebook'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Success Result */}
      {result && (
        <div className="result-success">
          <div className="success-icon">✓</div>
          <h2>Success!</h2>
          <h3>{result.gameName}</h3>

          <div className="result-details">
            <div className="detail-section">
              <h4>{result.isExisting ? 'Game Updated' : 'Game Entity Created'}</h4>
              <p><strong>Game ID:</strong> <code>{result.game_id}</code></p>
              <p className="entity-link">
                → View in <a href={`/entities/board-games`}>Board Games Entities</a>
              </p>
              {result.game_data && (
                <>
                  {result.game_data.designer && (
                    <p><strong>Designer:</strong> {result.game_data.designer}</p>
                  )}
                  {result.game_data.publisher && (
                    <p><strong>Publisher:</strong> {result.game_data.publisher}</p>
                  )}
                  {result.game_data.year && (
                    <p><strong>Year:</strong> {result.game_data.year}</p>
                  )}
                  {result.game_data.player_count_min && result.game_data.player_count_max && (
                    <p><strong>Players:</strong> {result.game_data.player_count_min === result.game_data.player_count_max
                      ? result.game_data.player_count_min
                      : `${result.game_data.player_count_min}-${result.game_data.player_count_max}`}
                    </p>
                  )}
                  {result.game_data.complexity && (
                    <p><strong>Complexity:</strong> {result.game_data.complexity.toFixed(1)}/5</p>
                  )}
                </>
              )}
            </div>

            {result.document_id ? (
              <div className="detail-section">
                <h4>📄 Document Entity Created</h4>
                <p><strong>Document ID:</strong> <code>{result.document_id}</code></p>
                <p className="entity-link">
                  → View in <a href={`/entities/documents`}>Documents Entities</a>
                </p>
                {result.pdf_path && (
                  <p><strong>File:</strong> <code>{result.pdf_path}</code></p>
                )}
                {result.pdf_url && (
                  <p><strong>Source:</strong> <a href={result.pdf_url} target="_blank" rel="noopener noreferrer">View on BGG ↗</a></p>
                )}
                <div className="connection-info">
                  <p>✓ Document is linked to this board game</p>
                  <p><strong>Game ID:</strong> <code>{result.game_id}</code> ↔ <strong>Document ID:</strong> <code>{result.document_id}</code></p>
                </div>
                <div className="next-steps">
                  <p><strong>Next step:</strong> Use the <a href="/tools/document-processor">Document Processor</a> tool to convert this PDF to searchable text and enable Q&A.</p>
                </div>
              </div>
            ) : (
              <div className="detail-section warning">
                <h4>⚠️ No Rulebook Found</h4>
                <p>Game entity was {result.isExisting ? 'updated' : 'created'}, but no rulebook PDF was found on BoardGameGeek.</p>
                <p>You can manually upload a rulebook PDF later or try searching again.</p>
              </div>
            )}
          </div>

          <div className="action-buttons">
            <button onClick={handleReset} className="new-search-button">
              Search Another Game
            </button>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!query && searchResults.length === 0 && !result && !error && (
        <div className="empty-state">
          <div className="empty-icon">🎲</div>
          <h3>Search BoardGameGeek</h3>
          <p>Enter a game name to search BoardGameGeek's database.</p>
          <p>When you find your game, click "Download Rulebook" to:</p>
          <ul>
            <li>Create a board game entity with complete metadata</li>
            <li>Download the rulebook PDF (if available)</li>
            <li>Create a document entity ready for processing</li>
          </ul>
        </div>
      )}
    </div>
  )
}

export default BGGRulebookFetcher
