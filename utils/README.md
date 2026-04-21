# Utility Tools

This directory contains various utility scripts for asset management, viewing, and analysis.

## Asset Viewers

### [tile_viewer.py](tile_viewer.py)
Industrial zone tile viewer that:
- Displays all tiles in a grid layout
- Shows tile numbers/IDs for reference
- Helps identify tiles when building maps

**Run:** `python utils/tile_viewer.py`

### [nature_tile_viewer.py](nature_tile_viewer.py)
Nature environment tile viewer that:
- Shows tiles and objects from nature tileset
- Organized by category (Tiles, Objects)
- Visual reference for map creation

**Run:** `python utils/nature_tile_viewer.py`

## Rendering Tools

### [render_tiles.py](render_tiles.py)
Power station tile renderer that:
- Renders all power station tiles
- Creates reference images
- Useful for documentation

**Run:** `python utils/render_tiles.py`

### [render_objs.py](render_objs.py)
Power station object renderer that:
- Renders all decorative objects
- Creates sprite sheets or reference images
- Batch processing of object assets

**Run:** `python utils/render_objs.py`

## Analysis Tools

### [analyze_map.py](analyze_map.py)
Map analysis utility that:
- Analyzes reference images
- Extracts tile information
- Helps reverse-engineer map layouts
- Color-based tile detection

**Run:** `python utils/analyze_map.py`

## Usage Examples

### Viewing Tiles
```bash
# View industrial tiles
python utils/tile_viewer.py

# View nature tiles
python utils/nature_tile_viewer.py
```

### Rendering Assets
```bash
# Render power station tiles to image
python utils/render_tiles.py

# Render power station objects
python utils/render_objs.py
```

### Analyzing Maps
```bash
# Analyze a reference map image
python utils/analyze_map.py
```

## When to Use

- **Tile Viewers**: When you need to identify specific tiles for map building
- **Renderers**: When creating documentation or reference materials
- **Analyzer**: When studying existing maps or reference images

## Adding New Utilities

To add a new utility tool:
1. Create a new Python file in this directory
2. Follow the naming convention: descriptive_name.py
3. Add documentation here
4. Make it runnable standalone with `if __name__ == "__main__":`

## Dependencies

All utilities use:
- Pygame for image loading and display
- OS module for file paths (relative paths for portability)
- Standard Python libraries

No external dependencies beyond Pygame.
