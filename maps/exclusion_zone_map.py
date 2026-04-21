import os
import sys
import pygame
import math

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT       = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
base_path  = os.path.join(PARENT_DIR, "assets", "craftpix-net-115897-free-exclusion-zone-tileset-pixel-art")
player_path = os.path.join(PARENT_DIR, "assets", "MainCharacters", "VirtualGuy")

# ── Init ───────────────────────────────────────────────────────────────────
pygame.init()

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

pygame.display.set_caption("Exclusion Zone - Platformer")

# ── Tile mapping ───────────────────────────────────────────────────────────
# Row 0: Tile_01–03  -> grass-top left/mid/right
# Row 1: Tile_11–13  -> concrete mid left/mid/right
# Row 2: Tile_21–23  -> deep concrete left/mid/right
# Tile_04 & Tile_07  -> slope tiles
TILE_MAPPING = {
    '1': "Tile_01.png",  # grass top-left
    '2': "Tile_02.png",  # grass top-mid
    '3': "Tile_03.png",  # grass top-right
    '4': "Tile_11.png",  # concrete left
    '5': "Tile_12.png",  # concrete mid
    '6': "Tile_13.png",  # concrete right
    '7': "Tile_21.png",  # deep left
    '8': "Tile_22.png",  # deep mid
    '9': "Tile_23.png",  # deep right
    'L': "Tile_04.png",  # slope up-right
    'R': "Tile_07.png",  # slope up-left
    'A': "Tile_31.png",  # platform left
    'B': "Tile_32.png",  # platform mid
    'C': "Tile_33.png",  # platform right
}

SOLID_TILES = set('123456789LRABCc')

# ── Map layout ─────────────────────────────────────────────────────────────
# Legend:
#  ' '  = air
#  'C'  = coin pickup (drawn separately, not a tile)
#  1-9  = ground/dirt tiles
#  L/R  = slope tiles
#  A/B/C = dark platform tiles

MAP_LAYOUT = [
    " " * 80,
    " " * 80,
    " " * 52 + "c" + " " * 4 + "c" + " " * 22,
    " " * 48 + "c" + " " * 4 + "c" + " " * 4 + "c" + " " * 20,
    " " * 42 + "ABC" + " c" + " " * 6 + "c" + " " * 4 + "c" + " " * 20,
    " " * 42 + "ABC" + " " * 35,
    " " * 80,
    " " * 50 + "ABC" + " " * 8 + "ABC" + " " * 17,
    " " * 50 + "ABC" + " " * 8 + "ABC" + " " * 17,
    " " * 80,
    " " * 28 + "123" + " " * 5 + "c" + " " * 4 + "c" + " " * 35,
    " " * 28 + "456" + " " * 49,
    " " * 80,
    " " * 36 + "c  c  c" + " " * 4 + "c  c  c" + " " * 29,
    " " * 15 + "L123" + " " * 8 + "123R" + " " * 45,
    # main ground — left plateau  gap  middle pillar  gap  right ground
    "12222222222222222223      12223        123      12222222222222222223",
]
# Extend downward so no sky shows through
for _i in range(25):
    inner = "45555555555555555556      45556        456      45555555555555555556"
    MAP_LAYOUT.append(inner)
MAP_LAYOUT.append("78888888888888888889      78889        789      78888888888888888889")

# ── Helpers ────────────────────────────────────────────────────────────────
def load_image(path, scale=1):
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale != 1:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
        return img
    except Exception:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((80, 80, 80, 200))
        return surf

def load_spritesheet(path, fw, fh, scale=1.0):
    try:
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for x in range(0, sheet.get_width(), fw):
            surf = pygame.Surface((fw, fh), pygame.SRCALPHA)
            surf.blit(sheet, (0, 0), (x, 0, fw, fh))
            if scale != 1:
                surf = pygame.transform.scale(surf, (int(fw * scale), int(fh * scale)))
            frames.append(surf)
        if not frames:
            raise ValueError("empty")
        return frames
    except Exception:
        s = pygame.Surface((int(fw * scale), int(fh * scale)), pygame.SRCALPHA)
        s.fill((180, 0, 0))
        return [s]

# ── Load tiles ─────────────────────────────────────────────────────────────
tiles_dir = os.path.join(base_path, "1 Tiles")
loaded_tiles = {}
for sym, fname in TILE_MAPPING.items():
    loaded_tiles[sym] = load_image(os.path.join(tiles_dir, fname))

# ── Background layers ──────────────────────────────────────────────────────
bg_layers = []
bg_dir = os.path.join(base_path, "2 Background", "Day")
for i in range(1, 6):
    img = load_image(os.path.join(bg_dir, f"{i}.png"))
    if img.get_width() > 1:
        img = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        bg_layers.append(img)

# ── Object helpers ─────────────────────────────────────────────────────────
o_path = lambda p: os.path.join(base_path, "3 Objects", p)
a_path = lambda p: os.path.join(base_path, "4 Animated objects", p)

# Trees
tree1 = load_image(o_path("Trees/4.png"))
tree2 = load_image(o_path("Trees/3.png"))
tree3 = load_image(o_path("Trees/5.png"))
tree4 = load_image(o_path("Trees/7.png"))

# Stones
stone1 = load_image(o_path("Stones/1.png"))
stone2 = load_image(o_path("Stones/3.png"))
stone3 = load_image(o_path("Stones/5.png"))

# Grass clumps as ground decoration
grass1 = load_image(o_path("Grass/1.png"))
grass2 = load_image(o_path("Grass/7.png"))
grass3 = load_image(o_path("Grass/14.png"))

# Boxes / props
box1 = load_image(o_path("Other/Box1.png"))
box2 = load_image(o_path("Other/Box2.png"))
box3 = load_image(o_path("Other/Box3.png"))
ptr1 = load_image(o_path("Other/Pointer1.png"))
ptr2 = load_image(o_path("Other/Pointer2.png"))

# Animated objects
coin_frames  = load_spritesheet(a_path("Money.png"), 24, 24, scale=1.0)
card_frames  = load_spritesheet(a_path("Card.png"),  32, 32, scale=1.0)

# ── Collect coin positions from map ('c' lower-case) ──────────────────────
COIN_COORDS = []
for r, row in enumerate(MAP_LAYOUT):
    for c, ch in enumerate(row):
        if ch == 'c':
            COIN_COORDS.append([c, r])   # mutable so we can remove on pickup

# ── Decorations ────────────────────────────────────────────────────────────
# Each entry: (image, pixel_x, tile_row)  — row is converted to y in loop below
DECOR_RAW = []

# LEFT SIDE — dead trees near the start
DECOR_RAW.append((tree4, 0,              14))
DECOR_RAW.append((tree3, 3*TILE_SIZE,    14))
DECOR_RAW.append((tree2, 7*TILE_SIZE,    14))

# Grass tufts along left ground
for gx in [1, 5, 9, 13, 16]:
    DECOR_RAW.append((grass1, gx*TILE_SIZE, 14))

# Stone scatter left
DECOR_RAW.append((stone1, 2*TILE_SIZE,   14))
DECOR_RAW.append((stone2, 11*TILE_SIZE,  14))

# Warning pointer sign near gap
DECOR_RAW.append((ptr1, 21*TILE_SIZE, 14))

# MIDDLE PILLAR — boxes stacked
DECOR_RAW.append((box2, 36*TILE_SIZE,        15))
DECOR_RAW.append((box1, 37*TILE_SIZE + 8,    15))
DECOR_RAW.append((box3, 36*TILE_SIZE + 10,   14))  # top box

# Mid platform — small trees + grass
DECOR_RAW.append((tree1, 28*TILE_SIZE, 10))
DECOR_RAW.append((grass2, 30*TILE_SIZE, 10))
DECOR_RAW.append((stone3, 32*TILE_SIZE, 10))

# Floating dark platforms — grass & stone on top
DECOR_RAW.append((grass3, 42*TILE_SIZE, 4))
DECOR_RAW.append((stone1,  44*TILE_SIZE, 4))
DECOR_RAW.append((grass2,  60*TILE_SIZE, 7))
DECOR_RAW.append((stone2,  62*TILE_SIZE, 7))

# RIGHT GROUND — trees + warning pointer
DECOR_RAW.append((tree2, 52*TILE_SIZE, 14))
DECOR_RAW.append((tree3, 57*TILE_SIZE, 14))
DECOR_RAW.append((tree4, 63*TILE_SIZE, 14))
for gx in [50, 55, 60, 65]:
    DECOR_RAW.append((grass1, gx*TILE_SIZE, 14))
DECOR_RAW.append((stone3, 68*TILE_SIZE, 14))
DECOR_RAW.append((ptr2,   70*TILE_SIZE, 14))

# Additional decorations for improved terrain
DECOR_RAW.append((tree1, 45*TILE_SIZE, 10))
DECOR_RAW.append((grass2, 48*TILE_SIZE, 7))
DECOR_RAW.append((grass3, 55*TILE_SIZE, 4))
DECOR_RAW.append((stone1, 58*TILE_SIZE, 10))
DECOR_RAW.append((box2, 62*TILE_SIZE + 8, 15))
DECOR_RAW.append((ptr1, 40*TILE_SIZE, 14))

# Convert row → pixel y (bottom of image sits on ground row)
decorations = []
for img, px, row in DECOR_RAW:
    if img and img.get_width() > 1:
        py = row * TILE_SIZE - img.get_height()
        decorations.append((img, px, py))

# ── Map dimensions ─────────────────────────────────────────────────────────
map_width  = max(len(r) for r in MAP_LAYOUT) * TILE_SIZE
map_height = len(MAP_LAYOUT) * TILE_SIZE

# ── Player ─────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        scale = 1.5
        self.anims = {
            'idle':        load_spritesheet(os.path.join(player_path, "idle.png"),        32, 32, scale),
            'run':         load_spritesheet(os.path.join(player_path, "run.png"),         32, 32, scale),
            'jump':        load_spritesheet(os.path.join(player_path, "jump.png"),        32, 32, scale),
            'double_jump': load_spritesheet(os.path.join(player_path, "double_jump.png"),32, 32, scale),
            'fall':        load_spritesheet(os.path.join(player_path, "fall.png"),        32, 32, scale),
        }
        self.state = 'idle'
        self.frame_idx = 0.0
        self.facing_right = True

        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(x, y, int(16 * scale), int(24 * scale))

        self.vx = 0.0
        self.vy = 0.0
        self.speed = 260
        self.jump_force = -460
        self.gravity = 1200

        self.on_ground = False
        self.jump_count = 0
        self.on_wall_left = False
        self.on_wall_right = False
        self.wall_slide = False
        self.wall_jump_cd = 0.0

    # ── collision helpers ──────────────────────────────────────────────────
    def _tiles_for(self, rect):
        hits = []
        sc = max(0, rect.left  // TILE_SIZE)
        sr = max(0, rect.top   // TILE_SIZE)
        er = min(len(MAP_LAYOUT) - 1, (rect.bottom - 1) // TILE_SIZE)
        for row in range(sr, er + 1):
            row_str = MAP_LAYOUT[row]
            ec = min(len(row_str) - 1, (rect.right - 1) // TILE_SIZE)
            for col in range(sc, ec + 1):
                if 0 <= col < len(row_str) and row_str[col] in SOLID_TILES:
                    hits.append(pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return hits

    def _check_wall(self, direction):
        probe = self.rect.copy()
        probe.x += -2 if direction == 'left' else 2
        return any(True for _ in self._tiles_for(probe))

    # ── jump ──────────────────────────────────────────────────────────────
    def jump(self):
        if self.on_wall_left and not self.on_ground:
            self.vy = self.jump_force; self.vx =  self.speed * 1.2
            self.wall_jump_cd = 0.15;  self.facing_right = True;  return
        if self.on_wall_right and not self.on_ground:
            self.vy = self.jump_force; self.vx = -self.speed * 1.2
            self.wall_jump_cd = 0.15;  self.facing_right = False; return
        if self.jump_count < 2:
            self.vy = self.jump_force
            self.jump_count += 1
            self.on_ground = False
            self.frame_idx = 0

    # ── update ────────────────────────────────────────────────────────────
    def update(self, dt, map_h):
        # Clamp dt to prevent physics explosions on frame drops
        dt = min(dt, 0.05)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.vx = -self.speed; self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx =  self.speed; self.facing_right = True
        else: self.vx = 0

        # left boundary
        if self.x < 0:
            self.x = 0; self.vx = max(0, self.vx)

        if not self.on_ground and self.wall_jump_cd <= 0:
            self.on_wall_left  = self._check_wall('left')
            self.on_wall_right = self._check_wall('right')
            self.wall_slide = (self.on_wall_left or self.on_wall_right) and self.vy > 0
        else:
            self.on_wall_left = self.on_wall_right = self.wall_slide = False
        if self.wall_jump_cd > 0: self.wall_jump_cd = max(0, self.wall_jump_cd - dt)

        self.vy += (self.gravity * 0.3 if self.wall_slide else self.gravity) * dt
        if self.wall_slide: self.vy = min(self.vy, 150)

        # X movement
        self.x += self.vx * dt
        if self.x < 0:
            self.x = 0; self.vx = 0; self.rect.x = 0
        else:
            self.rect.x = int(self.x)
        for h in self._tiles_for(self.rect):
            if self.vx > 0: self.rect.right = h.left;  self.x = float(self.rect.x)
            elif self.vx < 0: self.rect.left = h.right; self.x = float(self.rect.x)

        # Y movement
        self.y += self.vy * dt
        self.rect.y = int(self.y)
        for h in self._tiles_for(self.rect):
            if self.vy > 0: self.rect.bottom = h.top; self.y = float(self.rect.y); self.vy = 0
            elif self.vy < 0: self.rect.top = h.bottom; self.y = float(self.rect.y); self.vy = 0

        # ground check (probe method matching green zone)
        self.rect.y += 1
        ground_hits = self._tiles_for(self.rect)
        self.rect.y -= 1
        if len(ground_hits) > 0 and self.vy >= 0:
            self.on_ground = True
            self.jump_count = 0
        else:
            self.on_ground = False

        # animation
        self._update_state()
        spd = 20 if self.state == 'run' else 12
        self.frame_idx += spd * dt

        # fall reset (fix: also update rect position)
        if self.rect.y > map_h:
            self.x, self.y = 120.0, 200.0
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
            self.vy = 0
            return True  # signal: player fell off map
        return False

    def _update_state(self):
        new = 'idle'
        if not self.on_ground:
            new = 'double_jump' if self.jump_count == 2 else ('jump' if self.vy < 0 else 'fall')
        elif self.vx != 0:
            new = 'run'
        if new != self.state:
            self.state = new; self.frame_idx = 0

    def draw(self, surface, sx, sy):
        frames = self.anims[self.state]
        if not frames: return
        idx = (int(self.frame_idx) % len(frames)) if self.state not in ('jump','fall','double_jump') \
              else min(int(self.frame_idx), len(frames) - 1)
        img = frames[idx]
        if not self.facing_right: img = pygame.transform.flip(img, True, False)
        bx = self.rect.centerx - img.get_width()  // 2 - sx
        by = self.rect.bottom  - img.get_height()      - sy
        surface.blit(img, (bx, by))

# ── HUD ────────────────────────────────────────────────────────────────────
def draw_hud(surface, gs):
    try:
        f_big = pygame.font.SysFont("segoeui",  18, bold=True)
        f_sm  = pygame.font.SysFont("consolas", 13)
    except Exception:
        f_big = f_sm = pygame.font.Font(None, 20)

    # health panel
    panel = pygame.Surface((170, 50), pygame.SRCALPHA)
    pygame.draw.rect(panel, (10, 10, 25, 210), (0, 0, 170, 50), border_radius=10)
    pygame.draw.rect(panel, (60, 180, 220, 90), (0, 0, 170, 50), 2, border_radius=10)
    surface.blit(panel, (10, 10))
    for i in range(gs["max_health"]):
        cx = 28 + i * 34; cy = 35
        filled = i < gs["health"]
        pygame.draw.circle(surface, (0, 200, 255) if filled else (30, 60, 80), (cx, cy), 13, 2)
        pygame.draw.circle(surface, (0, 160, 220) if filled else (15, 40, 60), (cx, cy), 10)
        if filled:
            pygame.draw.circle(surface, (180, 240, 255), (cx - 4, cy - 4), 4)

    # score panel
    sp = pygame.Surface((170, 44), pygame.SRCALPHA)
    pygame.draw.rect(sp, (10, 10, 25, 210), (0, 0, 170, 44), border_radius=10)
    pygame.draw.rect(sp, (60, 180, 220, 90), (0, 0, 170, 44), 2, border_radius=10)
    surface.blit(sp, (SCREEN_W - 180, 10))
    score_lbl = f_big.render(f"SCORE  {gs['score']}", True, (0, 220, 255))
    surface.blit(score_lbl, (SCREEN_W - 178, 22))

    # level name
    lvl = f_sm.render("EXCLUSION  ZONE", True, (80, 200, 255))
    surface.blit(lvl, (SCREEN_W // 2 - lvl.get_width() // 2, 8))

    # controls
    controls = [("[A]/[D] or Arrows", "Move"), ("[Space]/[W]/[↑]", "Double Jump"), ("[ESC]", "Quit")]
    py = SCREEN_H - 20 - len(controls) * 20
    for i, (k, a) in enumerate(controls):
        surface.blit(f_sm.render(k, True, (140, 210, 255)), (20, py + i * 20))
        surface.blit(f_sm.render(a, True, (80,  160, 200)), (160, py + i * 20))

# ── Main level loop ────────────────────────────────────────────────────────
def run_level(surface, game_state=None):
    global SCREEN_W, SCREEN_H, bg_layers

    if game_state is None:
        game_state = {"health": 3, "max_health": 3, "score": 0, "lives": 3}

    player = Player(120, 340)
    clock  = pygame.time.Clock()
    t      = 0.0
    sx = sy = 0.0
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w): player.jump()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = event.w, event.h
                surface = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
                bg_layers.clear()
                for i in range(1, 6):
                    img = load_image(os.path.join(bg_dir, f"{i}.png"))
                    if img.get_width() > 1:
                        bg_layers.append(pygame.transform.scale(img, (SCREEN_W, SCREEN_H)))

        fell_off = player.update(dt, map_height)

        # coin collection
        for entry in COIN_COORDS[:]:
            cx, cy = entry
            cr = pygame.Rect(cx * TILE_SIZE, cy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if player.rect.colliderect(cr):
                game_state["score"] += 10
                COIN_COORDS.remove(entry)

        # fall damage (using return value from update)
        if fell_off:
            game_state["health"] = max(0, game_state["health"] - 1)
            if game_state["health"] <= 0:
                game_state["health"] = game_state["max_health"]
                game_state["lives"]  = max(0, game_state["lives"] - 1)

        # smooth camera
        tx = player.rect.centerx - SCREEN_W // 2
        ty = player.rect.centery - SCREEN_H // 2
        sx += (tx - sx) * 5 * dt
        sy += (ty - sy) * 5 * dt
        sx = max(0, min(sx, map_width  - SCREEN_W))
        sy = max(0, min(sy, map_height - SCREEN_H))

        # ─ draw ─────────────────────────────────────────────────────────
        surface.fill((20, 28, 40))

        # parallax background
        for i, bg in enumerate(bg_layers):
            px = (sx * 0.06 * i) % bg.get_width()
            py = SCREEN_H - bg.get_height() + sy * 0.02 * i
            surface.blit(bg, (-px, py))
            if px > 0: surface.blit(bg, (bg.get_width() - px, py))

        # tiles (drawn before decorations so objects appear on top)
        for ri, row in enumerate(MAP_LAYOUT):
            ry = ri * TILE_SIZE - sy
            if ry < -TILE_SIZE or ry > SCREEN_H + TILE_SIZE: continue
            for ci, sym in enumerate(row):
                if sym in (' ', 'c'): continue
                rx = ci * TILE_SIZE - sx
                if rx < -TILE_SIZE or rx > SCREEN_W + TILE_SIZE: continue
                if sym in loaded_tiles:
                    surface.blit(loaded_tiles[sym], (rx, ry))

        # decorations (drawn after tiles so objects appear on top of platforms)
        for img, ox, oy in decorations:
            bx = ox - sx; by = oy - sy
            if -img.get_width() < bx < SCREEN_W and -img.get_height() < by < SCREEN_H:
                surface.blit(img, (bx, by))

        # animated coins
        if coin_frames:
            cf = coin_frames[int(t * 8) % len(coin_frames)]
            for entry in COIN_COORDS:
                cx, cy = entry
                bx = cx * TILE_SIZE - sx + (TILE_SIZE - cf.get_width())  // 2
                by = cy * TILE_SIZE - sy + (TILE_SIZE - cf.get_height()) // 2
                if -32 < bx < SCREEN_W and -32 < by < SCREEN_H:
                    # gentle float
                    surface.blit(cf, (bx, by + int(math.sin(t * 4 + cx) * 3)))

        # animated cards on the right platform
        if card_frames:
            kf = card_frames[int(t * 5) % len(card_frames)]
            for cpx, cpy in [(62*TILE_SIZE, 6), (64*TILE_SIZE, 6)]:
                bx = cpx - sx; by = cpy * TILE_SIZE - kf.get_height() - sy
                if -64 < bx < SCREEN_W and -64 < by < SCREEN_H:
                    surface.blit(kf, (bx, by + int(math.sin(t * 3 + cpx) * 3)))

        draw_hud(surface, game_state)
        player.draw(surface, int(sx), int(sy))
        pygame.display.flip()

    return "quit"

# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_level(screen)
    pygame.quit()
    sys.exit()
