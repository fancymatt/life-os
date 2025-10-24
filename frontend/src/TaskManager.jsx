import { useState, useEffect } from 'react'
import './TaskManager.css'
import api from './api/client'

function TaskManager() {
  const [jobs, setJobs] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  const [filter, setFilter] = useState('all') // all, running, completed, failed

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

          // Handle connection message
          if (data.type === 'connected') {
            console.log('✅ Job stream connected')
            // Fetch initial jobs
            fetchJobs()
            return
          }

          // Update job in list
          const job = data
          setJobs(prevJobs => {
            const existingIndex = prevJobs.findIndex(j => j.job_id === job.job_id)
            if (existingIndex >= 0) {
              // Update existing job
              const newJobs = [...prevJobs]
              newJobs[existingIndex] = job
              return newJobs
            } else {
              // Add new job
              return [job, ...prevJobs]
            }
          })

          // Note: Removed auto-dismiss - let user manually dismiss completed jobs
        } catch (err) {
          console.error('Failed to parse job update:', err)
        }
      }

      eventSource.onerror = (err) => {
        console.error('SSE connection error:', err)
        eventSource.close()

        // Reconnect after 5 seconds
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

  // Fetch initial jobs
  const fetchJobs = async () => {
    try {
      console.log('🔍 Fetching jobs...')
      const response = await api.get('/jobs?limit=20')
      console.log('✅ Fetched', response.data.length, 'jobs:', response.data)
      setJobs(response.data)
    } catch (err) {
      console.error('❌ Failed to fetch jobs:', err)
      console.error('Error details:', err.response?.data || err.message)
    }
  }

  // Cancel job
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

  // Dismiss completed/failed job
  const handleDismiss = async (jobId) => {
    try {
      await api.delete(`/jobs/${jobId}`)
      setJobs(prevJobs => prevJobs.filter(j => j.job_id !== jobId))
    } catch (err) {
      console.error('Failed to dismiss job:', err)
    }
  }

  // Filter jobs
  const filteredJobs = jobs.filter(job => {
    if (filter === 'all') return true
    if (filter === 'running') return job.status === 'running' || job.status === 'queued'
    if (filter === 'completed') return job.status === 'completed'
    if (filter === 'failed') return job.status === 'failed' || job.status === 'cancelled'
    return true
  })

  // Count active jobs
  const activeCount = jobs.filter(j =>
    j.status === 'running' || j.status === 'queued'
  ).length

  // Determine button color based on job statuses
  const getButtonColor = () => {
    const hasRunning = jobs.some(j => j.status === 'running' || j.status === 'queued')
    const hasFailed = jobs.some(j => j.status === 'failed')

    if (hasFailed) return 'failed'
    if (hasRunning) return 'running'
    return 'idle'
  }

  // Debug logging
  console.log('📊 TaskManager render - jobs.length:', jobs.length, 'filteredJobs.length:', filteredJobs.length, 'filter:', filter)

  return (
    <>
      {/* Floating Button */}
      <button
        className={`task-manager-button ${getButtonColor()}`}
        onClick={() => setIsOpen(!isOpen)}
        title="Task Manager"
      >
        <span className="task-icon">⚡</span>
        {activeCount > 0 && (
          <span className="task-badge">{activeCount}</span>
        )}
      </button>

      {/* Task Panel */}
      {isOpen && (
        <div className="task-panel">
          <div className="task-panel-header">
            <h3>Tasks ({jobs.length})</h3>
            <button
              className="close-panel-button"
              onClick={() => setIsOpen(false)}
            >
              ×
            </button>
          </div>

          {/* Filter Tabs */}
          <div className="task-filters">
            <button
              className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All
            </button>
            <button
              className={`filter-tab ${filter === 'running' ? 'active' : ''}`}
              onClick={() => setFilter('running')}
            >
              Active
            </button>
            <button
              className={`filter-tab ${filter === 'completed' ? 'active' : ''}`}
              onClick={() => setFilter('completed')}
            >
              Completed
            </button>
            <button
              className={`filter-tab ${filter === 'failed' ? 'active' : ''}`}
              onClick={() => setFilter('failed')}
            >
              Failed
            </button>
          </div>

          {/* Task List */}
          <div className="task-list">
            {filteredJobs.length === 0 ? (
              <div className="no-tasks">
                {filter === 'all' ? 'No tasks yet' : `No ${filter} tasks`}
              </div>
            ) : (
              filteredJobs.map(job => (
                <TaskItem
                  key={job.job_id}
                  job={job}
                  onCancel={handleCancel}
                  onDismiss={handleDismiss}
                />
              ))
            )}
          </div>
        </div>
      )}
    </>
  )
}

function TaskItem({ job, onCancel, onDismiss }) {
  const [expanded, setExpanded] = useState(false)

  // Format elapsed time
  const getElapsedTime = () => {
    const start = new Date(job.started_at || job.created_at)
    const end = job.completed_at ? new Date(job.completed_at) : new Date()
    const seconds = Math.floor((end - start) / 1000)

    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    return `${minutes}m ${seconds % 60}s`
  }

  // Status icon
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

  return (
    <div className={`task-item ${job.status}`}>
      <div className="task-item-header" onClick={() => setExpanded(!expanded)}>
        <span className="task-status-icon">{getStatusIcon()}</span>
        <div className="task-info">
          <div className="task-title">{job.title}</div>
          {job.description && (
            <div className="task-description">{job.description}</div>
          )}
          <div className="task-meta">
            {job.status === 'running' && job.progress_message && (
              <span className="task-progress-msg">{job.progress_message}</span>
            )}
            {(job.status === 'completed' || job.status === 'failed') && (
              <span className="task-time">{getElapsedTime()}</span>
            )}
          </div>
        </div>
        <div className="task-actions">
          {job.status === 'running' && job.cancelable && (
            <button
              className="task-action-btn cancel"
              onClick={(e) => {
                e.stopPropagation()
                onCancel(job.job_id)
              }}
              title="Cancel"
            >
              Cancel
            </button>
          )}
          {(job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled') && (
            <button
              className="task-action-btn dismiss"
              onClick={(e) => {
                e.stopPropagation()
                onDismiss(job.job_id)
              }}
              title="Dismiss"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {(job.status === 'running' || job.status === 'queued') && (
        <div className="task-progress-container">
          <div
            className="task-progress-bar"
            style={{ width: `${job.progress * 100}%` }}
          />
          {job.total_steps && (
            <div className="task-progress-text">
              {job.current_step || 0}/{job.total_steps}
            </div>
          )}
        </div>
      )}

      {/* Expanded Details */}
      {expanded && (
        <div className="task-details">
          {job.description && (
            <div className="task-detail-item">
              <strong>Description:</strong> {job.description}
            </div>
          )}
          {job.error && (
            <div className="task-detail-item error">
              <strong>Error:</strong> {job.error}
            </div>
          )}
          {job.result && job.result.created_presets && (
            <div className="task-detail-item">
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
          <div className="task-detail-item">
            <strong>Job ID:</strong> <code>{job.job_id}</code>
          </div>
        </div>
      )}
    </div>
  )
}

export default TaskManager
