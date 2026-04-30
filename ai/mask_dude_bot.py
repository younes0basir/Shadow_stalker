"""
mask_dude_bot.py - AI Bot Character (MaskDude)
=============================================================
An AI-controlled character that chases the player.
Uses MaskDude assets and implements pursuit behavior.
"""

import os
import pygame
import math

# Paths
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
MASK_DUDE_PATH = os.path.join(PARENT_DIR, "assets", "MainCharacters", "MaskDude")

# Physics constants for bot (matching player capabilities)
BOT_SPEED = 180       # Slower than player (220-280) for "not too hard"
BOT_JUMP_FORCE = -420  # Slightly lower jump
BOT_GRAVITY = 1200
BOT_DETECTION_RANGE = 500  # Pixels - how far bot can "see" player
BOT_JUMP_REACH = 80   # Pixels - gap size bot will attempt to jump


def load_spritesheet(path, f_width, f_height, scale=1):
    """Load animation frames from a spritesheet."""
    try:
        sheet = pygame.image.load(path)
        if pygame.display.get_surface():
            sheet = sheet.convert_alpha()
        frames = []
        for x in range(0, sheet.get_width(), f_width):
            rect = pygame.Rect(x, 0, f_width, f_height)
            surf = sheet.subsurface(rect).copy()
            if scale != 1:
                surf = pygame.transform.scale(surf, (int(f_width * scale), int(f_height * scale)))
            frames.append(surf)
        return frames
    except Exception:
        # Return pink placeholder if loading fails
        s = pygame.Surface((int(f_width * scale), int(f_height * scale)), pygame.SRCALPHA)
        s.fill((255, 0, 255))
        return [s]


class MaskDudeBot:
    """AI Bot that chases the player through the level."""
    
    def __init__(self, x, y, tile_size=32, map_layout=None, solid_tiles=None):
        # Position and physics
        self.x = float(x)
        self.y = float(y)
        self.tile_size = tile_size
        self.map_layout = map_layout
        self.solid_tiles = solid_tiles or set()
        
        # Animation
        self.anims = {}
        self.state = 'idle'
        self.frame_idx = 0
        self.anim_timer = 0
        self.load_animations()
        
        self.facing_right = True
        
        # Hitbox (slightly smaller than visual)
        scale = 1.5
        self.rect = pygame.Rect(x, y, 16 * scale, 24 * scale)
        
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.jump_count = 0
        
        # AI state
        self.target = None  # Player to chase
        self.ai_state = 'idle'  # idle, chase, patrol, lost
        self.patrol_direction = 1  # 1 = right, -1 = left
        self.last_seen_player_pos = None
        self.search_timer = 0
        self.jump_cooldown = 0
        
        # Wall slide/jump state (matching player)
        self.on_wall_l = False
        self.on_wall_r = False
        self.wall_slide = False
        self.wall_cd = 0.0
        
        # Animation timer
        self.anim_timer = 0
        
    def set_target(self, player):
        """Set the player as chase target."""
        self.target = player
        
    def load_animations(self):
        scale = 1.5
        for s in ('idle', 'run', 'jump', 'fall', 'double_jump', 'hit', 'wall_jump'):
            p = os.path.join(MASK_DUDE_PATH, f"{s}.png")
            if os.path.exists(p):
                sheet = pygame.image.load(p).convert_alpha()
                frames = []
                fw = 32
                for x in range(0, sheet.get_width(), fw):
                    s_surf = pygame.Surface((fw, fw), pygame.SRCALPHA)
                    s_surf.blit(sheet, (0, 0), (x, 0, fw, fw))
                    s_surf = pygame.transform.scale(s_surf, (int(fw*scale), int(fw*scale)))
                    # Tint red to distinguish from player
                    tint = pygame.Surface(s_surf.get_size(), pygame.SRCALPHA)
                    tint.fill((255, 50, 50, 100)) # Stronger red stalker tint
                    s_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    frames.append(s_surf)
                self.anims[s] = frames
        
    def get_collisions(self):
        """Check collision with solid tiles."""
        if not self.map_layout:
            return []
            
        hits = []
        start_col = max(0, int(self.rect.left // self.tile_size))
        start_row = max(0, int(self.rect.top // self.tile_size))
        end_row = min(len(self.map_layout)-1, int((self.rect.bottom - 1) // self.tile_size))
        
        for row in range(start_row, end_row + 1):
            # Get the actual length of this row (rows may vary in length)
            row_len = len(self.map_layout[row])
            end_col = min(row_len - 1, int((self.rect.right - 1) // self.tile_size))
            
            for col in range(start_col, end_col + 1):
                if 0 <= col < row_len:
                    if self.map_layout[row][col] in self.solid_tiles:
                        hits.append(pygame.Rect(
                            col * self.tile_size, 
                            row * self.tile_size, 
                            self.tile_size, 
                            self.tile_size
                        ))
        return hits
    
    def can_see_player(self):
        """Check if bot has line of sight to player."""
        if not self.target:
            return False
            
        # Distance check
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > BOT_DETECTION_RANGE:
            return False
            
        # Simple line of sight - could be improved with raycasting
        return True
    
    def check_gap_ahead(self, direction, tile_check_distance=2):
        """Check if there's a gap in the floor ahead."""
        if not self.map_layout:
            return False
            
        # Check tiles ahead in movement direction
        check_x = self.rect.centerx + (direction * self.tile_size * tile_check_distance)
        check_y = self.rect.bottom + self.tile_size  # One tile below feet
        
        col = int(check_x // self.tile_size)
        row = int(check_y // self.tile_size)
        
        if 0 <= row < len(self.map_layout):
            row_len = len(self.map_layout[row])
            if 0 <= col < row_len:
                tile = self.map_layout[row][col]
                # Gap detected if no solid tile below
                return tile not in self.solid_tiles
        # If out of bounds, treat as gap (don't jump off map)
        return True
    
    def check_wall_ahead(self, direction, distance=20):
        """Check if there's a wall ahead."""
        test_rect = self.rect.copy()
        test_rect.x += direction * distance
        
        start_col = max(0, int(test_rect.left // self.tile_size))
        start_row = max(0, int(test_rect.top // self.tile_size))
        end_row = min(len(self.map_layout)-1, int((test_rect.bottom - 1) // self.tile_size))
        
        for row in range(start_row, end_row + 1):
            row_len = len(self.map_layout[row])
            end_col = min(row_len - 1, int((test_rect.right - 1) // self.tile_size))
            
            for col in range(start_col, end_col + 1):
                if 0 <= col < row_len and self.map_layout[row][col] in self.solid_tiles:
                    tile_rect = pygame.Rect(
                        col * self.tile_size, 
                        row * self.tile_size, 
                        self.tile_size, 
                        self.tile_size
                    )
                    if test_rect.colliderect(tile_rect):
                        return True
        return False
    
    def check_wall(self, direction):
        """Check if player is touching a wall on the specified side (left/right)."""
        # Temporarily move rect to check for collision
        offset = 2  # Small buffer for wall detection
        test_rect = self.rect.copy()
        if direction == 'left':
            test_rect.x -= offset
        else:
            test_rect.x += offset
            
        start_col = max(0, int(test_rect.left // self.tile_size))
        start_row = max(0, int(test_rect.top // self.tile_size))
        end_row = min(len(self.map_layout)-1, int((test_rect.bottom - 1) // self.tile_size))
        
        for row in range(start_row, end_row + 1):
            row_len = len(self.map_layout[row])
            end_col = min(row_len - 1, int((test_rect.right - 1) // self.tile_size))
            
            for col in range(start_col, end_col + 1):
                if 0 <= col < row_len and self.map_layout[row][col] in self.solid_tiles:
                    tile_rect = pygame.Rect(col*self.tile_size, row*self.tile_size, self.tile_size, self.tile_size)
                    if test_rect.colliderect(tile_rect):
                        return True
        return False
    
    def jump(self):
        """Make the bot jump (supports wall jump like player)."""
        # Wall jump left
        if self.on_wall_l and not self.on_ground:
            self.vy = BOT_JUMP_FORCE
            self.vx = BOT_SPEED * 1.2
            self.wall_cd = 0.15
            self.facing_right = True
            self.jump_count = 1
            self.on_ground = False
            return
        # Wall jump right
        if self.on_wall_r and not self.on_ground:
            self.vy = BOT_JUMP_FORCE
            self.vx = -BOT_SPEED * 1.2
            self.wall_cd = 0.15
            self.facing_right = False
            self.jump_count = 1
            self.on_ground = False
            return
        # Normal / double jump
        if self.jump_count < 2 and self.jump_cooldown <= 0:
            self.vy = BOT_JUMP_FORCE
            self.jump_count += 1
            self.on_ground = False
            self.jump_cooldown = 0.3
            
    def update_ai(self, dt):
        """AI decision making - determine movement direction and actions."""
        if not self.target:
            self.ai_state = 'idle'
            self.vx = 0
            return
            
        can_see = self.can_see_player()
        
        if can_see:
            # Chase mode!
            self.ai_state = 'chase'
            self.last_seen_player_pos = (self.target.rect.centerx, self.target.rect.centery)
            self.search_timer = 3.0  # Search for 3 seconds after losing sight
            
            # Determine direction to player
            dx = self.target.rect.centerx - self.rect.centerx
            
            if abs(dx) > 20:  # Don't micro-adjust
                direction = 1 if dx > 0 else -1
                self.vx = direction * BOT_SPEED
                self.facing_right = direction > 0
            else:
                self.vx = 0
                
            # Jump logic - jump over gaps or up to platforms
            if self.on_ground:
                # Jump if gap ahead
                direction = 1 if self.vx > 0 else -1 if self.vx < 0 else (1 if self.facing_right else -1)
                if direction != 0 and self.check_gap_ahead(direction):
                    self.jump()
                        
                # Jump if wall ahead and player is above or on other side
                if self.check_wall_ahead(direction):
                    if self.target.rect.y < self.rect.y - 30:
                        self.jump()
                    elif self.target.rect.y < self.rect.y - 80 and self.jump_count < 2:
                        self.jump()
            elif self.wall_slide:
                # Wall sliding - jump off wall toward player
                if self.target.rect.y < self.rect.y - 20:
                    self.jump()
                elif self.on_wall_l and self.target.rect.centerx > self.rect.centerx:
                    self.jump()
                elif self.on_wall_r and self.target.rect.centerx < self.rect.centerx:
                    self.jump()
            elif not self.on_ground and self.vy > 0:
                # Falling - double jump if player is above
                if self.target.rect.y < self.rect.y - 80 and self.jump_count < 2:
                    self.jump()
                        
        elif self.search_timer > 0:
            # Search mode - go to last known position
            self.ai_state = 'search'
            self.search_timer -= dt
            
            if self.last_seen_player_pos:
                dx = self.last_seen_player_pos[0] - self.rect.centerx
                if abs(dx) > 30:
                    direction = 1 if dx > 0 else -1
                    self.vx = direction * BOT_SPEED * 0.7  # Slower when searching
                    self.facing_right = direction > 0
                else:
                    self.vx = 0
                    self.last_seen_player_pos = None  # Reached last known position
            else:
                self.vx = 0
                
        else:
            # Patrol mode - walk back and forth
            self.ai_state = 'patrol'
            
            # Check for obstacles
            if self.check_wall_ahead(self.patrol_direction) or self.check_gap_ahead(self.patrol_direction):
                self.patrol_direction *= -1  # Turn around
                
            self.vx = self.patrol_direction * BOT_SPEED * 0.5
            self.facing_right = self.patrol_direction > 0
    
    def update(self, dt, map_h):
        """Update bot physics and AI."""
        # Update AI decisions
        self.update_ai(dt)
        
        # Update cooldowns
        if self.jump_cooldown > 0:
            self.jump_cooldown -= dt
        if self.wall_cd > 0:
            self.wall_cd = max(0, self.wall_cd - dt)
            
        # Wall detection (only when airborne and not in wall jump cooldown)
        if not self.on_ground and self.wall_cd <= 0:
            self.on_wall_l = self.check_wall('left')
            self.on_wall_r = self.check_wall('right')
            self.wall_slide = (self.on_wall_l or self.on_wall_r) and self.vy > 0
        else:
            self.on_wall_l = self.on_wall_r = self.wall_slide = False
        
        # Gravity (reduced when wall sliding, matching player)
        if self.wall_slide:
            self.vy += BOT_GRAVITY * 0.3 * dt
            self.vy = min(self.vy, 150)
        else:
            self.vy += BOT_GRAVITY * dt
        
        # Move X & resolve collisions
        self.x += self.vx * dt
        self.rect.x = int(self.x)
        hits = self.get_collisions()
        for hit in hits:
            if self.vx > 0:
                self.rect.right = hit.left
                self.x = float(self.rect.x)
            elif self.vx < 0:
                self.rect.left = hit.right
                self.x = float(self.rect.x)
        
        # Move Y & resolve collisions
        self.y += self.vy * dt
        self.rect.y = int(self.y)
        
        hits = self.get_collisions()
        for hit in hits:
            if self.vy > 0:
                self.rect.bottom = hit.top
                self.y = float(self.rect.y)
                self.vy = 0
                self.on_ground = True
                self.jump_count = 0
            elif self.vy < 0:
                self.rect.top = hit.bottom
                self.y = float(self.rect.y)
                self.vy = 0
        
        # Ground check probe
        if not hits:
            self.rect.y += 1
            ground_hits = self.get_collisions()
            self.rect.y -= 1
            if len(ground_hits) > 0 and self.vy >= 0:
                self.on_ground = True
                self.jump_count = 0
            else:
                self.on_ground = False
        
        # Update animation state
        self.update_animation_state()
        
        # Animation frame progression
        self.anim_timer += dt
        if self.anim_timer >= 0.1:  # 10 fps animation
            self.anim_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.anims[self.state])
        
        # Respawn near player if fell off map (chasing game: stalker always returns)
        if self.rect.y > map_h:
            if self.target:
                # Spawn behind the player so chase continues
                offset = -200 if self.target.facing_right else 200
                self.x = float(self.target.rect.centerx + offset)
                self.y = float(self.target.rect.y - 100)
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
            else:
                self.x = 100.0
                self.y = 100.0
                self.rect.x = 100
                self.rect.y = 100
            self.vx = 0
            self.vy = 0
            
    def update_animation_state(self):
        """Update visual animation state based on physics."""
        new_state = self.state
        
        if not self.on_ground:
            if self.vy < 0:
                if self.jump_count == 2:
                    new_state = 'double_jump'
                else:
                    new_state = 'jump'
            else:
                new_state = 'fall'
        elif self.vx != 0:
            new_state = 'run'
        else:
            new_state = 'idle'
            
        if self.state != new_state:
            self.state = new_state
            self.frame_idx = 0
    
    def draw(self, surface, scroll_x, scroll_y):
        """Draw the bot on screen."""
        # Get current animation frame
        frames = self.anims.get(self.state, self.anims['idle'])
        if frames:
            frame = frames[self.frame_idx % len(frames)]
            
            # Flip if facing left
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)
                
            # Calculate screen position
            screen_x = self.rect.x - scroll_x
            screen_y = self.rect.y - scroll_y
            
            # Draw the sprite
            surface.blit(frame, (screen_x, screen_y))
            
            # Debug: draw AI state above head
            # font = pygame.font.Font(None, 20)
            # text = font.render(self.ai_state, True, (255, 0, 0))
            # surface.blit(text, (screen_x, screen_y - 20))
    
    def get_rect(self):
        """Get collision rectangle."""
        return self.rect


# ═════════════════════════════════════════════════════════════
#  BOT MANAGER - Handle multiple bots
# ═════════════════════════════════════════════════════════════

class BotManager:
    """Manages multiple AI bots in a level."""
    
    def __init__(self, tile_size=32, map_layout=None, solid_tiles=None):
        self.bots = []
        self.tile_size = tile_size
        self.map_layout = map_layout
        self.solid_tiles = solid_tiles
        
    def add_bot(self, x, y):
        """Add a new bot at position."""
        bot = MaskDudeBot(x, y, self.tile_size, self.map_layout, self.solid_tiles)
        self.bots.append(bot)
        return bot
        
    def set_target(self, player):
        """Set chase target for all bots."""
        for bot in self.bots:
            bot.set_target(player)
            
    def update(self, dt, map_h):
        """Update all bots."""
        for bot in self.bots:
            bot.update(dt, map_h)
            
    def draw(self, surface, scroll_x, scroll_y):
        """Draw all bots."""
        for bot in self.bots:
            bot.draw(surface, scroll_x, scroll_y)
            
    def check_player_collision(self, player_rect):
        """Check if any bot touches the player."""
        for bot in self.bots:
            if bot.rect.colliderect(player_rect):
                return bot
        return None
        
    def get_bots(self):
        """Get list of all bots."""
        return self.bots


# ═════════════════════════════════════════════════════════════
#  TEST / DEBUG
# ═════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("MaskDude Bot Test")
    clock = pygame.time.Clock()
    
    # Simple test map
    test_map = [
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "G                              G",
        "G                              G",
        "G                              G",
        "G                              G",
        "G      GGGG       GGGG         G",
        "G              GG              G",
        "G     G                 G      G",
        "G                              G",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    ]
    
    solid = set('G')
    tile_size = 32
    
    # Create bot
    bot = MaskDudeBot(200, 100, tile_size, test_map, solid)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bot.jump()
                    
        keys = pygame.key.get_pressed()
        
        # Manual control for testing
        if keys[pygame.K_LEFT]:
            bot.vx = -BOT_SPEED
            bot.facing_right = False
        elif keys[pygame.K_RIGHT]:
            bot.vx = BOT_SPEED
            bot.facing_right = True
        else:
            bot.vx = 0
            
        bot.update(dt, 1000)
        
        # Draw
        screen.fill((50, 50, 70))
        
        # Draw map
        for row_idx, row in enumerate(test_map):
            for col_idx, char in enumerate(row):
                if char in solid:
                    rect = pygame.Rect(col_idx * tile_size, row_idx * tile_size, tile_size, tile_size)
                    pygame.draw.rect(screen, (100, 100, 100), rect)
                    
        # Draw bot
        bot.draw(screen, 0, 0)
        
        # Draw info
        font = pygame.font.Font(None, 24)
        info_text = f"State: {bot.state} | On Ground: {bot.on_ground} | AI: {bot.ai_state}"
        text = font.render(info_text, True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        
    pygame.quit()
