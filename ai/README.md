# AI Systems

This directory contains AI and bot implementations for the game.

## Files

### [mask_dude_bot.py](mask_dude_bot.py)
AI Bot Character system featuring:
- Autonomous enemy bots that patrol and chase players
- Pathfinding and navigation logic
- Collision detection with map tiles
- Animation system for bot movement
- BotManager class to manage multiple bots

**Usage:** Imported by map modules that use bots (e.g., green_zone_map.py, build_demo_map.py)

## Features

- **Patrol Behavior**: Bots move back and forth on platforms
- **Chase Behavior**: Bots detect and pursue nearby players
- **Wall Detection**: Bots avoid falling off edges
- **Animation**: Sprite-based animation for bot movement
- **Scalable**: Easy to add more bots or modify behavior

## Integration

Maps can use the bot system by:
```python
from mask_dude_bot import MaskDudeBot, BotManager

# Initialize bot manager
bot_manager = BotManager(TILE_SIZE, MAP_LAYOUT, SOLID_TILES)

# Add bots at specific positions
bot_manager.add_bot(x, y)

# Set player as target
bot_manager.set_target(player)

# Update in game loop
bot_manager.update(dt, map_height)

# Check collisions
hit_bot = bot_manager.check_player_collision(player.rect)
```

## Extending

To create new AI behaviors:
1. Extend the `MaskDudeBot` class
2. Override update methods for custom behavior
3. Add new states (e.g., attack, defend, hide)
4. Integrate with your map module
