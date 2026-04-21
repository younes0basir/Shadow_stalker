# Shadow Stalker - Complete Project Structure

## 📁 Directory Organization

```
Shadow_stalker/
│
├── core/                    # Main Game Engine
│   ├── __init__.py
│   ├── game.py             # Main launcher & level manager
│   ├── menu.py             # Menu UI system
│   └── README.md
│
├── maps/                    # Playable Levels/Maps
│   ├── __init__.py
│   ├── map.py              # Mossy Forest
│   ├── kenney_level.py     # Sunny Grassland
│   ├── exclusion_level.py  # Exclusion Zone Industrial
│   ├── exclusion_zone_map.py  # Classic Exclusion Zone
│   ├── green_zone_map.py   # Green Zone Park (with AI bots)
│   ├── nature_adventure_map.py  # Dungeon Adventure
│   ├── industrial_zone_map.py   # Industrial Zone
│   ├── power_station_map.py     # Power Station
│   ├── build_demo_map.py   # Demo Map Builder
│   └── README.md
│
├── ai/                      # AI Systems
│   ├── __init__.py
│   ├── mask_dude_bot.py    # Bot enemy AI system
│   └── README.md
│
├── editor/                  # Map Editor Tools
│   ├── __init__.py
│   ├── map_editor.py       # Visual map editor
│   └── README.md
│
├── utils/                   # Utility & Viewer Tools
│   ├── __init__.py
│   ├── tile_viewer.py      # Industrial tile viewer
│   ├── nature_tile_viewer.py  # Nature tile viewer
│   ├── render_tiles.py     # Power station tile renderer
│   ├── render_objs.py      # Power station object renderer
│   ├── analyze_map.py      # Map analysis tool
│   └── README.md
│
├── assets/                  # Game Assets (Images, Sprites)
│   ├── Background/
│   ├── MainCharacters/
│   ├── Items/
│   ├── Traps/
│   ├── craftpix-net-*/     # Various tilesets
│   ├── kenney_pixel-platformer/
│   └── ... (other asset folders)
│
├── custom_map.json          # Example custom map file
│
└── Documentation/
    ├── PATH_FIX_SUMMARY.md        # Path portability fixes
    ├── ORGANIZATION_UPDATE.md     # Folder organization changes
    ├── EDITOR_SPEED_GUIDE.md      # Map editor guide
    └── MAP_EDITOR_README.md       # Editor documentation
```

## 🎮 Quick Start

### Run the Game
```bash
python core/game.py
```
This launches the main menu where you can select any level.

### Run Individual Maps
```bash
python maps/green_zone_map.py
python maps/map.py
python maps/kenney_level.py
```

### Open Map Editor
```bash
python editor/map_editor.py
```

### Use Utility Tools
```bash
python utils/tile_viewer.py
python utils/nature_tile_viewer.py
python utils/render_tiles.py
```

## 📂 Folder Descriptions

### `core/` - Game Engine
The heart of the game. Contains the main launcher, menu system, and level management.
- **game.py**: Loads levels, manages game state, handles transitions
- **menu.py**: Beautiful pixel-art menu UI with level selection

### `maps/` - Playable Levels
All game levels and maps live here. Each file is a complete playable level.
- 9 different themed levels
- Each with unique tilesets, layouts, and gameplay
- Can be run individually or through the main menu

### `ai/` - Artificial Intelligence
AI systems for enemies and NPCs.
- **mask_dude_bot.py**: Autonomous bot enemies with patrol/chase behavior
- Used by maps that have enemy characters

### `editor/` - Level Creation Tools
Tools for creating and editing game maps.
- **map_editor.py**: Full visual editor with tile palettes and object placement
- Save/load maps as JSON files

### `utils/` - Developer Utilities
Helper tools for development and asset management.
- Tile viewers for reference
- Asset renderers
- Map analysis tools

### `assets/` - Game Resources
All images, sprites, and tilesets.
- Organized by source/type
- Used by all maps and levels
- Portable paths work anywhere

## 🔧 Key Features

✅ **Modular Design**: Each component is separate and reusable  
✅ **Portable Paths**: All paths use relative references - works anywhere  
✅ **Well Documented**: Every folder has README with usage instructions  
✅ **Easy to Extend**: Add new maps, AI, or utilities easily  
✅ **Professional Structure**: Clean separation of concerns  

## 🚀 Adding New Content

### Add a New Map
1. Create Python file in `maps/`
2. Follow existing map structure
3. Add to `core/game.py` level loader
4. Optionally add to `core/menu.py` level selection

### Add New AI
1. Create Python file in `ai/`
2. Implement AI logic
3. Import in maps that need it

### Add New Utility
1. Create Python file in `utils/`
2. Make it runnable standalone
3. Document in `utils/README.md`

### Add New Editor Feature
1. Modify `editor/map_editor.py`
2. Test thoroughly
3. Update documentation

## 📝 Development Workflow

1. **Design**: Plan your level or feature
2. **Create**: Build in appropriate folder
3. **Test**: Run and verify it works
4. **Document**: Update relevant README
5. **Integrate**: Connect to main game if needed

## 🎯 Project Goals

- Clean, maintainable code structure
- Easy to add new content
- Portable across systems
- Well documented for collaboration
- Modular for reuse

## 📖 Documentation

Each folder contains its own README with:
- File descriptions
- Usage instructions
- Examples
- Extension guides

See individual folder READMEs for detailed information.
