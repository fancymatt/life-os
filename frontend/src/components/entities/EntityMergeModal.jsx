import React, { useState, useEffect } from 'react'
import api from '../../api/client'
import './EntityMergeModal.css'

/**
 * EntityMergeModal - Modal for merging duplicate entities
 *
 * Features:
 * - Side-by-side comparison of source and target entities
 * - AI-generated merged preview (editable)
 * - Shows references that will be affected
 * - Confirmation step before executing merge
 */
function EntityMergeModal({
  entityType,
  sourceEntity,
  targetEntity,
  onClose,
  onMergeComplete
}) {
  const [step, setStep] = useState('compare') // compare -> analyze -> confirm
  const [references, setReferences] = useState(null)
  const [mergedData, setMergedData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [changesSummary, setChangesSummary] = useState(null)

  // Load references for target entity when modal opens
  useEffect(() => {
    loadReferences()
  }, [])

  const loadReferences = async () => {
    try {
      setLoading(true)
      const response = await api.post('/merge/find-references', {
        entity_type: entityType,
        entity_id: targetEntity.id
      })
      setReferences(response.data)
      setLoading(false)
    } catch (err) {
      console.error('Error loading references:', err)
      setError(err.response?.data?.detail || 'Failed to load references')
      setLoading(false)
    }
  }

  const analyzeWithAI = async () => {
    try {
      setLoading(true)
      setError(null)

      // Call analyze endpoint with job-based workflow
      const response = await api.post('/merge/analyze', {
        entity_type: entityType,
        source_entity: sourceEntity.data || sourceEntity,
        target_entity: targetEntity.data || targetEntity,
        source_id: sourceEntity.id,  // Include IDs explicitly
        target_id: targetEntity.id,
        auto_approve: true  // Auto-approve for now (skip Brief card workflow)
      })

      // Response now contains job_id - poll for completion
      const jobId = response.data.job_id

      // Poll job status until completed
      const pollInterval = setInterval(async () => {
        try {
          const jobResponse = await api.get(`/jobs/${jobId}`)
          const job = jobResponse.data

          if (job.status === 'completed') {
            clearInterval(pollInterval)

            // Extract merged_data from job result
            if (job.result?.merged_data) {
              setMergedData(job.result.merged_data)
              setChangesSummary(job.result.changes_summary)
              setStep('confirm')
            } else if (job.result?.merge_result) {
              // If auto_approve completed the merge, show success
              setLoading(false)
              onMergeComplete()
              return
            }

            setLoading(false)
          } else if (job.status === 'failed') {
            clearInterval(pollInterval)
            setError(job.error || 'Analysis failed')
            setLoading(false)
          }
        } catch (pollErr) {
          clearInterval(pollInterval)
          console.error('Error polling job:', pollErr)
          setError('Failed to check job status')
          setLoading(false)
        }
      }, 1000) // Poll every second

    } catch (err) {
      console.error('Error analyzing merge:', err)
      setError(err.response?.data?.detail || 'Failed to analyze merge')
      setLoading(false)
    }
  }

  const executeMerge = async () => {
    try {
      setLoading(true)
      setError(null)

      await api.post('/merge/execute', {
        entity_type: entityType,
        source_id: sourceEntity.id,
        target_id: targetEntity.id,
        merged_data: mergedData
      })

      setLoading(false)
      onMergeComplete()
    } catch (err) {
      console.error('Error executing merge:', err)
      setError(err.response?.data?.detail || 'Failed to execute merge')
      setLoading(false)
    }
  }

  const handleFieldEdit = (field, value) => {
    setMergedData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const renderCompareStep = () => (
    <div className="merge-step merge-compare">
      <h3>Compare Entities</h3>

      <div className="merge-entities-side-by-side">
        {/* Source Entity (Keep) */}
        <div className="merge-entity-column">
          <div className="merge-column-header">
            <span className="merge-label">Source (Keep)</span>
            <span className="merge-entity-id">{sourceEntity.id}</span>
          </div>
          {renderEntityDetails(sourceEntity)}
        </div>

        {/* Target Entity (Archive) */}
        <div className="merge-entity-column">
          <div className="merge-column-header">
            <span className="merge-label">Target (Archive)</span>
            <span className="merge-entity-id">{targetEntity.id}</span>
          </div>
          {renderEntityDetails(targetEntity)}
        </div>
      </div>

      {/* References that will be updated */}
      {references && (
        <div className="merge-references">
          <h4>References to Update ({references.total_references})</h4>
          {references.total_references === 0 ? (
            <p className="merge-no-references">No references found - safe to merge</p>
          ) : (
            <div className="merge-reference-list">
              {references.references.stories?.length > 0 && (
                <div className="merge-reference-group">
                  <strong>Stories ({references.references.stories.length}):</strong>
                  <ul>
                    {references.references.stories.map(ref => (
                      <li key={ref.story_id}>{ref.title}</li>
                    ))}
                  </ul>
                </div>
              )}
              {references.references.images?.length > 0 && (
                <div className="merge-reference-group">
                  <strong>Images ({references.references.images.length}):</strong>
                  <span className="merge-reference-count">
                    {references.references.images.length} generated images
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="merge-actions">
        <button
          className="merge-btn merge-btn-secondary"
          onClick={onClose}
        >
          Cancel
        </button>
        <button
          className="merge-btn merge-btn-primary"
          onClick={analyzeWithAI}
          disabled={loading}
        >
          {loading ? 'Analyzing...' : 'Analyze with AI →'}
        </button>
      </div>
    </div>
  )

  const renderConfirmStep = () => (
    <div className="merge-step merge-confirm">
      <h3>Review Merged Entity</h3>

      {changesSummary && (
        <div className="merge-summary">
          <p>
            <strong>{changesSummary.fields_from_source}</strong> fields from source,
            <strong> {changesSummary.fields_from_target}</strong> from target,
            <strong> {changesSummary.fields_merged}</strong> merged
          </p>
        </div>
      )}

      <div className="merge-preview">
        <h4>Merged Entity Preview (Editable)</h4>
        <div className="merge-fields">
          {mergedData && Object.entries(mergedData).map(([field, value]) => {
            // Skip IDs and timestamps
            if (field.endsWith('_id') || field.endsWith('_at')) {
              return null
            }

            return (
              <div key={field} className="merge-field">
                <label>{field.replace(/_/g, ' ').toUpperCase()}:</label>
                {typeof value === 'string' ? (
                  <textarea
                    value={value}
                    onChange={(e) => handleFieldEdit(field, e.target.value)}
                    rows={value.length > 100 ? 4 : 2}
                  />
                ) : Array.isArray(value) ? (
                  <div className="merge-array-field">
                    {value.map((item, i) => (
                      <span key={i} className="merge-array-item">{item}</span>
                    ))}
                  </div>
                ) : (
                  <input
                    type="text"
                    value={JSON.stringify(value)}
                    onChange={(e) => {
                      try {
                        handleFieldEdit(field, JSON.parse(e.target.value))
                      } catch {
                        // If not valid JSON, treat as string
                        handleFieldEdit(field, e.target.value)
                      }
                    }}
                  />
                )}
              </div>
            )
          })}
        </div>
      </div>

      <div className="merge-warning">
        <strong>⚠️ Warning:</strong> This will:
        <ul>
          <li>Update source entity with merged data above</li>
          <li>Update {references?.total_references || 0} references to point to source</li>
          <li>Archive target entity with "merged_into" metadata</li>
        </ul>
        <p>This action can be reversed by unarchiving the target entity.</p>
      </div>

      <div className="merge-actions">
        <button
          className="merge-btn merge-btn-secondary"
          onClick={() => setStep('compare')}
          disabled={loading}
        >
          ← Back
        </button>
        <button
          className="merge-btn merge-btn-danger"
          onClick={executeMerge}
          disabled={loading}
        >
          {loading ? 'Merging...' : 'Execute Merge'}
        </button>
      </div>
    </div>
  )

  const renderEntityDetails = (entity) => {
    const data = entity.data || entity

    return (
      <div className="merge-entity-details">
        {Object.entries(data).map(([key, value]) => {
          // Skip IDs and complex objects
          if (key.endsWith('_id') || key.endsWith('_at') || typeof value === 'object') {
            return null
          }

          return (
            <div key={key} className="merge-detail-row">
              <span className="merge-detail-label">{key}:</span>
              <span className="merge-detail-value">
                {value ? String(value).substring(0, 100) : '(empty)'}
              </span>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="merge-modal-overlay" onClick={onClose}>
      <div className="merge-modal" onClick={(e) => e.stopPropagation()}>
        <div className="merge-modal-header">
          <h2>Merge {entityType} Entities</h2>
          <button className="merge-close-btn" onClick={onClose}>×</button>
        </div>

        <div className="merge-modal-body">
          {error && (
            <div className="merge-error">
              <strong>Error:</strong> {error}
            </div>
          )}

          {step === 'compare' && renderCompareStep()}
          {step === 'confirm' && renderConfirmStep()}
        </div>
      </div>
    </div>
  )
}

export default EntityMergeModal
