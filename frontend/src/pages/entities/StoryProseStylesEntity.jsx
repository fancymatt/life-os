import { useState, useMemo } from 'react'
import EntityBrowser from '../../components/entities/EntityBrowser'
import { storyProseStylesConfig } from '../../components/entities/configs'
import StoryPresetModal from '../../components/story/StoryPresetModal'

function StoryProseStylesEntity() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  // Create a modified config with the modal handlers
  const config = useMemo(() => ({
    ...storyProseStylesConfig,
    actions: [
      {
        label: 'New Prose Style',
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
        category="story_prose_styles"
        config={{
          entityType: 'prose style',
          icon: '✍️'
        }}
      />
    </>
  )
}

export default StoryProseStylesEntity
