import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';
import QAInterface from '../components/QAInterface';
import QADisplay from '../components/QADisplay';
import './GameDetail.css';

function GameDetail() {
  const { gameId } = useParams();
  const navigate = useNavigate();

  const [game, setGame] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [qas, setQas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [processingDoc, setProcessingDoc] = useState(null);
  const [filterFavorites, setFilterFavorites] = useState(false);

  useEffect(() => {
    loadGameData();
  }, [gameId]);

  const loadGameData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load game, documents, and Q&As in parallel
      const [gameRes, docsRes, qasRes] = await Promise.all([
        api.get(`/board-games/${gameId}`),
        api.get(`/board-games/${gameId}/documents`),
        api.get(`/board-games/${gameId}/qa`)
      ]);

      setGame(gameRes.data);
      setDocuments(docsRes.data.documents || []);
      setQas(qasRes.data.qas || []);
    } catch (err) {
      console.error('Failed to load game data:', err);
      setError(err.response?.data?.detail || 'Failed to load game');
    } finally {
      setLoading(false);
    }
  };

  const handleProcessDocument = async (documentId) => {
    try {
      setProcessingDoc(documentId);
      await api.post(`/documents/${documentId}/process`, null, {
        params: {
          chunk_size: 500,
          overlap: 50
        }
      });

      // Reload documents to get updated status
      const docsRes = await api.get(`/board-games/${gameId}/documents`);
      setDocuments(docsRes.data.documents || []);

      alert('Document processed successfully!');
    } catch (err) {
      console.error('Failed to process document:', err);
      alert(err.response?.data?.detail || 'Failed to process document');
    } finally {
      setProcessingDoc(null);
    }
  };

  const handleQuestionAsked = () => {
    // Reload Q&As after new question
    loadGameData();
  };

  const handleQAUpdated = () => {
    // Reload Q&As after update (favorite, feedback, etc.)
    loadGameData();
  };

  if (loading) {
    return (
      <div className="game-detail-container">
        <div className="loading">Loading game...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="game-detail-container">
        <div className="error">{error}</div>
        <button onClick={() => navigate('/board-games')}>Back to Games</button>
      </div>
    );
  }

  if (!game) {
    return (
      <div className="game-detail-container">
        <div className="error">Game not found</div>
        <button onClick={() => navigate('/board-games')}>Back to Games</button>
      </div>
    );
  }

  const filteredQas = filterFavorites
    ? qas.filter(qa => qa.is_favorite)
    : qas;

  return (
    <div className="game-detail-container">
      <button
        className="back-button"
        onClick={() => navigate('/board-games')}
      >
        ← Back to Games
      </button>

      <div className="game-header">
        <div>
          <h1>{game.name}</h1>
          {game.designer && <p className="designer">by {game.designer}</p>}
        </div>
      </div>

      <div className="game-stats-bar">
        {game.player_count_min && game.player_count_max && (
          <div className="stat-item">
            <span className="stat-label">Players</span>
            <span className="stat-value">
              {game.player_count_min === game.player_count_max
                ? game.player_count_min
                : `${game.player_count_min}-${game.player_count_max}`}
            </span>
          </div>
        )}

        {game.playtime_min && game.playtime_max && (
          <div className="stat-item">
            <span className="stat-label">Time</span>
            <span className="stat-value">
              {game.playtime_min === game.playtime_max
                ? `${game.playtime_min} min`
                : `${game.playtime_min}-${game.playtime_max} min`}
            </span>
          </div>
        )}

        {game.complexity && (
          <div className="stat-item">
            <span className="stat-label">Complexity</span>
            <span className="stat-value">{game.complexity.toFixed(1)}/5</span>
          </div>
        )}

        {game.year && (
          <div className="stat-item">
            <span className="stat-label">Year</span>
            <span className="stat-value">{game.year}</span>
          </div>
        )}
      </div>

      <div className="tabs">
        <button
          className={activeTab === 'overview' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={activeTab === 'rulebooks' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('rulebooks')}
        >
          Rulebooks ({documents.length})
        </button>
        <button
          className={activeTab === 'qa' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('qa')}
        >
          Q&A ({qas.length})
        </button>
      </div>

      {activeTab === 'overview' && (
        <div className="tab-content">
          {game.description && (
            <div className="description">
              <h2>Description</h2>
              <p>{game.description}</p>
            </div>
          )}

          <div className="quick-stats">
            <h2>Quick Info</h2>
            <div className="info-grid">
              {game.publisher && (
                <div className="info-item">
                  <strong>Publisher:</strong> {game.publisher}
                </div>
              )}
              {game.bgg_id && (
                <div className="info-item">
                  <strong>BGG ID:</strong>{' '}
                  <a
                    href={`https://boardgamegeek.com/boardgame/${game.bgg_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {game.bgg_id}
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'rulebooks' && (
        <div className="tab-content">
          <h2>Rulebooks</h2>

          {documents.length === 0 ? (
            <p className="empty-message">No rulebooks found for this game.</p>
          ) : (
            <div className="documents-list">
              {documents.map(doc => (
                <div key={doc.document_id} className="document-card">
                  <div className="document-info">
                    <h3>{doc.title}</h3>
                    <div className="document-meta">
                      {doc.page_count && <span>{doc.page_count} pages</span>}
                      {doc.file_size_bytes && (
                        <span>{(doc.file_size_bytes / 1024 / 1024).toFixed(1)} MB</span>
                      )}
                    </div>
                  </div>

                  <div className="document-status">
                    {doc.processed ? (
                      <span className="status-badge processed">✓ Processed</span>
                    ) : (
                      <button
                        onClick={() => handleProcessDocument(doc.document_id)}
                        disabled={processingDoc === doc.document_id}
                        className="process-button"
                      >
                        {processingDoc === doc.document_id
                          ? 'Processing...'
                          : 'Process for Q&A'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'qa' && (
        <div className="tab-content">
          <div className="qa-section">
            <h2>Ask a Question</h2>
            <QAInterface
              gameId={gameId}
              documentIds={documents
                .filter(d => d.processed)
                .map(d => d.document_id)}
              onQuestionAsked={handleQuestionAsked}
            />
          </div>

          <div className="qa-list-section">
            <div className="qa-list-header">
              <h2>Previous Questions ({filteredQas.length})</h2>
              <label className="filter-favorites">
                <input
                  type="checkbox"
                  checked={filterFavorites}
                  onChange={(e) => setFilterFavorites(e.target.checked)}
                />
                Favorites only
              </label>
            </div>

            {filteredQas.length === 0 ? (
              <p className="empty-message">
                {filterFavorites
                  ? 'No favorite questions yet'
                  : 'No questions asked yet. Ask the first one!'}
              </p>
            ) : (
              <div className="qa-list">
                {filteredQas.map(qa => (
                  <QADisplay
                    key={qa.qa_id}
                    qa={qa}
                    onUpdate={handleQAUpdated}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default GameDetail;
