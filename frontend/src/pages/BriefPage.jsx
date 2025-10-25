import React, { useState, useEffect } from 'react'
import api from '../api/client'
import './BriefPage.css'

/**
 * BriefPage - Daily Brief UI
 *
 * Shows cards for:
 * - Jobs awaiting user input (merge previews, agent approvals)
 * - Completed background tasks
 * - Suggested actions
 *
 * Foundation for Phase 8 Daily Brief system
 */
function BriefPage() {
  const [cards, setCards] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedCard, setSelectedCard] = useState(null)

  useEffect(() => {
    loadCards()
    // Poll for new cards every 5 seconds
    const interval = setInterval(loadCards, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadCards = async () => {
    try {
      const response = await api.get('/brief/')
      setCards(response.data)
      setLoading(false)
    } catch (err) {
      console.error('Error loading Brief cards:', err)
      setError(err.response?.data?.detail || 'Failed to load Brief')
      setLoading(false)
    }
  }

  const handleCardAction = async (cardId, action, editedData = null) => {
    try {
      if (action === 'dismiss') {
        await api.post(`/brief/${cardId}/dismiss/`)
      } else {
        await api.post(`/brief/${cardId}/respond/`, {
          response: {
            action,
            edited_data: editedData
          }
        })
      }

      // Reload cards
      await loadCards()
      setSelectedCard(null)
    } catch (err) {
      console.error('Error responding to card:', err)
      alert(err.response?.data?.detail || 'Failed to respond to card')
    }
  }

  const renderCardPreview = (card) => (
    <div
      key={card.card_id}
      className="brief-card"
      onClick={() => setSelectedCard(card)}
    >
      <div className="brief-card-header">
        <h3>{card.title}</h3>
        <span className="brief-card-category">{card.category}</span>
      </div>
      <p className="brief-card-description">{card.description}</p>
      <div className="brief-card-footer">
        <span className="brief-card-time">
          {new Date(card.created_at).toLocaleString()}
        </span>
        <span className="brief-card-actions-count">
          {card.actions.length} actions
        </span>
      </div>
    </div>
  )

  const renderCardDetail = (card) => (
    <div className="brief-card-detail">
      <div className="brief-card-detail-header">
        <h2>{card.title}</h2>
        <button
          className="brief-close-btn"
          onClick={() => setSelectedCard(null)}
        >
          ×
        </button>
      </div>

      <p className="brief-card-detail-description">{card.description}</p>

      {/* Show data if available */}
      {card.data && (
        <div className="brief-card-data">
          <h4>Preview Data</h4>
          <pre>{JSON.stringify(card.data, null, 2)}</pre>
        </div>
      )}

      {/* Provenance */}
      {card.provenance && (
        <div className="brief-card-provenance">
          <small>{card.provenance}</small>
        </div>
      )}

      {/* Action buttons */}
      <div className="brief-card-actions">
        {card.actions.map((action) => (
          <button
            key={action.action_id}
            className={`brief-action-btn brief-action-${action.style || 'secondary'}`}
            onClick={() => handleCardAction(card.card_id, action.action_id)}
          >
            {action.label}
          </button>
        ))}
        <button
          className="brief-action-btn brief-action-secondary"
          onClick={() => handleCardAction(card.card_id, 'dismiss')}
        >
          Dismiss
        </button>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="brief-page">
        <div className="brief-loading">Loading Brief...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="brief-page">
        <div className="brief-error">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="brief-page">
      <div className="brief-header">
        <h1>Daily Brief</h1>
        <p className="brief-subtitle">
          {cards.length} {cards.length === 1 ? 'item' : 'items'} need your attention
        </p>
      </div>

      {cards.length === 0 ? (
        <div className="brief-empty">
          <h3>All caught up! 🎉</h3>
          <p>No items need your attention right now.</p>
        </div>
      ) : (
        <div className="brief-grid">
          {cards.map(renderCardPreview)}
        </div>
      )}

      {/* Card detail modal */}
      {selectedCard && (
        <div className="brief-modal-overlay" onClick={() => setSelectedCard(null)}>
          <div className="brief-modal" onClick={(e) => e.stopPropagation()}>
            {renderCardDetail(selectedCard)}
          </div>
        </div>
      )}
    </div>
  )
}

export default BriefPage
