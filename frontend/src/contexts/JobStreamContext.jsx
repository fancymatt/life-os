import { createContext, useContext, useEffect, useRef } from 'react'

/**
 * JobStreamContext - Provides a single shared SSE connection for job updates
 *
 * Instead of each component creating its own SSE connection (which fails with many components),
 * this context provides one shared connection that all components can listen to.
 *
 * Performance: Uses useRef for listeners to avoid re-renders when components subscribe/unsubscribe
 */

const JobStreamContext = createContext(null)

export function JobStreamProvider({ children }) {
  const listenersRef = useRef([])

  // Create single SSE connection
  useEffect(() => {
    const es = new EventSource('/api/jobs/stream')

    es.onopen = () => {
      console.log('📡 SSE connection opened')
    }

    es.onmessage = (event) => {
      try {
        const job = JSON.parse(event.data)
        // Notify all registered listeners (access current listeners via ref)
        listenersRef.current.forEach(listener => listener(job))
      } catch (error) {
        console.error('Error processing SSE message:', error)
      }
    }

    es.onerror = (error) => {
      console.error('SSE connection error:', error)
      es.close()
    }

    return () => {
      console.log('📡 Closing SSE connection')
      es.close()
    }
  }, []) // Empty deps - only create once

  const subscribe = (listener) => {
    // Add listener to ref (no re-render)
    listenersRef.current = [...listenersRef.current, listener]

    // Return unsubscribe function
    return () => {
      listenersRef.current = listenersRef.current.filter(l => l !== listener)
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
