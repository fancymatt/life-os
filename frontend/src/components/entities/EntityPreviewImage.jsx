import { useState, useEffect, useRef } from 'react'
import { useJobStream } from '../../contexts/JobStreamContext'
import api from '../../api/client'

/**
 * EntityPreviewImage - Universal preview image component with job tracking
 *
 * Handles:
 * - Stand-in icons when no preview exists (maintains square shape)
 * - Actual preview images when available
 * - Auto-detection of preview generation jobs (even if triggered externally)
 * - Real-time "Generating..." overlay with progress
 * - Automatic image update when generation completes (no refresh needed)
 *
 * Works with any entity type (clothing items, characters, outfits, etc.)
 *
 * @param {Object} props
 * @param {string} props.entityType - Entity type for job matching (e.g., 'clothing_item', 'character')
 * @param {string} props.entityId - Entity ID for job matching
 * @param {string} props.previewImageUrl - Current preview image URL (or null/undefined)
 * @param {string} props.standInIcon - Emoji or text to show when no preview (e.g., '👕', '👤')
 * @param {string} props.size - Size variant: 'small' (100x100), 'medium' (400x400), 'large' (800x800), 'full' (original) (default: 'medium')
 * @param {string} props.shape - Shape: 'square', 'circle', 'preserve' (default: 'square')
 *                                'preserve' maintains original aspect ratio (for images entity)
 * @param {Function} props.onUpdate - Optional callback when image updates
 */
function EntityPreviewImage({
  entityType,
  entityId,
  previewImageUrl,
  standInIcon = '🖼️',
  size = 'medium',
  shape = 'square',
  onUpdate
}) {
  const [generatingJobId, setGeneratingJobId] = useState(null)
  const [jobProgress, setJobProgress] = useState(null)
  const [currentImageUrl, setCurrentImageUrl] = useState(previewImageUrl)
  const [imageKey, setImageKey] = useState(0) // Force re-mount of img tag
  const { subscribe } = useJobStream()

  // Use ref for retry count to avoid triggering re-renders
  const retryCountRef = useRef(0)
  const retryTimeoutRef = useRef(null)
  const optimizationTriggeredRef = useRef(false) // Track if we've triggered optimization

  // Size mappings
  const sizeStyles = {
    small: { fontSize: '2rem', padding: '1.5rem' },
    medium: { fontSize: '4rem', padding: '3rem' },
    large: { fontSize: '6rem', padding: '4rem' }
  }

  /**
   * Get size-appropriate image URL
   *
   * Transforms preview URLs to use optimized versions (small/medium/large) when available.
   * This reduces bandwidth usage by 80-99% for grid/list views.
   *
   * Sizes:
   * - small: 100x100px (~3-5KB)
   * - medium: 400x400px (~40-60KB) - used for grid cards
   * - large: 800x800px (~180-220KB) - used for preview panels
   * - full: Original resolution (~1MB+)
   *
   * @param {string} baseUrl - Base preview image URL
   * @param {string} size - Size variant ('small', 'medium', 'large', 'full')
   * @param {Object} jobResult - Optional job result with explicit size URLs
   * @returns {string} Size-appropriate URL
   */
  const getSizedImageUrl = (baseUrl, size, jobResult = null) => {
    if (!baseUrl) return null

    // If job result has explicit size URLs, use those
    if (jobResult) {
      if (size === 'small' && jobResult.preview_image_small) {
        return jobResult.preview_image_small
      }
      if (size === 'medium' && jobResult.preview_image_medium) {
        return jobResult.preview_image_medium
      }
      if (size === 'large' && jobResult.preview_image_large) {
        return jobResult.preview_image_large
      }
      if (jobResult.preview_image_path) {
        return jobResult.preview_image_path
      }
    }

    // Strip existing query params and timestamp
    const stripQuery = (url) => url.split('?')[0]
    const cleanUrl = stripQuery(baseUrl)

    // Transform URL based on size
    // Pattern: /entity_previews/{type}/{id}_preview.png -> /entity_previews/{type}/{id}_preview_{size}.png
    if (size === 'small' && cleanUrl.includes('_preview.png')) {
      return cleanUrl.replace('_preview.png', '_preview_small.png')
    }
    if (size === 'medium' && cleanUrl.includes('_preview.png')) {
      return cleanUrl.replace('_preview.png', '_preview_medium.png')
    }
    if (size === 'large' && cleanUrl.includes('_preview.png')) {
      return cleanUrl.replace('_preview.png', '_preview_large.png')
    }

    // Full size or non-standard URL: use as-is
    return cleanUrl
  }

  // Check for active jobs on mount
  useEffect(() => {
    const checkForActiveJobs = async () => {
      try {
        const response = await api.get('/jobs?limit=50')
        console.log(`🔍 Checking for active jobs for ${entityType}:${entityId}`)

        // API returns jobs array directly in response.data
        const jobs = Array.isArray(response.data) ? response.data : response.data.jobs

        if (!jobs || !Array.isArray(jobs)) {
          console.warn('No jobs array in response:', response.data)
          return
        }

        // Look for any active job for this entity
        const activeJobs = jobs.filter(job => {
          const isActive = job.status === 'queued' || job.status === 'pending' || job.status === 'running'
          const isOurEntity = job.metadata?.entity_type === entityType &&
                             job.metadata?.entity_id === entityId
          return isActive && isOurEntity
        })

        console.log(`Found ${activeJobs.length} active jobs for this entity`)

        if (activeJobs.length > 0) {
          const activeJob = activeJobs[0]
          console.log(`🎨 Found active job on mount for ${entityType}:`, entityId, activeJob.job_id)
          setGeneratingJobId(activeJob.job_id)
          setJobProgress(activeJob.progress || 0)
        }
      } catch (error) {
        console.error('Error checking for active jobs:', error)
      }
    }

    checkForActiveJobs()
  }, [entityType, entityId])

  // Listen to shared SSE connection
  useEffect(() => {
    const handleJobUpdate = (job) => {
      // Check if this job is for OUR entity
      const isOurJob = generatingJobId && job.job_id === generatingJobId

      // Check metadata (available immediately when job is created)
      const isOurEntityMeta = job.metadata &&
                              job.metadata.entity_type === entityType &&
                              job.metadata.entity_id === entityId

      // Check result (only available when job completes)
      const isOurEntity = job.result &&
                         job.result.entity_type === entityType &&
                         job.result.entity_id === entityId

      // Also check item_id for backward compatibility with existing jobs
      const isOurItemLegacy = job.result && job.result.item_id === entityId

      if (!isOurJob && !isOurEntityMeta && !isOurEntity && !isOurItemLegacy) return

      // If we weren't tracking this job, start tracking it
      // Detect job in ANY active state (queued, pending, running)
      if (!generatingJobId && (isOurEntityMeta || isOurEntity || isOurItemLegacy)) {
        if (job.status === 'queued' || job.status === 'pending' || job.status === 'running') {
          console.log(`🎨 Detected preview generation for ${entityType}:`, entityId, `(${job.status})`)
          setGeneratingJobId(job.job_id)
        }
      }

      setJobProgress(job.progress)

      if (job.status === 'completed') {
        console.log(`✅ Preview generation completed for ${entityType}:`, entityId)

        // Update the preview image immediately from job result
        // Use size-appropriate version (small/medium/full) to save bandwidth
        // Check both preview_image_path (full generation) and path (optimization)
        const imagePath = job.result?.preview_image_path || job.result?.path
        if (imagePath) {
          const sizedUrl = getSizedImageUrl(imagePath, size, job.result)
          const imageUrl = `${sizedUrl}?t=${Date.now()}`
          setCurrentImageUrl(imageUrl)
          console.log(`Updated preview image (${size}):`, imageUrl)
        }

        setGeneratingJobId(null)
        setJobProgress(null)
        optimizationTriggeredRef.current = false // Reset for future optimizations

        // Trigger callback if provided
        if (onUpdate) onUpdate()
      } else if (job.status === 'failed') {
        console.error(`❌ Preview generation failed for ${entityType}:`, job.error)
        setGeneratingJobId(null)
        setJobProgress(null)
        optimizationTriggeredRef.current = false // Allow retry
      }
    }

    // Subscribe to shared job stream
    const unsubscribe = subscribe(handleJobUpdate)

    return () => {
      unsubscribe()
    }
  }, [generatingJobId, entityType, entityId, onUpdate, subscribe])

  // Initialize image from prop (always use fresh timestamp to prevent caching)
  useEffect(() => {
    if (!previewImageUrl) {
      setCurrentImageUrl(null)
      return
    }

    // ALWAYS use a fresh cache-busting timestamp
    // This ensures browser never shows stale cached images
    // Also transform URL to use size-appropriate version (small/medium/full)
    const sizedUrl = getSizedImageUrl(previewImageUrl, size)
    const urlWithTimestamp = `${sizedUrl}?t=${Date.now()}`

    console.log(`📸 Loading ${size} preview:`, urlWithTimestamp)
    setCurrentImageUrl(urlWithTimestamp)
  }, [previewImageUrl, size])

  // Handle image load errors with on-demand optimization
  const handleImageError = async () => {
    // Clear any pending retry
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current)
    }

    // Check if this is an optimized size (small/medium/large) that might not exist yet
    const isOptimizedSize = currentImageUrl && (
      currentImageUrl.includes('_preview_small.png') ||
      currentImageUrl.includes('_preview_medium.png') ||
      currentImageUrl.includes('_preview_large.png')
    )

    // If it's an optimized size and we haven't triggered optimization yet, do it now
    if (isOptimizedSize && !optimizationTriggeredRef.current && !generatingJobId) {
      console.log(`🔧 Optimized ${size} version not found, triggering generation...`)
      optimizationTriggeredRef.current = true

      try {
        const response = await api.post('/entity-previews/optimize', {
          entity_type: entityType,
          entity_id: entityId,
          size: size
        })

        if (response.data.status === 'generating') {
          console.log(`✨ Started optimization job: ${response.data.job_id}`)
          setGeneratingJobId(response.data.job_id)
          setJobProgress(0)
          // SSE will pick up the job and update when complete
        } else if (response.data.status === 'exists') {
          console.log(`✅ Optimized version already exists, retrying load...`)
          // Force reload
          setImageKey(prev => prev + 1)
        }
      } catch (error) {
        console.error('Failed to trigger optimization:', error)
        optimizationTriggeredRef.current = false // Allow retry
      }
      return
    }

    // If optimization is already running, don't retry - wait for SSE
    if (generatingJobId) {
      console.log(`⏳ Optimization in progress (job ${generatingJobId}), waiting...`)
      return
    }

    // Only retry for fresh URLs (likely newly generated images)
    const isFreshUrl = currentImageUrl && currentImageUrl.includes('?t=')

    if (isFreshUrl && retryCountRef.current < 10) {
      // Exponential backoff: 100ms, 200ms, 400ms, 800ms, etc.
      const delay = Math.min(100 * Math.pow(2, retryCountRef.current), 3000)

      console.log(`Image load failed (attempt ${retryCountRef.current + 1}/10), retrying in ${delay}ms...`)

      retryTimeoutRef.current = setTimeout(() => {
        // Increment retry count using ref (doesn't cause re-render)
        retryCountRef.current += 1

        // Force reload by incrementing key (re-mounts img tag)
        setImageKey(prev => prev + 1)
      }, delay)
    } else if (retryCountRef.current >= 10) {
      console.error('Image failed to load after 10 retries, giving up')
      retryCountRef.current = 0 // Reset for next attempt
    }
  }

  // Reset retry count and optimization flag when entity changes
  useEffect(() => {
    retryCountRef.current = 0
    optimizationTriggeredRef.current = false
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current)
    }
  }, [entityId, size])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [])

  // Container styles based on shape
  const containerStyle = shape === 'preserve' ? {
    // Preserve aspect ratio - let image determine height
    position: 'relative',
    width: '100%',
    borderRadius: '8px',
    overflow: 'hidden',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  } : {
    // Square or circle - force square aspect ratio
    position: 'relative',
    width: '100%',
    paddingBottom: '100%', // Square aspect ratio
    borderRadius: shape === 'circle' ? '50%' : '8px',
    overflow: 'hidden'
  }

  // Image styles based on shape
  const imageStyle = shape === 'preserve' ? {
    width: '100%',
    height: 'auto',
    display: 'block'
  } : {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    objectFit: 'cover'
  }

  return (
    <div style={containerStyle}>
      {currentImageUrl ? (
        // Show actual preview image
        <img
          key={imageKey}
          src={currentImageUrl}
          alt="Preview"
          onError={handleImageError}
          style={imageStyle}
        />
      ) : (
        // Show stand-in icon
        <div style={shape === 'preserve' ? {
          // For preserved aspect - show minimal stand-in
          width: '100%',
          aspectRatio: '16/9', // Default aspect ratio for stand-in
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2))',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: sizeStyles[size].fontSize
        } : {
          // For square/circle - fill the container
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2))',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: sizeStyles[size].fontSize
        }}>
          {standInIcon}
        </div>
      )}

      {/* Subtle loading indicator when generating */}
      {generatingJobId && (
        <div style={{
          position: 'absolute',
          bottom: '0.5rem',
          right: '0.5rem',
          width: '1.5rem',
          height: '1.5rem',
          borderRadius: '50%',
          border: '2px solid rgba(255, 255, 255, 0.3)',
          borderTopColor: 'white',
          animation: 'spin 0.8s linear infinite',
          background: 'rgba(0, 0, 0, 0.3)',
          boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
        }} />
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export default EntityPreviewImage
