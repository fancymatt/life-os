import EntityBrowser from '../../components/entities/EntityBrowser'
import { charactersConfig } from '../../components/entities/entityConfigs'

function CharactersEntity() {
  return <EntityBrowser config={charactersConfig} />
}

export default CharactersEntity
