import { useState, useEffect } from 'react'
import api from '../api/client'
import './ToolPage.css'

/**
 * Document Question Asker Tool
 *
 * Ask questions about processed documents with citations.
 */
function DocumentQuestionAsker() {
  const [documents, setDocuments] = useState([])
  const [selectedDocs, setSelectedDocs] = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(true)
  const [asking, setAsking] = useState(false)
  const [error, setError] = useState(null)
  const [answer, setAnswer] = useState(null)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      setLoading(true)
      const response = await api.get('/documents/')
      const processed = (response.data.documents || []).filter(d => d.processed)
      setDocuments(processed)
    } catch (err) {
      console.error('Failed to load documents:', err)
      setError('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const toggleDocument = (docId) => {
    setSelectedDocs(prev =>
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    )
  }

  const handleAsk = async (e) => {
    e.preventDefault()
    if (!question.trim()) return
    if (selectedDocs.length === 0) {
      setError('Please select at least one document')
      return
    }

    try {
      setAsking(true)
      setError(null)
      setAnswer(null)

      const response = await api.post('/qa/ask', {
        question: question.trim(),
        document_ids: selectedDocs,
        context_type: 'document',
        top_k: 5
      })

      setAnswer(response.data)
    } catch (err) {
      console.error('Failed to ask question:', err)
      setError(err.response?.data?.detail || 'Failed to get answer')
    } finally {
      setAsking(false)
    }
  }

  const handleReset = () => {
    setQuestion('')
    setAnswer(null)
    setError(null)
  }

  return (
    <div className="tool-page">
      <div className="tool-header">
        <h1>💬 Document Question Asker</h1>
        <p>Ask questions about board game rulebooks with cited answers</p>
      </div>

      {error && <div className="error-message"><strong>Error:</strong> {error}</div>}

      {!answer && loading && (
        <div className="loading">Loading documents...</div>
      )}

      {!answer && !loading && documents.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">💬</div>
          <h3>No Processed Documents Found</h3>
          <p>Use the Document Processor tool to process PDFs first.</p>
        </div>
      )}

      {!answer && !loading && documents.length > 0 && (
        <>
          <div className="document-selection">
            <h3>Select Documents to Search</h3>
            <div className="documents-grid">
              {documents.map(doc => (
                <div
                  key={doc.document_id}
                  className={`document-card selectable ${selectedDocs.includes(doc.document_id) ? 'selected' : ''}`}
                  onClick={() => toggleDocument(doc.document_id)}
                >
                  <div className="document-info">
                    <h4>{doc.title}</h4>
                    <p className="doc-meta">{doc.vector_ids?.length || 0} chunks</p>
                  </div>
                  {selectedDocs.includes(doc.document_id) && (
                    <div className="selected-badge">✓</div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <form onSubmit={handleAsk} className="question-form">
            <textarea
              placeholder="Ask a question about the selected documents..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={asking}
              rows={4}
              autoFocus
            />
            <button type="submit" disabled={asking || !question.trim() || selectedDocs.length === 0}>
              {asking ? 'Finding Answer...' : 'Ask Question'}
            </button>
          </form>
        </>
      )}

      {answer && (
        <div className="answer-result">
          <div className="answer-header">
            <h3>Question:</h3>
            <p>{answer.question}</p>
          </div>

          <div className="answer-body">
            <h3>Answer:</h3>
            <p>{answer.answer}</p>
          </div>

          {answer.citations && answer.citations.length > 0 && (
            <div className="citations">
              <h3>Sources ({answer.citations.length})</h3>
              {answer.citations.map((citation, idx) => (
                <div key={idx} className="citation-card">
                  <div className="citation-header">
                    <strong>Page {citation.page}</strong>
                    {citation.section && <span> • {citation.section}</span>}
                  </div>
                  {citation.text && (
                    <p className="citation-text">"{citation.text}"</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {answer.confidence > 0 && (
            <div className="confidence">
              <strong>Confidence:</strong> {(answer.confidence * 100).toFixed(0)}%
            </div>
          )}

          <div className="action-buttons">
            <button onClick={handleReset} className="action-button">
              Ask Another Question
            </button>
          </div>
        </div>
      )}

      {asking && (
        <div className="processing-status">
          <div className="spinner"></div>
          <p>Searching documents and generating answer...</p>
        </div>
      )}
    </div>
  )
}

export default DocumentQuestionAsker
