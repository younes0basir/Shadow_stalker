# Map Editor

This directory contains tools for creating and editing game levels.

## Files

### [map_editor.py](map_editor.py)
Full-featured map editor with:
- Visual tile placement interface
- Multiple tileset support (Nature, Industrial, Power Station, etc.)
- Object placement (trees, boxes, decorations)
- Save/Load maps as JSON
- Real-time preview
- Grid-based editing

**Run:** `python editor/map_editor.py`

## Features

- **Tile Palette**: Browse and select tiles from different tilesets
- **Object Tools**: Place decorative objects on the map
- **Layer Support**: Work with background and foreground layers
- **Undo/Redo**: Revert mistakes easily
- **Export**: Save maps in JSON format compatible with game engine
- **Import**: Load existing maps for editing

## Usage

1. Launch the editor: `python editor/map_editor.py`
2. Select a tileset from the palette
3. Click on the grid to place tiles
4. Use object tools to add decorations
5. Save your map as JSON
6. Load it in your game by importing the JSON file

## Keyboard Shortcuts

- **Mouse Click**: Place tile/object
- **Right Click**: Remove tile/object
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **Ctrl+S**: Save map
- **Ctrl+O**: Open map
- **ESC**: Exit editor

## Creating Custom Maps

To create a new map:
1. Start with a blank canvas or load a template
2. Design your level layout using tiles
3. Add objects and decorations
4. Test the map by loading it in the game
5. Iterate and refine based on playtesting

## Map Format

Maps are saved as JSON files with:
- Tile grid data
- Object positions and types
- Metadata (name, author, description)
- Layer information

See `custom_map.json` in root for an example format.
