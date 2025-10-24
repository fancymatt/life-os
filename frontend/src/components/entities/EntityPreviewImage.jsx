import { useState, useEffect } from 'react'
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
 * @param {string} props.size - Size variant: 'small', 'medium', 'large' (default: 'medium')
 * @param {string} props.shape - Shape: 'square', 'circle' (default: 'square')
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
  const [jobUpdatedImage, setJobUpdatedImage] = useState(false) // Track if job updated the image
  const { subscribe } = useJobStream()

  // Size mappings
  const sizeStyles = {
    small: { fontSize: '2rem', padding: '1.5rem' },
    medium: { fontSize: '4rem', padding: '3rem' },
    large: { fontSize: '6rem', padding: '4rem' }
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
        if (job.result && job.result.preview_image_path) {
          const imageUrl = `${job.result.preview_image_path}?t=${Date.now()}`
          setCurrentImageUrl(imageUrl)
          setJobUpdatedImage(true) // Mark that job updated the image
          console.log('Updated preview image:', imageUrl)
        }

        setGeneratingJobId(null)
        setJobProgress(null)

        // Trigger callback if provided
        if (onUpdate) onUpdate()
      } else if (job.status === 'failed') {
        console.error(`❌ Preview generation failed for ${entityType}:`, job.error)
        setGeneratingJobId(null)
        setJobProgress(null)
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
    // If a job just updated the image, don't overwrite it with the stale prop
    if (jobUpdatedImage) {
      console.log('Skipping prop update - job updated image recently')
      return
    }

    if (!previewImageUrl) {
      setCurrentImageUrl(null)
      return
    }

    // ALWAYS use a fresh cache-busting timestamp
    // This ensures browser never shows stale cached images
    const stripQuery = (url) => url?.split('?')[0]
    const baseUrl = stripQuery(previewImageUrl)
    const urlWithTimestamp = `${baseUrl}?t=${Date.now()}`

    setCurrentImageUrl(urlWithTimestamp)
    console.log('Set image from prop with fresh timestamp:', urlWithTimestamp)
  }, [previewImageUrl, jobUpdatedImage])

  // Reset job updated flag when entity changes
  useEffect(() => {
    setJobUpdatedImage(false)
  }, [entityId])

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      paddingBottom: '100%', // Square aspect ratio
      borderRadius: shape === 'circle' ? '50%' : '8px',
      overflow: 'hidden'
    }}>
      {currentImageUrl ? (
        // Show actual preview image
        <img
          src={currentImageUrl}
          alt="Preview"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover'
          }}
        />
      ) : (
        // Show stand-in icon
        <div style={{
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
