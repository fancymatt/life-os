import { useRef, useCallback, useState } from 'react'

/**
 * Custom hook that implements an LRU (Least Recently Used) cache
 *
 * Automatically evicts the least recently used items when the cache reaches
 * its maximum size. Useful for caching expensive computations or API results
 * without unbounded memory growth.
 *
 * @param {number} maxSize - Maximum number of items to cache (default: 50)
 * @returns {Object} Cache operations { get, set, has, clear, size }
 *
 * @example
 * const cache = useLRUCache(50)
 * cache.set('key1', { data: 'value' })
 * const value = cache.get('key1')  // Returns { data: 'value' }
 * const exists = cache.has('key1')  // Returns true
 */
export function useLRUCache(maxSize = 50) {
  // Use ref to avoid re-renders and circular dependencies
  const cacheRef = useRef([])
  // Use state only for size to trigger re-renders when needed
  const [size, setSize] = useState(0)

  /**
   * Get a value from the cache by key
   * Updates the item's timestamp to mark it as recently used
   */
  const get = useCallback((key) => {
    const index = cacheRef.current.findIndex(item => item.key === key)

    if (index === -1) {
      return null
    }

    // Update timestamp to mark as recently used
    const item = cacheRef.current[index]
    cacheRef.current[index] = { ...item, timestamp: Date.now() }

    return item.value
  }, [])

  /**
   * Set a value in the cache
   * Evicts the least recently used item if cache is full
   */
  const set = useCallback((key, value) => {
    // Check if key already exists
    const existingIndex = cacheRef.current.findIndex(item => item.key === key)

    if (existingIndex !== -1) {
      // Update existing item
      cacheRef.current[existingIndex] = { key, value, timestamp: Date.now() }
      return
    }

    // Add new item
    cacheRef.current.push({ key, value, timestamp: Date.now() })

    // Evict least recently used item if cache is full
    if (cacheRef.current.length > maxSize) {
      // Sort by timestamp (oldest first) and remove the oldest
      cacheRef.current.sort((a, b) => a.timestamp - b.timestamp)
      cacheRef.current.shift()  // Remove oldest item
    }

    // Update size state to trigger re-render
    setSize(cacheRef.current.length)
  }, [maxSize])

  /**
   * Check if a key exists in the cache
   */
  const has = useCallback((key) => {
    return cacheRef.current.some(item => item.key === key)
  }, [])

  /**
   * Clear all items from the cache
   */
  const clear = useCallback(() => {
    cacheRef.current = []
    setSize(0)
  }, [])

  return {
    get,
    set,
    has,
    clear,
    size
  }
}
