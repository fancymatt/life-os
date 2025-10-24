import { useState, useMemo, useEffect } from 'react'
import EntityBrowser from '../../components/entities/EntityBrowser'
import { charactersConfig } from '../../components/entities/configs'
import CharacterCreationModal from '../../components/characters/CharacterCreationModal'
import EntitySelectorModal from '../../components/entities/EntitySelectorModal'
import EntityMergeModal from '../../components/entities/EntityMergeModal'
import api from '../../api/client'

function CharactersEntity() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  // Merge state
  const [showEntitySelector, setShowEntitySelector] = useState(false)
  const [showMergeModal, setShowMergeModal] = useState(false)
  const [mergeSource, setMergeSource] = useState(null) // Entity to keep
  const [mergeTarget, setMergeTarget] = useState(null) // Entity to merge into source
  const [allCharacters, setAllCharacters] = useState([])

  // Load all characters for merge selector
  useEffect(() => {
    loadCharacters()
  }, [refreshTrigger])

  const loadCharacters = async () => {
    try {
      const response = await api.get('/characters/')
      const characters = (response.data.characters || []).map(char => ({
        id: char.character_id,
        characterId: char.character_id,
        title: char.name,
        name: char.name,
        archived: char.archived || false,
        data: {
          personality: char.personality,
          age: char.age || '',
          skin_tone: char.skin_tone || '',
          face_description: char.face_description || '',
          hair_description: char.hair_description || '',
          body_description: char.body_description || ''
        }
      }))
      setAllCharacters(characters)
    } catch (err) {
      console.error('Failed to load characters:', err)
    }
  }

  const handleMergeClick = (character) => {
    setMergeSource(character)
    setShowEntitySelector(true)
  }

  const handleTargetSelected = (target) => {
    setMergeTarget(target)
    setShowEntitySelector(false)
    setShowMergeModal(true)
  }

  const handleMergeComplete = () => {
    setShowMergeModal(false)
    setMergeSource(null)
    setMergeTarget(null)
    // Refresh the entity list
    setRefreshTrigger(prev => prev + 1)
  }

  const handleMergeModalClose = () => {
    setShowMergeModal(false)
    setMergeSource(null)
    setMergeTarget(null)
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
        label: 'Merge with...',
        icon: '🔀',
        primary: false,
        handler: async (character) => {
          handleMergeClick(character)
          return { success: true }
        }
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

      {/* Entity Selector for Merge */}
      {showEntitySelector && mergeSource && (
        <EntitySelectorModal
          entities={allCharacters}
          currentEntity={mergeSource}
          entityType="character"
          title="Select Character to Merge"
          onSelect={handleTargetSelected}
          onClose={() => {
            setShowEntitySelector(false)
            setMergeSource(null)
          }}
        />
      )}

      {/* Merge Modal */}
      {showMergeModal && mergeSource && mergeTarget && (
        <EntityMergeModal
          entityType="character"
          sourceEntity={mergeSource}
          targetEntity={mergeTarget}
          onClose={handleMergeModalClose}
          onMergeComplete={handleMergeComplete}
        />
      )}
    </>
  )
}

export default CharactersEntity
