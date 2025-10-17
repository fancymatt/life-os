"""
Board Game Routes

Endpoints for managing board game entities and integrating with BoardGameGeek.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional

from api.models.requests import BoardGameCreate, BoardGameUpdate
from api.models.responses import (
    BoardGameInfo,
    BoardGameListResponse,
    BGGSearchResponse,
    BGGSearchResult,
    DocumentInfo,
    DocumentListResponse
)
from api.services.board_game_service import BoardGameService
from api.services.document_service import DocumentService
from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from ai_tools.board_game_rules_gatherer.tool import BoardGameRulesGatherer

router = APIRouter()


@router.get("/", response_model=BoardGameListResponse)
async def list_board_games(
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all board games

    Returns a list of all board game entities with their metadata.
    """
    service = BoardGameService()
    games = service.list_board_games()

    game_infos = [
        BoardGameInfo(
            game_id=game['game_id'],
            name=game['name'],
            bgg_id=game.get('bgg_id'),
            designer=game.get('designer'),
            publisher=game.get('publisher'),
            year=game.get('year'),
            description=game.get('description'),
            player_count_min=game.get('player_count_min'),
            player_count_max=game.get('player_count_max'),
            playtime_min=game.get('playtime_min'),
            playtime_max=game.get('playtime_max'),
            complexity=game.get('complexity'),
            created_at=game.get('created_at'),
            updated_at=game.get('updated_at'),
            metadata=game.get('metadata', {})
        )
        for game in games
    ]

    return BoardGameListResponse(
        count=len(game_infos),
        games=game_infos
    )


@router.post("/", response_model=BoardGameInfo)
async def create_board_game(
    request: BoardGameCreate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new board game (manual entry)

    Creates a board game entity with name, designer, publisher, etc.
    For automatic import from BoardGameGeek, use /search or /gather endpoints.
    """
    service = BoardGameService()

    game_data = service.create_board_game(
        name=request.name,
        bgg_id=request.bgg_id,
        designer=request.designer,
        publisher=request.publisher,
        year=request.year,
        description=request.description,
        player_count_min=request.player_count_min,
        player_count_max=request.player_count_max,
        playtime_min=request.playtime_min,
        playtime_max=request.playtime_max,
        complexity=request.complexity
    )

    return BoardGameInfo(
        game_id=game_data['game_id'],
        name=game_data['name'],
        bgg_id=game_data.get('bgg_id'),
        designer=game_data.get('designer'),
        publisher=game_data.get('publisher'),
        year=game_data.get('year'),
        description=game_data.get('description'),
        player_count_min=game_data.get('player_count_min'),
        player_count_max=game_data.get('player_count_max'),
        playtime_min=game_data.get('playtime_min'),
        playtime_max=game_data.get('playtime_max'),
        complexity=game_data.get('complexity'),
        created_at=game_data.get('created_at'),
        updated_at=game_data.get('updated_at'),
        metadata=game_data.get('metadata', {})
    )


@router.get("/{game_id}", response_model=BoardGameInfo)
async def get_board_game(
    game_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a board game by ID

    Returns full game data including name, designer, complexity, etc.
    """
    service = BoardGameService()
    game_data = service.get_board_game(game_id)

    if not game_data:
        raise HTTPException(status_code=404, detail=f"Board game {game_id} not found")

    return BoardGameInfo(
        game_id=game_data['game_id'],
        name=game_data['name'],
        bgg_id=game_data.get('bgg_id'),
        designer=game_data.get('designer'),
        publisher=game_data.get('publisher'),
        year=game_data.get('year'),
        description=game_data.get('description'),
        player_count_min=game_data.get('player_count_min'),
        player_count_max=game_data.get('player_count_max'),
        playtime_min=game_data.get('playtime_min'),
        playtime_max=game_data.get('playtime_max'),
        complexity=game_data.get('complexity'),
        created_at=game_data.get('created_at'),
        updated_at=game_data.get('updated_at'),
        metadata=game_data.get('metadata', {})
    )


@router.put("/{game_id}", response_model=BoardGameInfo)
async def update_board_game(
    game_id: str,
    request: BoardGameUpdate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update a board game

    Updates game fields. Only provided fields will be updated.
    """
    service = BoardGameService()

    game_data = service.update_board_game(
        game_id=game_id,
        name=request.name,
        designer=request.designer,
        publisher=request.publisher,
        year=request.year,
        description=request.description,
        player_count_min=request.player_count_min,
        player_count_max=request.player_count_max,
        playtime_min=request.playtime_min,
        playtime_max=request.playtime_max,
        complexity=request.complexity
    )

    if not game_data:
        raise HTTPException(status_code=404, detail=f"Board game {game_id} not found")

    return BoardGameInfo(
        game_id=game_data['game_id'],
        name=game_data['name'],
        bgg_id=game_data.get('bgg_id'),
        designer=game_data.get('designer'),
        publisher=game_data.get('publisher'),
        year=game_data.get('year'),
        description=game_data.get('description'),
        player_count_min=game_data.get('player_count_min'),
        player_count_max=game_data.get('player_count_max'),
        playtime_min=game_data.get('playtime_min'),
        playtime_max=game_data.get('playtime_max'),
        complexity=game_data.get('complexity'),
        created_at=game_data.get('created_at'),
        updated_at=game_data.get('updated_at'),
        metadata=game_data.get('metadata', {})
    )


@router.delete("/{game_id}")
async def delete_board_game(
    game_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete a board game

    Removes the board game entity.
    Note: Does not delete associated documents.
    """
    service = BoardGameService()
    success = service.delete_board_game(game_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Board game {game_id} not found")

    return {"message": f"Board game {game_id} deleted successfully"}


@router.get("/{game_id}/documents", response_model=DocumentListResponse)
async def list_game_documents(
    game_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List documents for a board game

    Returns all documents (rulebooks, references, etc.) associated with this game.
    """
    # Verify game exists
    game_service = BoardGameService()
    game_data = game_service.get_board_game(game_id)
    if not game_data:
        raise HTTPException(status_code=404, detail=f"Board game {game_id} not found")

    # Get documents
    document_service = DocumentService()
    documents = document_service.list_documents(game_id=game_id)

    document_infos = [
        DocumentInfo(
            document_id=doc['document_id'],
            game_id=doc.get('game_id'),
            title=doc['title'],
            source_type=doc['source_type'],
            source_url=doc.get('source_url'),
            file_path=doc.get('file_path'),
            page_count=doc.get('page_count'),
            file_size_bytes=doc.get('file_size_bytes'),
            processed=doc.get('processed', False),
            processed_at=doc.get('processed_at'),
            markdown_path=doc.get('markdown_path'),
            vector_ids=doc.get('vector_ids', []),
            created_at=doc.get('created_at'),
            metadata=doc.get('metadata', {})
        )
        for doc in documents
    ]

    return DocumentListResponse(
        count=len(document_infos),
        documents=document_infos
    )


# ============================================================================
# BoardGameGeek Integration Endpoints
# ============================================================================

@router.post("/search", response_model=BGGSearchResponse)
async def search_bgg_games(
    query: str,
    exact: bool = False,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Search BoardGameGeek for games

    Searches the BGG database for games matching the query.
    Returns list of games with BGG IDs that can be used to gather full details.
    """
    tool = BoardGameRulesGatherer()

    try:
        results = tool.search_games(query, exact=exact)

        search_results = [
            BGGSearchResult(
                bgg_id=result['bgg_id'],
                name=result['name'],
                year=result.get('year'),
                type=result['type']
            )
            for result in results
        ]

        return BGGSearchResponse(
            query=query,
            count=len(search_results),
            results=search_results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BGG search failed: {str(e)}")


@router.post("/gather")
async def gather_game_and_rules(
    bgg_id: int,
    create_entities: bool = True,
    background_tasks: BackgroundTasks = None,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get game details and download rulebook from BoardGameGeek

    Fetches comprehensive game information from BGG and downloads the rulebook PDF.
    Optionally creates board game and document entities for persistence.

    Returns:
        - Game details (name, designer, publisher, complexity, etc.)
        - Path to downloaded PDF rulebook (if available)
        - Entity IDs (if create_entities=True)
    """
    tool = BoardGameRulesGatherer()

    try:
        result = tool.gather_game_and_rules(bgg_id, create_entities=create_entities)

        if result['status'] == 'failed':
            raise HTTPException(status_code=404, detail=result.get('error', 'Unknown error'))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to gather game data: {str(e)}")


@router.post("/gather-from-search")
async def gather_from_search(
    query: str,
    exact: bool = False,
    auto_select_first: bool = True,
    create_entities: bool = True,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Search for a game and automatically download its rules

    Combines search and gather operations. Searches BGG for the query,
    then automatically downloads rules for the first result.

    Useful for quick "I want the rules for Wingspan" style requests.
    """
    tool = BoardGameRulesGatherer()

    try:
        result = tool.gather_from_search(
            query=query,
            exact=exact,
            auto_select_first=auto_select_first,
            create_entities=create_entities
        )

        if result['status'] == 'failed':
            raise HTTPException(status_code=404, detail=result.get('error', 'No results found'))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to gather from search: {str(e)}")
