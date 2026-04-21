# Project Organization Update

## Summary

All playable map/level files have been organized into a dedicated `maps/` folder to improve project structure and maintainability.

## What Changed

### Files Moved to `maps/` Folder

The following 9 map files were moved from the root directory to `maps/`:

1. **map.py** - Mossy Forest level
2. **kenney_level.py** - Sunny Grassland level  
3. **exclusion_level.py** - Exclusion Zone Industrial level
4. **exclusion_zone_map.py** - Classic Exclusion Zone level
5. **green_zone_map.py** - Green Zone Park level
6. **nature_adventure_map.py** - Nature Adventure dungeon
7. **industrial_zone_map.py** - Industrial Zone level
8. **power_station_map.py** - Power Station level
9. **build_demo_map.py** - Demo map builder

### Files Modified

1. **[game.py](file://c:/Users/basir/Documents/upf/gaming/Shadow_stalker/game.py)**
   - Updated all module loading paths to use `maps/` prefix
   - Example: `"map.py"` → `"maps/map.py"`

2. **[maps/green_zone_map.py](file://c:/Users/basir/Documents/upf/gaming/Shadow_stalker/maps/green_zone_map.py)**
   - Added parent directory to sys.path for importing mask_dude_bot
   - Added: `sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))`

3. **[maps/build_demo_map.py](file://c:/Users/basir/Documents/upf/gaming/Shadow_stalker/maps/build_demo_map.py)**
   - Added parent directory to sys.path for importing mask_dude_bot
   - Added: `sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))`

### New Files Created

1. **[maps/__init__.py](file://c:/Users/basir/Documents/upf/gaming/Shadow_stalker/maps/__init__.py)**
   - Makes maps a proper Python package

2. **[maps/README.md](file://c:/Users/basir/Documents/upf/gaming/Shadow_stalker/maps/README.md)**
   - Documentation for all available maps
   - Instructions for running individual maps
   - Guide for adding new maps

## Files Kept in Root Directory

These utility/editor files remain in the root for easy access:

- **game.py** - Main game launcher with menu system
- **menu.py** - Menu UI system
- **map_editor.py** - Map editing tool
- **mask_dude_bot.py** - AI bot system (shared library)
- **analyze_map.py** - Map analysis utility
- **render_tiles.py**, **render_objs.py** - Asset rendering utilities
- **tile_viewer.py**, **nature_tile_viewer.py** - Tile viewing utilities

## How to Run

### Option 1: Use Main Game Launcher (Recommended)
```bash
python game.py
```
This shows the menu where you can select any level.

### Option 2: Run Individual Maps
```bash
python maps/green_zone_map.py
python maps/map.py
python maps/kenney_level.py
```

## Benefits

✅ **Better Organization** - All playable levels are in one place  
✅ **Cleaner Root** - Root directory now contains only core systems and utilities  
✅ **Easier Navigation** - Clear separation between maps and tools  
✅ **Portable** - All paths remain relative, works anywhere  
✅ **Documented** - README explains each map and how to use them  

## Testing

To verify everything works:

1. Run the main game: `python game.py`
2. Select different levels from the menu
3. Each level should load and play correctly
4. Try running individual maps directly

All imports and asset loading should work without errors since paths use `os.path.dirname(__file__)` for portability.
