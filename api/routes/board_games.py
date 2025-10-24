"""
Board Game Routes

Endpoints for managing board game entities and integrating with BoardGameGeek.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Request
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.requests import BoardGameCreate, BoardGameUpdate
from api.models.responses import (
    BoardGameInfo,
    BoardGameListResponse,
    BGGSearchResponse,
    BGGSearchResult,
    DocumentInfo,
    DocumentListResponse,
    TagInfo
)
from api.services.board_game_service_db import BoardGameServiceDB
from api.services.tag_service import TagService
from api.database import get_db
from api.services.document_service import DocumentService
from api.services.qa_service import QAService
from api.models.auth import User
from api.dependencies.auth import get_current_active_user
from ai_tools.board_game_rules_gatherer.tool import BoardGameRulesGatherer
from api.middleware.cache import cached, invalidates_cache

router = APIRouter()


# Helper Functions
async def get_entity_tags_info(
    db: AsyncSession,
    entity_type: str,
    entity_id: str
) -> List[TagInfo]:
    """
    Helper function to fetch tags for an entity and convert to TagInfo response objects.
    """
    tag_service = TagService(db_session=db)
    tags = await tag_service.get_entity_tags(entity_type, entity_id)

    return [
        TagInfo(
            tag_id=tag.tag_id,
            name=tag.name,
            category=tag.category,
            color=tag.color,
            usage_count=tag.usage_count,
            created_at=tag.created_at.isoformat() if tag.created_at else None,
            updated_at=tag.updated_at.isoformat() if tag.updated_at else None
        )
        for tag in tags
    ]


@router.get("/", response_model=BoardGameListResponse)
@cached(cache_type="list", include_user=True)
async def list_board_games(
    request: Request,
    limit: Optional[int] = Query(None, description="Maximum number of board games to return"),
    offset: int = Query(0, description="Number of board games to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List all board games

    Returns a list of all board game entities with their metadata.
    Supports pagination via limit/offset parameters.

    **Cached**: 60 seconds (user-specific)
    """
    service = BoardGameServiceDB(db, user_id=current_user.id if current_user else None)

    # Get both games and total count
    games = await service.list_board_games(limit=limit, offset=offset)
    total_count = await service.count_board_games()

    # Fetch tags for each game
    game_infos = []
    for game in games:
        tags_info = await get_entity_tags_info(db, "board_game", game['game_id'])
        game_infos.append(
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
                tags=tags_info,
                created_at=game.get('created_at'),
                updated_at=game.get('updated_at'),
                metadata=game.get('metadata', {})
            )
        )

    return BoardGameListResponse(
        count=total_count,  # Total count, not page count
        games=game_infos
    )


@router.post("/", response_model=BoardGameInfo)
@invalidates_cache(entity_types=["board_games"])
async def create_board_game(
    request: BoardGameCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Create a new board game (manual entry)

    Creates a board game entity with name, designer, publisher, etc.
    For automatic import from BoardGameGeek, use /search or /gather endpoints.

    **Cache Invalidation**: Clears all board_games caches
    """
    service = BoardGameServiceDB(db, user_id=current_user.id if current_user else None)

    game_data = await service.create_board_game(
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

    # Fetch tags (will be empty for new games)
    tags_info = await get_entity_tags_info(db, "board_game", game_data['game_id'])

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
        tags=tags_info,
        created_at=game_data.get('created_at'),
        updated_at=game_data.get('updated_at'),
        metadata=game_data.get('metadata', {})
    )


@router.get("/{game_id}", response_model=BoardGameInfo)
@cached(cache_type="detail", include_user=True)
async def get_board_game(
    request: Request,
    game_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a board game by ID

    Returns full game data including name, designer, complexity, etc.

    **Cached**: 5 minutes (user-specific)
    """
    service = BoardGameServiceDB(db, user_id=current_user.id if current_user else None)
    game_data = await service.get_board_game(game_id)

    if not game_data:
        raise HTTPException(status_code=404, detail=f"Board game {game_id} not found")

    tags_info = await get_entity_tags_info(db, "board_game", game_id)

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
        tags=tags_info,
        created_at=game_data.get('created_at'),
        updated_at=game_data.get('updated_at'),
        metadata=game_data.get('metadata', {})
    )


@router.put("/{game_id}", response_model=BoardGameInfo)
@invalidates_cache(entity_types=["board_games"])
async def update_board_game(
    game_id: str,
    request: BoardGameUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Update a board game

    Updates game fields. Only provided fields will be updated.

    **Cache Invalidation**: Clears all board_games caches
    """
    service = BoardGameServiceDB(db, user_id=current_user.id if current_user else None)

    game_data = await service.update_board_game(
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

    tags_info = await get_entity_tags_info(db, "board_game", game_id)

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
        tags=tags_info,
        created_at=game_data.get('created_at'),
        updated_at=game_data.get('updated_at'),
        metadata=game_data.get('metadata', {})
    )


@router.delete("/{game_id}")
@invalidates_cache(entity_types=["board_games"])
async def delete_board_game(
    game_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Delete a board game

    Removes the board game entity.
    Note: Does not delete associated documents.

    **Cache Invalidation**: Clears all board_games caches
    """
    service = BoardGameServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.delete_board_game(game_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Board game {game_id} not found")

    return {"message": f"Board game {game_id} deleted successfully"}


@router.post("/{game_id}/archive")
@invalidates_cache(entity_types=["board_games"])
async def archive_board_game(
    game_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Archive a board game (soft delete)

    Archives the board game instead of permanently deleting it.
    Archived games are hidden from default views but can be unarchived.

    **Cache Invalidation**: Clears all board_games caches
    """
    service = BoardGameServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.archive_board_game(game_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Board game {game_id} not found")

    return {"message": f"Board game {game_id} archived successfully"}


@router.post("/{game_id}/unarchive")
@invalidates_cache(entity_types=["board_games"])
async def unarchive_board_game(
    game_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Unarchive a board game

    Restores an archived board game to active status.

    **Cache Invalidation**: Clears all board_games caches
    """
    service = BoardGameServiceDB(db, user_id=current_user.id if current_user else None)
    success = await service.unarchive_board_game(game_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Board game {game_id} not found")

    return {"message": f"Board game {game_id} unarchived successfully"}


@router.get("/{game_id}/documents", response_model=DocumentListResponse)
@cached(cache_type="list", include_user=True)
async def list_game_documents(
    request: Request,
    game_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List documents for a board game

    Returns all documents (rulebooks, references, etc.) associated with this game.

    **Cached**: 60 seconds (user-specific)
    """
    # Verify game exists
    game_service = BoardGameServiceDB(db, user_id=current_user.id if current_user else None)
    game_data = await game_service.get_board_game(game_id)
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


@router.get("/{game_id}/qa")
@cached(cache_type="list", include_user=True)
async def list_game_qas(
    request: Request,
    game_id: str,
    context_type: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    List Q&As for a board game

    Returns all questions and answers associated with this game.
    Useful for browsing previous rules questions.

    Filters:
    - context_type: Filter by context (document, general, image, comparison)
    - is_favorite: Show only favorites

    **Cached**: 60 seconds (user-specific)
    """
    # Verify game exists
    game_service = BoardGameServiceDB(db, user_id=current_user.id if current_user else None)
    game_data = await game_service.get_board_game(game_id)
    if not game_data:
        raise HTTPException(status_code=404, detail=f"Board game {game_id} not found")

    # Get Q&As
    qa_service = QAService()
    qas = await qa_service.list_qas(
        game_id=game_id,
        context_type=context_type,
        is_favorite=is_favorite
    )

    return {
        "game_id": game_id,
        "game_name": game_data.get("name"),
        "count": len(qas),
        "qas": qas
    }


# ============================================================================
# BoardGameGeek Integration Endpoints
# ============================================================================

@router.post("/search", response_model=BGGSearchResponse)
async def search_bgg_games(
    query: str,
    exact: bool = False,
    db: AsyncSession = Depends(get_db),
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
@invalidates_cache(entity_types=["board_games"])
async def gather_game_and_rules(
    bgg_id: int,
    create_entities: bool = True,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
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

    **Cache Invalidation**: Clears all board_games caches (if entities created)
    """
    tool = BoardGameRulesGatherer(
        db_session=db,
        user_id=current_user.id if current_user else None
    )

    try:
        result = await tool.gather_game_and_rules(bgg_id, create_entities=create_entities)

        if result['status'] == 'failed':
            raise HTTPException(status_code=404, detail=result.get('error', 'Unknown error'))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to gather game data: {str(e)}")


@router.post("/gather-from-search")
@invalidates_cache(entity_types=["board_games"])
async def gather_from_search(
    query: str,
    exact: bool = False,
    auto_select_first: bool = True,
    create_entities: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Search for a game and automatically download its rules

    Combines search and gather operations. Searches BGG for the query,
    then automatically downloads rules for the first result.

    Useful for quick "I want the rules for Wingspan" style requests.

    **Cache Invalidation**: Clears all board_games caches (if entities created)
    """
    tool = BoardGameRulesGatherer(
        db_session=db,
        user_id=current_user.id if current_user else None
    )

    try:
        result = await tool.gather_from_search(
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
