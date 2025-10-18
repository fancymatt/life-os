import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import './BoardGames.css';

function BoardGames() {
  const navigate = useNavigate();
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    loadGames();
  }, []);

  const loadGames = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/board-games/');
      setGames(response.data.games || []);
    } catch (err) {
      console.error('Failed to load board games:', err);
      setError('Failed to load board games');
    } finally {
      setLoading(false);
    }
  };

  const handleGameClick = (gameId) => {
    navigate(`/board-games/${gameId}`);
  };

  if (loading) {
    return (
      <div className="board-games-container">
        <div className="loading">Loading board games...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="board-games-container">
        <div className="error">{error}</div>
        <button onClick={loadGames}>Retry</button>
      </div>
    );
  }

  return (
    <div className="board-games-container">
      <div className="board-games-header">
        <h1>Board Games</h1>
        <button
          className="add-game-button"
          onClick={() => setShowAddModal(true)}
        >
          + Add Game
        </button>
      </div>

      {games.length === 0 ? (
        <div className="empty-state">
          <p>No board games yet</p>
          <p>Click "Add Game" to search BoardGameGeek and download rulebooks</p>
        </div>
      ) : (
        <div className="games-grid">
          {games.map(game => (
            <div
              key={game.game_id}
              className="game-card"
              onClick={() => handleGameClick(game.game_id)}
            >
              <div className="game-card-header">
                <h3>{game.name}</h3>
                {game.year && <span className="game-year">({game.year})</span>}
              </div>

              {game.designer && (
                <p className="game-designer">by {game.designer}</p>
              )}

              <div className="game-stats">
                {game.player_count_min && game.player_count_max && (
                  <span className="stat">
                    👥 {game.player_count_min === game.player_count_max
                      ? game.player_count_min
                      : `${game.player_count_min}-${game.player_count_max}`}
                  </span>
                )}

                {game.playtime_min && game.playtime_max && (
                  <span className="stat">
                    ⏱️ {game.playtime_min === game.playtime_max
                      ? `${game.playtime_min} min`
                      : `${game.playtime_min}-${game.playtime_max} min`}
                  </span>
                )}

                {game.complexity && (
                  <span className="stat">
                    🧩 {game.complexity.toFixed(1)}/5
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showAddModal && (
        <AddGameModal
          onClose={() => setShowAddModal(false)}
          onGameAdded={loadGames}
        />
      )}
    </div>
  );
}

function AddGameModal({ onClose, onGameAdded }) {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [gathering, setGathering] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setSearching(true);
      setError(null);
      const response = await api.post('/board-games/search', null, {
        params: { query: query.trim() }
      });
      setSearchResults(response.data.results || []);
      if (response.data.results.length === 0) {
        setError('No games found. Try a different search.');
      }
    } catch (err) {
      console.error('Search failed:', err);
      setError('Search failed. Please try again.');
    } finally {
      setSearching(false);
    }
  };

  const handleAddGame = async (result) => {
    try {
      setGathering(true);
      setError(null);
      setSuccess(null);

      // Gather game data and download rulebook
      const response = await api.post('/board-games/gather', null, {
        params: {
          bgg_id: result.bgg_id,
          create_entities: true
        }
      });

      if (response.data.status === 'completed') {
        setSuccess(`${result.name} added successfully!`);
        setTimeout(() => {
          onGameAdded();
          onClose();
        }, 1500);
      } else if (response.data.status === 'failed') {
        setError(response.data.error || 'Failed to add game');
      }
    } catch (err) {
      console.error('Failed to add game:', err);
      setError(err.response?.data?.detail || 'Failed to add game');
    } finally {
      setGathering(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add Board Game</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search BoardGameGeek..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={searching || gathering}
            autoFocus
          />
          <button type="submit" disabled={searching || gathering}>
            {searching ? 'Searching...' : 'Search'}
          </button>
        </form>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {gathering && (
          <div className="gathering-progress">
            <div className="spinner"></div>
            <p>Downloading rulebook from BoardGameGeek...</p>
          </div>
        )}

        {searchResults.length > 0 && (
          <div className="search-results">
            <h3>Search Results</h3>
            {searchResults.map(result => (
              <div key={result.bgg_id} className="search-result">
                <div className="result-info">
                  <strong>{result.name}</strong>
                  {result.year && <span className="result-year">({result.year})</span>}
                  <span className="result-type">{result.type}</span>
                </div>
                <button
                  onClick={() => handleAddGame(result)}
                  disabled={gathering}
                  className="add-button"
                >
                  Add
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default BoardGames;
