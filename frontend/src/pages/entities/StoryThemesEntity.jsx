import { useState, useMemo } from 'react'
import EntityBrowser from '../../components/entities/EntityBrowser'
import { storyThemesConfig } from '../../components/entities/configs'
import StoryPresetModal from '../../components/story/StoryPresetModal'

function StoryThemesEntity() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  // Create a modified config with the modal handlers
  const config = useMemo(() => ({
    ...storyThemesConfig,
    actions: [
      {
        label: 'New Story Theme',
        icon: '+',
        primary: true,
        onClick: () => setIsModalOpen(true)
      }
    ]
  }), [])

  const handlePresetCreated = () => {
    // Trigger a refresh by updating the key
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <>
      <EntityBrowser key={refreshTrigger} config={config} />
      <StoryPresetModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onPresetCreated={handlePresetCreated}
        category="story_themes"
        config={{
          entityType: 'story theme',
          icon: '📚'
        }}
      />
    </>
  )
}

export default StoryThemesEntity
