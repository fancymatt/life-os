import { useState, useMemo } from 'react'
import EntityBrowser from '../../components/entities/EntityBrowser'
import { charactersConfig } from '../../components/entities/configs'
import CharacterCreationModal from '../../components/characters/CharacterCreationModal'

function CharactersEntity() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  // Create a modified config with the modal handlers
  const config = useMemo(() => ({
    ...charactersConfig,
    actions: [
      {
        label: 'New Character',
        icon: '+',
        primary: true,
        onClick: () => setIsModalOpen(true)
      }
    ]
  }), [])

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
