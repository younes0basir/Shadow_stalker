# Core Game Engine

This directory contains the main game engine components.

## Files

### [game.py](game.py)
Main game launcher that:
- Shows the level selection menu
- Loads selected levels dynamically
- Manages shared game state (health, score, lives) across levels
- Handles level transitions

**Run:** `python core/game.py` or `python game.py` from root (if symlinked)

### [menu.py](menu.py)
Menu UI system featuring:
- Main menu with Play, Levels, Controls, Quit options
- Level selection screen with preview cards
- Controls/instructions screen
- Pixel-art styled buttons and UI elements
- Mouse-based navigation

**Usage:** Imported by game.py, not run directly

## How It Works

1. `game.py` initializes Pygame and shows the menu
2. User selects a level from the menu
3. `game.py` dynamically loads the selected map module from `../maps/`
4. The level runs with shared game state
5. When level ends, returns to menu or quits

## Adding New Features

To add a new menu option or game mode:
1. Modify `menu.py` to add the UI element
2. Update `game.py` to handle the new selection
3. Ensure proper module loading if it's a new level type
