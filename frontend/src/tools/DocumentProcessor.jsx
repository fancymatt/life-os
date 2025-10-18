import { useState, useEffect } from 'react'
import api from '../api/client'
import './ToolPage.css'

/**
 * Document Processor Tool
 *
 * Converts PDF documents to markdown and creates vector embeddings for Q&A.
 */
function DocumentProcessor() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      setLoading(true)
      const response = await api.get('/documents/')
      setDocuments(response.data.documents || [])
    } catch (err) {
      console.error('Failed to load documents:', err)
      setError('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const handleProcess = async (document) => {
    try {
      setProcessing(true)
      setError(null)
      setResult(null)

      const response = await api.post(`/documents/${document.document_id}/process`, null, {
        params: {
          chunk_size: 500,
          overlap: 50
        }
      })

      setResult({
        ...response.data,
        documentTitle: document.title
      })

      // Reload documents to update processed status
      await loadDocuments()
    } catch (err) {
      console.error('Failed to process document:', err)
      setError(err.response?.data?.detail || 'Failed to process document')
    } finally {
      setProcessing(false)
    }
  }

  const unprocessedDocs = documents.filter(d => !d.processed)
  const processedDocs = documents.filter(d => d.processed)

  return (
    <div className="tool-page">
      <div className="tool-header">
        <h1>📄 Document Processor</h1>
        <p>Convert PDFs to searchable text and enable Q&A</p>
      </div>

      {error && <div className="error-message"><strong>Error:</strong> {error}</div>}

      {processing && (
        <div className="processing-status">
          <div className="spinner"></div>
          <p>Processing document...</p>
        </div>
      )}

      {result && (
        <div className="result-success">
          <div className="success-icon">✓</div>
          <h2>Document Processed!</h2>
          <h3>{result.documentTitle}</h3>
          <div className="result-details">
            <p><strong>Chunks Created:</strong> {result.chunks_created || 'N/A'}</p>
            <p><strong>Markdown Path:</strong> <code>{result.markdown_path}</code></p>
            <div className="next-steps">
              <p><strong>Next step:</strong> Use the Document Question Asker tool to ask questions about this document.</p>
            </div>
          </div>
          <button onClick={() => setResult(null)} className="action-button">
            Process Another Document
          </button>
        </div>
      )}

      {!result && loading && (
        <div className="loading">Loading documents...</div>
      )}

      {!result && !loading && (
        <>
          {unprocessedDocs.length > 0 && (
            <div className="document-section">
              <h3>📋 Unprocessed Documents ({unprocessedDocs.length})</h3>
              <div className="documents-grid">
                {unprocessedDocs.map(doc => (
                  <div key={doc.document_id} className="document-card">
                    <div className="document-info">
                      <h4>{doc.title}</h4>
                      <p className="doc-meta">{doc.source_type.toUpperCase()}</p>
                      {doc.page_count && <p className="doc-meta">{doc.page_count} pages</p>}
                    </div>
                    <button
                      onClick={() => handleProcess(doc)}
                      disabled={processing}
                      className="process-button"
                    >
                      {processing ? 'Processing...' : 'Process Document'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {processedDocs.length > 0 && (
            <div className="document-section">
              <h3>✓ Processed Documents ({processedDocs.length})</h3>
              <div className="documents-grid">
                {processedDocs.map(doc => (
                  <div key={doc.document_id} className="document-card processed">
                    <div className="document-info">
                      <h4>{doc.title}</h4>
                      <p className="doc-meta">{doc.source_type.toUpperCase()}</p>
                      {doc.vector_ids && <p className="doc-meta">{doc.vector_ids.length} chunks</p>}
                    </div>
                    <div className="processed-badge">✓ Ready for Q&A</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {documents.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <h3>No Documents Found</h3>
              <p>Use the BGG Rulebook Fetcher tool to download rulebooks first.</p>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default DocumentProcessor
