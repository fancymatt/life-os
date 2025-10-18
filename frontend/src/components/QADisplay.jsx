import React, { useState } from 'react';
import api from '../api/client';
import './QADisplay.css';

function QADisplay({ qa, onUpdate }) {
  const [showCitations, setShowCitations] = useState(false);
  const [updating, setUpdating] = useState(false);

  const handleToggleFavorite = async () => {
    try {
      setUpdating(true);
      await api.put(`/qa/${qa.qa_id}`, {
        is_favorite: !qa.is_favorite
      });
      if (onUpdate) {
        onUpdate();
      }
    } catch (err) {
      console.error('Failed to update favorite:', err);
      alert('Failed to update favorite');
    } finally {
      setUpdating(false);
    }
  };

  const handleFeedback = async (wasHelpful) => {
    try {
      setUpdating(true);
      await api.put(`/qa/${qa.qa_id}`, {
        was_helpful: wasHelpful
      });
      if (onUpdate) {
        onUpdate();
      }
    } catch (err) {
      console.error('Failed to submit feedback:', err);
      alert('Failed to submit feedback');
    } finally {
      setUpdating(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  const hasCitations = qa.citations && qa.citations.length > 0;

  return (
    <div className="qa-display">
      <div className="qa-header">
        <div className="qa-meta">
          <span className="qa-context-badge">{qa.context_type}</span>
          <span className="qa-time">{formatDate(qa.created_at)}</span>
          {qa.confidence > 0 && (
            <span className="qa-confidence" title="Confidence score">
              {(qa.confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>

        <button
          className={`favorite-button ${qa.is_favorite ? 'active' : ''}`}
          onClick={handleToggleFavorite}
          disabled={updating}
          title={qa.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          {qa.is_favorite ? '★' : '☆'}
        </button>
      </div>

      <div className="qa-question">
        <strong>Q:</strong> {qa.question}
      </div>

      <div className="qa-answer">
        <strong>A:</strong> {qa.answer}
      </div>

      {hasCitations && (
        <div className="qa-citations">
          <button
            className="citations-toggle"
            onClick={() => setShowCitations(!showCitations)}
          >
            📖 Sources ({qa.citations.length})
            <span className="toggle-icon">{showCitations ? '▼' : '▶'}</span>
          </button>

          {showCitations && (
            <div className="citations-list">
              {qa.citations.map((citation, idx) => (
                <div key={idx} className="citation-item">
                  <div className="citation-header">
                    <strong>Page {citation.page}</strong>
                    {citation.section && (
                      <span className="citation-section">
                        Section: "{citation.section}"
                      </span>
                    )}
                  </div>
                  {citation.text && (
                    <div className="citation-text">"{citation.text}"</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="qa-actions">
        <div className="feedback-buttons">
          <span className="feedback-label">Was this helpful?</span>
          <button
            className={`feedback-button ${qa.was_helpful === true ? 'active thumbs-up' : ''}`}
            onClick={() => handleFeedback(true)}
            disabled={updating}
            title="Helpful"
          >
            👍
          </button>
          <button
            className={`feedback-button ${qa.was_helpful === false ? 'active thumbs-down' : ''}`}
            onClick={() => handleFeedback(false)}
            disabled={updating}
            title="Not helpful"
          >
            👎
          </button>
        </div>
      </div>
    </div>
  );
}

export default QADisplay;
