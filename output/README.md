# Output

This directory contains **generated images and videos** organized by date and timestamp.

## Directory Structure

```
output/
└── YYYY-MM-DD/           # Date folder (e.g., 2025-10-14)
    └── HHMMSS/           # Timestamp folder (e.g., 143022)
        ├── image1.png
        ├── image2.png
        └── video.mp4
```

## File Naming Convention

### Images

Format: `{outfit}_{style}_{subject}_{timestamp}.png`

Examples:
- `fancy-suit_dramatic_jaimee_20251014_143025.png`
- `casual-kimono_soft-natural_kat_20251014_143028.png`

### Videos

Format: `{timestamp}.mp4`

Examples:
- `20251014-143022.mp4`

## Organization

All outputs from a single command are grouped in the same timestamp folder:

```bash
ai-workflow outfit-swap fancy-suit --subjects "jaimee kat izzy"
```

Creates:

```
output/2025-10-14/143022/
├── fancy-suit_default_jaimee_20251014_143025.png
├── fancy-suit_default_kat_20251014_143028.png
└── fancy-suit_default_izzy_20251014_143031.png
```

## Best Practices

1. **Review regularly** - Move keepers to a permanent location
2. **Clean up** - Delete unused generations to save space
3. **Archive** - Keep important outputs elsewhere for safekeeping
4. **Organize externally** - This is staging, not permanent storage

## Metadata

Each generation may include a sidecar JSON file with metadata:

```
output/2025-10-14/143022/
├── fancy-suit_default_jaimee_20251014_143025.png
└── fancy-suit_default_jaimee_20251014_143025.json  # Metadata
```

Metadata includes:
- Generation request parameters
- Model used
- Cost estimate
- Timestamp
- Preset references used
