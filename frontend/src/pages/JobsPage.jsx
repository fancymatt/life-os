import { useState, useEffect } from 'react'
import './JobsPage.css'
import api from '../api/client'

function JobsPage() {
  const [jobs, setJobs] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  // Connect to SSE for real-time job updates
  useEffect(() => {
    let eventSource

    const connectSSE = () => {
      eventSource = new EventSource('/api/jobs/stream')

      eventSource.onopen = () => {
        console.log('📡 Connected to job stream')
      }

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === 'connected') {
            console.log('✅ Job stream connected')
            fetchJobs()
            return
          }

          const job = data
          setJobs(prevJobs => {
            const existingIndex = prevJobs.findIndex(j => j.job_id === job.job_id)
            if (existingIndex >= 0) {
              const newJobs = [...prevJobs]
              newJobs[existingIndex] = job
              return newJobs
            } else {
              return [job, ...prevJobs]
            }
          })
        } catch (err) {
          console.error('Failed to parse job update:', err)
        }
      }

      eventSource.onerror = (err) => {
        console.error('SSE connection error:', err)
        eventSource.close()
        setTimeout(connectSSE, 5000)
      }
    }

    connectSSE()

    return () => {
      if (eventSource) {
        eventSource.close()
      }
    }
  }, [])

  const fetchJobs = async () => {
    try {
      setLoading(true)
      const response = await api.get('/jobs?limit=100')
      setJobs(response.data)
    } catch (err) {
      console.error('Failed to fetch jobs:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (jobId) => {
    try {
      const response = await api.post(`/jobs/${jobId}/cancel`)
      setJobs(prevJobs =>
        prevJobs.map(j => j.job_id === jobId ? response.data : j)
      )
    } catch (err) {
      console.error('Failed to cancel job:', err)
    }
  }

  const handleDismiss = async (jobId) => {
    try {
      await api.delete(`/jobs/${jobId}`)
      setJobs(prevJobs => prevJobs.filter(j => j.job_id !== jobId))
    } catch (err) {
      console.error('Failed to dismiss job:', err)
    }
  }

  const filteredJobs = jobs.filter(job => {
    if (filter === 'all') return true
    if (filter === 'running') return job.status === 'running' || job.status === 'queued'
    if (filter === 'completed') return job.status === 'completed'
    if (filter === 'failed') return job.status === 'failed' || job.status === 'cancelled'
    return true
  })

  return (
    <div className="jobs-page">
      <div className="jobs-header">
        <h2>Task History</h2>
        <p className="jobs-subtitle">
          {jobs.length} total task{jobs.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="jobs-filters">
        <button
          className={`filter-button ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All ({jobs.length})
        </button>
        <button
          className={`filter-button ${filter === 'running' ? 'active' : ''}`}
          onClick={() => setFilter('running')}
        >
          Active ({jobs.filter(j => j.status === 'running' || j.status === 'queued').length})
        </button>
        <button
          className={`filter-button ${filter === 'completed' ? 'active' : ''}`}
          onClick={() => setFilter('completed')}
        >
          Completed ({jobs.filter(j => j.status === 'completed').length})
        </button>
        <button
          className={`filter-button ${filter === 'failed' ? 'active' : ''}`}
          onClick={() => setFilter('failed')}
        >
          Failed ({jobs.filter(j => j.status === 'failed' || j.status === 'cancelled').length})
        </button>
      </div>

      <div className="jobs-list">
        {loading ? (
          <div className="jobs-loading">Loading tasks...</div>
        ) : filteredJobs.length === 0 ? (
          <div className="jobs-empty">
            {filter === 'all' ? 'No tasks yet' : `No ${filter} tasks`}
          </div>
        ) : (
          filteredJobs.map(job => (
            <JobItem
              key={job.job_id}
              job={job}
              onCancel={handleCancel}
              onDismiss={handleDismiss}
            />
          ))
        )}
      </div>
    </div>
  )
}

function JobItem({ job, onCancel, onDismiss }) {
  const [expanded, setExpanded] = useState(false)

  const getElapsedTime = () => {
    const start = new Date(job.started_at || job.created_at)
    const end = job.completed_at ? new Date(job.completed_at) : new Date()
    const seconds = Math.floor((end - start) / 1000)

    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    return `${minutes}m ${seconds % 60}s`
  }

  const getStatusIcon = () => {
    switch (job.status) {
      case 'queued':
        return '⏳'
      case 'running':
        return '⟳'
      case 'completed':
        return '✓'
      case 'failed':
        return '✗'
      case 'cancelled':
        return '⊘'
      default:
        return '•'
    }
  }

  const getStatusClass = () => {
    return `job-item ${job.status}`
  }

  return (
    <div className={getStatusClass()}>
      <div className="job-item-header" onClick={() => setExpanded(!expanded)}>
        <span className="job-status-icon">{getStatusIcon()}</span>
        <div className="job-info">
          <div className="job-title">{job.title}</div>
          <div className="job-meta">
            <span className="job-id">#{job.job_id.slice(0, 8)}</span>
            {job.status === 'running' && job.progress_message && (
              <span className="job-progress-msg">{job.progress_message}</span>
            )}
            {(job.status === 'completed' || job.status === 'failed') && (
              <span className="job-time">{getElapsedTime()}</span>
            )}
          </div>
        </div>
        <div className="job-actions">
          {job.status === 'running' && job.cancelable && (
            <button
              className="job-action-btn cancel"
              onClick={(e) => {
                e.stopPropagation()
                onCancel(job.job_id)
              }}
            >
              Cancel
            </button>
          )}
          {(job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled') && (
            <button
              className="job-action-btn dismiss"
              onClick={(e) => {
                e.stopPropagation()
                onDismiss(job.job_id)
              }}
            >
              ×
            </button>
          )}
        </div>
      </div>

      {(job.status === 'running' || job.status === 'queued') && (
        <div className="job-progress-container">
          <div
            className="job-progress-bar"
            style={{ width: `${job.progress * 100}%` }}
          />
          {job.total_steps && (
            <div className="job-progress-text">
              {job.current_step || 0}/{job.total_steps}
            </div>
          )}
        </div>
      )}

      {expanded && (
        <div className="job-details">
          {job.description && (
            <div className="job-detail-item">
              <strong>Description:</strong> {job.description}
            </div>
          )}
          {job.error && (
            <div className="job-detail-item error">
              <strong>Error:</strong> {job.error}
            </div>
          )}
          {job.result && job.result.created_presets && (
            <div className="job-detail-item">
              <strong>Created Presets:</strong>
              <ul>
                {job.result.created_presets.map((preset, idx) => (
                  <li key={idx}>
                    {preset.name} ({preset.type})
                  </li>
                ))}
              </ul>
            </div>
          )}
          <div className="job-detail-item">
            <strong>Job ID:</strong> <code>{job.job_id}</code>
          </div>
          <div className="job-detail-item">
            <strong>Created:</strong> {new Date(job.created_at).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  )
}

export default JobsPage
