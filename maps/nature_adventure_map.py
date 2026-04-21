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
W, H = 60, 34
_layout = []
import random
for r in range(H):
    row = list(' ' * W)
    _layout.append(row)

# Ground level — left section (cols 0-22)
for c in range(0, 23):
    _layout[19][c] = '2'  # grass top
    _layout[20][c] = _layout[21][c] = '5'  # dirt middle
    _layout[22][c] = '8'  # dirt bottom

# Ground level — right section (cols 27-59) with gap for waterfall
for c in range(27, 60):
    _layout[19][c] = '2'
    _layout[20][c] = _layout[21][c] = '5'
    _layout[22][c] = '8'

# Floating Platforms helper
def add_plat(r, c1, c2):
    _layout[r][c1] = '['
    for c in range(c1+1, c2): _layout[r][c] = '-'
    _layout[r][c2] = ']'

# Floating platform — left mid (similar to test: 180, 430)
add_plat(13, 6, 11)

# Floating platform — top small (similar to test: 290, 220)
add_plat(7, 10, 13)

# Floating platform — right mid (similar to test: 660, 330)
add_plat(10, 22, 27)

# Tall right pillar cap (similar to test: 920, 380)
add_plat(12, 30, 37)

# Tall pillar body (cols 30-37, rows 13-18)
for r in range(13, 19):
    for c in range(30, 38):
        if c == 30 or c == 37:
            _layout[r][c] = random.choice('reo')  # pillar edges
        else:
            _layout[r][c] = '5'  # pillar body

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
    
    # Left floating platform - pines/grass
    (grass_tuft, 7, 13),
    (grass_tuft, 8, 13),
    (grass_tuft, 9, 13),
    (rock1, 11, 13),
    
    # Top small platform - pink cherry tree
    (pink_tree, 11, 7),
    
    # Right mid platform - rocks
    (rock2, 23, 10),
    (rock3, 25, 10),
    
    # Pillar top tree
    (tree1, 33, 12),
    
    # Right ground section trees
    (tree2, 30, 19),
    (tree3, 35, 19),
    (tree1, 40, 19),
    
    # Ground rocks scattered
    (rock1, 4, 19),
    (rock2, 15, 19),
    (rock3, 32, 19),
    (rock1, 38, 19),
    (rock2, 45, 19),
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
        self.vx = 0.0; self.vy = 0.0
        self.speed = 280; self.jump_force = -480; self.gravity = 1400
        self.on_ground = False; self.jump_count = 0

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

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.vx = -self.speed; self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx = self.speed; self.facing_right = True

        self.vy += self.gravity * dt
        self.x += self.vx * dt; self.rect.x = int(self.x)
        for h in self._tiles(self.rect):
            if self.vx > 0: self.rect.right = h.left; self.x = float(self.rect.x)
            elif self.vx < 0: self.rect.left = h.right; self.x = float(self.rect.x)

        self.y += self.vy * dt; self.rect.y = int(self.y)
        for h in self._tiles(self.rect):
            if self.vy > 0: self.rect.bottom = h.top; self.y = float(self.rect.y); self.vy = 0; self.on_ground = True
            elif self.vy < 0: self.rect.top = h.bottom; self.y = float(self.rect.y); self.vy = 0

        if self.on_ground: self.jump_count = 0
        
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
        surface.blit(img, (self.rect.x - sx - (img.get_width()-self.rect.width)//2, 
                           self.rect.y - sy - (img.get_height()-self.rect.height)))

# ── Main Loop ──────────────────────────────────────────────────────────────────
def main():
    clock = pygame.time.Clock()
    player = Player(100, 540)  # Spawn player on left ground section
    sx, sy = 0, 0
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP): player.jump()

        player.update(dt)
        
        # Camera
        sx += (player.rect.x - SCREEN_W//2 - sx) * 5 * dt
        sy += (player.rect.y - SCREEN_H//2 - sy) * 5 * dt
        sx = max(0, min(sx, W*TILE_SIZE - SCREEN_W))
        sy = max(0, min(sy, len(MAP_LAYOUT)*TILE_SIZE - SCREEN_H))
        
        # Draw
        draw_background(screen, int(sx*0.2), int(sy*0.2))
        
        # Decorative objects
        for img, tx, ty in DECORATIONS:
            if img:
                screen.blit(img, (tx*TILE_SIZE - sx, ty*TILE_SIZE - sy - img.get_height() + TILE_SIZE))

        # Tiles
        for r_idx, row in enumerate(MAP_LAYOUT):
            for c_idx, sym in enumerate(row):
                if sym in loaded_tiles:
                    screen.blit(loaded_tiles[sym], (c_idx*TILE_SIZE - int(sx), r_idx*TILE_SIZE - int(sy)))

        player.draw(screen, int(sx), int(sy))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
