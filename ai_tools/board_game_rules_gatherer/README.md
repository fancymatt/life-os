# Board Game Rules Gatherer

Searches BoardGameGeek (BGG) for board games and downloads rulebooks.

## Features

- **Search BGG**: Find games by name
- **Get Game Details**: Fetch comprehensive game information (designer, publisher, complexity, etc.)
- **Download Rulebooks**: Automatically find and download PDF rulebooks
- **Create Entities**: Optionally create Board Game and Document entities

## Usage

### Search for Games

```python
from ai_tools.board_game_rules_gatherer import BoardGameRulesGatherer

tool = BoardGameRulesGatherer()

# Search for a game (synchronous - no DB needed)
results = tool.search_games("Wingspan")
# Returns: [{"bgg_id": 266192, "name": "Wingspan", "year": 2019, "type": "boardgame"}]
```

### Gather Game and Rules

```python
from api.database import get_session

# Get game details and download rulebook
async with get_session() as session:
    tool = BoardGameRulesGatherer(db_session=session, user_id=1)

    result = await tool.gather_game_and_rules(
        bgg_id=266192,
        create_entities=True  # Creates Board Game + Document entities
    )

# Returns:
# {
#     "status": "completed",
#     "game_data": {...},
#     "pdf_path": "/path/to/Wingspan-266192-rules.pdf",
#     "game_id": "bgg-266192",
#     "document_id": "abc123def"
# }
```

### Search and Auto-Gather

```python
from api.database import get_session

# Search and automatically download first result
async with get_session() as session:
    tool = BoardGameRulesGatherer(db_session=session, user_id=1)

    result = await tool.gather_from_search(
        query="Wingspan",
        exact=True,
        auto_select_first=True,
        create_entities=True
    )
```

## API Endpoints

### POST /api/board-games/search
Search BoardGameGeek for games.

**Request:**
```json
{
  "query": "Wingspan",
  "exact": false
}
```

**Response:**
```json
{
  "query": "Wingspan",
  "count": 3,
  "results": [
    {
      "bgg_id": 266192,
      "name": "Wingspan",
      "year": 2019,
      "type": "boardgame"
    }
  ]
}
```

### POST /api/board-games/gather
Get game details and download rulebook.

**Request:**
```json
{
  "bgg_id": 266192,
  "create_entities": true
}
```

**Response:**
```json
{
  "status": "completed",
  "game_data": {
    "name": "Wingspan",
    "designer": "Elizabeth Hargrave",
    "publisher": "Stonemaier Games",
    "year": 2019,
    "description": "...",
    "player_count_min": 1,
    "player_count_max": 5,
    "playtime_min": 40,
    "playtime_max": 70,
    "complexity": 2.4
  },
  "pdf_path": "/path/to/Wingspan-266192-rules.pdf",
  "game_id": "bgg-266192",
  "document_id": "abc123"
}
```

## Technical Details

### BGG XML API v2

Uses the official BGG XML API for game search and details:
- Search: `https://boardgamegeek.com/xmlapi2/search?query=...`
- Details: `https://boardgamegeek.com/xmlapi2/thing?id=...&stats=1`

### Web Scraping

Scrapes the BGG files page to find rulebook PDFs:
- Files page: `https://boardgamegeek.com/boardgame/{id}/files`
- Looks for links matching: `rulebook*.pdf`, `rules*.pdf`, `manual*.pdf`

### Rate Limiting

Be respectful of BGG's servers:
- Includes User-Agent header
- 10-second timeout on requests
- Consider adding delays between requests if bulk downloading

## Error Handling

The tool gracefully handles:
- Game not found on BGG
- No rulebook PDF available
- Network errors
- Invalid BGG IDs

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `lxml`: XML parsing

## Cost

**LLM Cost**: $0 (no LLM used)
**Time**: ~3-5 seconds per game

## Notes

- Not all games have rulebooks on BGG
- Some rulebooks may require BGG login (not currently supported)
- PDFs are stored in `data/downloads/pdfs/`
- Game IDs use format: `bgg-{bgg_id}` (e.g., `bgg-266192`)
