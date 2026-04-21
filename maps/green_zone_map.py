import os
import sys
import pygame
import random
import math

# Add parent directory and ai directory to path for imports
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
sys.path.insert(0, PARENT_DIR)
sys.path.insert(0, os.path.join(PARENT_DIR, "ai"))

# Bot spawning handled by merged_game.py - disabled in individual map files
BOT_AVAILABLE = False

# Paths
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
base_path = os.path.join(PARENT_DIR, "assets", "craftpix-net-846754-free-green-zone-tileset-pixel-art")
player_path = os.path.join(PARENT_DIR, "assets", "MainCharacters", "VirtualGuy")

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
pygame.display.set_caption("Green Zone - Platformer Test")

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
    " " * 80,
    " " * 80,
    " " * 44 + "C" + " " * 9 + "C" + " " * 25,
    " " * 39 + "C" + " " * 9 + "C" + " " * 9 + "C" + " " * 22,
    " " * 28 + "122223" + "   C" + " " * 9 + "C" + " " * 9 + "C" + " " * 23,
    " " * 28 + "455556" + "        C" + "    12223   1223" + " " * 12 + "12223" + " " * 8,
    " " * 28 + "788889" + "             45556   4556" + " " * 12 + "45556" + " " * 8,
    " " * 80,
    " " * 35 + "122223" + " " * 8 + "122223" + " " * 24,
    " " * 24 + "122223" + "             455556" + " " * 8 + "455556" + " " * 23,
    " " * 18 + "/455556\\" + "             455556" + " " * 8 + "/455556\\" + " " * 20,
    "12222222222222222222222455556             455556   4555555555555555556" + "   45555555555555555556",
]
for _i in range(25):
    center = "1223" if _i == 0 else "4556"
    MAP_LAYOUT.append("45555555555555555555555555556   " + center + "      455556   4555555555555555556" + "   45555555555555555556")
MAP_LAYOUT.append("78888888888888888888888888889   7889      788889   7888888888888888889" + "   78888888888888888889")



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
        if not frames:
            raise ValueError("No frames loaded")
        return frames
    except Exception as e:
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
bg_dir = os.path.join(base_path, "2 Background", "Day")
for i in range(1, 6):
    bg_path = os.path.join(bg_dir, f"{i}.png")
    bg_img = load_image(bg_path)
    if bg_img.get_width() > 0:
        bg_img = pygame.transform.scale(bg_img, (SCREEN_W, SCREEN_H))
        bg_layers.append(bg_img)

# Decor objects
t_path = lambda p: os.path.join(base_path, "3 Objects", p)
a_path = lambda p: os.path.join(base_path, "4 Animated objects", p)

# Large objects loaded safely
tree1 = load_image(t_path("Other/Tree4.png"))  # Big Tree
tree2 = load_image(t_path("Other/Tree1.png"))
box_img = load_image(t_path("Other/Box.png"))
ramp1 = load_image(t_path("Other/Ramp1.png"))
ramp2 = load_image(t_path("Other/Rapm3.png")) # Rapm3 in original zip
bench = load_image(t_path("Benches/1.png"))
fence_seg = load_image(t_path("Fence/1.png"))
fence_seg_mid = load_image(t_path("Fence/2.png"))
fence_seg_end = load_image(t_path("Fence/3.png"))
ladder = load_image(t_path("Other/Ladder1.png"))
garbage = load_image(t_path("Other/Garbage_Can1.png"))
garbage2 = load_image(t_path("Other/Garbage_Can2.png"))
bush1 = load_image(t_path("Bushes/1.png"))
bush2 = load_image(t_path("Bushes/2.png"))
bush3 = load_image(t_path("Bushes/3.png"))
sb1 = load_image(t_path("Other/Skateboard1.png"))
sb2 = load_image(t_path("Other/Skateboard2.png"))
stone1 = load_image(t_path("Stones/1.png"))
stone2 = load_image(t_path("Stones/2.png"))
stone3 = load_image(t_path("Stones/3.png"))
stone4 = load_image(t_path("Stones/4.png"))

# Sprites & animations
fountain = load_image(t_path("Fountain/1.png"))
money = load_image(a_path("Money.png"))

# Simple coin scaling from spritesheet if needed, but treat as static for demo
# We will just use the c tile in MAP_LAYOUT or parse 'C' manually.
def get_first_frame(img, w=24):
    if img.get_width() > w:
        surf = pygame.Surface((w, img.get_height()), pygame.SRCALPHA)
        surf.blit(img, (0, 0), (0, 0, w, img.get_height()))
        return surf
    return img

money_img = get_first_frame(money, 24)
coin_frames = load_spritesheet(a_path("Money.png"), 24, 24, scale=1.0)
fountain_frames = load_spritesheet(a_path("Fountain.png"), 64, 64, scale=1.0) if a_path("Fountain.png") else [fountain]

decorations = [] 

# Add explicitly matching the reference image layout
EXPLICIT_OBJS = []

# Left side tree and background fence (only behind ramps)
EXPLICIT_OBJS.append((tree1, -1*TILE_SIZE, 11))
EXPLICIT_OBJS.append((fence_seg, 3*TILE_SIZE, 11))
for i in range(4, 21):
    EXPLICIT_OBJS.append((fence_seg_mid, i*TILE_SIZE, 11))
EXPLICIT_OBJS.append((fence_seg_end, 21*TILE_SIZE, 11))

# Skateboard ramps (gap in between)
EXPLICIT_OBJS.append((sb2, 4*TILE_SIZE + 10, 11))
EXPLICIT_OBJS.append((ramp1, 5*TILE_SIZE, 11))
EXPLICIT_OBJS.append((sb1, 12*TILE_SIZE + 16, 11))
EXPLICIT_OBJS.append((ramp2, 16*TILE_SIZE, 11))
EXPLICIT_OBJS.append((bush1, 4*TILE_SIZE, 11))
EXPLICIT_OBJS.append((bush2, 22*TILE_SIZE, 11))

# Medium tree on slope
EXPLICIT_OBJS.append((tree2, 25*TILE_SIZE, 9))

# Bushes on the floating platform
EXPLICIT_OBJS.append((bush2, 28*TILE_SIZE, 4))
EXPLICIT_OBJS.append((bush3, 30*TILE_SIZE, 4))
EXPLICIT_OBJS.append((bush1, 31*TILE_SIZE + 10, 4))

# Ladder hanging from floating platform
for i in range(4, 11):
    EXPLICIT_OBJS.append((ladder, 32*TILE_SIZE + 16, i))

# Rocks in the pit and on right floating platforms
EXPLICIT_OBJS.append((stone4, 32*TILE_SIZE, 12)) 
EXPLICIT_OBJS.append((stone2, 47*TILE_SIZE, 5)) 
EXPLICIT_OBJS.append((stone3, 56*TILE_SIZE, 5)) 
EXPLICIT_OBJS.append((stone1, 62*TILE_SIZE, 10)) 

# Boxes on the middle pillar
EXPLICIT_OBJS.append((box_img, 44*TILE_SIZE + 5, 8))
EXPLICIT_OBJS.append((box_img, 45*TILE_SIZE + 10, 8))
# top box
EXPLICIT_OBJS.append((box_img, 44*TILE_SIZE + 16, 7))

# Fountain area on the right
EXPLICIT_OBJS.append((bench, 53*TILE_SIZE, 10))
EXPLICIT_OBJS.append((bench, 66*TILE_SIZE, 10))
EXPLICIT_OBJS.append((bush2, 69*TILE_SIZE, 10))
EXPLICIT_OBJS.append((garbage, 65*TILE_SIZE, 10))

# Additional decorations for improved terrain
EXPLICIT_OBJS.append((tree1, 48*TILE_SIZE, 10))
EXPLICIT_OBJS.append((stone1, 55*TILE_SIZE, 8))
EXPLICIT_OBJS.append((stone2, 60*TILE_SIZE, 10))
EXPLICIT_OBJS.append((bush3, 52*TILE_SIZE, 4))
EXPLICIT_OBJS.append((box_img, 58*TILE_SIZE + 5, 8))

for obj_img, col, row in EXPLICIT_OBJS:
    if obj_img and obj_img.get_width() > 0:
        ox = col
        if row > 0:  # If row is specified in tiles, else treat col/row as direct coords
            oy = row * TILE_SIZE - obj_img.get_height()
        else:
            oy = 0
        decorations.append((obj_img, ox, oy))

# Coins
CHEST_COORDS = []
for r, row in enumerate(MAP_LAYOUT):
    for c, char in enumerate(row):
        if char == 'C':
            CHEST_COORDS.append((c, r))

# ── Player Class ──────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
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
        
        self.x = float(x)
        self.y = float(y)
        
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
        self.wall_jump_cooldown = 0

    def check_wall(self, direction):
        offset = 2
        test_rect = self.rect.copy()
        if direction == 'left': test_rect.x -= offset
        else: test_rect.x += offset
            
        start_col = max(0, int(test_rect.left // TILE_SIZE))
        start_row = max(0, int(test_rect.top // TILE_SIZE))
        end_row = min(len(MAP_LAYOUT)-1, int((test_rect.bottom - 1) // TILE_SIZE))
        
        for row in range(start_row, end_row + 1):
            row_len = len(MAP_LAYOUT[row])
            end_col = min(row_len - 1, int((test_rect.right - 1) // TILE_SIZE))
            for col in range(start_col, end_col + 1):
                if 0 <= col < row_len and MAP_LAYOUT[row][col] in SOLID_TILES:
                    if test_rect.colliderect(pygame.Rect(col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE)): return True
        return False

    def get_collisions(self):
        hits = []
        start_col = max(0, int(self.rect.left // TILE_SIZE))
        start_row = max(0, int(self.rect.top // TILE_SIZE))
        end_row = min(len(MAP_LAYOUT)-1, int((self.rect.bottom - 1) // TILE_SIZE))
        for row in range(start_row, end_row + 1):
            row_len = len(MAP_LAYOUT[row])
            end_col = min(row_len - 1, int((self.rect.right - 1) // TILE_SIZE))
            for col in range(start_col, end_col + 1):
                if 0 <= col < row_len and MAP_LAYOUT[row][col] in SOLID_TILES:
                    hits.append(pygame.Rect(col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return hits

    def jump(self):
        if self.on_wall_left and not self.on_ground:
            self.vy = self.jump_force
            self.vx = self.speed * 1.2
            self.wall_jump_cooldown = 0.15
            self.facing_right = True
            self.frame_idx = 0
            return
        elif self.on_wall_right and not self.on_ground:
            self.vy = self.jump_force
            self.vx = -self.speed * 1.2
            self.wall_jump_cooldown = 0.15
            self.facing_right = False
            self.frame_idx = 0
            return
        
        if self.jump_count < 2:
            self.vy = self.jump_force
            self.jump_count += 1
            self.on_ground = False
            self.frame_idx = 0

    def update_state(self):
        new_state = self.state
        if not self.on_ground:
            if self.vy < 0:
                new_state = 'double_jump' if self.jump_count == 2 else 'jump'
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
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.facing_right = True
        else:
            self.vx = 0

        if not self.on_ground and self.wall_jump_cooldown <= 0:
            self.on_wall_left = self.check_wall('left')
            self.on_wall_right = self.check_wall('right')
            self.wall_slide = (self.on_wall_left or self.on_wall_right) and self.vy > 0
        else:
            self.on_wall_left, self.on_wall_right, self.wall_slide = False, False, False
        
        if self.wall_jump_cooldown > 0: self.wall_jump_cooldown = max(0, self.wall_jump_cooldown - dt)
        
        if self.wall_slide:
            self.vy += self.gravity * 0.3 * dt
            self.vy = min(self.vy, 150)
        else:
            self.vy += self.gravity * dt
        
        self.x += self.vx * dt
        if self.x < 0: 
            self.x = 0
            self.vx = 0
            self.rect.x = 0
        else:
            self.rect.x = int(self.x)
        for hit in self.get_collisions():
            if self.vx > 0: self.rect.right = hit.left; self.x = float(self.rect.x)
            elif self.vx < 0:
                self.rect.left = hit.right; self.x = float(self.rect.x)
                if self.on_wall_left: self.on_wall_left = False
        
        self.y += self.vy * dt
        self.rect.y = int(self.y)
        for hit in self.get_collisions():
            if self.vy > 0: self.rect.bottom = hit.top; self.y = float(self.rect.y); self.vy = 0
            elif self.vy < 0: self.rect.top = hit.bottom; self.y = float(self.rect.y); self.vy = 0

        self.rect.y += 1
        ground_hits = self.get_collisions()
        self.rect.y -= 1
        
        if len(ground_hits) > 0 and self.vy >= 0:
            self.on_ground = True
            self.jump_count = 0
        else:
            self.on_ground = False

        self.update_state()
        if self.rect.y > map_h:
            self.y = 0.0
            self.vy = 0
            self.x = float(100)

        anim_speed = 20 if self.state == 'run' else 12 
        self.frame_idx += anim_speed * dt
        
    def draw(self, surface, scroll_x, scroll_y):
        frames = self.anims[self.state]
        if not frames: return
            
        if self.state in ('jump', 'fall', 'double_jump'):
            idx = min(int(self.frame_idx), len(frames) - 1)
        else:
            idx = int(self.frame_idx) % len(frames)
            
        img = frames[idx]
        if not self.facing_right: img = pygame.transform.flip(img, True, False)
            
        blit_x = self.rect.centerx - img.get_width() // 2 - scroll_x
        blit_y = self.rect.bottom - img.get_height() - scroll_y
        surface.blit(img, (blit_x, blit_y))

def draw_hud(surface, game_state, player):
    try:
        font_hud = pygame.font.SysFont("segoeui", 18, bold=True)
        font_sm  = pygame.font.SysFont("consolas", 13)
    except Exception:
        font_hud = font_sm = pygame.font.Font(None, 20)

    panel_w, panel_h = 160, 50
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (10, 35, 10, 200), (0, 0, panel_w, panel_h), border_radius=10)
    pygame.draw.rect(panel, (80, 200, 50, 80), (0, 0, panel_w, panel_h), 2, border_radius=10)
    surface.blit(panel, (10, 10))

    for i in range(game_state["max_health"]):
        cx = 28 + i * 34
        cy = 35
        filled = i < game_state["health"]
        col_ring = (100, 255, 120) if filled else (30, 90, 40)
        col_fill = (80, 220, 100) if filled else (20, 55, 30)
        pygame.draw.circle(surface, col_ring, (cx, cy), 13, 2)
        pygame.draw.circle(surface, col_fill, (cx, cy), 10)
        if filled:
            pygame.draw.circle(surface, (200, 255, 200), (cx - 4, cy - 4), 4)

    score_w = 160
    sp = pygame.Surface((score_w, 44), pygame.SRCALPHA)
    pygame.draw.rect(sp, (10, 35, 10, 200), (0, 0, score_w, 44), border_radius=10)
    pygame.draw.rect(sp, (80, 200, 50, 80), (0, 0, score_w, 44), 2, border_radius=10)
    surface.blit(sp, (SCREEN_W - score_w - 10, 10))

    score_lbl = font_hud.render(f"SCORE  {game_state['score']}", True, (255, 210, 80))
    surface.blit(score_lbl, (SCREEN_W - score_w + 2, 22))

    lvl = font_sm.render("GREEN ZONE PARK", True, (150, 255, 120))
    surface.blit(lvl, (SCREEN_W // 2 - lvl.get_width() // 2, 8))

    controls = [
        ("[A] [D] / [<] [>]", "Move"),
        ("[SPACE] / [W] / [^]", "Double Jump"),
        ("[ESC]", "Quit Game")
    ]
    pad_y = SCREEN_H - 20 - (len(controls) * 20)
    for idx, (keys, action) in enumerate(controls):
        key_lbl = font_sm.render(keys, True, (200, 255, 200))
        act_lbl = font_sm.render(action, True, (120, 180, 120))
        surface.blit(key_lbl, (20, pad_y + idx * 20))
        surface.blit(act_lbl, (150, pad_y + idx * 20))

map_width = max(len(row) for row in MAP_LAYOUT) * TILE_SIZE
map_height = len(MAP_LAYOUT) * TILE_SIZE

def run_level(surface, game_state=None):
    global SCREEN_W, SCREEN_H, bg_layers

    if game_state is None:
        game_state = {"health": 3, "max_health": 3, "score": 0, "lives": 3}

    player = Player(120, 200)

    clock = pygame.time.Clock()
    frame_time = 0
    scroll_x = 0
    scroll_y = 0
    
    run = True
    while run:
        dt = clock.tick(60) / 1000.0
        frame_time += dt

        coin_idx = int(frame_time * 8) % len(coin_frames) if coin_frames else 0

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

        # Update Player physics
        player.update(dt, map_height)
        
        # Coin collection
        for mcx, mcy in CHEST_COORDS[:]:
            chest_rect = pygame.Rect(mcx * TILE_SIZE, mcy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if player.rect.colliderect(chest_rect):
                game_state["score"] += 10
                CHEST_COORDS.remove((mcx, mcy))

        if player.rect.y > map_height:
            game_state["health"] = max(0, game_state["health"] - 1)
            if game_state["health"] <= 0:
                game_state["health"] = game_state["max_health"]
                game_state["lives"] = max(0, game_state["lives"] - 1)

        target_scroll_x = player.rect.centerx - SCREEN_W // 2
        target_scroll_y = player.rect.centery - SCREEN_H // 2
        
        scroll_x += (target_scroll_x - scroll_x) * 5 * dt
        scroll_y += (target_scroll_y - scroll_y) * 5 * dt
            
        scroll_x = max(0, min(scroll_x, map_width - SCREEN_W))
        scroll_y = max(0, min(scroll_y, map_height - SCREEN_H))

        # Fill background
        surface.fill((150, 200, 255))

        for i, bg in enumerate(bg_layers):
            parallax_x = scroll_x * (0.05 * i)
            parallax_y = scroll_y * (0.02 * i) + (SCREEN_H - bg.get_height())
            rel_x = parallax_x % bg.get_width()
            surface.blit(bg, (-rel_x, parallax_y))
            if rel_x > 0:
                surface.blit(bg, (bg.get_width() - rel_x, parallax_y))

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
                if symbol in (' ', 'C'): continue
                    
                x = col_idx * TILE_SIZE - scroll_x
                if x < -TILE_SIZE or x > SCREEN_W + TILE_SIZE: continue

                if symbol in loaded_tiles:
                    surface.blit(loaded_tiles[symbol], (x, y))

        # Draw Fountain if present 
        if fountain_frames:
            f_idx = int(frame_time * 6) % len(fountain_frames)
            # Match fountain position to image
            fx, fy = 59*TILE_SIZE - scroll_x, 10*TILE_SIZE - fountain_frames[0].get_height() - scroll_y
            if -100 < fx < SCREEN_W and -100 < fy < SCREEN_H:
                surface.blit(fountain_frames[f_idx], (fx, fy))

        # Coins
        if coin_frames:
            c_frame = coin_frames[coin_idx]
            for mcx, mcy in CHEST_COORDS:
                mx = mcx * TILE_SIZE - scroll_x + (TILE_SIZE - c_frame.get_width()) // 2
                my = mcy * TILE_SIZE - scroll_y + (TILE_SIZE - c_frame.get_height()) // 2
                if mx < -32 or mx > SCREEN_W or my < -32 or my > SCREEN_H: continue
                surface.blit(c_frame, (mx, my))

        draw_hud(surface, game_state, player)

        player.draw(surface, scroll_x, scroll_y)
        pygame.display.flip()

    return "quit"

if __name__ == "__main__":
    run_level(screen)
    pygame.quit()
    sys.exit()
