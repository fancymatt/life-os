import { useState } from 'react'
import api from '../api/client'
import './BGGRulebookFetcher.css'

/**
 * BGG Rulebook Fetcher Tool
 *
 * Standalone tool for searching BoardGameGeek and downloading rulebooks.
 * Creates board game and document entities automatically.
 */
function BGGRulebookFetcher() {
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [gathering, setGathering] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

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

  const handleGather = async (game) => {
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
          gameName: game.name
        })
        setSearchResults([])  // Clear search results
        setQuery('')  // Clear search query
      } else if (response.data.status === 'failed') {
        setError(response.data.error || 'Failed to fetch game data')
      }
    } catch (err) {
      console.error('Failed to gather:', err)
      setError(err.response?.data?.detail || 'Failed to gather game data')
    } finally {
      setGathering(false)
    }
  }

  const handleReset = () => {
    setQuery('')
    setSearchResults([])
    setError(null)
    setResult(null)
  }

  return (
    <div className="bgg-fetcher-page">
      <div className="tool-header">
        <h1>🎲 BGG Rulebook Fetcher</h1>
        <p>Search BoardGameGeek and download rulebooks automatically</p>
      </div>

      {/* Search Form */}
      {!result && (
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search for a board game..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={searching || gathering}
            autoFocus
          />
          <button type="submit" disabled={searching || gathering || !query.trim()}>
            {searching ? 'Searching...' : 'Search BoardGameGeek'}
          </button>
        </form>
      )}

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {gathering && (
        <div className="gathering-progress">
          <div className="spinner"></div>
          <p>Downloading game data and rulebook from BoardGameGeek...</p>
        </div>
      )}

      {/* Search Results */}
      {searchResults.length > 0 && !result && (
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
                  onClick={() => handleGather(game)}
                  disabled={gathering}
                  className="gather-button"
                >
                  {gathering ? 'Downloading...' : 'Download Rulebook'}
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
              <h4>Game Entity Created</h4>
              <p><strong>Game ID:</strong> <code>{result.game_id}</code></p>
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
                <h4>Rulebook Downloaded</h4>
                <p><strong>Document ID:</strong> <code>{result.document_id}</code></p>
                {result.pdf_path && (
                  <p><strong>File:</strong> <code>{result.pdf_path}</code></p>
                )}
                {result.pdf_url && (
                  <p><strong>Source:</strong> <a href={result.pdf_url} target="_blank" rel="noopener noreferrer">View on BGG ↗</a></p>
                )}
                <div className="next-steps">
                  <p><strong>Next step:</strong> Use the Document Processor tool to convert this PDF to searchable text and enable Q&A.</p>
                </div>
              </div>
            ) : (
              <div className="detail-section warning">
                <h4>⚠️ No Rulebook Found</h4>
                <p>Game entity was created, but no rulebook PDF was found on BoardGameGeek.</p>
                <p>You can manually upload a rulebook PDF later.</p>
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
