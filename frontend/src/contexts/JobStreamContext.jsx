import { createContext, useContext, useEffect, useState } from 'react'

/**
 * JobStreamContext - Provides a single shared SSE connection for job updates
 *
 * Instead of each component creating its own SSE connection (which fails with many components),
 * this context provides one shared connection that all components can listen to.
 */

const JobStreamContext = createContext(null)

export function JobStreamProvider({ children }) {
  const [eventSource, setEventSource] = useState(null)
  const [listeners, setListeners] = useState([])

  // Create single SSE connection
  useEffect(() => {
    const es = new EventSource('/api/jobs/stream')

    es.onopen = () => {
      console.log('📡 SSE connection opened')
    }

    es.onmessage = (event) => {
      try {
        const job = JSON.parse(event.data)
        // Notify all registered listeners
        listeners.forEach(listener => listener(job))
      } catch (error) {
        console.error('Error processing SSE message:', error)
      }
    }

    es.onerror = (error) => {
      console.error('SSE connection error:', error)
      es.close()
    }

    setEventSource(es)

    return () => {
      console.log('📡 Closing SSE connection')
      es.close()
    }
  }, []) // Empty deps - only create once

  // Re-notify listeners when job updates come in
  useEffect(() => {
    if (!eventSource) return

    const handler = (event) => {
      try {
        const job = JSON.parse(event.data)
        listeners.forEach(listener => listener(job))
      } catch (error) {
        console.error('Error processing SSE message:', error)
      }
    }

    eventSource.addEventListener('message', handler)

    return () => {
      eventSource.removeEventListener('message', handler)
    }
  }, [eventSource, listeners])

  const subscribe = (listener) => {
    setListeners(prev => [...prev, listener])
    // Return unsubscribe function
    return () => {
      setListeners(prev => prev.filter(l => l !== listener))
    }
  }

  return (
    <JobStreamContext.Provider value={{ subscribe }}>
      {children}
    </JobStreamContext.Provider>
  )
}

export function useJobStream() {
  const context = useContext(JobStreamContext)
  if (!context) {
    throw new Error('useJobStream must be used within JobStreamProvider')
  }
  return context
}
