# Shadow Stalker - File Structure Documentation

This document provides a comprehensive overview of the Shadow Stalker project file structure, including descriptions and purposes for each file and directory.

## 📁 Root Directory Structure

```
Shadow_stalker/
├── ai/                          # AI systems and bot implementations
├── assets/                      # Game assets (images, sprites, tilesets)
├── core/                        # Core game engine and systems
├── editor/                      # Map editor tools
├── maps/                        # Game map definitions and layouts
├── utils/                       # Utility scripts and tools
├── merged_game.py               # Main merged game file with pursuit mechanic
├── presentation.html            # General game presentation
├── university_presentation.html  # University-style presentation
└── [Documentation files]        # Various markdown documentation files
```

---

## 📂 Detailed Directory Structure

### 🤖 `/ai/` - AI Systems

**Purpose**: Contains AI-controlled characters and bot implementations for the game.

```
ai/
├── __init__.py                 # AI package initialization
├── README.md                   # AI system documentation
└── mask_dude_bot.py            # MaskDude AI bot with pursuit behavior
```

**Key Files**:
- **mask_dude_bot.py**: Advanced AI bot with states (idle, chase, patrol, search), line of sight detection, gap/wall detection, and double jump capability. Used as the enemy in the pursuit mechanic.

---

### 🎨 `/assets/` - Game Assets

**Purpose**: Contains all visual assets including sprites, tilesets, backgrounds, and game objects.

```
assets/
├── 20 Enemies.png              # Enemy sprite sheet
├── craftpix-net-846754-free-green-zone-tileset-pixel-art/  # Green zone tileset
├── craftpix-net-115897-free-exclusion-zone-tileset-pixel-art/  # Exclusion zone tileset
├── craftpix-net-156752-nature-pixel-art-environment-free-assets-pack/  # Nature assets
├── craftpix-785611-free-dungeon-platformer-pixel-art-tiles/  # Dungeon tiles
├── craftpix-net-924041-power-station-free-tileset-pixel-art/  # Power station tileset
├── Background/                 # Background images (Blue, Brown, Gray, Green, Pink, Purple, Yellow)
├── Items/                      # Collectible items
│   ├── Fruits/                 # Fruit collectibles (Apple, Banana, Cherries, etc.)
│   └── Checkpoints/            # Checkpoint items
├── MainCharacters/             # Player character sprites
│   ├── VirtualGuy/             # VirtualGuy character animations
│   ├── Appearing (96x96).png   # Player appearing animation
│   └── Desappearing (96x96).png # Player disappearing animation
├── Other/                      # Miscellaneous objects
├── Seasonal Tilesets/          # Seasonal environment assets
│   └── 1 - Grassland/          # Grassland tileset with backgrounds
├── Traps/                      # Hazard objects
│   ├── Fan/                    # Fan trap
│   ├── Spikes/                 # Spike trap
│   ├── Spiked Ball/            # Spiked ball on chain
│   ├── Spike Head/             # Animated spike head
│   └── Trampoline/             # Trampoline for jumping
└── wmremove-transformed.webp  # Transformed asset file
```

**Asset Categories**:
- **Backgrounds**: 7 different colored backgrounds for variety
- **Characters**: VirtualGuy with full animation set
- **Tilesets**: 4 different themed tilesets (Green Zone, Exclusion Zone, Nature, Dungeon, Power Station)
- **Traps**: 5 different trap types for platforming challenges
- **Items**: Fruits for collectibles and checkpoints
- **Seasonal**: Grassland environment with parallax backgrounds

---

### 🎮 `/core/` - Core Game Systems

**Purpose**: Contains the core game engine, main game loop, and menu systems.

```
core/
├── __init__.py                 # Core package initialization
├── README.md                   # Core system documentation
├── game.py                     # Main game engine and loop
└── menu.py                     # Game menu system
```

**Key Files**:
- **game.py**: Core game engine handling the main game loop, state management, and game logic
- **menu.py**: Menu system for game navigation and options

---

### ✏️ `/editor/` - Map Editor Tools

**Purpose**: Contains tools for creating and editing game maps.

```
editor/
├── __init__.py                 # Editor package initialization
├── README.md                   # Editor documentation
└── map_editor.py               # Map editor tool
```

**Key Files**:
- **map_editor.py**: Tool for visually creating and editing game maps with tile placement

---

### 🗺️ `/maps/` - Game Maps

**Purpose**: Contains all game map definitions, layouts, and level data.

```
maps/
├── __init__.py                 # Maps package initialization
├── README.md                   # Maps documentation
├── industrial_zone_map.py     # Industrial zone level (first map)
├── green_zone_map.py           # Green zone level (second map)
├── exclusion_zone_map.py       # Exclusion zone level (third map)
├── power_station_map.py        # Power station level
├── nature_adventure_map.py     # Nature adventure level
├── kenney_level.py             # Kenney-style level
├── build_demo_map.py           # Demo map for testing
├── map.py                      # Generic map template
└── __pycache__/                # Python cache files
```

**Active Maps in Merged Game**:
1. **industrial_zone_map.py**: First map with industrial theme, conveyor belts, platforms
2. **green_zone_map.py**: Second map with nature theme, fountains, trees
3. **exclusion_zone_map.py**: Third map with exclusion zone theme, hazards, warning signs

**Map Features**:
- Each map defines its own layout, tile mapping, solid tiles, decorations, animated objects
- Coin/collectible positions
- Background layers
- Player spawn points
- Platform sections and hazards

---

### 🔧 `/utils/` - Utility Scripts

**Purpose**: Contains utility scripts for asset viewing, map analysis, and development tools.

```
utils/
├── __init__.py                 # Utils package initialization
├── README.md                   # Utils documentation
├── analyze_map.py              # Map analysis tool
├── nature_tile_viewer.py       # Nature tileset viewer
├── render_objs.py              # Object rendering tool
├── render_tiles.py             # Tile rendering tool
└── tile_viewer.py              # General tile viewer
```

**Key Utilities**:
- **analyze_map.py**: Analyzes map structure and identifies potential issues
- **tile_viewer.py**: Visual tool for viewing tilesets
- **render_objs.py**: Renders game objects for preview
- **render_tiles.py**: Renders tiles for preview

---

## 📄 Root-Level Files

### Main Game Files

- **merged_game.py**: Main merged game file that combines all three active maps (Industrial, Green, Exclusion zones) with:
  - Player character with physics and animations
  - Map transition system
  - Pursuit mechanic using MaskDudeBot AI
  - Game over system
  - Coin collection
  - Shared game state (health, score, lives)

### Presentation Files

- **presentation.html**: General web-based game presentation with interactive elements
- **university_presentation.html**: Academic-style presentation for 3 presenters with slide navigation

### Documentation Files

- **PROJECT_STRUCTURE.md**: Project structure documentation
- **ASSET_PATH_FIX.md**: Asset path fix documentation
- **COMPLETE_ASSET_FIX.md**: Complete asset path fix summary
- **EDITOR_SPEED_GUIDE.md**: Editor usage guide
- **MAP_EDITOR_README.md**: Map editor documentation
- **ORGANIZATION_UPDATE.md**: Project organization updates
- **PATH_FIX_SUMMARY.md**: Path fix summary
- **QUICK_REFERENCE.md**: Quick reference guide
- **REORGANIZATION_COMPLETE.md**: Reorganization completion documentation

### Configuration Files

- **custom_map.json**: Custom map configuration data
- **6ce3e0d2-5b77-49bc-9d98-17f85287531bCAHIER_DES_CHARGES.pdf**: Project requirements document (French)

### Reference Images

- **nature_assets_reference.png**: Reference image for nature assets
- **power_station_objects.png**: Reference image for power station objects
- **power_station_tiles_numbered.png**: Numbered reference for power station tiles
- **map_ui_test.png**: UI test reference image
- **ref_map.png**: Reference map image
- **reference_image.png**: General reference image

---

## 🎯 Game Flow Architecture

```
merged_game.py
    ├── Player Class (movement, physics, animations)
    ├── MapManager Class (handles map transitions)
    ├── MaskDudeBot AI (pursuit enemy)
    ├── Industrial Zone Map → Green Zone Map → Exclusion Zone Map
    └── Game Loop
        ├── Update player
        ├── Update AI enemy
        ├── Handle collisions
        ├── Check map transitions
        ├── Update camera
        └── Render (background, tiles, decorations, player, enemy)
```

---

## 🔗 Key Dependencies

- **Pygame**: Game engine and rendering
- **Python 3.14**: Programming language
- **Asset Libraries**: Multiple craftpix.net tilesets for different themes

---

## 📝 File Naming Conventions

- **Maps**: `[name]_zone_map.py` or `[name]_map.py`
- **AI**: `[character]_bot.py`
- **Utils**: `[function]_viewer.py` or `[function]_tool.py`
- **Documentation**: `[topic]_README.md` or `[topic].md`

---

## 🚀 Quick Start

1. **Run Merged Game**: `python merged_game.py`
2. **Run Individual Map**: `python maps/[map_name].py`
3. **Run Map Editor**: `python editor/map_editor.py`
4. **View Presentations**: Open `presentation.html` or `university_presentation.html` in browser

---

## 📊 Statistics

- **Total Maps**: 8 map files (3 active in merged game)
- **Asset Tilesets**: 5 themed tilesets
- **AI Systems**: 1 (MaskDudeBot)
- **Utility Tools**: 5 development tools
- **Documentation Files**: 9 markdown files
- **Main Game**: 1 merged game with pursuit mechanic

---

## 🔄 Recent Updates

- **Pursuit Mechanic**: Added MaskDudeBot AI for enemy pursuit
- **Map Transitions**: Implemented seamless map switching
- **Tree Fixes**: Fixed tree asset loading in exclusion zone
- **Industrial Zone**: Fixed closed path issue with platform bridge
- **Asset Paths**: Updated all asset paths to use PARENT_DIR for proper loading

---

## 📌 Important Notes

- All maps use 32x32 pixel tiles
- Screen resolution: 1280x720 (resizable)
- Player character: VirtualGuy with full animation set
- Enemy AI: MaskDudeBot with advanced pursuit behavior
- Game state shared across maps (health, score, lives)
- Each map has unique theme and gameplay elements

---

*Last Updated: April 15, 2026*
