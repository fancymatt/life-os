import { useState, useCallback } from 'react'

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
  // Store cache as array of { key, value, timestamp } objects
  const [cache, setCache] = useState([])

  /**
   * Get a value from the cache by key
   * Updates the item's timestamp to mark it as recently used
   */
  const get = useCallback((key) => {
    const index = cache.findIndex(item => item.key === key)

    if (index === -1) {
      return null
    }

    // Update timestamp to mark as recently used
    const item = cache[index]
    const updatedItem = { ...item, timestamp: Date.now() }

    setCache(prev => {
      const newCache = [...prev]
      newCache[index] = updatedItem
      return newCache
    })

    return item.value
  }, [cache])

  /**
   * Set a value in the cache
   * Evicts the least recently used item if cache is full
   */
  const set = useCallback((key, value) => {
    setCache(prev => {
      // Check if key already exists
      const existingIndex = prev.findIndex(item => item.key === key)

      if (existingIndex !== -1) {
        // Update existing item
        const newCache = [...prev]
        newCache[existingIndex] = { key, value, timestamp: Date.now() }
        return newCache
      }

      // Add new item
      let newCache = [...prev, { key, value, timestamp: Date.now() }]

      // Evict least recently used item if cache is full
      if (newCache.length > maxSize) {
        // Sort by timestamp (oldest first) and remove the oldest
        newCache.sort((a, b) => a.timestamp - b.timestamp)
        newCache.shift()  // Remove oldest item
      }

      return newCache
    })
  }, [maxSize])

  /**
   * Check if a key exists in the cache
   */
  const has = useCallback((key) => {
    return cache.some(item => item.key === key)
  }, [cache])

  /**
   * Clear all items from the cache
   */
  const clear = useCallback(() => {
    setCache([])
  }, [])

  /**
   * Get current cache size
   */
  const size = cache.length

  return {
    get,
    set,
    has,
    clear,
    size
  }
}
