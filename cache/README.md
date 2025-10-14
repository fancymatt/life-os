# Cache

This directory contains **ephemeral cache** - temporary storage for analysis results to avoid redundant API calls.

## What is Cache?

Cache is automatically managed storage that:

- **Expires** - 7-day TTL by default
- **Auto-generated** - Created automatically by analysis tools
- **Hash-based** - Keyed by file content hash
- **Validated** - File changes invalidate cache
- **Not user-edited** - Managed by the system

## Directory Structure

```
cache/
├── outfits/           # Cached outfit analyses
├── visual-styles/     # Cached visual style analyses
├── art-styles/        # Cached art style analyses
├── hair-styles/       # Cached hair style analyses
├── hair-colors/       # Cached hair color analyses
├── makeup/            # Cached makeup analyses
├── expressions/       # Cached expression analyses
└── accessories/       # Cached accessories analyses
```

## How Cache Works

### Automatic Caching

When you analyze an image:

```bash
ai-tool analyze outfit refs/suit.jpg
```

The result is automatically cached with:
- File content hash as key
- 7-day expiration
- Source file validation

### Cache Hit

If you analyze the same file again within 7 days:

```bash
ai-tool analyze outfit refs/suit.jpg  # Uses cache, no API call
```

### Cache Miss

Cache is invalidated if:
- File content changes (hash mismatch)
- 7 days have passed (TTL expired)
- Cache manually cleared

### Promotion to Preset

If you like a cached result:

```bash
# Promote to permanent preset
ai-tool save-preset outfit refs/suit.jpg --name fancy-suit
```

## Cache vs Presets

| Aspect | Cache | Presets |
|--------|-------|---------|
| **Purpose** | Performance | Reusability |
| **Lifetime** | 7 days | Permanent |
| **Naming** | File hash | User-chosen |
| **Editable** | No | Yes |
| **Git-tracked** | No | Yes |
| **Key** | Hash | Name |

## Management Commands

```bash
# View cache stats
ai-tool cache stats

# Clean expired entries
ai-tool cache clean

# Clear all cache
ai-tool cache clear

# Clear specific type
ai-tool cache clear --type outfits

# List cached entries
ai-tool cache list outfits
```

## Cache Entry Format

Each cache entry is a JSON file:

```json
{
  "key": "a3f8b92c",
  "tool_type": "outfits",
  "data": {
    "clothing_items": [...],
    "style_genre": "..."
  },
  "created_at": "2025-10-14T14:30:22Z",
  "expires_at": "2025-10-21T14:30:22Z",
  "source_file": "refs/suit.jpg",
  "source_hash": "a3f8b92c"
}
```

## Best Practices

1. **Let it work automatically** - Cache is managed for you
2. **Don't edit cache files** - They'll be overwritten
3. **Promote to presets** - Save important results as presets
4. **Clean periodically** - Run `cache clean` to remove expired entries
5. **Clear when needed** - Clear cache if you want fresh analyses

## Performance

Cache provides significant benefits:

- **Avoid redundant API calls** - Save time and money
- **Instant results** - Cached analyses return immediately
- **File validation** - Ensures cache matches current file

## Troubleshooting

**Cache not being used?**
- File may have changed (hash validation)
- Cache may have expired (7-day TTL)
- Check with: `ai-tool cache list <type>`

**Want fresh analysis?**
- Use `--no-cache` flag
- Or clear cache: `ai-tool cache clear --type <type>`

**Running out of disk space?**
- Run: `ai-tool cache clean` (removes expired)
- Or: `ai-tool cache clear` (removes all)
