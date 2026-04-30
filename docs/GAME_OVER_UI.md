# Game Over UI and Effects

## Overview

The Shadow Stalker game now features a polished **Game Over screen** with visual effects, animations, and sound. This provides a better user experience when the player is caught by the Shadow Stalker or loses all their health.

## Features

### Visual Effects
- **Screen Shake**: Intense shaking effect when game over triggers
- **Particle System**: Explosive particle effects in red/orange colors
- **Fade Transitions**: Smooth fade-in/fade-out animations
- **Glow Effects**: Pulsing glow around the "GAME OVER" title
- **Dark Overlay**: Dramatic darkening of the game screen

### Audio Effects
- **Game Over Voice**: Professional voice announcement "Game Over"
- **Death Impact**: Punch/hit sound effect for dramatic impact
- **Button Sounds**: Retro UI click and hover sounds

### Interactive Elements
- **Restart Button**: Quickly restart from the beginning
- **Main Menu Button**: Return to the main menu
- **Keyboard Shortcuts**:
  - `SPACE` or `ENTER`: Restart the game
  - `ESC`: Return to main menu

### Animations
- **Timed Reveal**: UI elements appear after a brief delay
- **Particle Spawning**: Continuous particle generation for dynamic visuals
- **Button Hover Effects**: Visual feedback on mouse hover

## Implementation Details

### File Structure
```
core/
├── game_over.py      # Main game over screen implementation
├── audio.py          # Updated with game over sound effects
└── game.py           # Integrated game over screen calls
```

### Key Components

#### 1. Particle System (`Particle` class)
- Creates explosion-like particle effects
- Each particle has:
  - Position and velocity
  - Color (red/orange variations)
  - Lifetime and fade-out
  - Size reduction over time

#### 2. GameOverScreen Class
Manages the entire game over experience:
- **Initialization**: Sets up fonts, buttons, and effects
- **Animation State**: Tracks fade, shake, and timing
- **Event Handling**: Processes input for restart/menu
- **Rendering**: Draws all visual elements with effects

#### 3. Sound Effects
Loaded from `assets/FreeSFX/` folder:
```python
'game_over': "Voices/Game Over.wav"          # Voice announcement
'death': "GameSFX/Impact/Retro Impact Punch Hurt 01.wav"  # Impact sound
'click': "GameSFX/Events/Retro Event UI StereoUP 01.wav"  # Button click
'hover': "GameSFX/Events/Retro Event UI 01.wav"           # Button hover
```

**Benefits:**
- Professional voice acting for major events
- Retro game aesthetic matches visual style
- High-quality WAV files
- Fallback system if files missing

## Usage

### In Core Game Engine (`core/game.py`)

The game over screen is automatically triggered when a level returns `"game_over"`:

```python
elif next_level_signal == "game_over":
    # Show game over screen
    result = show_game_over(screen, game_state)
    if result == "restart":
        # Reset and restart from beginning
        game_state["health"] = game_state["max_health"]
        game_state["score"] = 0
        current_level = "exclusion"
    else:
        # Return to menu
        current_level = "menu"
```

This is implemented for all four levels:
- Exclusion Zone
- Green Zone
- Industrial Zone
- Nature Adventure

### In Merged Game (`merged_game.py`)

The merged game also supports the new game over screen with fallback:

```python
if GAME_OVER_AVAILABLE:
    result = show_game_over(screen, game_state)
    if result == "restart":
        # Reset game state and respawn
        ...
    else:
        running = False
else:
    # Fallback to simple text overlay
    ...
```

### Standalone Testing

Test the game over screen independently:

```bash
python test_game_over.py
```

Or directly:
```python
from core.game_over import show_game_over

result = show_game_over(screen, game_state)
# Returns: "restart", "menu", or "quit"
```

## Customization

### Adjusting Effects

#### Screen Shake Intensity
In `core/game_over.py`, modify the `update_shake` method:
```python
intensity = 10 * (self.shake_timer / self.shake_duration)  # Change 10 to adjust
```

#### Particle Count
In the `spawn_particles` method:
```python
self.spawn_particles(50)  # Initial burst - change count
self.spawn_particles(5)   # Periodic spawn - change count
```

#### Fade Speed
In the `run` method:
```python
if self.fade_alpha < 255 and self.display_time < 0.5:
    self.fade_alpha = min(255, int(self.display_time * 510))  # Adjust multiplier
```

### Changing Colors

Modify the color choices in `spawn_particles`:
```python
color_choice = pygame.random.choice([
    (255, 50, 50),    # Red
    (255, 100, 50),   # Orange
    (255, 150, 100),  # Light orange
    (200, 50, 50),    # Dark red
])
```

### Button Styling

Buttons use the `MenuButton` class from `menu.py`. Customize in the `__init__` method:
```python
self.restart_btn = MenuButton(
    center_x - button_width - 10, 
    button_y_start, 
    button_width, 
    button_height, 
    "RESTART", 
    font_size=36  # Adjust font size
)
```

## Technical Notes

### Performance
- Particles are automatically cleaned up when their lifetime expires
- Screen shake uses simple offset calculations (minimal performance impact)
- Alpha blending is optimized using pygame's SRCALPHA surfaces

### Compatibility
- Works with both the modular game engine (`core/game.py`)
- Compatible with the merged game (`merged_game.py`)
- Graceful fallback if game over module fails to import

### State Management
- Game state is passed to the screen but not modified
- Score display is read-only
- Actual state reset happens in the calling code based on return value

## Future Enhancements

Potential improvements:
- [ ] Add statistics display (time survived, coins collected, etc.)
- [ ] Implement different game over messages based on death type
- [ ] Add achievement unlocks on game over
- [ ] Include screenshot capture of final moment
- [ ] Add slow-motion replay of death
- [ ] Implement shareable score cards
- [ ] Add more particle effect varieties
- [ ] Include background music transition

## Troubleshooting

### Game Over Screen Not Showing
1. Check that `core/game_over.py` exists
2. Verify imports in `core/game.py` or `merged_game.py`
3. Look for error messages in console about missing modules

### No Sound Effects
1. Check console for warnings about missing files
2. Verify FreeSFX folder exists at `assets/FreeSFX/`
3. Ensure pygame mixer is initialized
4. Check system volume settings

### Performance Issues
1. Reduce particle count in `spawn_particles()`
2. Decrease shake duration or intensity
3. Lower the frequency of periodic particle spawning

## Credits

Implemented as part of the Shadow Stalker game enhancement project. Uses:
- Pygame for rendering and audio
- Custom particle system for visual effects
- Procedurally generated sound effects
- Consistent UI styling with existing menu system
