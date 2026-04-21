# Path Configuration Fix

## Summary
All hardcoded absolute paths in the project have been converted to relative paths using `os.path.dirname(__file__)`. This ensures the project will work correctly regardless of where the folder is moved on your system or another computer.

## Files Modified

The following files had their hardcoded paths fixed:

1. **green_zone_map.py**
   - Changed from: `c:\Users\basir\Documents\GitHub\Python-Platformer\assets\...`
   - Changed to: `os.path.join(ROOT, "assets", "craftpix-net-846754-free-green-zone-tileset-pixel-art")`

2. **build_demo_map.py**
   - Changed from: `c:\Users\basir\Documents\GitHub\Python-Platformer\assets\...`
   - Changed to: `os.path.join(ROOT, "assets", "craftpix-net-115897-free-exclusion-zone-tileset-pixel-art")`

3. **nature_tile_viewer.py**
   - Changed from: `c:\Users\basir\Documents\GitHub\Python-Platformer\assets\...`
   - Changed to: `os.path.join(ROOT, "assets", "craftpix-net-156752-nature-pixel-art-environment-free-assets-pack", "PNG")`

4. **render_objs.py**
   - Changed from: `c:\Users\basir\Documents\GitHub\Python-Platformer\assets\...`
   - Changed to: `os.path.join(ROOT, "assets", "craftpix-net-924041-power-station-free-tileset-pixel-art")`

5. **render_tiles.py**
   - Changed from: `c:\Users\basir\Documents\GitHub\Python-Platformer\assets\...`
   - Changed to: `os.path.join(ROOT, "assets", "craftpix-net-924041-power-station-free-tileset-pixel-art")`

6. **tile_viewer.py**
   - Changed from: `c:\Users\basir\Documents\GitHub\Python-Platformer\assets\...`
   - Changed to: `os.path.join(ROOT, "assets", "craftpix-net-314143-free-industrial-zone-tileset-pixel-art")`

## How It Works

Each file now uses this pattern:
```python
import os
ROOT = os.path.dirname(__file__)  # Gets the directory where the script is located
base_path = os.path.join(ROOT, "assets", "folder-name")  # Builds path relative to script location
```

This means:
- ✅ The project can be moved to any folder
- ✅ The project can be shared with others
- ✅ Paths work on Windows, Mac, and Linux
- ✅ No need to update paths when moving the project

## Files Already Using Correct Paths

These files were already using the correct relative path approach and didn't need changes:
- map_editor.py
- map.py
- nature_adventure_map.py
- industrial_zone_map.py
- exclusion_zone_map.py
- exclusion_level.py
- power_station_map.py
- kenney_level.py

## Testing

To verify everything works:
1. Move the entire `Shadow_stalker` folder to a different location
2. Run any of the Python files (e.g., `python green_zone_map.py`)
3. All assets should load correctly without any path errors
