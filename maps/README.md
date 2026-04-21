# Game Maps / Levels

This directory contains all playable map/level modules for the Shadow Stalker game.

## Available Maps

### 1. **map.py** - Mossy Forest
- Atmospheric mossy forest with floating islands
- Soft teal underwater-forest aesthetic
- Features: double jump, wall jump, glowing particles

### 2. **kenney_level.py** - Sunny Grassland
- Bright outdoor world using Kenney Pixel Platformer assets
- Features: grass platforms, trees, coins, clouds, enemies, checkpoints
- Family-friendly and colorful

### 3. **exclusion_level.py** - Exclusion Zone Industrial
- Industrial wasteland with hazards
- Metal platforms, fences, industrial props
- Post-apocalyptic atmosphere

### 4. **exclusion_zone_map.py** - Classic Exclusion Zone
- Original exclusion zone demo level
- Different layout from exclusion_level.py

### 5. **green_zone_map.py** - Green Zone Park
- Urban park environment with green tileset
- Features: skate ramps, benches, fountains, AI bots
- Includes bot enemy system (mask_dude_bot.py)

### 6. **nature_adventure_map.py** - Dungeon Adventure
- 8-stage dungeon adventure
- Nature-themed with treasures and boss fight
- Progressive difficulty

### 7. **industrial_zone_map.py** - Industrial Zone
- Industrial environment using Craftpix tileset
- Factory/warehouse themed

### 8. **power_station_map.py** - Power Station
- Power station themed level
- Electrical/industrial aesthetics

### 9. **build_demo_map.py** - Demo Map Builder
- Demonstration/experimental map
- Features AI bot system
- Used for testing new features

## How to Run Individual Maps

You can run any map directly:
```bash
python maps/green_zone_map.py
python maps/map.py
python maps/kenney_level.py
```

Or use the main game launcher which includes a menu:
```bash
python game.py
```

## Map Structure

Each map module typically includes:
- Tile definitions and loading
- Player class with physics
- Level layout (grid-based or procedural)
- Decorations and objects
- HUD/UI elements
- Optional: AI enemies, collectibles, hazards

## Adding New Maps

To add a new map:
1. Create a new Python file in this directory
2. Follow the structure of existing maps
3. Add it to `game.py` in the root directory
4. Optionally add it to the menu in `menu.py`

## Dependencies

Maps may import from the parent directory:
- `mask_dude_bot.py` - AI bot system (used by some maps)
- Assets are loaded from `../assets/` relative to each map file

All paths use `os.path.dirname(__file__)` for portability.
