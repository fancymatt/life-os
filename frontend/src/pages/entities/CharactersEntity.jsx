import { useState, useMemo } from 'react'
import EntityBrowser from '../../components/entities/EntityBrowser'
import { charactersConfig } from '../../components/entities/configs'
import CharacterCreationModal from '../../components/characters/CharacterCreationModal'
import ImportSubjectsModal from '../../components/characters/ImportSubjectsModal'

function CharactersEntity() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isImportModalOpen, setIsImportModalOpen] = useState(false)
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
      },
      {
        label: 'Import from Subjects',
        icon: '📸',
        primary: false,
        onClick: () => setIsImportModalOpen(true)
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
      <ImportSubjectsModal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        onCharactersImported={handleCharacterCreated}
      />
    </>
  )
}

export default CharactersEntity
