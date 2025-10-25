# Game Equipment Import System - Comprehensive Design Document

**Version:** 1.0
**Date:** 2025-10-24
**Status:** Proposal / Planning Phase

---

## Executive Summary

This document proposes a system to batch-import video game equipment (armor, clothing, accessories) from various games into lifeOS's clothing_items database. The system will extract equipment data from game wikis and databases, use AI vision models to analyze visual appearance, and make these items available for outfit generation and visualization.

**Key Benefits:**
- Massively expand clothing database with diverse, high-quality content (1000s of items)
- Enable cross-game style analysis and outfit composition
- Support multiple aesthetic universes (fantasy, sci-fi, modern, cyberpunk)
- Leverage existing infrastructure (tags, preview system, job queue)
- Open new creative possibilities (style harmonization, AR try-on, 3D printing)

---

## Table of Contents

1. [Core Concept](#1-core-concept)
2. [Data Extraction Strategies](#2-data-extraction-strategies)
3. [Image Analysis Pipeline](#3-image-analysis-pipeline)
4. [Data Mapping](#4-data-mapping)
5. [Tagging System](#5-tagging-system)
6. [Game Selection](#6-game-selection)
7. [Art Style Capture](#7-art-style-capture)
8. [Core Features](#8-core-features)
9. [Extended Applications](#9-extended-applications)
10. [Technical Architecture](#10-technical-architecture)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Open Questions](#12-open-questions)

---

## 1. Core Concept

### Problem
Currently, clothing items are manually created by analyzing outfit images one-by-one. This is time-consuming and limits the database size and diversity.

### Solution
Automate clothing item creation by importing equipment from video games:
- Games have comprehensive equipment databases (wikis, APIs, mod files)
- Equipment includes rich metadata (stats, rarity, materials)
- Visual assets are readily available (icons, screenshots, 3D models)
- Community-maintained data is already validated and categorized

### Vision
Transform lifeOS from a specialized image generation platform into a **universal style and fashion database** that spans:
- Multiple game universes (fantasy, sci-fi, modern, historical)
- Thousands of professionally-designed clothing items
- Cross-universe style analysis and composition
- AI-driven outfit creation from natural language queries

---

## 2. Data Extraction Strategies

### 2.1 MediaWiki Cargo Tables (RECOMMENDED)

**Best for:** Games with well-maintained Cargo-enabled wikis (BG3, Skyrim, Path of Exile)

**How it works:**
- Cargo extension stores structured data in queryable database tables
- Public API access (no authentication required)
- Clean, validated data maintained by community

**API Endpoint Format:**
```
https://bg3.wiki/w/api.php?action=cargoquery&format=json&tables={table}&fields={fields}&where={conditions}&limit={limit}
```

**Example Query (BG3 Light Armor):**
```bash
curl "https://bg3.wiki/w/api.php?action=cargoquery&format=json&tables=equipment&fields=name,type,rarity,armour_class,weight,price,description,icon,uuid&where=type='Light%20Armour'&limit=50"
```

**Python Implementation:**
```python
import requests

def fetch_bg3_equipment(equipment_type="Light Armour", limit=50):
    base_url = "https://bg3.wiki/w/api.php"
    params = {
        "action": "cargoquery",
        "format": "json",
        "tables": "equipment",
        "fields": "name,type,rarity,armour_class,weight,price,description,icon,uuid",
        "where": f"type='{equipment_type}'",
        "limit": limit
    }
    response = requests.get(base_url, params=params)
    return response.json().get("cargoquery", [])
```

**Finding Available Tables:**
Most wikis expose their Cargo schema at: `https://{wiki}/wiki/Special:CargoTables`

**Pros:**
- Structured, clean data
- Rich metadata (rarity, stats, UUIDs)
- Community-validated
- No HTML parsing required

**Cons:**
- Limited to Cargo-enabled wikis
- API rate limits (respect 1-2 req/sec max)

---

### 2.2 JSON Data Dumps from Modding Communities

**Best for:** Games with active modding scenes (BG3, Skyrim, Fallout)

**Sources:**
1. **BG3 Nexus Mods - Developer Resource**
   - Complete `items.json` with ALL game items
   - Includes localized strings, tags, inheritance
   - URL: https://www.nexusmods.com/baldursgate3/mods/1303

2. **Steam Community Spreadsheets**
   - Item UUIDs and spawn codes
   - CSV/spreadsheet format (convertible to JSON)

**Pros:**
- Complete official game data
- No rate limiting
- Often includes asset file references

**Cons:**
- Depends on modding community maintenance
- May be version-specific (outdated after patches)

---

### 2.3 Direct Wiki Scraping

**Best for:** Games without APIs but with comprehensive wikis

**Process:**
1. Identify wiki structure (Fextralife, Game8, etc.)
2. Use Python: `BeautifulSoup`, `scrapy`, or `mediawiki-scraper`
3. Parse infoboxes for structured data
4. Extract images from pages

**Pros:**
- Works for ANY game with a wiki
- Customizable parsing logic

**Cons:**
- Fragile (breaks if wiki layout changes)
- Slower than API
- May violate ToS if not rate-limited properly

---

### 2.4 Game Asset Extraction

**Best for:** Games where you own files (Unity/Unreal games)

**Tools:**
- **AssetRipper** (Unity) - Extracts sprites, textures, icons
- **UModel** (Unreal Engine)
- **Disunity** (Unity asset bundles)

**Pros:**
- Direct access to official game assets (high-quality)
- No dependency on community wikis

**Cons:**
- Legal gray area (requires game ownership, respect EULA)
- Technical setup required
- No metadata (must cross-reference with wiki)

---

## 3. Image Analysis Pipeline

**Key Insight:** Text descriptions like "The sun's harsh light has dulled this armour's dark lustre" don't convey visual appearance. **Image analysis is the primary data source.**

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Fetch Metadata from API                             │
│ - Name, rarity, game source, equipment slot                 │
│ - Icon/screenshot URLs                                       │
│ - Game-specific IDs (UUID, UID)                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Download Images (Multi-angle if available)          │
│ - Icon (front view, usually transparent PNG)                │
│ - In-game screenshots (character wearing item)              │
│ - Concept art (if available)                                │
│ - Multiple views: front, back, side                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Vision Model Analysis (PRIMARY DATA SOURCE)         │
│ Model: Gemini 2.0 Flash Exp (multimodal)                    │
│                                                              │
│ Prompt: "Analyze this armor/clothing in detail:             │
│ - Fabric/material (leather, metal, cloth, synthetic)        │
│ - Primary and accent colors                                 │
│ - Design elements (studs, buckles, embroidery, tech)        │
│ - Style theme (fantasy, sci-fi, modern, cyberpunk)          │
│ - Silhouette and shape                                      │
│ - Condition/wear (pristine, weathered, damaged)             │
│ - Cultural/aesthetic influences                             │
│ - Coverage and fit"                                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Merge Vision Analysis + Metadata                    │
│ - clothing_items.fabric ← Vision analysis                   │
│ - clothing_items.color ← Vision analysis                    │
│ - clothing_items.details ← Vision + game description        │
│ - clothing_items.category ← Metadata (equipment slot)       │
│ - Tags ← Both sources (rarity from metadata, style from AI) │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Angle Image Analysis

Many wikis provide character preview images showing front/back/side views. The system should leverage multiple viewpoints for comprehensive analysis.

**Schema Addition:**
```sql
CREATE TABLE clothing_item_images (
  id SERIAL PRIMARY KEY,
  clothing_item_id INT REFERENCES clothing_items(id),
  image_path VARCHAR(500),
  view_angle VARCHAR(50),  -- 'front', 'back', 'side_left', 'side_right', 'detail'
  image_type VARCHAR(50),  -- 'icon', 'in_game_screenshot', 'concept_art'
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Vision Analysis with Multiple Images:**
```python
async def analyze_equipment_comprehensive(images: List[str], metadata: dict):
    """Analyze equipment from multiple angles"""

    prompt = """
    Analyze this piece of equipment from multiple angles.

    Images provided:
    1. Icon (transparent, front view)
    2. In-game screenshot (character wearing, front)
    3. In-game screenshot (character wearing, back)

    Provide detailed analysis:
    - **Materials**: What is this made of? (leather, metal plates, cloth, synthetic)
    - **Colors**: Primary color, accent colors, metallic finishes
    - **Construction**: How is it assembled? Visible seams, straps, buckles, tech ports?
    - **Design Elements**: Decorative features (engravings, studs, embroidery, LEDs)
    - **Coverage**: What body parts does it cover? How much skin is visible?
    - **Silhouette**: Overall shape (form-fitting, loose, armored, flowing)
    - **Style Theme**: Fantasy medieval? Sci-fi? Modern tactical? Cyberpunk?
    - **Condition**: New/pristine, worn/weathered, damaged, magical glow?
    - **Cultural Aesthetic**: What culture/faction does this evoke?

    Format as JSON.
    """

    response = await router.generate_structured(
        model="gemini/gemini-2.0-flash-exp",
        prompt=prompt,
        images=images,
        response_schema=EquipmentAnalysisSchema
    )

    return response
```

---

## 4. Data Mapping

### 4.1 Field Mapping (Game → lifeOS)

**Example using BG3's "Faded Drow Leather Armour":**

| lifeOS Field | BG3 Source | Example Value | Notes |
|---|---|---|---|
| `item_id` | `uuid` | `cf6237a2-7f37-4796-b239-0685505510d4` | Use game's UUID |
| `category` | `type` + `slot` | `"Light Armor - Body"` | Map to existing categories |
| `item` | `name` | `"Faded Drow Leather Armour"` | Display name |
| `fabric` | Vision analysis | `"Leather (Drow-style, studded, faded)"` | Extract from images with LLM |
| `color` | Vision analysis | `"Dark gray, faded black, silver studs"` | LLM analysis of images |
| `details` | `description` + vision + stats | `"The sun's harsh light has dulled this armour's dark lustre. Studded leather construction with Drow-style patterns. AC: 12 + Dex. Light armour proficiency required."` | Full description |
| `source_image` | `icon_url` (downloaded) | `"/game_assets/bg3/icons/ARM_StuddedLeather_Drow_Faded.png"` | Download and store locally |
| `preview_image_path` | Generated via visualizer | `"/entity_previews/clothing_items/{uuid}_preview.png"` | Use existing preview system |
| `source_entity_id` | `uid` | `"ARM_StuddedLeather_Drow_Faded"` | Game's internal ID |
| `user_id` | NULL or system user | NULL | Imported items shared? |
| `manually_modified` | FALSE | FALSE | Mark as auto-imported |

### 4.2 New Database Fields

```sql
-- Add game source tracking
ALTER TABLE clothing_items ADD COLUMN game_source VARCHAR(100);  -- "Baldur's Gate 3"
ALTER TABLE clothing_items ADD COLUMN rarity VARCHAR(50);         -- "Common", "Legendary"
ALTER TABLE clothing_items ADD COLUMN weight_value DECIMAL(10,2); -- 5.85 (kg)
ALTER TABLE clothing_items ADD COLUMN game_metadata JSONB;        -- Additional game-specific data
ALTER TABLE clothing_items ADD COLUMN description_embedding vector(768);  -- Semantic search
```

### 4.3 game_metadata JSONB Structure

**Example:**
```json
{
  "game": "Baldur's Gate 3",
  "game_slug": "bg3",
  "rarity": "Common",
  "armor_class": "12 + Dex",
  "proficiency_required": "Light Armour",
  "weight_kg": 5.85,
  "weight_lb": 11.7,
  "price_gp": 130,
  "location_found": "Waukeen's Rest (X: -71, Y: 592)",
  "wiki_url": "https://bg3.wiki/wiki/Faded_Drow_Leather_Armour",
  "original_uid": "ARM_StuddedLeather_Drow_Faded",
  "set_name": "Drow Armor Set",
  "set_bonus": "Stealth advantage in darkness"
}
```

---

## 5. Tagging System

Leverage existing `tags` and `entity_tags` tables for powerful filtering and search.

### 5.1 Auto-Generated Tag Categories

| Tag Category | Example Tags | Purpose |
|---|---|---|
| **Source Game** | `baldurs-gate-3`, `cyberpunk-2077`, `skyrim`, `witcher-3` | Filter by game universe |
| **Rarity** | `common`, `uncommon`, `rare`, `legendary`, `unique` | Filter by power level |
| **Equipment Type** | `light-armor`, `heavy-armor`, `clothing`, `shield`, `accessory` | Filter by armor class |
| **Body Slot** | `head`, `chest`, `legs`, `hands`, `feet`, `neck`, `ring`, `cloak` | Filter by equipment slot |
| **Style Theme** | `fantasy`, `sci-fi`, `cyberpunk`, `modern`, `historical`, `post-apocalyptic` | Filter by aesthetic |
| **Cultural/Faction** | `drow-style`, `elven`, `dwarven`, `corpo`, `nomad`, `steampunk` | Filter by design influence |
| **Material** | `leather`, `plate`, `cloth`, `chain-mail`, `synthetic`, `tech-fabric` | Filter by material |
| **Condition** | `pristine`, `weathered`, `damaged`, `enchanted`, `glowing` | Filter by wear state |

### 5.2 Batch Tag Creation

**Example: Importing Faded Drow Leather Armour**
```python
tags_to_create = [
    {"name": "baldurs-gate-3", "category": "game_source", "color": "#8B4513"},
    {"name": "common", "category": "rarity", "color": "#9CA3AF"},
    {"name": "light-armor", "category": "equipment_type", "color": "#60A5FA"},
    {"name": "chest", "category": "body_slot", "color": "#34D399"},
    {"name": "drow-style", "category": "style", "color": "#A78BFA"},
    {"name": "leather", "category": "material", "color": "#F59E0B"},
    {"name": "fantasy", "category": "theme", "color": "#EC4899"},
    {"name": "weathered", "category": "condition", "color": "#78716C"}
]

# Automatically create tags and link via entity_tags table
for tag_data in tags_to_create:
    tag = await tag_service.get_or_create_tag(tag_data)
    await tag_service.link_entity(clothing_item_id, tag.tag_id)
```

---

## 6. Game Selection

### Philosophy
**Diversity is key.** Avoid limiting to single aesthetic (e.g., only fantasy). Prioritize variety across genres to maximize creative possibilities.

### 6.1 Priority Games by Genre

#### Fantasy (Medieval/Magic)
- **Baldur's Gate 3** - D&D-style fantasy, ~300-400 items
- **Skyrim** - Nordic fantasy, ~200-300 items
- **The Witcher 3** - Dark fantasy, ~100-200 items
- **Dragon Age: Inquisition** - High fantasy
- **Elden Ring** - Dark fantasy, unique armor designs

#### Sci-Fi
- **Mass Effect trilogy** - Futuristic armor, alien designs, ~100-200 items
- **Destiny 2** - Space fantasy armor, ~1000+ armor sets
- **Warframe** - Bio-mechanical suits, hundreds of frames
- **Halo** - Military sci-fi armor
- **Star Wars: The Old Republic** - Robes, armor, alien gear

#### Cyberpunk/Dystopian
- **Cyberpunk 2077** - Street fashion, corpo wear, netrunner gear, ~500+ items
- **Deus Ex** - Augmented clothing, tactical wear
- **Mirror's Edge** - Minimalist urban parkour gear

#### Modern/Contemporary
- **The Sims 4** - Everyday clothing, formal wear, casual, ~1000+ items
- **Grand Theft Auto V** - Modern street fashion
- **Watch Dogs** - Urban hacker aesthetic
- **The Last of Us** - Post-apocalyptic survival gear

#### Unique Aesthetics
- **World of Warcraft** - Stylized proportions, vibrant colors, ~500+ armor sets
- **Fortnite** - Wild variety (realistic to cartoon)
- **Final Fantasy XIV** - Japanese-influenced high fashion, ~3000+ glamour items
- **Animal Crossing** - Cute/cozy clothing

#### Historical
- **Assassin's Creed series** - Period-accurate clothing (Egyptian, Renaissance, Viking, Colonial)
- **Red Dead Redemption 2** - Western wear, ~200+ items

### 6.2 Data Source Availability

| Game | Wiki/API | Modding Data | Est. Items | Feasibility |
|---|---|---|---|---|
| Baldur's Gate 3 | ✅ Cargo tables | ✅ JSON dumps | 300-400 | **High** |
| Cyberpunk 2077 | ✅ Fandom wiki | ✅ Modding tools | 500+ | **High** |
| Skyrim | ✅ UESP (Cargo) | ✅ Extensive | 200-300 | **High** |
| The Sims 4 | ✅ Fandom wiki | ✅ CC community | 1000+ | **Medium** |
| Elder Scrolls Online | ✅ UESP API | ✅ LibSets addon | 500+ | **High** |
| Destiny 2 | ✅ light.gg API | ❌ Limited | 1000+ | **Medium** |
| Mass Effect | ✅ Fandom wiki | ❌ Limited | 100-200 | **Medium** |
| FFXIV | ✅ XIVAPI, Garland | ✅ Yes | 3000+ | **Medium** |
| World of Warcraft | ✅ Wowhead | ✅ Yes | 500+ | **Medium** (API key) |

### 6.3 Estimated Total Dataset

**Conservative estimate (10 games):** 5,000-8,000 clothing items
**Aggressive estimate (20 games):** 15,000-20,000 clothing items
**Storage:** 500MB-2GB for icons/screenshots

---

## 7. Art Style Capture

Each game has unique visual DNA beyond composition. The system must capture and reproduce these distinctive styles.

### 7.1 Art Style Analysis Framework

**Process:**
1. Collect 10-20 representative screenshots from game
2. Analyze with vision model to extract style parameters
3. Generate detailed style guide
4. Store as visualization config template

**Analysis Dimensions:**
- **Character Proportions** - Realistic, stylized, exaggerated (e.g., WoW's oversized heads)
- **Rendering Style** - Photorealistic, cel-shaded, painterly, low-poly
- **Color Palette** - Vibrant/desaturated, warm/cool bias, signature colors
- **Lighting** - Realistic GI, stylized rim lighting, flat
- **Texture Style** - High-detail PBR, stylized/simplified, hand-painted
- **Post-Processing** - Bloom, film grain, vignette, motion blur
- **Overall Aesthetic** - Fantasy realism, comic book, anime, gritty

### 7.2 Implementation

```python
class GameArtStyleAnalyzer:
    """Capture the unique visual style of a game"""

    async def analyze_game_style(self, game_name: str, screenshot_urls: List[str]):
        """
        Analyze 10-20 screenshots from a game to extract visual DNA.
        """

        prompt = f"""
        Analyze these screenshots from {game_name} to extract the game's visual DNA.

        Focus on:
        1. **Character Proportions**: Are heads oversized (WoW style)? Realistic? Anime-influenced?
        2. **Rendering Technique**: Photorealistic? Cel-shaded? Painterly? Low-poly?
        3. **Color Grading**: Warm/cool bias? Saturation level? Signature colors?
        4. **Lighting Style**: Realistic global illumination? Stylized rim lighting? Flat?
        5. **Texture Quality**: High-detail PBR? Stylized/simplified? Hand-painted?
        6. **Post-Processing**: Bloom? Film grain? Vignette? Motion blur?
        7. **Overall Aesthetic**: Fantasy realism? Comic book? Anime? Gritty?

        Generate a detailed style guide that could be used to recreate this aesthetic.
        Include specific prompt language for image generation.
        """

        style_guide = await router.generate(
            model="gemini/gemini-2.0-flash-exp",
            prompt=prompt,
            images=screenshot_urls
        )

        return style_guide
```

### 7.3 Storage Structure

```
data/tool_configs/art_styles/
├── baldurs_gate_3_style.md
├── cyberpunk_2077_style.md
├── world_of_warcraft_style.md
├── the_sims_4_style.md
├── destiny_2_style.md
└── witcher_3_style.md
```

### 7.4 Example Style Guide

**`world_of_warcraft_style.md`:**
```markdown
# World of Warcraft Art Style

## Character Proportions
- Heads slightly oversized (8-10% larger than realistic)
- Hands and feet exaggerated (larger, more defined)
- Shoulders broader and more pronounced
- Muscular definition stylized and simplified

## Rendering Style
- Hand-painted textures (visible brush strokes)
- Bold, defined edges and outlines
- Simplified geometry with strong silhouettes
- Vibrant, saturated colors

## Color Palette
- High saturation across all hues
- Strong use of complementary colors
- Signature glows on magical items (purple, blue, orange)
- Metallic finishes are bright and reflective

## Lighting
- Multiple light sources common
- Rim lighting on characters (edge highlighting)
- Dramatic shadows with soft falloff
- Magical items emit visible light

## Texture Style
- Hand-painted appearance
- Simplified detail (not photorealistic)
- Strong color blocking
- Visible brush strokes and pattern work

## Generation Prompt Template
"[Subject description], World of Warcraft art style, hand-painted textures,
stylized proportions with oversized hands and shoulders, vibrant saturated colors,
rim lighting, bold outlines, simplified geometry, fantasy art aesthetic"
```

---

## 8. Core Features

### 8.1 Style Harmonization ("Coat of Paint")

**Problem:** Eclectic outfit with items from different universes looks disjointed.
- Cyberpunk 2077 neon jacket
- Witcher 3 leather boots
- Skyrim fur cloak

**Solution:** Apply unifying style transformation that preserves shape/function but harmonizes aesthetics.

#### Implementation Approach

**Method A: AI Style Transfer**
```python
async def harmonize_outfit_style(
    clothing_items: List[ClothingItem],
    target_style: str = "unified_fantasy"  # or "cyberpunk", "modern", etc.
):
    """
    Apply style unification to eclectic outfit.

    Process:
    1. Analyze each item's core structure (shape, silhouette, function)
    2. Apply target art style while preserving structure
    3. Unify color palette across items
    4. Ensure material consistency
    """

    prompt = f"""
    Transform this eclectic outfit into a cohesive {target_style} style.

    Current items:
    - Cyberpunk neon jacket (tech fabric, glowing accents)
    - Medieval leather boots (worn leather, buckles)
    - Nordic fur cloak (thick fur, heavy)

    Unification rules:
    1. **Preserve silhouette**: Keep overall shapes and proportions
    2. **Harmonize materials**: Convert to style-appropriate materials
       - Tech fabric → Enchanted cloth with subtle glow
       - Modern leather → Medieval tanned leather
       - Maintain functional elements (pockets→pouches, zippers→laces)
    3. **Unified color palette**: Choose 2-3 complementary colors
    4. **Consistent wear level**: All pristine, or all weathered
    5. **Shared decorative theme**: Common motifs (Celtic knots, geometric patterns)

    Result should look like outfit designed as cohesive set, not random pieces.
    """
```

**Method B: Metadata-Driven Transformation Rules**
```yaml
# configs/style_harmonization/cyberpunk_to_fantasy.yaml
transformations:
  materials:
    tech_fabric: "enchanted_cloth_with_runes"
    synthetic_leather: "dragon_leather"
    neon_lights: "magical_glow"
    metal_plating: "plate_armor"

  colors:
    neon_blue: "arcane_blue"
    chrome_silver: "mithril_silver"
    carbon_black: "shadow_black"

  design_elements:
    circuit_patterns: "runic_engravings"
    LED_strips: "glowing_enchantments"
    zippers: "leather_laces"
    velcro: "buckles_and_straps"
```

#### Use Cases
1. **Eclectic to Cohesive**: "Make these random items look like a matching set"
2. **Universe Translation**: "Take this Cyberpunk outfit and render it as if it existed in Skyrim"
3. **Era Shift**: "Convert this medieval armor to cyberpunk aesthetic"
4. **Material Unification**: "Make this outfit all-leather" or "all-metal"

---

### 8.2 AI Outfit Composition (Natural Language)

With thousands of items, manual outfit creation becomes impractical. Enable natural language queries.

#### User Experience

**Query:** "Create a tough and regal outfit for a warrior queen"

**System Response:**
1. Parse semantic intent (themes, colors, materials, style)
2. Search clothing database with embeddings
3. Ensure outfit completeness (head, chest, legs, feet, accessories)
4. Check aesthetic compatibility
5. Optionally apply style harmonization
6. Generate outfit visualization

#### Implementation

**Step 1: Semantic Search Infrastructure**
```sql
-- Add embedding field for semantic search
ALTER TABLE clothing_items ADD COLUMN description_embedding vector(768);

-- Create vector similarity index
CREATE INDEX ON clothing_items USING ivfflat (description_embedding vector_cosine_ops);
```

**Step 2: Generate Embeddings on Import**
```python
# When importing equipment
description_text = f"{item.name} {item.fabric} {item.color} {item.details} {item.game_source}"
embedding = await generate_embedding(description_text)  # OpenAI, Voyage, Cohere
item.description_embedding = embedding
```

**Step 3: Natural Language Outfit Composition**
```python
async def compose_outfit_from_query(
    query: str,
    constraints: dict = None  # {"game_source": "bg3", "rarity": "legendary"}
):
    """Generate complete outfit from natural language query"""

    # Step 1: Analyze query intent
    intent = await analyze_outfit_query(query)
    # Result: {
    #   "themes": ["tough", "regal", "warrior"],
    #   "suggested_colors": ["gold", "deep red", "black"],
    #   "suggested_materials": ["heavy armor", "ornate metal"],
    #   "required_slots": ["head", "chest", "legs", "boots", "accessories"],
    #   "style": "fantasy_royalty"
    # }

    # Step 2: Semantic search for each slot
    outfit_pieces = {}
    for slot in intent["required_slots"]:
        # Vector search
        query_embedding = await generate_embedding(f"{query} {slot}")

        candidates = await db.execute(
            """
            SELECT *, description_embedding <=> :query_embedding AS similarity
            FROM clothing_items
            WHERE category LIKE :slot
            ORDER BY similarity
            LIMIT 10
            """
        )

        # Rank by aesthetic compatibility
        best_match = await rank_by_aesthetic_fit(candidates, intent)
        outfit_pieces[slot] = best_match

    # Step 3: Check outfit harmony
    compatibility_score = await check_outfit_harmony(outfit_pieces)

    if compatibility_score < 0.7:
        # Apply style unification
        outfit_pieces = await harmonize_outfit_style(
            outfit_pieces.values(),
            target_style=intent["style"]
        )

    return outfit_pieces
```

#### Example Queries
- "Stealth assassin outfit with dark colors" → Black leather, hooded cloak, lightweight
- "Corporate executive from cyberpunk universe" → Suit jacket, synthetic materials, tech accents
- "Post-apocalyptic scavenger" → Weathered clothing, mismatched pieces, functional
- "Elven archer, forest theme" → Green/brown tones, leather and cloth, nature motifs

---

### 8.3 Equipment Set Tracking

Many games organize equipment into sets with bonuses. Track these relationships.

**Schema:**
```sql
CREATE TABLE equipment_sets (
  set_id VARCHAR(50) PRIMARY KEY,
  game_source VARCHAR(100),
  set_name VARCHAR(200),
  set_bonus_description TEXT,
  rarity VARCHAR(50),
  piece_count INT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE equipment_set_pieces (
  id SERIAL PRIMARY KEY,
  set_id VARCHAR(50) REFERENCES equipment_sets(set_id),
  clothing_item_id INT REFERENCES clothing_items(id),
  slot VARCHAR(50),  -- "head", "chest", "legs", "hands", "feet"
  required_for_bonus BOOLEAN DEFAULT TRUE
);
```

**Features:**
- Import full sets (e.g., "Drow Studded Leather Set": helmet, chest, gloves, boots)
- Track set bonuses from game (e.g., "2-piece: +10% stealth, 4-piece: Invisibility spell")
- Generate "complete set" outfit presets
- Achievement system: "Collected all Legendary BG3 armor sets!"
- UI: Show set completion progress (3/5 pieces owned)

---

### 8.4 Character Build Templates

Import famous character builds from games as ready-to-use outfit presets.

**Examples:**
- **"Skyrim Stealth Archer Build"** → All equipment from Dark Brotherhood questline
- **"BG3 Paladin of Tyr Build"** → Heavy plate armor, holy symbols
- **"Witcher 3 Griffin School Build"** → Complete Griffin armor set
- **"Cyberpunk 2077 Netrunner Build"** → Tech-heavy clothing with cyberdeck

**Schema:**
```sql
CREATE TABLE character_builds (
  build_id VARCHAR(50) PRIMARY KEY,
  game_source VARCHAR(100),
  build_name VARCHAR(200),
  character_class VARCHAR(100),  -- "Stealth Archer", "Netrunner", "Paladin"
  description TEXT,
  playstyle TEXT,  -- "Long-range stealth, one-shot kills"
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE build_equipment (
  id SERIAL PRIMARY KEY,
  build_id VARCHAR(50) REFERENCES character_builds(build_id),
  clothing_item_id INT REFERENCES clothing_items(id),
  slot VARCHAR(50),
  importance VARCHAR(20)  -- "required", "recommended", "optional"
);
```

**UI Feature:**
- Browse builds by game or playstyle
- "Load Build" button → auto-selects all equipment
- Generate character portrait with build outfit

---

### 8.5 Cross-Game Style Search

Search for similar items across different game universes.

**Example Queries:**
- "Show me all heavy armor with gold accents from any game"
- "Find clothing items similar to Skyrim's Thieves Guild outfit in other games"
- "Compare fantasy armor evolution: BG3 vs Skyrim vs Witcher 3"
- "All sci-fi helmets with visors"

**Implementation:**
Uses semantic embeddings to find visually/thematically similar items regardless of game source.

```python
async def cross_game_style_search(query: str):
    """Search for similar items across all games"""

    query_embedding = await generate_embedding(query)

    results = await db.execute(
        """
        SELECT
            id, item, game_source, fabric, color,
            description_embedding <=> :query_embedding AS similarity
        FROM clothing_items
        ORDER BY similarity
        LIMIT 50
        """
    )

    # Group by game for comparison
    by_game = defaultdict(list)
    for item in results:
        by_game[item.game_source].append(item)

    return by_game
```

---

### 8.6 Game-Specific Visualization Configs

Apply game-specific art style to generated images to make characters look like they belong in that universe.

**Storage:**
```
data/tool_configs/visualization_presets/
├── baldurs_gate_3_cinematic.md
├── cyberpunk_2077_night_city.md
├── world_of_warcraft_painted.md
├── skyrim_nordic_landscape.md
└── witcher_3_dark_fantasy.md
```

**Usage:**
When generating outfit visualization:
1. User selects "Baldur's Gate 3 Style"
2. System loads `baldurs_gate_3_cinematic.md` preset
3. Applies BG3-specific:
   - Cinematic lighting
   - Realistic fantasy rendering
   - D&D color palette
   - Camera angles matching game cutscenes

**Universe Translation Feature:**
Take a single clothing item and render it in different game styles.

**Example:**
- Original: Cyberpunk 2077 corpo jacket
- Translations:
  - "In Witcher 3 universe" → Becomes ornate merchant's coat with medieval details
  - "In Skyrim universe" → Nordic-style leather coat with fur trim
  - "In World of Warcraft" → Stylized with exaggerated proportions and hand-painted look

---

## 9. Extended Applications

### 9.1 3D Model Generation

**Goal:** Create 3D printable models from clothing items.

**Technical Path:**
1. Generate multi-view renders (front, back, sides) using image generator
2. Use AI 3D reconstruction (TripoSR, Luma AI, Meshy.ai)
3. Export as STL/OBJ for 3D printing or viewing

**Implementation:**
```python
async def generate_3d_model(clothing_item_id: int):
    """Create 3D model from clothing item"""

    # 1. Generate turnaround views (8 angles)
    views = await generate_turnaround_views(
        clothing_item_id,
        angles=8,  # 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°
        pose="T-pose"
    )

    # 2. Send to 3D reconstruction API
    model_3d = await triposr_api.image_to_3d(
        images=views,
        format="obj",  # or "stl", "glb"
        quality="high"
    )

    # 3. Store 3D model file
    model_path = f"/3d_models/{clothing_item_id}.obj"
    await save_file(model_path, model_3d)

    return model_path
```

**UI Feature:**
- "Download 3D Model" button on clothing item page
- Interactive 3D viewer in browser (Three.js)
- Export formats: STL (3D printing), OBJ (modeling software), GLB (web/game engines)

**Use Cases:**
- 3D print cosplay armor
- Import into Blender for modification
- Use in VR/AR applications
- Create physical collectibles

---

### 9.2 Cosplay Creation Guides

**Goal:** Auto-generate step-by-step instructions for creating clothing item as cosplay.

**Implementation:**
```python
async def generate_cosplay_guide(clothing_item_id: int):
    """Analyze clothing item and generate crafting instructions"""

    item = await get_clothing_item(clothing_item_id)

    prompt = f"""
    Create detailed cosplay/costume creation guide for this item:

    Name: {item.name}
    Visual Description: {item.details}
    Materials: {item.fabric}
    Colors: {item.color}
    Game Source: {item.game_source}

    Generate:
    1. **Materials List**: What to buy (fabrics, hardware, paints, foam, etc.)
       - Be specific (e.g., "2 yards of black faux leather, 0.5mm thickness")

    2. **Tools Needed**: Sewing machine, heat gun, foam cutting tools, etc.

    3. **Pattern/Template**:
       - Which commercial pattern to use/modify
       - Or links to free patterns online
       - Custom pattern pieces needed

    4. **Step-by-Step Instructions**:
       - Construction process (cutting, sewing, assembly)
       - Weathering/painting techniques
       - Attachment methods (velcro, snaps, buckles)

    5. **Budget Estimate**: Approximate cost
       - Low-budget option ($50-100)
       - Mid-range ($100-250)
       - High-quality ($250+)

    6. **Difficulty Level**: Beginner/Intermediate/Advanced

    7. **Time Estimate**: Hours to complete

    8. **Tips & Tricks**:
       - Common mistakes to avoid
       - Alternative materials if on budget
       - How to make it more comfortable for all-day wear

    Be specific and practical. Target audience is cosplayers with basic crafting skills.
    """

    guide = await router.generate(
        model="gemini/gemini-2.0-flash-exp",
        prompt=prompt,
        images=[item.source_image] + [img.image_path for img in item.images]
    )

    return guide
```

**UI Features:**
- "Generate Cosplay Guide" button
- Save guides to user library
- Community sharing (users upload photos of completed cosplay)
- Link to material vendors (Etsy, Amazon, fabric stores)

**Future Enhancement:**
- AR overlay showing pattern pieces on fabric
- Video tutorials generated from guide steps
- Community ratings and photo submissions

---

### 9.3 Game Modding Export

**Goal:** Export clothing items as game mod files.

**Example: Skyrim Mod Export**
```python
async def export_to_skyrim_mod(clothing_item_id: int):
    """Generate Skyrim mod files for custom armor"""

    item = await get_clothing_item(clothing_item_id)

    # 1. Generate 3D model
    model_path = await generate_3d_model(clothing_item_id)

    # 2. Convert to Skyrim format (.nif file)
    nif_file = await convert_to_nif(
        model_path,
        target_game="skyrim_se",
        body_type="CBBE"  # or "vanilla", "UNP"
    )

    # 3. Generate textures (diffuse, normal, specular maps)
    textures = await generate_pbr_textures(
        clothing_item_id,
        resolution=2048  # 2K textures
    )

    # 4. Create ESP file (Skyrim plugin) with item stats
    esp_file = await create_skyrim_esp(
        name=item.item,
        armor_class=calculate_skyrim_armor(item),
        weight=item.weight_value or 5.0,
        value=calculate_skyrim_value(item),
        enchantments=extract_special_abilities(item)
    )

    # 5. Package as installable mod
    mod_zip = await package_mod(
        nif_file,
        textures,
        esp_file,
        mod_name=f"{item.item} Custom Armor",
        author="lifeOS",
        readme=generate_mod_readme(item)
    )

    return mod_zip  # User downloads and installs via Mod Organizer 2
```

**Supported Games (potential):**
- Skyrim / Skyrim SE
- Fallout 4
- The Witcher 3 (via modding tools)
- Baldur's Gate 3 (limited modding support)

**Challenges:**
- Each game has unique modding format
- Legal considerations (mod policies vary by game/publisher)
- 3D model quality must be game-engine compatible
- Rigging/weight painting for animations

**Legal Safeguards:**
- Only for games that officially support modding
- User must own the game
- Clear disclaimers about fan-made content
- No commercial use

---

### 9.4 AR Virtual Try-On

**Goal:** Point camera at yourself and see outfit overlaid in real-time.

**Technical Stack:**
- Mobile app (iOS/Android)
- ARKit (iOS) / ARCore (Android)
- Body tracking SDK (MediaPipe, ARKit Body Tracking)
- Real-time rendering

**Implementation (High-Level):**
```python
# Mobile app feature (pseudocode)
async def ar_try_on(clothing_item_id: int, camera_feed):
    """Overlay clothing item on user's body in real-time"""

    # 1. Detect body pose and dimensions
    body_landmarks = mediapipe.detect_pose(camera_feed)
    # Returns: shoulder_width, torso_length, arm_length, etc.

    # 2. Scale clothing item to user's body
    scaled_item = await scale_to_body(
        clothing_item_id,
        shoulder_width=body_landmarks.shoulder_width,
        torso_length=body_landmarks.torso_length
    )

    # 3. Render clothing on body with proper occlusion
    # (clothing behind arms should be hidden)
    overlaid_frame = await render_clothing_overlay(
        camera_feed,
        scaled_item,
        body_landmarks,
        lighting_estimation=True  # Match real-world lighting
    )

    return overlaid_frame  # Display in AR view (30-60 fps)
```

**Features:**
- Real-time try-on (30+ fps)
- Multiple items at once (full outfit)
- Screenshot/video recording
- Share to social media
- "Buy this look" button (if items are from retail games like The Sims)

**Simpler MVP:**
- Static mannequin try-on (upload photo, not live camera)
- 2D overlay instead of full 3D AR
- Pre-generated outfit composites

---

### 9.5 Material Sourcing for Real-World Recreation

**Goal:** Help users find real-world materials to recreate clothing items.

**Implementation:**
```python
async def find_materials(clothing_item_id: int):
    """Find purchasable materials to recreate this item"""

    item = await get_clothing_item(clothing_item_id)

    prompt = f"""
    This is a {item.game_source} clothing item called "{item.item}".

    Visual details: {item.details}
    Materials: {item.fabric}
    Colors: {item.color}

    Find real-world equivalents:
    1. **Fabric/Material**: What to search for on fabric stores
       - Specific fabric type (e.g., "vegan leather", "brocade", "neoprene")
       - Color/finish needed
       - Approximate yardage

    2. **Hardware**: Buckles, zippers, buttons, snaps, D-rings
       - Style (antique brass, chrome, leather)
       - Size/quantity

    3. **Decorative Elements**: Studs, embroidery thread, patches

    4. **Suggested Vendors**:
       - Fabric.com, Joann, Mood Fabrics (general)
       - Etsy (specialty items, custom hardware)
       - Amazon (bulk hardware, foam)

    5. **Total Estimated Cost**: Low/medium/high budget options

    6. **Search Keywords**: Exact terms to use on vendor sites

    Be specific and practical for someone shopping online.
    """

    sourcing_guide = await router.generate(
        model="gemini/gemini-2.0-flash-exp",
        prompt=prompt,
        images=[item.source_image]
    )

    # Optionally: Integrate with shopping APIs
    # - Amazon Product Advertising API
    # - Etsy API
    # - Fabric.com affiliate links

    return sourcing_guide
```

**UI Features:**
- "Find Materials" button on clothing item page
- Direct links to vendor product pages
- Price tracking (alert when material goes on sale)
- Community notes ("I used THIS fabric and it worked great!")

---

### 9.6 Outfit Video Generation (Future)

**Goal:** Animate outfits with character movement.

**Technologies:**
- Sora (OpenAI video generation)
- Runway Gen-2/Gen-3
- Stable Video Diffusion

**Use Cases:**
- Fashion show runways with game outfits
- Character walk cycles
- Combat animations (armor in action)
- Social media content (TikTok, Instagram Reels)

**Implementation (Future):**
```python
async def generate_outfit_video(
    clothing_item_ids: List[int],
    animation: str = "runway_walk",  # or "combat", "idle", "dance"
    style: str = "cinematic"
):
    """Generate video of character wearing outfit"""

    # 1. Generate outfit visualization (static image)
    outfit_image = await generate_outfit_composition(clothing_item_ids)

    # 2. Use video generation API
    video = await sora_api.image_to_video(
        image=outfit_image,
        motion_prompt=f"{animation}, {style} lighting, smooth camera movement",
        duration_seconds=5,
        resolution="1080p"
    )

    return video
```

---

## 10. Technical Architecture

### 10.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│ Game Equipment Importer Tool                                │
│ ai_tools/game_equipment_importer/                           │
│ - tool.py (main importer logic)                             │
│ - adapters/ (pluggable data source adapters)                │
│ - README.md                                                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Data Source Adapters (Pluggable)                            │
│ - BG3CargoAdapter (wiki Cargo API)                          │
│ - BG3NexusAdapter (JSON data dumps)                         │
│ - SkyrimUESPAdapter (UESP Cargo API)                        │
│ - CyberpunkFandomAdapter (Fandom wiki scraper)              │
│ - GenericWikiScraperAdapter (fallback)                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Processing Pipeline (Background Jobs)                        │
│ 1. Fetch equipment list from source                         │
│ 2. Download associated images/icons                         │
│ 3. Vision model analysis (multi-angle if available)         │
│ 4. Map fields to clothing_items schema                      │
│ 5. Generate semantic embeddings                             │
│ 6. Auto-generate tags                                       │
│ 7. Create preview images (via existing system)              │
│ 8. Batch insert into database                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Database Records (PostgreSQL)                                │
│ - clothing_items (core data + embeddings)                   │
│ - clothing_item_images (multi-angle views)                  │
│ - tags (auto-generated + manual)                            │
│ - entity_tags (many-to-many)                                │
│ - equipment_sets (optional)                                 │
│ - character_builds (optional)                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Frontend Features                                            │
│ - Browse imported items (filter by game, rarity, slot)      │
│ - Natural language outfit composition                       │
│ - Style harmonization controls                              │
│ - Art style preset selection                                │
│ - Equipment set tracking                                    │
│ - 3D model viewer/download                                  │
│ - Cosplay guide generation                                  │
└─────────────────────────────────────────────────────────────┘
```

### 10.2 Adapter Pattern (Pluggable Data Sources)

**Base Adapter Interface:**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class GameEquipmentAdapter(ABC):
    """Base class for game equipment data adapters"""

    @abstractmethod
    async def fetch_equipment_list(
        self,
        filters: Dict[str, Any] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Fetch list of equipment items from data source"""
        pass

    @abstractmethod
    async def download_images(
        self,
        equipment_data: Dict
    ) -> List[str]:
        """Download images associated with equipment item"""
        pass

    @abstractmethod
    def map_to_schema(
        self,
        equipment_data: Dict,
        vision_analysis: Dict
    ) -> Dict:
        """Map source data + vision analysis to clothing_items schema"""
        pass

    @property
    @abstractmethod
    def game_name(self) -> str:
        """Return game name (e.g., 'Baldur's Gate 3')"""
        pass

    @property
    @abstractmethod
    def game_slug(self) -> str:
        """Return game slug (e.g., 'bg3')"""
        pass
```

**Example Adapter:**
```python
class BG3CargoAdapter(GameEquipmentAdapter):
    """Adapter for BG3 wiki Cargo tables"""

    BASE_URL = "https://bg3.wiki/w/api.php"

    async def fetch_equipment_list(self, filters=None, limit=100):
        equipment_types = filters.get("types", ["Light Armour", "Medium Armour", "Heavy Armour"])

        all_items = []
        for eq_type in equipment_types:
            params = {
                "action": "cargoquery",
                "format": "json",
                "tables": "equipment",
                "fields": "name,type,rarity,armour_class,weight,price,description,icon,uuid",
                "where": f"type='{eq_type}'",
                "limit": limit
            }

            response = await self.http_client.get(self.BASE_URL, params=params)
            data = response.json()
            items = data.get("cargoquery", [])
            all_items.extend(items)

        return all_items

    async def download_images(self, equipment_data):
        # Download icon from wiki
        icon_url = equipment_data.get("icon")
        if icon_url:
            # Wiki icons are relative paths, construct full URL
            full_url = f"https://bg3.wiki{icon_url}"
            local_path = f"/game_assets/bg3/icons/{equipment_data['uuid']}.png"
            await download_file(full_url, local_path)
            return [local_path]
        return []

    def map_to_schema(self, equipment_data, vision_analysis):
        return {
            "item_id": equipment_data.get("uuid"),
            "category": f"{equipment_data.get('type')} - Body",
            "item": equipment_data.get("name"),
            "fabric": vision_analysis.get("materials"),
            "color": vision_analysis.get("colors"),
            "details": f"{equipment_data.get('description')}. {vision_analysis.get('design_details')}",
            "source_image": vision_analysis.get("primary_image_path"),
            "game_source": "Baldur's Gate 3",
            "rarity": equipment_data.get("rarity"),
            "weight_value": float(equipment_data.get("weight", 0)),
            "game_metadata": {
                "armor_class": equipment_data.get("armour_class"),
                "price_gp": equipment_data.get("price"),
                "wiki_url": f"https://bg3.wiki/wiki/{equipment_data.get('name').replace(' ', '_')}"
            }
        }

    @property
    def game_name(self):
        return "Baldur's Gate 3"

    @property
    def game_slug(self):
        return "bg3"
```

**Registering Adapters:**
```python
# ai_tools/game_equipment_importer/adapters/__init__.py
AVAILABLE_ADAPTERS = {
    "bg3_cargo": BG3CargoAdapter,
    "bg3_nexus": BG3NexusAdapter,
    "skyrim_uesp": SkyrimUESPAdapter,
    "cyberpunk_fandom": CyberpunkFandomAdapter,
}

def get_adapter(adapter_name: str) -> GameEquipmentAdapter:
    adapter_class = AVAILABLE_ADAPTERS.get(adapter_name)
    if not adapter_class:
        raise ValueError(f"Unknown adapter: {adapter_name}")
    return adapter_class()
```

### 10.3 Batch Import Pipeline

```python
# ai_tools/game_equipment_importer/tool.py

async def import_game_equipment(
    adapter_name: str,
    filters: Dict = None,
    limit: int = 100
):
    """
    Main import pipeline
    """

    # 1. Get adapter
    adapter = get_adapter(adapter_name)
    logger.info(f"Starting import from {adapter.game_name} using {adapter_name} adapter")

    # 2. Fetch equipment list
    equipment_list = await adapter.fetch_equipment_list(filters, limit)
    logger.info(f"Fetched {len(equipment_list)} items")

    # 3. Process each item
    for idx, equipment_data in enumerate(equipment_list):
        logger.info(f"Processing {idx+1}/{len(equipment_list)}: {equipment_data.get('name')}")

        # 3a. Download images
        image_paths = await adapter.download_images(equipment_data)

        # 3b. Vision analysis
        vision_analysis = await analyze_equipment_comprehensive(
            images=image_paths,
            metadata=equipment_data
        )

        # 3c. Map to schema
        clothing_item_data = adapter.map_to_schema(equipment_data, vision_analysis)

        # 3d. Generate embedding
        description_text = f"{clothing_item_data['item']} {clothing_item_data['fabric']} {clothing_item_data['color']} {clothing_item_data['details']}"
        embedding = await generate_embedding(description_text)
        clothing_item_data["description_embedding"] = embedding

        # 3e. Insert into database
        clothing_item = await clothing_item_service.create(clothing_item_data)

        # 3f. Auto-generate tags
        tags = await generate_tags_for_item(clothing_item_data, adapter.game_slug)
        for tag_data in tags:
            tag = await tag_service.get_or_create_tag(tag_data)
            await tag_service.link_entity(clothing_item.id, tag.tag_id)

        # 3g. Store multiple images
        for image_path in image_paths:
            await clothing_item_image_service.create({
                "clothing_item_id": clothing_item.id,
                "image_path": image_path,
                "view_angle": "front",  # TODO: detect angle
                "image_type": "icon"
            })

        # 3h. Generate preview (background job)
        await job_queue.enqueue(
            "generate_preview",
            clothing_item_id=clothing_item.id
        )

        logger.info(f"✅ Imported: {clothing_item.item} (ID: {clothing_item.id})")

    logger.info(f"Import complete: {len(equipment_list)} items processed")
```

### 10.4 Tag Generation Logic

```python
async def generate_tags_for_item(item_data: Dict, game_slug: str) -> List[Dict]:
    """Auto-generate tags based on item data"""

    tags = []

    # Game source tag
    tags.append({
        "name": game_slug,
        "category": "game_source",
        "color": GAME_COLORS.get(game_slug, "#6B7280")
    })

    # Rarity tag
    if item_data.get("rarity"):
        tags.append({
            "name": item_data["rarity"].lower(),
            "category": "rarity",
            "color": RARITY_COLORS.get(item_data["rarity"].lower(), "#9CA3AF")
        })

    # Equipment type (from category)
    if "armor" in item_data["category"].lower():
        armor_type = item_data["category"].split("-")[0].strip().lower()
        tags.append({
            "name": armor_type,
            "category": "equipment_type",
            "color": "#60A5FA"
        })

    # Material tags (from fabric field)
    materials = extract_materials(item_data.get("fabric", ""))
    for material in materials:
        tags.append({
            "name": material.lower(),
            "category": "material",
            "color": "#F59E0B"
        })

    # Style theme (use LLM to infer)
    theme = await infer_style_theme(item_data)
    if theme:
        tags.append({
            "name": theme.lower(),
            "category": "theme",
            "color": "#EC4899"
        })

    return tags
```

### 10.5 Admin UI (Import Control Panel)

**Frontend Component: `GameEquipmentImporter.jsx`**

Features:
- Select game from dropdown
- Choose data source adapter
- Set filters (equipment types, rarity, etc.)
- Set batch size
- Start import job
- View progress (real-time)
- Review imported items
- Handle conflicts (duplicate detection)

**Workflow:**
1. User selects "Baldur's Gate 3" from game list
2. Adapter auto-selected: "BG3 Cargo API"
3. User sets filters: "Light Armor, Medium Armor, Rare+"
4. User clicks "Start Import"
5. Background job created (RQ worker)
6. Progress shown in UI (10/100 items processed)
7. User can navigate away, job continues
8. Notification when complete: "Imported 100 items from BG3"

---

## 11. Implementation Roadmap

### Phase 1: Proof of Concept (2-3 weeks)
**Goal:** Validate approach with single game

**Tasks:**
1. ✅ Research data sources (Cargo APIs, JSON dumps)
2. ✅ Design database schema changes
3. Build BG3 Cargo adapter
4. Implement vision analysis pipeline (multi-angle support)
5. Create tag auto-generation logic
6. Import 50-100 BG3 items
7. Test outfit generation with imported items
8. Validate semantic search with embeddings

**Success Criteria:**
- 50+ BG3 items in database with rich descriptions
- Tags auto-created and searchable
- Can filter by game source, rarity, equipment type
- Outfit generation uses imported items successfully

**Deliverables:**
- `ai_tools/game_equipment_importer/` tool structure
- `BG3CargoAdapter` working
- Database migrations applied
- Documentation updated

---

### Phase 2: Multi-Game Expansion (3-4 weeks)
**Goal:** Add 3-4 more games with diverse aesthetics

**Games Priority:**
1. Cyberpunk 2077 (sci-fi/modern)
2. Skyrim (fantasy, different aesthetic from BG3)
3. The Sims 4 (contemporary fashion)
4. Destiny 2 or Mass Effect (space fantasy/sci-fi)

**Tasks:**
1. Build adapters for each game
2. Import 100-200 items per game
3. Capture art style guides (10-20 screenshots per game)
4. Create game-specific visualization presets
5. Test cross-game outfit mixing
6. Refine tag taxonomy based on multi-game data

**Success Criteria:**
- 500+ items across 4-5 games
- Art style presets working for each game
- Can create eclectic outfits (items from multiple games)
- Semantic search works across games

**Deliverables:**
- 4+ adapters functional
- Art style templates for each game
- Expanded tag system
- Admin UI for managing imports

---

### Phase 3: AI Composition & Harmonization (3-4 weeks)
**Goal:** Smart outfit creation and style unification

**Tasks:**
1. Implement semantic embedding generation
2. Add pgvector extension to PostgreSQL
3. Build natural language outfit composition engine
4. Implement style harmonization ("coat of paint" feature)
5. Create outfit compatibility scoring
6. Build "universe translation" feature
7. UI for natural language queries

**Success Criteria:**
- Query "tough regal warrior outfit" generates cohesive result
- Style harmonization makes eclectic outfits look unified
- Can translate items across universes (e.g., Cyberpunk jacket → medieval coat)
- Compatibility scoring prevents clashing items

**Deliverables:**
- Semantic search API endpoints
- Style harmonization tool
- Natural language query UI
- Universe translation feature

---

### Phase 4: Extended Features (4-6 weeks, ongoing)
**Goal:** Add advanced capabilities

**Potential Features (prioritize based on user interest):**
1. **Equipment Set Tracking**
   - Schema for sets and bonuses
   - UI for set completion tracking

2. **Character Build Templates**
   - Import famous builds from games
   - "Load build" functionality

3. **3D Model Generation**
   - Integration with TripoSR or Meshy.ai
   - 3D viewer in browser
   - STL export for 3D printing

4. **Cosplay Guide Generation**
   - Material sourcing
   - Step-by-step instructions
   - Budget estimates

5. **AR Virtual Try-On** (ambitious)
   - Mobile app development
   - Body tracking integration
   - Real-time rendering

**Success Criteria:**
- At least 2-3 extended features fully implemented
- User feedback incorporated
- Documentation complete

---

### Phase 5: Community & Scaling (Ongoing)
**Goal:** Community contributions and dataset growth

**Tasks:**
1. Community adapter contributions (GitHub)
2. Expand to 10+ games
3. Performance optimization (caching, CDN for images)
4. Moderation tools (flag incorrect imports)
5. User-submitted corrections
6. API for third-party integrations

**Long-term Vision:**
- 20+ games, 10,000+ items
- Community-maintained adapters
- Public API for developers
- Integration with other platforms

---

## 12. Open Questions

### Technical Decisions Needed

1. **Embedding Model Selection**
   - **Options:** OpenAI ada-002, Voyage AI, Cohere, local models
   - **Criteria:** Cost, quality, latency, self-hosting capability
   - **Recommendation:** Start with OpenAI ada-002 (proven), migrate to Voyage or self-hosted later

2. **3D Reconstruction Approach**
   - **Options:** TripoSR (self-hosted), Meshy.ai (API), Luma AI (API)
   - **Criteria:** Quality, cost, processing time
   - **Recommendation:** Start with Meshy.ai API for MVP (easier), self-host TripoSR if cost becomes issue

3. **Image Storage at Scale**
   - **Current:** Local filesystem
   - **Future (10k+ items):** S3, Cloudflare R2, or local NAS?
   - **Recommendation:** Stay local until 5k items, then evaluate cloud

4. **Rate Limiting Strategy**
   - Wiki APIs: 1-2 req/sec (respectful)
   - LLM APIs: Batch processing to avoid rate limits
   - Should we cache all API responses permanently?

5. **Conflict Resolution**
   - What if item already exists (re-import after game update)?
   - Options: Skip, update, version, manual review
   - **Recommendation:** UUID-based deduplication, update only if manually_modified=false

6. **Art Style Versioning**
   - Games update graphics (Skyrim SE, BG3 patches)
   - How to manage multiple style versions?
   - **Recommendation:** Version field in style templates, latest as default

### Design Decisions Needed

1. **User Access Control**
   - Are imported items global (all users) or per-user?
   - **Recommendation:** Global imports, but users can clone and customize

2. **Tag Taxonomy**
   - Need standardized tag categories
   - Who maintains canonical tag list?
   - **Recommendation:** Start with fixed categories, allow user tags later

3. **Preview Image Generation**
   - Auto-generate for all imports? (could be 1000s of jobs)
   - Or lazy-load (generate on first view)?
   - **Recommendation:** Lazy-load to avoid overwhelming job queue

4. **Multi-Language Support**
   - Many games have localized item names
   - Import multiple languages?
   - **Recommendation:** English only initially, add i18n later if needed

### Business/Legal Questions

1. **Copyright Considerations**
   - Using game assets (icons, screenshots) for personal use
   - Clear user disclaimers needed
   - No commercial use without permission
   - **Recommendation:** Add ToS disclaimer, mark as fan project

2. **Modding Export Legality**
   - Skyrim: Officially supported modding ✅
   - Other games: Check EULA
   - **Recommendation:** Only support games with official mod support

3. **Community Contributions**
   - Allow user-submitted adapters?
   - Code review process needed
   - **Recommendation:** Yes, but require review and testing

---

## Appendix A: Example Data Structures

### Clothing Item (BG3 Armor)
```json
{
  "id": 1234,
  "item_id": "cf6237a2-7f37-4796-b239-0685505510d4",
  "category": "Light Armor - Body",
  "item": "Faded Drow Leather Armour",
  "fabric": "Studded leather with Drow-style patterns, faded from sun exposure",
  "color": "Dark gray, faded black, silver studs",
  "details": "The sun's harsh light has dulled this armour's dark lustre. Constructed from studded leather with intricate Drow patterns now barely visible. Provides moderate protection while maintaining mobility. AC: 12 + Dexterity modifier. Requires Light Armour proficiency.",
  "source_image": "/game_assets/bg3/icons/cf6237a2-7f37-4796-b239-0685505510d4.png",
  "preview_image_path": "/entity_previews/clothing_items/1234_preview.png",
  "game_source": "Baldur's Gate 3",
  "rarity": "Common",
  "weight_value": 5.85,
  "source_entity_id": "ARM_StuddedLeather_Drow_Faded",
  "game_metadata": {
    "game": "Baldur's Gate 3",
    "game_slug": "bg3",
    "armor_class": "12 + Dex",
    "proficiency_required": "Light Armour",
    "weight_kg": 5.85,
    "weight_lb": 11.7,
    "price_gp": 130,
    "location_found": "Waukeen's Rest (X: -71, Y: 592)",
    "wiki_url": "https://bg3.wiki/wiki/Faded_Drow_Leather_Armour",
    "original_uid": "ARM_StuddedLeather_Drow_Faded"
  },
  "description_embedding": [0.023, -0.145, 0.089, ...],  // 768-dimensional vector
  "manually_modified": false,
  "created_at": "2025-10-24T10:30:00Z"
}
```

### Equipment Set
```json
{
  "set_id": "bg3_drow_studded_leather",
  "game_source": "Baldur's Gate 3",
  "set_name": "Drow Studded Leather Set",
  "set_bonus_description": "2-piece: +5 Stealth in darkness. 4-piece: Advantage on Stealth checks in darkness.",
  "rarity": "Common",
  "piece_count": 4,
  "pieces": [
    {
      "clothing_item_id": 1234,
      "slot": "chest",
      "required_for_bonus": true
    },
    {
      "clothing_item_id": 1235,
      "slot": "head",
      "required_for_bonus": true
    },
    {
      "clothing_item_id": 1236,
      "slot": "hands",
      "required_for_bonus": false
    },
    {
      "clothing_item_id": 1237,
      "slot": "feet",
      "required_for_bonus": false
    }
  ]
}
```

### Art Style Template (BG3)
```yaml
# data/tool_configs/art_styles/baldurs_gate_3_style.yaml
game: "Baldur's Gate 3"
game_slug: "bg3"
style_name: "BG3 Cinematic Fantasy"

character_proportions:
  head_size: "realistic"
  body_type: "realistic with subtle idealization"
  muscle_definition: "natural, not exaggerated"

rendering_style:
  technique: "photorealistic with cinematic grading"
  detail_level: "high (AAA game quality)"
  geometry: "realistic, high-poly"

color_palette:
  saturation: "moderate to high"
  bias: "slight warm bias, golden hour lighting common"
  signature_colors:
    - "Deep burgundy reds"
    - "Rich forest greens"
    - "Warm golds and brass"
    - "Deep shadows with blue tints"

lighting:
  style: "cinematic, dramatic"
  techniques:
    - "Three-point lighting"
    - "Rim lighting on characters"
    - "God rays and volumetric lighting"
    - "High contrast with deep shadows"

textures:
  style: "PBR (Physically Based Rendering)"
  detail: "High-resolution, realistic materials"
  weathering: "Visible wear and age on equipment"

post_processing:
  - "Subtle bloom on magical items"
  - "Slight film grain"
  - "Color grading (teal shadows, warm highlights)"
  - "Depth of field in cutscenes"

prompt_template: |
  {subject}, Baldur's Gate 3 cinematic style, photorealistic fantasy rendering,
  dramatic three-point lighting, high detail PBR materials, {color_palette},
  subtle bloom, cinematic color grading, AAA game quality, Forgotten Realms aesthetic

reference_images:
  - "/game_assets/bg3/references/character_portrait_1.jpg"
  - "/game_assets/bg3/references/armor_showcase_1.jpg"
  - "/game_assets/bg3/references/cutscene_lighting_1.jpg"
```

---

## Appendix B: Estimated Costs

### API Costs (per 1000 items imported)

| Service | Usage | Cost per 1000 items | Notes |
|---|---|---|---|
| **Wiki API Calls** | Free | $0 | Public APIs, just respect rate limits |
| **Vision Analysis** (Gemini 2.0 Flash) | ~3 images/item × 1000 items | ~$15-30 | $0.005-0.01 per image |
| **Embedding Generation** (OpenAI ada-002) | 1000 items | ~$0.40 | $0.0004 per 1K tokens |
| **Preview Generation** | 1000 items | ~$50-100 | Using existing generator |
| **3D Model Generation** (optional) | 100 items | ~$50-200 | Meshy.ai: $0.50-2.00 per model |
| **Total (without 3D)** | | **~$65-130** | |
| **Total (with 3D for all)** | | **~$565-1130** | |

**Recommendation:** Import items without 3D models initially. Generate 3D on-demand when user requests.

### Storage Costs

| Data Type | Size per Item | 1000 Items | 10,000 Items |
|---|---|---|---|
| **Icons** (PNG, ~50-200KB) | 100KB | 100MB | 1GB |
| **Screenshots** (PNG, ~500KB-2MB) | 1MB | 1GB | 10GB |
| **3D Models** (OBJ, ~5-20MB) | 10MB | 10GB | 100GB |
| **Database Records** | ~5KB | 5MB | 50MB |
| **Embeddings** (768-dim vector) | 3KB | 3MB | 30MB |
| **Total (no 3D)** | | **~1.1GB** | **~11GB** |
| **Total (with 3D)** | | **~11GB** | **~110GB** |

**Recommendation:** Local storage sufficient for 10k+ items. Consider S3/R2 only if scaling to 50k+ items.

---

## Appendix C: Similar Projects / Inspiration

### Existing Fashion/Style Databases
- **The Sims Resource** - User-generated Sims clothing, 100k+ items
- **Mod Nexus** - Game mod databases, searchable by category
- **Pinterest** - Visual discovery, but no structured data

### AI Fashion Projects
- **Lookbook.nu** - Fashion outfit sharing
- **Fashwell** - AI fashion recognition API
- **Vue.ai** - Fashion product tagging

### Game Item Databases
- **Wowhead** - WoW item database, extensive filtering
- **light.gg** - Destiny 2 armor/weapon database
- **XIVAPI** - Final Fantasy XIV API

### What Makes lifeOS Unique
- **Cross-game aggregation** - No one else combines multiple game universes
- **AI-driven analysis** - Vision model extracts details wikis don't provide
- **Style harmonization** - Unique "coat of paint" feature
- **Generative output** - Not just browsing, but creating new visualizations
- **Natural language queries** - "Tough regal warrior outfit" → instant results

---

## Conclusion

The Game Equipment Import System represents a **transformative expansion** of lifeOS's capabilities. By aggregating thousands of professionally-designed clothing items from diverse game universes, the platform evolves from a specialized image generator into a **universal style and fashion database**.

**Key Strengths:**
- ✅ Highly feasible (proven data sources, existing infrastructure)
- ✅ Scalable (pluggable adapter architecture)
- ✅ Low risk (start small with BG3, expand gradually)
- ✅ High impact (10x+ database size, cross-universe capabilities)
- ✅ Extensible (opens doors to 3D, AR, modding, cosplay)

**Next Steps:**
1. Review and approve this proposal
2. Prioritize Phase 1 features
3. Begin implementation with BG3 proof of concept
4. Gather user feedback
5. Iterate and expand

**Long-term Vision:**
lifeOS becomes the definitive platform for:
- Cross-game style analysis
- AI-driven outfit composition
- Virtual fashion experimentation
- Cosplay and modding community hub
- AR/VR fashion applications

This proposal is ready to be synthesized with other platform plans (board game assistant, workflows, agent framework) into a unified roadmap.

---

**Document Version:** 1.0
**Author:** Claude (Anthropic)
**Date:** 2025-10-24
**Status:** Awaiting review and roadmap integration
