import { useState, useMemo } from 'react'
import EntityBrowser from '../../components/entities/EntityBrowser'
import { charactersConfig } from '../../components/entities/configs'
import CharacterCreationModal from '../../components/characters/CharacterCreationModal'
import api from '../../api/client'

function CharactersEntity() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [analyzing, setAnalyzing] = useState(false)

  const handleAnalyzeAppearances = async () => {
    if (!confirm('Analyze appearances for all characters with images but no physical descriptions?\n\nThis will queue a background job that you can track in Job History.')) {
      return
    }

    setAnalyzing(true)

    try {
      const response = await api.post('/characters/analyze-appearances')
      const result = response.data

      if (!result.job_id) {
        // No characters to analyze
        alert(result.message || 'No characters need appearance analysis')
        setAnalyzing(false)
        return
      }

      // Job queued successfully - show success and optionally navigate to jobs
      const viewJobs = confirm(
        `✅ Analysis job queued successfully!\n\n` +
        `${result.message}\n\n` +
        `Would you like to view the job progress in Job History?`
      )

      if (viewJobs) {
        window.location.href = '/jobs'
      } else {
        // Refresh the entity list after a delay to show updated characters
        setTimeout(() => {
          setRefreshTrigger(prev => prev + 1)
        }, 2000)
      }
    } catch (error) {
      alert(`Failed to queue analysis: ${error.response?.data?.detail || error.message}`)
    } finally {
      setAnalyzing(false)
    }
  }

  // Create a modified config with the modal handlers
  const config = useMemo(() => ({
    ...charactersConfig,
    actions: [
      {
        label: 'New Character',
        icon: '+',
        primary: true,
        onClick: () => setIsModalOpen(true)
      },
      {
        label: analyzing ? 'Analyzing...' : 'Analyze Appearances',
        icon: '🔍',
        primary: false,
        onClick: handleAnalyzeAppearances
      }
    ]
  }), [analyzing])

  const handleCharacterCreated = () => {
    // Trigger a refresh by updating the key
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <>
      <EntityBrowser key={refreshTrigger} config={config} />
      <CharacterCreationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCharacterCreated={handleCharacterCreated}
      />
    </>
  )
}

export default CharactersEntity
