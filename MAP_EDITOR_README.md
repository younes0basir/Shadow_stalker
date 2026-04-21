# Map Editor - Visual Level Designer

A powerful visual editor for creating custom levels for the Nature Platformer game.

## Features

- **Visual Tile Placement**: Click and drag to place tiles on a grid
- **Decoration System**: Add trees, rocks, grass, and other objects
- **Zoom & Pan**: Navigate large maps easily
- **Save/Load**: Export your maps as JSON files
- **Real-time Preview**: See exactly what you're placing
- **Two Modes**: Switch between tile placement and decoration mode

## Controls

### Navigation
- **WASD / Arrow Keys**: Pan the camera
- **+ / -**: Zoom in/out (0.3x to 3.0x)
- **Scroll Wheel**: Cycle through available tiles

### Editing
- **Left Click**: Place selected tile or start decoration placement
- **Right Click**: Remove tile or decoration
- **Left Drag**: Paint multiple tiles (tile mode only)
- **T**: Toggle between Tile and Decoration mode
- **G**: Toggle grid visibility

### File Operations
- **S**: Save current map to `custom_map.json`
- **L**: Load map from `custom_map.json`
- **ESC**: Quit editor

## Interface Layout

```
┌──────────┬─────────────────────────────────────┐
│          │  Zoom: 1.0x | Pos: (0, 0) | ...    │ ← Info Bar
│  TILE    ├─────────────────────────────────────┤
│ PALETTE  │                                     │
│          │                                     │
│ [Tile 1] │         MAP CANVAS                  │
│ [Tile 2] │                                     │
│ [Tile 3] │    (Click to place tiles)           │
│   ...    │                                     │
│          │                                     │
│ Controls │                                     │
│ Help     │                                     │
└──────────┴─────────────────────────────────────┘
```

## How to Use

### Creating a New Map

1. **Launch the editor**: `py map_editor.py`
2. **Select a tile** from the left palette (or scroll wheel)
3. **Click or drag** on the canvas to place tiles
4. **Switch modes** with 'T' to add decorations (trees, rocks, etc.)
5. **Pan around** with WASD to access more of the map
6. **Zoom** with +/- for precision work

### Placing Tiles

1. Ensure you're in **Tile Mode** (press T if needed)
2. Select a tile from the palette (grass, dirt, platforms, etc.)
3. Left-click to place, right-click to remove
4. Drag to paint multiple tiles quickly

### Adding Decorations

1. Press **T** to switch to Decoration Mode
2. Select an object from the palette (trees, rocks, grass tufts)
3. Left-click on the map to place the decoration
4. Right-click to remove decorations

### Saving Your Map

1. Press **S** to save
2. The map will be saved as `custom_map.json`
3. This file contains all tile positions and decorations

### Loading a Map

1. Press **L** to load
2. The editor will read from `custom_map.json`
3. Your previous work will be restored

## Using Custom Maps in Your Game

To use a saved map in your platformer game:

```python
import json

# Load the custom map
with open('custom_map.json', 'r') as f:
    data = json.load(f)

# Access map data
map_width = data['width']
map_height = data['height']
tile_layer = data['tiles']
decorations = data['decorations']

# Convert to your game's format
MAP_LAYOUT = ["".join(row) for row in tile_layer]
```

## Tips

- **Start Small**: Begin with a smaller area and expand as needed
- **Use Grid**: Keep grid visible (G key) for precise alignment
- **Layer Planning**: Place ground tiles first, then platforms, then decorations
- **Zoom Out**: Use zoom out (+/-) to see the overall layout
- **Test Frequently**: Save often and test in your game

## File Format

Maps are saved as JSON with this structure:

```json
{
  "width": 80,
  "height": 40,
  "tiles": [
    [" ", " ", "2", "2", ...],
    [" ", " ", "5", "5", ...],
    ...
  ],
  "decorations": [
    ["trees2_1.png", 10, 15],
    ["rocks1_1.png", 25, 18],
    ...
  ]
}
```

## Troubleshooting

- **Can't see tiles?** Make sure assets are in the correct folder
- **Map too small?** Adjust `map_width` and `map_height` in the code
- **Performance issues?** Reduce zoom level or map size
- **Tiles not loading?** Check that the craftpix asset pack is in the assets folder

## Future Enhancements

Potential features to add:
- Multiple layer support (background, foreground)
- Undo/Redo functionality
- Map templates/presets
- Export to Python code directly
- Collision zone editing
- Enemy/object placement
- Testing mode within editor
