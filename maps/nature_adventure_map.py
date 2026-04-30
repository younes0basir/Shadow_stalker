import os, sys, pygame, math

ROOT        = os.path.dirname(__file__)
PARENT_DIR  = os.path.dirname(ROOT)
BASE        = os.path.join(PARENT_DIR, "assets", "craftpix-net-156752-nature-pixel-art-environment-free-assets-pack")
PLAYER_PATH = os.path.join(PARENT_DIR, "assets", "MainCharacters", "VirtualGuy")

pygame.init()
SCREEN_W, SCREEN_H = 1280, 720
TILE_SIZE = 32

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
else:
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
    else:
        SCREEN_W, SCREEN_H = screen.get_size()
pygame.display.set_caption("Nature Adventure – Outdoor Scene")

# ── Tile Mapping (Bright outdoor nature tiles) ──────────────────────────────
TILE_MAPPING = {
    # Grass top tiles
    '1': "tile46.png", '2': "tile47.png", '3': "tile48.png",
    # Dirt middle tiles
    '4': "tile52.png", '5': "tile68.png", '6': "tile55.png",
    # Dirt bottom/deep tiles
    '7': "tile111.png", '8': "tile112.png", '9': "tile113.png",
    # Rock/wall tiles
    'r': "tile73.png", 'e': "tile74.png", 'o': "tile75.png",
    # Wooden platform tiles
    '[': "tile99.png", '-': "tile100.png", ']': "tile101.png",
    # Slope tiles
    '/': "tile125.png", '\\': "tile124.png",
}

SOLID_TILES = set('123456789reo[]/\\')

# ── Map Layout (Outdoor Nature Scene with platforms and waterfall gap) ───────
W, H = 100, 34
_layout = []
import random
for r in range(H):
    row = list(' ' * W)
    _layout.append(row)

# Ground level — left section (cols 0-25)
for c in range(0, 26):
    _layout[19][c] = '2'  # grass top
    _layout[20][c] = _layout[21][c] = '5'  # dirt middle
    _layout[22][c] = '8'  # dirt bottom

# Ground level — right section (cols 30-99) with gap for waterfall
for c in range(30, 100):
    _layout[19][c] = '2'
    _layout[20][c] = _layout[21][c] = '5'
    _layout[22][c] = '8'

# Rocky terrain section (cols 60-80, rows 19-22)
for c in range(60, 81):
    _layout[19][c] = random.choice('123')
    _layout[20][c] = random.choice('456')
    _layout[21][c] = random.choice('456')
    _layout[22][c] = random.choice('789')

# Floating Platforms helper - uses ground tiles instead of platform tiles
def add_plat(r, c1, c2):
    _layout[r][c1] = '1'  # grass top left
    for c in range(c1+1, c2): _layout[r][c] = '2'  # grass top mid
    _layout[r][c2] = '3'  # grass top right

# Staircase platforms — each step at most 2 tiles above previous
# Step 1: left platform, 2 tiles above ground
add_plat(17, 5, 10)

# Step 2: mid-left, 2 tiles above step 1
add_plat(15, 10, 15)

# Step 3: mid, 1 tile above step 2
add_plat(14, 17, 22)

# Step 4: mid-right, 1 tile above step 3
add_plat(13, 24, 29)

# Pillar cap, 1 tile above step 4
add_plat(12, 30, 37)

# Pillar body (cols 30-37, rows 12-18)
for r in range(12, 19):
    for c in range(30, 38):
        if c == 30 or c == 37:
            _layout[r][c] = random.choice('reo')  # pillar edges
        else:
            _layout[r][c] = '5'  # pillar body

# Additional platforms on the right side
# Mid-right platform (cols 40-48, row 16)
add_plat(16, 40, 48)

# High platform (cols 50-58, row 13)
add_plat(13, 50, 58)

# Intermediate platform to bridge the gap to the wall
add_plat(16, 60, 63)

# Rock wall section (cols 65-75, rows 10-18) - vertical climb
for r in range(10, 19):
    for c in range(65, 76):
        if c == 65 or c == 75:
            _layout[r][c] = random.choice('reo')  # wall edges
        else:
            _layout[r][c] = random.choice('reo')  # wall body

# Add a ledge on the wall to help climbing from the intermediate platform
add_plat(13, 65, 68)

# Floating platform after wall (cols 78-88, row 14)
add_plat(14, 78, 88)

# Stepping stone between floating platform and final platform
_layout[12][81] = '1'
_layout[12][82] = '2'
_layout[13][85] = '1'
_layout[13][86] = '2'

# High far platform (cols 85-95, row 10)
add_plat(10, 85, 95)

# Slope section (cols 35-45, row 17) - ascending
for c in range(35, 45):
    _layout[17][c] = random.choice('123')
    _layout[18][c] = random.choice('456')

# Small stepping stones (cols 70, 75, 80 at row 15)
_layout[15][70] = '1'
_layout[15][75] = '1'
_layout[15][80] = '1'

MAP_LAYOUT = ["".join(row) for row in _layout]

# ── Background (Bright outdoor sky with clouds) ─────────────────────────────
def draw_background(surface, sx, sy):
    # Sky gradient (blue top to lighter blue bottom)
    for row in range(SCREEN_H):
        t = row / SCREEN_H
        r = int(60 + (140 - 60) * t)
        g = int(140 + (200 - 140) * t)
        b = int(210 + (235 - 210) * t)
        pygame.draw.line(surface, (r, g, b), (0, row), (SCREEN_W, row))
    
    # Clouds (slow drift based on camera position)
    cloud_color = (180, 215, 240)
    cloud_off = (int(sx * 0.1) // 3) % (SCREEN_W + 200)
    clouds = [
        (80, 80, 110), (260, 50, 90), (480, 110, 130),
        (700, 60, 95), (950, 90, 115), (1150, 55, 100)
    ]
    for cx, cy, cw in clouds:
        adjusted_cx = (cx - cloud_off) % (SCREEN_W + 160) - 80
        # Simple cloud shapes
        pygame.draw.rect(surface, cloud_color, (adjusted_cx, cy, cw, 14))
        pygame.draw.rect(surface, cloud_color, (adjusted_cx + 10, cy - 8, cw - 20, 10))

# ── Objects ───────────────────────────────────────────────────────────────────
o = lambda p: os.path.join(BASE, "PNG", "Objects", p)
t_dir = os.path.join(BASE, "PNG", "Tiles")

def load_img(path, sc=1.0):
    try:
        img = pygame.image.load(path).convert_alpha()
        if sc != 1.0:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w*sc), int(h*sc)))
        return img
    except: return None

# Load Tiles
loaded_tiles = {}
for sym, fname in TILE_MAPPING.items():
    img = load_img(os.path.join(t_dir, fname))
    if img: loaded_tiles[sym] = img

# Load Props
tree1 = load_img(o("trees2_1.png"))
tree2 = load_img(o("trees2_2.png"))
tree3 = load_img(o("trees2_3.png"))
pink_tree = load_img(o("pink_bush2.png"))
rock1 = load_img(o("rocks1_1.png")); rock2 = load_img(o("rocks1_3.png")); rock3 = load_img(o("rocks1_5.png"))
grass_tuft = load_img(o("grass1.png"))
sign = load_img(o("pointer.png"))

DECORATIONS = [
    # Ground tree grove (left section)
    (tree1, 2, 19),     # Tree on ground left
    (tree2, 5, 19),     # Tree on ground left
    (tree3, 9, 19),     # Tree on ground left
    (pink_tree, 12, 19), # Pink tree on ground left
    (tree1, 18, 19),    # Additional tree near gap
    
    # Step 1 platform (row 17) - grass tufts
    (grass_tuft, 6, 17),
    (grass_tuft, 7, 17),
    (grass_tuft, 8, 17),
    (rock1, 9, 17),
    
    # Step 2 platform (row 15) - pink cherry tree
    (pink_tree, 12, 15),
    
    # Step 3 platform (row 14) - rocks
    (rock2, 19, 14),
    
    # Step 4 platform (row 13) - rocks
    (rock2, 25, 13),
    (rock3, 27, 13),
    
    # Pillar cap (row 12) - tree
    (tree1, 33, 12),
    
    # Mid-right platform (row 16) - decorations
    (grass_tuft, 42, 16),
    (grass_tuft, 44, 16),
    (rock1, 46, 16),
    
    # High platform (row 13) - pink tree
    (pink_tree, 53, 13),
    
    # Right ground section trees (extended)
    (tree2, 30, 19),
    (tree3, 35, 19),
    (tree1, 40, 19),
    (tree2, 48, 19),
    (tree3, 55, 19),
    (tree1, 62, 19),
    (pink_tree, 70, 19),
    (tree2, 82, 19),
    (tree3, 90, 19),
    
    # Rocky terrain decorations
    (rock1, 63, 19),
    (rock2, 68, 19),
    (rock3, 73, 19),
    (rock1, 78, 19),
    (rock2, 83, 19),
    (rock3, 88, 19),
    (rock1, 93, 19),
    
    # Wall section decorations (rocks at base)
    (rock2, 66, 19),
    (rock3, 70, 19),
    (rock1, 74, 19),
    
    # Floating platform after wall (row 14)
    (grass_tuft, 80, 14),
    (grass_tuft, 83, 14),
    (rock1, 86, 14),
    
    # High far platform (row 10)
    (tree1, 87, 10),
    (grass_tuft, 90, 10),
    (grass_tuft, 93, 10),
    
    # Slope section decorations
    (rock2, 38, 17),
    (grass_tuft, 42, 17),
    
    # Stepping stones (small grass tufts)
    (grass_tuft, 70, 15),
    (grass_tuft, 75, 15),
    (grass_tuft, 80, 15),
    
    # Ground rocks scattered (extended)
    (rock1, 4, 19),
    (rock2, 15, 19),
    (rock3, 32, 19),
    (rock1, 38, 19),
    (rock2, 45, 19),
    (rock3, 52, 19),
    (rock1, 58, 19),
    (rock2, 65, 19),
    (rock3, 72, 19),
    (rock1, 78, 19),
    (rock2, 85, 19),
    (rock3, 92, 19),
    (rock1, 98, 19),
]

# ── Player ─────────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        sc = 1.5
        self.anims = {}
        for s in ('idle', 'run', 'jump', 'double_jump', 'fall'):
            p = os.path.join(PLAYER_PATH, f"{s}.png")
            self.anims[s] = self.load_ss(p, 32, 32, sc)
            
        self.state = 'idle'; self.frame_idx = 0.0; self.facing_right = True
        self.x = float(x); self.y = float(y)
        self.rect = pygame.Rect(x, y, int(16 * sc), int(24 * sc))
        self.vx = 0
        self.vy = 0
        self.speed = 280   # px per sec
        self.jump_force = -520 # Increased jump force for higher reach
        self.gravity = 1300    # Adjusted gravity for snappy fall
        
        self.on_ground = False
        self.jump_count = 0

    def load_ss(self, path, fw, fh, sc):
        try:
            sheet = pygame.image.load(path).convert_alpha()
            frames = []
            for x in range(0, sheet.get_width(), fw):
                s = pygame.Surface((fw, fh), pygame.SRCALPHA)
                s.blit(sheet, (0, 0), (x, 0, fw, fh))
                s = pygame.transform.scale(s, (int(fw*sc), int(fh*sc)))
                frames.append(s)
            return frames
        except: return [pygame.Surface((32,32))]

    def _tiles(self, rect):
        hits = []
        sc = max(0, rect.left // TILE_SIZE); sr = max(0, rect.top // TILE_SIZE)
        er = min(len(MAP_LAYOUT) - 1, (rect.bottom - 1) // TILE_SIZE)
        for r in range(sr, er + 1):
            row_str = MAP_LAYOUT[r]
            ec = min(len(row_str)-1, (rect.right-1)//TILE_SIZE)
            for c in range(sc, ec + 1):
                if 0 <= c < len(row_str) and row_str[c] in SOLID_TILES:
                    hits.append(pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return hits

    def jump(self):
        if self.jump_count < 2:
            self.vy = self.jump_force
            self.jump_count += 1
            self.on_ground = False

    def update(self, dt, map_w, map_h):
        # Clamp dt to prevent tunneling at high speeds
        dt = min(dt, 0.033)  # Max ~30fps equivalent
        
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.vx = -self.speed; self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx = self.speed; self.facing_right = True

        self.vy += self.gravity * dt
        self.x += self.vx * dt; self.rect.x = int(self.x)
        for h in self._tiles(self.rect):
            if self.vx > 0: self.rect.right = h.left; self.x = float(self.rect.x)
            elif self.vx < 0: self.rect.left = h.right; self.x = float(self.rect.x)
        
        # Boundary checks AFTER movement
        if self.x < 0:
            self.x = 0
            self.rect.x = 0
            self.vx = 0
        
        # Check if player reached the end of the map
        if self.x > map_w - TILE_SIZE:
            return "next"

        self.y += self.vy * dt; self.rect.y = int(self.y)
        tile_hits = self._tiles(self.rect)
        for h in tile_hits:
            if self.vy > 0:
                self.rect.bottom = h.top; self.y = float(self.rect.y); self.vy = 0; self.on_ground = True
            elif self.vy < 0:
                self.rect.top = h.bottom; self.y = float(self.rect.y); self.vy = 0

        # Ground probe check - check if player is standing on something
        self.rect.y += 1
        ground_hits = self._tiles(self.rect)
        self.rect.y -= 1
        if len(ground_hits) > 0 and self.vy >= 0:
            self.on_ground = True
            self.jump_count = 0
        elif self.vy > 0 or (self.vy == 0 and not ground_hits):
            self.on_ground = False
        
        if self.rect.y > map_h:
            return "fell"

        # Animations
        if not self.on_ground:
            self.state = 'jump' if self.vy < 0 else 'fall'
            if self.jump_count == 2: self.state = 'double_jump'
        elif self.vx != 0: self.state = 'run'
        else: self.state = 'idle'
        
        self.frame_idx += 12 * dt

    def draw(self, surface, sx, sy):
        frames = self.anims.get(self.state, self.anims['idle'])
        img = frames[int(self.frame_idx) % len(frames)]
        if not self.facing_right: img = pygame.transform.flip(img, True, False)
        bx = self.rect.centerx - img.get_width() // 2 - sx
        by = self.rect.bottom - img.get_height() - sy
        surface.blit(img, (bx, by))

# ── HUD ──────────────────────────────────────────────────────────────────────
def draw_hud(surface, gs):
    try: fb = pygame.font.SysFont("segoeui", 18, bold=True); fs = pygame.font.SysFont("consolas", 13)
    except Exception: fb = fs = pygame.font.Font(None, 20)

    p = pygame.Surface((170, 50), pygame.SRCALPHA)
    pygame.draw.rect(p, (20, 12, 5, 215), (0, 0, 170, 50), border_radius=10)
    pygame.draw.rect(p, (220, 100, 30, 120), (0, 0, 170, 50), 2, border_radius=10)
    surface.blit(p, (10, 10))
    for i in range(gs["max_health"]):
        cx = 28 + i * 34; cy = 35; f = i < gs["health"]
        pygame.draw.circle(surface, (255, 140, 20) if f else (80, 50, 20), (cx, cy), 13, 2)
        pygame.draw.circle(surface, (220, 110, 15) if f else (50, 30, 10), (cx, cy), 10)
        if f: pygame.draw.circle(surface, (255, 220, 130), (cx - 4, cy - 4), 4)

    sp = pygame.Surface((170, 44), pygame.SRCALPHA)
    pygame.draw.rect(sp, (20, 12, 5, 215), (0, 0, 170, 44), border_radius=10)
    pygame.draw.rect(sp, (220, 100, 30, 120), (0, 0, 170, 44), 2, border_radius=10)
    surface.blit(sp, (SCREEN_W - 180, 10))
    surface.blit(fb.render(f"SCORE  {gs['score']}", True, (255, 180, 60)), (SCREEN_W - 178, 22))
    lbl = fs.render("NATURE ADVENTURE", True, (255, 150, 50))
    surface.blit(lbl, (SCREEN_W // 2 - lbl.get_width() // 2, 8))
    ctrls = [("[A]/[D]", "Move"), ("[Space]/[W]", "Double Jump"), ("[ESC]", "Quit")]
    py = SCREEN_H - 20 - len(ctrls) * 20
    for i, (k, a) in enumerate(ctrls):
        surface.blit(fs.render(k, True, (255, 190, 110)), (20, py + i * 20))
        surface.blit(fs.render(a, True, (200, 140, 70)), (120, py + i * 20))

# ── Main Loop ──────────────────────────────────────────────────────────────────
def run_level(surface, game_state=None):
    if game_state is None:
        game_state = {"health": 3, "max_health": 3, "score": 0, "lives": 3}

    clock = pygame.time.Clock()
    # Spawn player on ground (row 19 = y=608, player height=36, so spawn at 608-36=572)
    player = Player(100.0, 500.0)
    map_width = W * TILE_SIZE
    map_height = len(MAP_LAYOUT) * TILE_SIZE
    # Initialize camera to player position immediately
    sx = max(0, min(100.0 - SCREEN_W // 2, map_width - SCREEN_W))
    sy = max(0, min(500.0 - SCREEN_H // 2, map_height - SCREEN_H))
    
    # Tileset configuration
    SOLID_TILES = set('123456789.Xre') # Include re as solid for bot
    
    # AI Bot
    bot = None
    if game_state.get("game_mode") == "kids":
        pass
    else:
        try:
            from ai.mask_dude_bot import MaskDudeBot
            # Spawn bot slightly behind the player's start (player is at 100)
            bot = MaskDudeBot(50, 450, TILE_SIZE, MAP_LAYOUT, SOLID_TILES)
        except ImportError:
            pass

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "quit"
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP): player.jump()

        status = player.update(dt, map_width, map_height)
        
        # Update Bot
        if bot:
            bot.set_target(player)
            bot.update(dt, map_height)
            # Save bot position to game_state for map-to-map persistence
            game_state["bot_x"] = bot.x
            game_state["bot_y"] = bot.y
            
            if bot.rect.colliderect(player.rect):
                # Bot caught player -> Game Over
                return "game_over"       
        if status == "next":
            # Before returning, draw one last time to avoid black flash
            draw_background(surface, int(sx*0.2), int(sy*0.2))
            player.draw(surface, int(sx), int(sy))
            draw_hud(surface, game_state)
            pygame.display.flip()
            return "next"
        if status == "fell":
            game_state["health"] -= 1
            if game_state["health"] <= 0:
                return "quit"
            # Respawn
            player.x, player.y = 100.0, 572.0
            player.vx = player.vy = 0
            player.rect.topleft = (int(player.x), int(player.y))
        
        # Camera
        sx += (player.rect.x - SCREEN_W//2 - sx) * 5 * dt
        sy += (player.rect.y - SCREEN_H//2 - sy) * 5 * dt
        sx = max(0, min(sx, map_width - SCREEN_W))
        sy = max(0, min(sy, map_height - SCREEN_H))
        
        # Draw
        draw_background(surface, int(sx*0.2), int(sy*0.2))
        
        # Decorative objects
        for img, tx, ty in DECORATIONS:
            if img:
                surface.blit(img, (tx*TILE_SIZE - sx, ty*TILE_SIZE - sy - img.get_height() + TILE_SIZE))

        # Tiles
        for r_idx, row in enumerate(MAP_LAYOUT):
            for c_idx, sym in enumerate(row):
                if sym in loaded_tiles:
                    surface.blit(loaded_tiles[sym], (c_idx*TILE_SIZE - int(sx), r_idx*TILE_SIZE - int(sy)))

        player.draw(surface, int(sx), int(sy))
        if bot:
            bot.draw(surface, int(sx), int(sy))
        draw_hud(surface, game_state)
        
        # Ensure we always flip even on the last frame before returning
        pygame.display.flip()

    # Final cleanup to ensure no black frames
    pygame.display.flip()
    return "quit"

if __name__ == "__main__":
    run_level(screen)
