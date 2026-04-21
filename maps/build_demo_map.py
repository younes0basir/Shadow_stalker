import os
import sys
import pygame
import random

# Add parent directory and ai directory to path for imports
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
sys.path.insert(0, PARENT_DIR)
sys.path.insert(0, os.path.join(PARENT_DIR, "ai"))

# Bot spawning handled by merged_game.py - disabled in individual map files

# Paths
ROOT = os.path.dirname(__file__)

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_W = 1280
SCREEN_H = 720
TILE_SIZE = 32

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
else:
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    else:
        SCREEN_W, SCREEN_H = screen.get_size()
pygame.display.set_caption("Exclusion Zone Dungeon - Platformer Test")

# Map of tile symbols
TILE_MAPPING = {
    '1': "Tile_01.png", '2': "Tile_02.png", '3': "Tile_03.png",
    '4': "Tile_11.png", '5': "Tile_12.png", '6': "Tile_13.png",
    '7': "Tile_21.png", '8': "Tile_22.png", '9': "Tile_23.png",
    'T': "Tile_32.png", 'L': "Tile_31.png", 'R': "Tile_33.png",
    'B': "Tile_49.png", 'c': "Tile_50.png", '<': "Tile_55.png",
    '>': "Tile_56.png", '/': "Tile_42.png", '\\':"Tile_44.png",
    'X': "Tile_77.png",
    'W': "Tile_22.png",
}

SOLID_TILES = set('123456789TLR<>/\\BcW')
MAP_LAYOUT = [
    "W" * 70,
    "W" + " " * 68 + "W",
    "W" + " " * 68 + "W",
    "W" + " " * 68 + "W",
    "W" + " " * 68 + "W",
    "W" + " " * 68 + "W",
    "W" + " " * 68 + "W",
    "W" + " " * 68 + "W",
    "W" + " " * 68 + "W",
    "W" + " " * 68 + "W",
    "W" + " " * 68 + "W",
    "W" + "1" + "2" * 66 + "3" + "W",
    "W" + "4" + "5" * 66 + "6" + "W",
    "W" + "4" + "5" * 66 + "6" + "W",
    "W" * 70,
]

# Paths
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
base_path = os.path.join(PARENT_DIR, "assets", "craftpix-net-115897-free-exclusion-zone-tileset-pixel-art")
player_path = os.path.join(PARENT_DIR, "assets", "MainCharacters", "VirtualGuy")

def load_image(path, scale=1):
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale != 1:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
        return img
    except Exception as e:
        return pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

def load_spritesheet(path, f_width, f_height, scale=1):
    try:
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for x in range(0, sheet.get_width(), f_width):
            surface = pygame.Surface((f_width, f_height), pygame.SRCALPHA)
            surface.blit(sheet, (0, 0), (x, 0, f_width, f_height))
            if scale != 1:
                surface = pygame.transform.scale(surface, (int(f_width*scale), int(f_height*scale)))
            frames.append(surface)
        return frames
    except Exception as e:
        # Fallback surface
        s = pygame.Surface((int(f_width * scale), int(f_height * scale)), pygame.SRCALPHA)
        s.fill((255, 0, 0))
        return [s]

loaded_tiles = {}
for symbol, filename in TILE_MAPPING.items():
    path = os.path.join(base_path, "1 Tiles", filename)
    loaded_tiles[symbol] = load_image(path)

# Fallback
if '1' not in loaded_tiles or loaded_tiles['1'].get_width() == 0:
    s = pygame.Surface((TILE_SIZE, TILE_SIZE))
    s.fill((100,200,100))
    loaded_tiles['1'] = s

bg_layers = []
bg_dir = os.path.join(base_path, "2 Background", "Night")
for i in range(1, 6):
    bg_path = os.path.join(bg_dir, f"{i}.png")
    bg_img = load_image(bg_path)
    if bg_img.get_width() > 0:
        bg_img = pygame.transform.scale(bg_img, (SCREEN_W, SCREEN_H))
        bg_layers.append(bg_img)

# Decorations
trees = [load_image(os.path.join(base_path, "3 Objects", "Trees", f"{i}.png")) for i in range(1, 4)]
boxes = [load_image(os.path.join(base_path, "3 Objects", "Other", f"Box{i}.png")) for i in range(1, 5)]
pointers = [load_image(os.path.join(base_path, "3 Objects", "Other", f"Pointer{i}.png")) for i in range(1, 4)]
chest_frames = load_spritesheet(os.path.join(base_path, "4 Animated objects", "Chest.png"), 32, 32, scale=1.0)
grass_imgs = [load_image(os.path.join(base_path, "3 Objects", "Grass", f"{i}.png")) for i in range(1, 8)]
stone_imgs = [load_image(os.path.join(base_path, "3 Objects", "Stones", f"{i}.png")) for i in range(1, 6)]

decorations = [] 
for r_idx, row in enumerate(MAP_LAYOUT):
    for c_idx, symbol in enumerate(row):
        if symbol in ('1', '2', '3', 'T'):
            if random.random() < 0.5:
                img = random.choice(grass_imgs)
                if img.get_width() > 0:
                    max_offset = max(0, TILE_SIZE - img.get_width())
                    x = c_idx * TILE_SIZE + random.randint(0, max_offset)
                    y = r_idx * TILE_SIZE - img.get_height() + 4
                    decorations.append((img, x, y))
            elif random.random() < 0.2:
                img = random.choice(stone_imgs)
                if img.get_width() > 0:
                    max_offset = max(0, TILE_SIZE - img.get_width() // 2)
                    x = c_idx * TILE_SIZE + random.randint(0, max_offset)
                    y = r_idx * TILE_SIZE - img.get_height() + 2
                    decorations.append((img, x, y))

EXPLICIT_OBJS = [
    (trees[0], 5, 11), (trees[1], 15, 11), (trees[2], 25, 11),
    (boxes[0], 10, 11), (boxes[1], 12, 11), (boxes[2], 35, 11),
    (pointers[0], 20, 11), (pointers[1], 40, 11),
]
for obj_img, col, row in EXPLICIT_OBJS:
    if obj_img and obj_img.get_width() > 0:
        ox = col * TILE_SIZE
        oy = row * TILE_SIZE - obj_img.get_height()
        decorations.append((obj_img, ox, oy))

# Chest positions for simple layout
CHEST_COORDS = [
    (8, 10),
    (30, 10),
    (50, 10),
]

# ── Player Class ──────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        # Load animations
        scale = 1.5
        self.anims = {
            'idle': load_spritesheet(os.path.join(player_path, "idle.png"), 32, 32, scale),
            'run': load_spritesheet(os.path.join(player_path, "run.png"), 32, 32, scale),
            'jump': load_spritesheet(os.path.join(player_path, "jump.png"), 32, 32, scale),
            'double_jump': load_spritesheet(os.path.join(player_path, "double_jump.png"), 32, 32, scale),
            'fall': load_spritesheet(os.path.join(player_path, "fall.png"), 32, 32, scale),
        }
        
        self.state = 'idle'
        self.frame_idx = 0
        self.facing_right = True
        
        # Float tracking for precise DT physics
        self.x = float(x)
        self.y = float(y)
        
        # Hitbox (slightly smaller width to prevent wall snagging)
        self.rect = pygame.Rect(x, y, 16 * scale, 24 * scale)
        
        self.vx = 0
        self.vy = 0
        self.speed = 250   # px per sec
        self.jump_force = -450
        self.gravity = 1200
        
        self.on_ground = False
        self.jump_count = 0
        
        # Wall jump tracking
        self.on_wall_left = False
        self.on_wall_right = False
        self.wall_slide = False
        self.wall_jump_cooldown = 0  # Prevents immediate re-sticking to wall

    def check_wall(self, direction):
        """Check if player is touching a wall on the specified side (left/right)."""
        # Temporarily move rect to check for collision
        offset = 2  # Small buffer for wall detection
        test_rect = self.rect.copy()
        if direction == 'left':
            test_rect.x -= offset
        else:
            test_rect.x += offset
            
        start_col = max(0, int(test_rect.left // TILE_SIZE))
        start_row = max(0, int(test_rect.top // TILE_SIZE))
        end_row = min(len(MAP_LAYOUT)-1, int((test_rect.bottom - 1) // TILE_SIZE))
        
        for row in range(start_row, end_row + 1):
            row_len = len(MAP_LAYOUT[row])
            end_col = min(row_len - 1, int((test_rect.right - 1) // TILE_SIZE))
            
            for col in range(start_col, end_col + 1):
                if 0 <= col < row_len and MAP_LAYOUT[row][col] in SOLID_TILES:
                    tile_rect = pygame.Rect(col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if test_rect.colliderect(tile_rect):
                        return True
        return False

    def get_collisions(self):
        hits = []
        # Subtracting 1px from right/bottom boundary checks prevents colliding with
        # adjacent tiles that aren't actually overlapping the internal area
        start_col = max(0, int(self.rect.left // TILE_SIZE))
        start_row = max(0, int(self.rect.top // TILE_SIZE))
        end_row = min(len(MAP_LAYOUT)-1, int((self.rect.bottom - 1) // TILE_SIZE))
        
        for row in range(start_row, end_row + 1):
            # Each row may have different length - check per row
            row_len = len(MAP_LAYOUT[row])
            end_col = min(row_len - 1, int((self.rect.right - 1) // TILE_SIZE))
            
            for col in range(start_col, end_col + 1):
                if 0 <= col < row_len and MAP_LAYOUT[row][col] in SOLID_TILES:
                    hits.append(pygame.Rect(col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return hits

    def jump(self):
        # Check for wall jump first (priority over regular jump)
        if self.on_wall_left and not self.on_ground:
            # Wall jump to the right
            self.vy = self.jump_force
            self.vx = self.speed * 1.2  # Push away from wall
            self.wall_jump_cooldown = 0.15  # Brief cooldown
            self.facing_right = True
            self.frame_idx = 0
            return
        elif self.on_wall_right and not self.on_ground:
            # Wall jump to the left
            self.vy = self.jump_force
            self.vx = -self.speed * 1.2  # Push away from wall
            self.wall_jump_cooldown = 0.15  # Brief cooldown
            self.facing_right = False
            self.frame_idx = 0
            return
        
        # Regular jump (ground or air)
        if self.jump_count < 2:
            self.vy = self.jump_force
            self.jump_count += 1
            self.on_ground = False
            self.frame_idx = 0  # reset animation

    def update_state(self):
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

    def update(self, dt, map_h):
        keys = pygame.key.get_pressed()
        
        # Horizontal Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.facing_right = True
        else:
            self.vx = 0

        # Wall detection (only when not on ground)
        if not self.on_ground and self.wall_jump_cooldown <= 0:
            self.on_wall_left = self.check_wall('left')
            self.on_wall_right = self.check_wall('right')
            # Enable wall slide when touching wall and falling
            self.wall_slide = (self.on_wall_left or self.on_wall_right) and self.vy > 0
        else:
            self.on_wall_left = False
            self.on_wall_right = False
            self.wall_slide = False
        
        # Decrease wall jump cooldown
        if self.wall_jump_cooldown > 0:
            self.wall_jump_cooldown = max(0, self.wall_jump_cooldown - dt)
        
        # Gravity (reduced when wall sliding for better control)
        if self.wall_slide:
            self.vy += self.gravity * 0.3 * dt  # Slower fall on wall
            # Cap wall slide speed
            self.vy = min(self.vy, 150)
        else:
            self.vy += self.gravity * dt
        
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
                # Cancel wall detection if we moved away from wall
                if self.on_wall_left:
                    self.on_wall_left = False
        
        # Move Y & resolve collisions
        self.y += self.vy * dt
        self.rect.y = int(self.y)
        
        hits = self.get_collisions()
        for hit in hits:
            if self.vy > 0:
                self.rect.bottom = hit.top
                self.y = float(self.rect.y)
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = hit.bottom
                self.y = float(self.rect.y)
                self.vy = 0

        # Robust ground check using a 1-pixel downward probe
        self.rect.y += 1
        ground_hits = self.get_collisions()
        self.rect.y -= 1
        
        if len(ground_hits) > 0 and self.vy >= 0:
            self.on_ground = True
            self.jump_count = 0  # Restored jump
        else:
            self.on_ground = False

        # Visual state logic
        self.update_state()

        # Safety catch if falling out of map elsewhere
        if self.rect.y > map_h:
            self.y = 0.0
            self.vy = 0
            self.x = float(5 * TILE_SIZE)

        # Animation frame progression
        # Run slower for idle, faster for running
        anim_speed = 20 if self.state == 'run' else 12 
        self.frame_idx += anim_speed * dt
        
    def draw(self, surface, scroll_x, scroll_y):
        frames = self.anims[self.state]
        if not frames:
            return
            
        # Loop animation or cap for jump frames
        if self.state in ('jump', 'fall', 'double_jump'):
            idx = min(int(self.frame_idx), len(frames) - 1)
        else:
            idx = int(self.frame_idx) % len(frames)
            
        img = frames[idx]
        
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
            
        # Center the sprite render horizontally on hitbox, bottom aligned
        blit_x = self.rect.centerx - img.get_width() // 2 - scroll_x
        blit_y = self.rect.bottom - img.get_height() - scroll_y
        
        surface.blit(img, (blit_x, blit_y))


def draw_hud(surface, game_state, player):
    """Draw a glassmorphism HUD showing shared health, score, and level name."""
    # Try to load font each time is wasteful; cache it
    try:
        font_hud = pygame.font.SysFont("segoeui", 18, bold=True)
        font_sm  = pygame.font.SysFont("consolas", 13)
    except Exception:
        font_hud = font_sm = pygame.font.Font(None, 20)

    # ── Health panel (top-left) ──
    panel_w, panel_h = 160, 50
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (10, 30, 35, 200), (0, 0, panel_w, panel_h), border_radius=10)
    pygame.draw.rect(panel, (50, 150, 200, 80), (0, 0, panel_w, panel_h), 2, border_radius=10)
    surface.blit(panel, (10, 10))

    # Health orbs
    for i in range(game_state["max_health"]):
        cx = 28 + i * 34
        cy = 35
        filled = i < game_state["health"]
        if filled:
            gc = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(gc, (80, 220, 160, 60), (15, 15), 15)
            surface.blit(gc, (cx - 15, cy - 15))
        col_ring = (60, 180, 160) if filled else (30, 90, 80)
        col_fill = (60, 200, 140) if filled else (20, 55, 50)
        pygame.draw.circle(surface, col_ring, (cx, cy), 13, 2)
        pygame.draw.circle(surface, col_fill, (cx, cy), 10)
        if filled:
            pygame.draw.circle(surface, (180, 255, 220), (cx - 4, cy - 4), 4)

    # ── Score panel (top-right) ──
    score_w = 160
    sp = pygame.Surface((score_w, 44), pygame.SRCALPHA)
    pygame.draw.rect(sp, (10, 30, 35, 200), (0, 0, score_w, 44), border_radius=10)
    pygame.draw.rect(sp, (50, 150, 200, 80), (0, 0, score_w, 44), 2, border_radius=10)
    surface.blit(sp, (SCREEN_W - score_w - 10, 10))

    score_lbl = font_hud.render(f"SCORE  {game_state['score']}", True, (255, 210, 80))
    surface.blit(score_lbl, (SCREEN_W - score_w + 2, 22))

    # ── Level name (top-center) ──
    lvl = font_sm.render("EXCLUSION ZONE", True, (100, 180, 160))
    surface.blit(lvl, (SCREEN_W // 2 - lvl.get_width() // 2, 8))

    # ── Controls / UX Shortcuts (bottom-left) ──
    controls = [
        ("[A] [D] / [<] [>]", "Move"),
        ("[SPACE] / [W] / [^]", "Double Jump"),
        ("[ESC]", "Quit Game")
    ]
    
    pad_y = SCREEN_H - 20 - (len(controls) * 20)
    for idx, (keys, action) in enumerate(controls):
        key_lbl = font_sm.render(keys, True, (200, 220, 255))
        act_lbl = font_sm.render(action, True, (120, 140, 160))
        surface.blit(key_lbl, (20, pad_y + idx * 20))
        surface.blit(act_lbl, (150, pad_y + idx * 20))


def draw_minimap(surface, player, scroll_x, scroll_y, map_width, map_height):
    # Map scale: 3 pixels per 32px tile (approx size 180x102 px)
    scale = 3
    mm_w = max(len(row) for row in MAP_LAYOUT) * scale
    mm_h = len(MAP_LAYOUT) * scale
    
    # Place bottom right corner
    mm_x = SCREEN_W - mm_w - 20
    mm_y = SCREEN_H - mm_h - 20
    
    # Draw dark glass background
    mm_bg = pygame.Surface((mm_w + 4, mm_h + 4), pygame.SRCALPHA)
    pygame.draw.rect(mm_bg, (5, 15, 25, 220), (0,0, mm_w+4, mm_h+4), border_radius=5)
    pygame.draw.rect(mm_bg, (50, 150, 200, 120), (0,0, mm_w+4, mm_h+4), 1, border_radius=5)
    surface.blit(mm_bg, (mm_x - 2, mm_y - 2))
    
    # Draw map schema blocks
    for r, row in enumerate(MAP_LAYOUT):
        for c, char in enumerate(row):
            if char != ' ':
                # Make dirt solid, grass green-ish
                color = (40, 100, 40) if char in ('1', '2', '3') else (80, 80, 90)
                pygame.draw.rect(surface, color, (mm_x + c * scale, mm_y + r * scale, scale, scale))
                
    # Draw player dot
    px = int((player.x / TILE_SIZE) * scale)
    py = int((player.y / TILE_SIZE) * scale)
    pygame.draw.rect(surface, (255, 215, 0), (mm_x + px - 1, mm_y + py - 1, 4, 4))
    
    # Draw camera view outline 
    cam_w = int((SCREEN_W / TILE_SIZE) * scale)
    cam_h = int((SCREEN_H / TILE_SIZE) * scale)
    cx = int((scroll_x / TILE_SIZE) * scale)
    cy = int((scroll_y / TILE_SIZE) * scale)
    pygame.draw.rect(surface, (255, 255, 255), (mm_x + cx, mm_y + cy, cam_w, cam_h), 1)

# Map dimensions
map_width = max(len(row) for row in MAP_LAYOUT) * TILE_SIZE
map_height = len(MAP_LAYOUT) * TILE_SIZE

def run_level(surface, game_state=None):
    global SCREEN_W, SCREEN_H, bg_layers
    
    if game_state is None:
        game_state = {"health": 3, "max_health": 3, "score": 0, "lives": 3}
    
    player = Player(120, 96)

    clock = pygame.time.Clock()
    frame_time = 0
    scroll_x = 0
    scroll_y = 0
    
    run = True
    while run:
        dt = clock.tick(60) / 1000.0
        frame_time += dt

        chest_idx = int(frame_time * 2) % len(chest_frames) if chest_frames else 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    player.jump()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = event.w, event.h
                surface = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
                for i in range(len(bg_layers)):
                    bg_path = os.path.join(bg_dir, f"{i+1}.png")
                    bg_img = load_image(bg_path)
                    if bg_img.get_width() > 0:
                        bg_layers[i] = pygame.transform.scale(bg_img, (SCREEN_W, SCREEN_H))

        # Next map transition check
        if player.rect.x > map_width - 80:
            game_state["score"] += 50  # bonus for finding exit
            return "mossy"

        # Update Player physics
        player.update(dt, map_height)

        # Chest collection scoring
        for mcx, mcy in CHEST_COORDS:
            chest_rect = pygame.Rect(mcx * TILE_SIZE, mcy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if player.rect.colliderect(chest_rect):
                game_state["score"] += 10

        # Fall damage — sync with shared state
        if player.rect.y > map_height:
            game_state["health"] = max(0, game_state["health"] - 1)
            if game_state["health"] <= 0:
                game_state["health"] = game_state["max_health"]
                game_state["lives"] = max(0, game_state["lives"] - 1)

        # Camera smoothly follows player
        target_scroll_x = player.rect.centerx - SCREEN_W // 2
        target_scroll_y = player.rect.centery - SCREEN_H // 2
        
        scroll_x += (target_scroll_x - scroll_x) * 5 * dt
        scroll_y += (target_scroll_y - scroll_y) * 5 * dt
            
        scroll_x = max(0, min(scroll_x, map_width - SCREEN_W))
        scroll_y = max(0, min(scroll_y, map_height - SCREEN_H))

        # Fill background
        surface.fill((10, 15, 25))

        # Parallax
        for i, bg in enumerate(bg_layers):
            parallax_x = scroll_x * (0.1 * i)
            parallax_y = scroll_y * (0.05 * i)
            rel_x = parallax_x % bg.get_width()
            surface.blit(bg, (-rel_x, -parallax_y))
            if rel_x > 0:
                surface.blit(bg, (bg.get_width() - rel_x, -parallax_y))

        # Decorations
        for img, ox, oy in decorations:
            if ox - scroll_x > SCREEN_W or ox + img.get_width() - scroll_x < 0: continue
            if oy - scroll_y > SCREEN_H or oy + img.get_height() - scroll_y < 0: continue
            surface.blit(img, (ox - scroll_x, oy - scroll_y))

        # Map tiles
        for row_idx, row in enumerate(MAP_LAYOUT):
            y = row_idx * TILE_SIZE - scroll_y
            if y < -TILE_SIZE or y > SCREEN_H + TILE_SIZE: continue
                
            for col_idx, symbol in enumerate(row):
                if symbol == ' ': continue
                    
                x = col_idx * TILE_SIZE - scroll_x
                if x < -TILE_SIZE or x > SCREEN_W + TILE_SIZE: continue

                if symbol in loaded_tiles:
                    surface.blit(loaded_tiles[symbol], (x, y))

        # Chests
        if chest_frames:
            c_frame = chest_frames[chest_idx]
            for mcx, mcy in CHEST_COORDS:
                mx = mcx * TILE_SIZE - scroll_x
                my = mcy * TILE_SIZE - scroll_y - c_frame.get_height() + TILE_SIZE
                if mx < -32 or mx > SCREEN_W or my < -32 or my > SCREEN_H: continue
                surface.blit(c_frame, (mx, my))

        # Draw Minimap HUD
        draw_minimap(surface, player, scroll_x, scroll_y, map_width, map_height)

        # Draw shared HUD
        draw_hud(surface, game_state, player)

        # Draw Player
        player.draw(surface, scroll_x, scroll_y)

        pygame.display.flip()

    return "quit"

if __name__ == "__main__":
    run_level(screen)
    pygame.quit()
    sys.exit()
