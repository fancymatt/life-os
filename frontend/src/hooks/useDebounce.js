import { useState, useEffect } from 'react'

/**
 * Custom hook that debounces a value
 *
 * Delays updating the returned value until the specified delay has passed
 * without the value changing. Useful for search inputs to avoid excessive
 * filtering/API calls on every keystroke.
 *
 * @param {any} value - The value to debounce
 * @param {number} delay - The delay in milliseconds (default: 300ms)
 * @returns {any} The debounced value
 *
 * @example
 * const [searchQuery, setSearchQuery] = useState('')
 * const debouncedSearchQuery = useDebounce(searchQuery, 500)
 *
 * // debouncedSearchQuery will only update 500ms after the user stops typing
 */
export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    // Set up a timer to update the debounced value after the delay
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    // Clean up the timer if value changes before delay completes
    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}
