# Asset Path Fix for Maps

## Problem

After moving map files to the `maps/` subfolder, all asset paths were broken because they were looking for assets in `maps/assets/` instead of the actual location at the project root `assets/`.

## Root Cause

Maps were using:
```python
ROOT = os.path.dirname(__file__)  # Points to maps/ folder
asset_path = os.path.join(ROOT, "assets", "...")  # Looks in maps/assets/ (WRONG!)
```

But assets are actually in:
```
Shadow_stalker/
├── maps/          ← ROOT points here
│   └── *.py
└── assets/        ← Assets are HERE (parent directory)
```

## Solution

Changed all maps to use `PARENT_DIR` for asset paths:

```python
ROOT = os.path.dirname(__file__)           # maps/
PARENT_DIR = os.path.dirname(ROOT)         # Shadow_stalker/ (project root)
asset_path = os.path.join(PARENT_DIR, "assets", "...")  # Correct!
```

## Files Fixed

All 9 map files updated:

1. ✅ **maps/kenney_level.py**
   - Fixed: KENNEY_TILES, KENNEY_CHARS, KENNEY_BG, PLAYER_PATH

2. ✅ **maps/map.py**
   - Fixed: MOSSY, PLANT_DIR, PLAYER_PATH, FRUIT_DIR

3. ✅ **maps/green_zone_map.py**
   - Fixed: base_path, player_path

4. ✅ **maps/build_demo_map.py**
   - Fixed: base_path, player_path

5. ✅ **maps/exclusion_zone_map.py**
   - Fixed: base_path, player_path

6. ✅ **maps/exclusion_level.py**
   - Fixed: EXCLUSION_TILES, PLAYER_PATH

7. ✅ **maps/nature_adventure_map.py**
   - Fixed: BASE, PLAYER_PATH

8. ✅ **maps/industrial_zone_map.py**
   - Fixed: BASE, PLAYER_PATH

9. ✅ **maps/power_station_map.py**
   - Fixed: BASE, PLAYER_PATH, money_frames path

## Pattern Used

Every map file now follows this pattern:

```python
import os

# Get directories
ROOT = os.path.dirname(__file__)           # Current file's directory (maps/)
PARENT_DIR = os.path.dirname(ROOT)         # Parent directory (project root)

# Asset paths use PARENT_DIR
ASSET_PATH = os.path.join(PARENT_DIR, "assets", "folder-name")
PLAYER_PATH = os.path.join(PARENT_DIR, "assets", "MainCharacters", "VirtualGuy")
```

## Verification

To verify assets load correctly:

```bash
# Test individual maps
python maps/kenney_level.py
python maps/map.py
python maps/green_zone_map.py

# Test through main game
python core/game.py
```

All maps should now:
- ✅ Load tilesets correctly
- ✅ Load player animations
- ✅ Load background images
- ✅ Load decorative objects
- ✅ Display all graphics properly

## Why This Works

The fix maintains portability:
- Uses relative paths (not hardcoded)
- Works regardless of where project folder is moved
- Works on Windows, Mac, and Linux
- No need to update paths when sharing project

## Technical Details

**Before:**
```
maps/kenney_level.py → maps/assets/... ❌ (doesn't exist)
```

**After:**
```
maps/kenney_level.py → ../assets/... ✅ (correct)
```

The `PARENT_DIR` variable goes up one level from `maps/` to the project root, then accesses the `assets/` folder.

---

**Status: ✅ ALL ASSET PATHS FIXED**

All 9 map files now correctly load assets from the project root's assets folder.
