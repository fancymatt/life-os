import React, { useState } from 'react';
import api from '../api/client';
import './QAInterface.css';

function QAInterface({ gameId, documentIds = [], onQuestionAsked }) {
  const [question, setQuestion] = useState('');
  const [contextType, setContextType] = useState('document');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    // Check if document Q&A is selected but no processed documents
    if (contextType === 'document' && documentIds.length === 0) {
      setError('No processed rulebooks available. Please process a rulebook first.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await api.post('/qa/ask', {
        question: question.trim(),
        game_id: gameId,
        document_ids: contextType === 'document' ? documentIds : null,
        context_type: contextType,
        top_k: 5
      });

      // Clear form and notify parent
      setQuestion('');
      if (onQuestionAsked) {
        onQuestionAsked();
      }
    } catch (err) {
      console.error('Failed to ask question:', err);
      setError(err.response?.data?.detail || 'Failed to ask question');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="qa-interface">
      <form onSubmit={handleSubmit}>
        <div className="context-type-selector">
          <label>
            <input
              type="radio"
              value="document"
              checked={contextType === 'document'}
              onChange={(e) => setContextType(e.target.value)}
              disabled={loading}
            />
            Search Rulebook
            {documentIds.length === 0 && (
              <span className="warning"> (no processed rulebooks)</span>
            )}
          </label>

          <label>
            <input
              type="radio"
              value="general"
              checked={contextType === 'general'}
              onChange={(e) => setContextType(e.target.value)}
              disabled={loading}
            />
            General Knowledge
          </label>
        </div>

        <div className="question-input-container">
          <textarea
            placeholder={
              contextType === 'document'
                ? 'Ask a question about the rules... (e.g., "How many cards do you draw during setup?")'
                : 'Ask a general board game question... (e.g., "What is worker placement?")'
            }
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={loading}
            rows={3}
          />

          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="ask-button"
          >
            {loading ? 'Asking...' : 'Ask Question'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {contextType === 'document' && documentIds.length > 0 && (
          <div className="context-info">
            Searching {documentIds.length} processed rulebook{documentIds.length > 1 ? 's' : ''}
          </div>
        )}
      </form>
    </div>
  );
}

export default QAInterface;
