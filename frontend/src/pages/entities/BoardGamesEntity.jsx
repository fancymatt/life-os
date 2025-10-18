import EntityBrowser from '../../components/entities/EntityBrowser'
import { boardGamesConfig } from '../../components/entities/configs/boardGamesConfig'

function BoardGamesEntity() {
  return <EntityBrowser config={boardGamesConfig} />
}

export default BoardGamesEntity
