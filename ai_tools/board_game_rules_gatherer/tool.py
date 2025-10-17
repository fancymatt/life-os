"""
Board Game Rules Gatherer Tool

Searches BoardGameGeek for games and downloads rulebooks.
This tool does not use LLM - it's a pure web scraping and download tool.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from api.services.bgg_service import BGGService
from api.services.board_game_service import BoardGameService
from api.services.document_service import DocumentService


class BoardGameRulesGatherer:
    """Tool for gathering board game rules from BoardGameGeek"""

    def __init__(self):
        """Initialize the tool"""
        self.bgg_service = BGGService()
        self.board_game_service = BoardGameService()
        self.document_service = DocumentService()

    def search_games(self, query: str, exact: bool = False) -> List[Dict[str, Any]]:
        """
        Search BoardGameGeek for games

        Args:
            query: Search query
            exact: If True, only return exact matches

        Returns:
            List of game search results
        """
        return self.bgg_service.search_games(query, exact)

    def gather_game_and_rules(
        self,
        bgg_id: int,
        create_entities: bool = True
    ) -> Dict[str, Any]:
        """
        Get game details and download rulebook from BGG

        Args:
            bgg_id: BoardGameGeek game ID
            create_entities: If True, create board game and document entities

        Returns:
            Dict with:
                - status: "completed" or "failed"
                - game_data: Game details
                - pdf_path: Path to downloaded rulebook (if found)
                - game_id: Created game entity ID (if create_entities=True)
                - document_id: Created document entity ID (if create_entities=True)
                - error: Error message (if failed)
        """
        try:
            # Get game details and download rulebook
            result = self.bgg_service.get_game_and_rulebook(bgg_id)

            if not result:
                return {
                    "status": "failed",
                    "error": f"Could not find game with BGG ID {bgg_id}"
                }

            response = {
                "status": "completed",
                "game_data": result,
                "pdf_path": result.get("pdf_path"),
                "pdf_url": result.get("pdf_url")
            }

            # Create entities if requested
            if create_entities:
                # Create or update board game entity
                existing_game = self.board_game_service.get_by_bgg_id(bgg_id)

                if existing_game:
                    # Update existing game
                    game_entity = self.board_game_service.update_board_game(
                        existing_game['game_id'],
                        name=result['name'],
                        designer=result['designer'],
                        publisher=result['publisher'],
                        year=result['year'],
                        description=result['description'],
                        player_count_min=result['player_count_min'],
                        player_count_max=result['player_count_max'],
                        playtime_min=result['playtime_min'],
                        playtime_max=result['playtime_max'],
                        complexity=result['complexity']
                    )
                else:
                    # Create new game
                    game_entity = self.board_game_service.create_board_game(
                        name=result['name'],
                        bgg_id=bgg_id,
                        designer=result['designer'],
                        publisher=result['publisher'],
                        year=result['year'],
                        description=result['description'],
                        player_count_min=result['player_count_min'],
                        player_count_max=result['player_count_max'],
                        playtime_min=result['playtime_min'],
                        playtime_max=result['playtime_max'],
                        complexity=result['complexity']
                    )

                response['game_id'] = game_entity['game_id']

                # Create document entity if PDF was downloaded
                if result.get('pdf_path'):
                    pdf_path = Path(result['pdf_path'])
                    file_size = pdf_path.stat().st_size if pdf_path.exists() else None

                    document_entity = self.document_service.create_document(
                        title=f"{result['name']} - Rulebook",
                        source_type="pdf",
                        game_id=game_entity['game_id'],
                        source_url=result.get('pdf_url'),
                        file_path=str(pdf_path),
                        file_size_bytes=file_size,
                        metadata={
                            "bgg_id": bgg_id,
                            "source": "boardgamegeek"
                        }
                    )

                    response['document_id'] = document_entity['document_id']
                else:
                    response['warning'] = "Game found but no rulebook PDF available"

            return response

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    def gather_from_search(
        self,
        query: str,
        exact: bool = False,
        auto_select_first: bool = True,
        create_entities: bool = True
    ) -> Dict[str, Any]:
        """
        Search for a game and download its rules

        Args:
            query: Search query
            exact: If True, only exact matches
            auto_select_first: If True, automatically use first result
            create_entities: If True, create board game and document entities

        Returns:
            Dict with search results and gathered data
        """
        try:
            # Search for games
            search_results = self.search_games(query, exact)

            if not search_results:
                return {
                    "status": "failed",
                    "error": f"No games found for query: {query}"
                }

            response = {
                "status": "completed",
                "search_results": search_results
            }

            # Auto-select first result if requested
            if auto_select_first:
                first_result = search_results[0]
                gather_result = self.gather_game_and_rules(
                    first_result['bgg_id'],
                    create_entities=create_entities
                )

                response.update(gather_result)
                response['selected_game'] = first_result

            return response

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }


# Tool metadata
TOOL_INFO = {
    "name": "board_game_rules_gatherer",
    "display_name": "Board Game Rules Gatherer",
    "category": "utility",
    "description": "Search BoardGameGeek and download rulebooks",
    "requires_llm": False,
    "estimated_cost": 0.0,  # No LLM costs
    "avg_time_seconds": 5.0
}
