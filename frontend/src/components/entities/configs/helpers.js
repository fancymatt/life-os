/**
 * Entity Config Helper Functions
 *
 * Shared utility functions used across entity configurations
 */

/**
 * Format a date string into a human-readable format
 * @param {string} dateString - ISO date string
 * @returns {string|null} Formatted date or null if invalid
 */
export const formatDate = (dateString) => {
  if (!dateString) return null
  const date = new Date(dateString)
  // Check if date is invalid or is Unix epoch (Jan 1, 1970 or earlier)
  if (isNaN(date.getTime()) || date.getFullYear() < 1971) {
    return null
  }
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Count the number of words in a text string
 * @param {string} text - Text to count words in
 * @returns {number} Word count
 */
export const getWordCount = (text) => {
  return text?.split(/\s+/).filter(word => word.length > 0).length || 0
}

/**
 * Get a preview of text with a maximum word count
 * @param {string} text - Text to preview
 * @param {number} maxWords - Maximum number of words (default: 30)
 * @returns {string} Truncated preview with ellipsis if needed
 */
export const getPreview = (text, maxWords = 30) => {
  if (!text) return ''
  const words = text.split(/\s+/)
  if (words.length <= maxWords) return text
  return words.slice(0, maxWords).join(' ') + '...'
}
