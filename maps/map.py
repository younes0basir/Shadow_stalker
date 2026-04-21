"""
map.py  ·  Mossy Forest Platformer  (atmospheric remake)
=========================================================
Reference aesthetic: soft teal underwater-forest sky, rounded mossy
floating islands, delicate plant decorations, glowing white particles.

Controls
--------
  A / D  or  ← →   move
  Space / W / ↑     jump  (double jump)
  ESC               quit
"""

import os, sys, math, random
import pygame
from functools import lru_cache

pygame.init()
SCREEN_W, SCREEN_H = 1280, 720
if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
else:
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    else:
        SCREEN_W, SCREEN_H = screen.get_size()
pygame.display.set_caption("🌿  Mossy Forest")

# ─── paths ────────────────────────────────────────────────────
ROOT        = os.path.dirname(__file__)
PARENT_DIR  = os.path.dirname(ROOT)
MOSSY       = os.path.join(PARENT_DIR, "assets", "mossy")
PLANT_DIR   = os.path.join(MOSSY, "Plant Animations")
PLAYER_PATH = os.path.join(PARENT_DIR, "assets", "MainCharacters", "VirtualGuy")

# ─── physics ──────────────────────────────────────────────────
GRAVITY    = 1400
JUMP_FORCE = -520
SPEED      = 270
TILE_SIZE  = 32          # collision / world grid size

# ─── UI palette ───────────────────────────────────────────────
UI_TEAL      = (60, 180, 160)
UI_TEAL_DIM  = (30,  90,  80)
UI_GOLD      = (255, 210,  80)
UI_WHITE     = (230, 245, 240)
UI_PANEL     = (10,  30,  35, 200)   # RGBA
UI_ACCENT    = (100, 230, 200)

# ═════════════════════════════════════════════════════════════
#  HELPERS
# ═════════════════════════════════════════════════════════════

def load_img(path, scale=1):
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale != 1:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (max(1,int(w*scale)), max(1,int(h*scale))))
        return img
    except Exception:
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        s.fill((80, 160, 60))
        return s

def load_sheet_frames(path, fw, fh, scale=1):
    try:
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for x in range(0, sheet.get_width(), fw):
            rect = pygame.Rect(x, 0, fw, fh)
            surf = sheet.subsurface(rect).copy()
            if scale != 1:
                surf = pygame.transform.scale(surf, (max(1,int(fw*scale)), max(1,int(fh*scale))))
            frames.append(surf)
        return frames
    except Exception:
        s = pygame.Surface((max(1,int(fw*scale)), max(1,int(fh*scale))), pygame.SRCALPHA)
        s.fill((200, 80, 80))
        return [s]

def slice_sheet_grid(path, tw, th):
    """Return grid[row][col] of surfaces sliced from a sprite sheet."""
    sheet = pygame.image.load(path).convert_alpha()
    sw, sh = sheet.get_size()
    grid = []
    for r in range(sh // th):
        row = []
        for c in range(sw // tw):
            rect = pygame.Rect(c * tw, r * th, tw, th)
            # Use subsurface copy to perfectly preserve the alpha channel 
            # without blending artifacts that cause dark boxes
            cell = sheet.subsurface(rect).copy()
            row.append(cell)
        grid.append(row)
    return grid

def load_plant_anim(name):
    folder = os.path.join(PLANT_DIR, name)
    frames = []
    if not os.path.isdir(folder):
        return frames
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith(".png"):
            try:
                frames.append(pygame.image.load(os.path.join(folder, f)).convert_alpha())
            except Exception:
                pass
    return frames

# ═════════════════════════════════════════════════════════════
#  BACKGROUND  — pure drawn gradient (teal/cyan atmospheric)
# ═════════════════════════════════════════════════════════════

def make_gradient_bg(w, h):
    """Draw a soft teal underwater-sky gradient."""
    surf = pygame.Surface((w, h))
    top_col    = (14, 48, 68)     # deep teal top
    mid_col    = (22, 88, 110)    # mid cyan
    bottom_col = (16, 60, 72)     # slightly darker bottom
    for y in range(h):
        t = y / h
        if t < 0.6:
            tt = t / 0.6
            r = int(top_col[0] + (mid_col[0]-top_col[0]) * tt)
            g = int(top_col[1] + (mid_col[1]-top_col[1]) * tt)
            b = int(top_col[2] + (mid_col[2]-top_col[2]) * tt)
        else:
            tt = (t - 0.6) / 0.4
            r = int(mid_col[0] + (bottom_col[0]-mid_col[0]) * tt)
            g = int(mid_col[1] + (bottom_col[1]-mid_col[1]) * tt)
            b = int(mid_col[2] + (bottom_col[2]-mid_col[2]) * tt)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
    return surf

# ═════════════════════════════════════════════════════════════
#  LOAD ASSETS
# ═════════════════════════════════════════════════════════════
print("Loading assets …")

# ── Gradient background ───────────────────────────────────────
BG_GRAD = make_gradient_bg(SCREEN_W, SCREEN_H)

# ── Background decoration layers ──────────────────────────────
# Used very subtly as blurred atmospheric layers
def load_bg_layer(fname, target_w, target_h, alpha):
    p = os.path.join(MOSSY, fname)
    try:
        img = pygame.image.load(p).convert_alpha()
        img = pygame.transform.scale(img, (target_w, target_h))
        img.set_alpha(alpha)
        return img
    except Exception:
        return None

# We load them at double-wide so parallax can tile seamlessly
BG_HILLS = load_bg_layer("Mossy - MossyHills.png",  SCREEN_W*2, SCREEN_H, 55)
BG_DECO  = load_bg_layer("Mossy - BackgroundDecoration.png", SCREEN_W*2, SCREEN_H, 30)

# ── Floating Island platform sprites ─────────────────────────
# FloatingPlatforms.png  2048×2048  → 4×4 grid of 512×512 sprites
# All 16 cells contain rich mossy island art
_fp_grid = slice_sheet_grid(os.path.join(MOSSY, "Mossy - FloatingPlatforms.png"), 512, 512)

# Scale platforms down to game-friendly sizes: ~160-260 px wide
# We want ~0.4 scale for large, 0.28 for small
PLATFORM_SPRITES = []
SCALES = [0.38, 0.30, 0.34, 0.26,
          0.40, 0.32, 0.28, 0.36,
          0.36, 0.38, 0.34, 0.28,
          0.32, 0.30, 0.38, 0.36]

for ri, row in enumerate(_fp_grid):
    for ci, cell in enumerate(row):
        sc = SCALES[ri*4 + ci]
        w, h = int(512*sc), int(512*sc)
        PLATFORM_SPRITES.append(pygame.transform.scale(cell, (w, h)))

print(f"  {len(PLATFORM_SPRITES)} platform sprites loaded")

# ── Spikes, Vines & Chompers (Hazards/Decorations) ───────────
_dh_grid = slice_sheet_grid(os.path.join(MOSSY, "Mossy - Decorations&Hazards.png"), 512, 512)
ENV_OBJECTS = []
# Hand-picked dense cells from our scan of Decorations&Hazards
for r, c in [(1,1), (1,2), (1,4), (1,6), (2,1), (2,2), (2,5), (5,4), (5,5), (5,6), (6,3), (6,4), (6,5), (7,4), (7,5)]:
    try:
        spr = _dh_grid[r][c]
        ENV_OBJECTS.append(pygame.transform.scale(spr, (int(512 * 0.32), int(512 * 0.32))))
    except IndexError:
        pass
print(f"  {len(ENV_OBJECTS)} hazard/decor sprites loaded")

_hp_grid = slice_sheet_grid(os.path.join(MOSSY, "Mossy - Hanging Plants.png"), 512, 512)
HANGING_VINES = []
for r, c in [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)]:
    try:
        spr = _hp_grid[r][c]
        HANGING_VINES.append(pygame.transform.scale(spr, (int(512 * 0.4), int(512 * 0.4))))
    except IndexError:
        pass
print(f"  {len(HANGING_VINES)} hanging vines loaded")

# ── Plant animations ─────────────────────────────────────────
# Plants are 512×512 px. We display at ~8% = ~40px tall — tasteful.
PLANT_NAMES = [
    "BlueFlower1", "BlueFlower2",
    "Plant 1", "Plant 2", "Plant 3", "Plant 4",
    "Plant 5", "Plant 6", "Plant 7",
    "Plant Wind 1", "PlantJump", "PlantJump2",
]
PLANT_ANIM   = {}   # name → list[Surface full-size]
PLANT_SCALED = {}   # name → list[Surface scaled]

PLANT_SCALE = 0.10   # 512 * 0.10 = ~51 px — small decorative
for pn in PLANT_NAMES:
    frames = load_plant_anim(pn)
    if frames:
        PLANT_ANIM[pn]   = frames
        # Pre-scale every 3rd frame to keep memory manageable
        scaled = []
        for i, f in enumerate(frames):
            w, h = f.get_size()
            scaled.append(pygame.transform.scale(f, (max(1,int(w*PLANT_SCALE)), max(1,int(h*PLANT_SCALE)))))
        PLANT_SCALED[pn] = scaled

print(f"  {len(PLANT_SCALED)} plant animations loaded")

# ── Player ────────────────────────────────────────────────────
PLAYER_ANIMS = {}
for state, fname in [
    ('idle','idle.png'), ('run','run.png'), ('jump','jump.png'),
    ('double_jump','double_jump.png'), ('fall','fall.png')]:
    PLAYER_ANIMS[state] = load_sheet_frames(
        os.path.join(PLAYER_PATH, fname), 32, 32, scale=2.0)

print("  Player animations loaded")

# ── Fruit collectibles ────────────────────────────────────────
FRUIT_DIR  = os.path.join(PARENT_DIR, "assets", "Items", "Fruits")
FRUIT_NAMES = ["Apple","Bananas","Cherries","Kiwi","Melon",
               "Orange","Pineapple","Strawberry"]
FRUIT_FRAMES = {}   # name → list[Surface]
for fn in FRUIT_NAMES:
    p = os.path.join(FRUIT_DIR, fn + ".png")
    try:
        sheet = pygame.image.load(p).convert_alpha()
        fw = sheet.get_height()           # fruits are square frames
        frames = []
        for x in range(0, sheet.get_width(), fw):
            rect = pygame.Rect(x, 0, fw, fw)
            cell = sheet.subsurface(rect).copy()
            # Scale up to nice visible size
            cell = pygame.transform.scale(cell, (28, 28))
            frames.append(cell)
        if frames:
            FRUIT_FRAMES[fn] = frames
    except Exception:
        pass
print(f"  {len(FRUIT_FRAMES)} fruit types loaded")

# ── Fonts  ─────────────────────────────────────────────────────
try:
    FONT_TITLE  = pygame.font.SysFont("segoeui",  36, bold=True)
    FONT_HUD    = pygame.font.SysFont("segoeui",  18, bold=True)
    FONT_SMALL  = pygame.font.SysFont("consolas", 13)
    FONT_HINT   = pygame.font.SysFont("segoeui",  13)
    FONT_PAUSE  = pygame.font.SysFont("segoeui",  28, bold=True)
except Exception:
    FONT_TITLE = FONT_HUD = FONT_SMALL = FONT_HINT = FONT_PAUSE = pygame.font.Font(None, 24)

print("All assets ready.\n")

# ═════════════════════════════════════════════════════════════
#  WORLD  — Platform objects
# ═════════════════════════════════════════════════════════════
# Each platform is a dict:
#   sprite_idx  → which PLATFORM_SPRITES entry to draw
#   wx, wy      → world position of top-left of sprite
#   col_rect    → pygame.Rect for collision (top surface only, world-space)
#   plants      → list of decoration dicts placed on top

WORLD_W = 4000   # horizontal extent of the level
WORLD_H = 1400

# Ground floor: a wide mossy island chain at the bottom
# We'll represent it as very large platform strips

# ── build_platform helper ─────────────────────────────────────
def make_platform(sprite_idx, wx, wy, col_top_ratio=0.38):
    """
    col_top_ratio: what fraction down from sprite top is the walkable surface.
    The mossy islands have a lot of transparent space above the moss top.
    """
    spr = PLATFORM_SPRITES[sprite_idx]
    sw, sh = spr.get_size()
    col_y  = int(sh * col_top_ratio)       # pixel row of the top surface
    col_h  = int(sh * (1.0 - col_top_ratio))
    return {
        "sprite_idx": sprite_idx,
        "wx": wx, "wy": wy,
        "col_rect": pygame.Rect(wx + int(sw*0.02), wy + col_y,
                                int(sw * 0.96), col_h),
        "plants": [],
        "env_objs": [],
        "hanging": [],
    }

# ── Define level platforms ────────────────────────────────────
random.seed(99)

PLATFORMS = []

def add_plat(si, wx, wy, ratio=0.38):
    PLATFORMS.append(make_platform(si, wx, wy, ratio))

# Diagonal dungeon: the route zig-zags upward and downward through
# staggered chambers instead of progressing as flat horizontal floors.
# S = spawn, U = upward exit chamber, D = downward exit chamber,
# X = solid block, P = isolated helper platform.
DUNGEON_GRID = [
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "X                                                      U        X",
    "X                                               XXXXXXXX        X",
    "X                                        P                      X",
    "X                                   XXXXXXXXXXXX               XX",
    "X                            P                                   X",
    "X                       XXXXXXXXXXXX                             X",
    "X                P                                               X",
    "X           XXXXXXXXXXXX                        P                X",
    "X    P                                                XXXXXXXXXXX",
    "X    XXXXXXXXXXXX                                              D X",
    "X                  XXXXXXXXXXXX                                 XX",
    "X                           P                                    X",
    "X                      XXXXXXXXXXXX                              X",
    "X               P                                                X",
    "X          XXXXXXXXXXXX                             P             X",
    "X   P                                                           XX",
    "X   XXXXXXXXXXXX                                                 X",
    "X                XXXXXXXXXXXX                                    X",
    "X                         P                                       X",
    "X                    XXXXXXXXXXXX                                X",
    "X             P                                                   X",
    "X        XXXXXXXXXXXX                                             X",
    "X S  P                                                            X",
    "X XXXXXXXXXXXX                                                    X",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
]

CELL_W, CELL_H = 170, 160
# Redefine world bounds based on grid size
WORLD_W = len(DUNGEON_GRID[0]) * CELL_W
WORLD_H = len(DUNGEON_GRID)    * CELL_H
ground_y = WORLD_H - 200

spawn_cord = (300, 300)
up_exit_rect = None
down_exit_rect = None

for r, row in enumerate(DUNGEON_GRID):
    for c, char in enumerate(row):
        px = c * CELL_W
        py = r * CELL_H
        if char == 'S':
            spawn_cord = (px, py)
        elif char == 'X':
            # Solid cavern block — single sprite, no duplicates (avoids dark box artifacts)
            si = random.choice([0, 1, 2, 4, 5, 8, 9, 12, 13])
            add_plat(si, px, py, ratio=0.15)
        elif char == 'P':
            # Solitary floating platform — only visually clean sprites
            si = random.choice([0, 1, 2, 4, 5, 8, 9, 12, 13])
            add_plat(si, px + random.randint(-20, 20), py + random.randint(40, 60), ratio=0.30)
        elif char == 'U':
            up_exit_rect = pygame.Rect(px, py, CELL_W, CELL_H)
        elif char == 'D':
            down_exit_rect = pygame.Rect(px, py, CELL_W, CELL_H)


# ═════════════════════════════════════════════════════════════
#  PLANT DECORATIONS
# ═════════════════════════════════════════════════════════════
plant_names_list = list(PLANT_SCALED.keys())

def _add_plants_to_platform(plat):
    if not plant_names_list:
        return
    spr      = PLATFORM_SPRITES[plat["sprite_idx"]]
    sw, sh   = spr.get_size()
    cr       = plat["col_rect"]
    n_plants = random.randint(2, 6)
    for _ in range(n_plants):
        name   = random.choice(plant_names_list)
        frames = PLANT_SCALED[name]
        fw, fh = frames[0].get_size()
        # place along the top surface
        px = cr.left + random.randint(0, max(1, cr.width - fw))
        py = cr.top  - fh + random.randint(0, 8)
        plat["plants"].append({
            "frames": frames,
            "wx": px, "wy": py,
            "fc":  random.uniform(0, len(frames)),
            "spd": random.uniform(6, 14),
            "bob_phase": random.uniform(0, math.pi*2),
        })

def _add_env_objects_to_platform(plat, _rng):
    """Add spiky hazards, weird plants, or hanging vines near the platform."""
    if ENV_OBJECTS and _rng.random() < 0.45:
        # Add 1-2 environment objects
        for _ in range(_rng.randint(1, 2)):
            obj_img = _rng.choice(ENV_OBJECTS)
            cr = plat["col_rect"]
            ow, oh = obj_img.get_size()
            # Position generally around the platform, sometimes above, sometimes to side
            ox = cr.left + _rng.randint(-ow//2, cr.width - ow//2)
            oy = cr.top - oh + _rng.randint(0, oh//2)
            plat["env_objs"].append({"img": obj_img, "wx": ox, "wy": oy})
    
    if HANGING_VINES and _rng.random() < 0.35:
        # Add a hanging vine hanging DOWN from the platform bottom
        vine_img = _rng.choice(HANGING_VINES)
        cr = plat["col_rect"]
        vw, vh = vine_img.get_size()
        vx_min = -vw//4
        vx_max = max(vx_min + 1, cr.width - vw*3//4)
        vx = cr.left + _rng.randint(vx_min, vx_max)
        # Hang it below the bottom
        vy = cr.bottom - _rng.randint(0, 20)
        plat["hanging"].append({"img": vine_img, "wx": vx, "wy": vy})

random.seed(42)
for plat in PLATFORMS:
    _add_plants_to_platform(plat)
    _add_env_objects_to_platform(plat, random)

# Count all decorations
total_plants = sum(len(p["plants"]) for p in PLATFORMS)
total_env = sum(len(p["env_objs"]) for p in PLATFORMS)
total_hang = sum(len(p["hanging"]) for p in PLATFORMS)
print(f"Placed {total_plants} small plants, {total_env} world objects, {total_hang} vines.")

# ═════════════════════════════════════════════════════════════
#  AMBIENT PARTICLES  (white glowing sparkles like reference)
# ═════════════════════════════════════════════════════════════
SPARKS = []
random.seed(7)
for _ in range(80):
    SPARKS.append({
        "x":  random.uniform(0, WORLD_W),
        "y":  random.uniform(0, WORLD_H - 300),
        "vx": random.uniform(-12, 12),
        "vy": random.uniform(-6,   6),
        "phase": random.uniform(0, math.pi*2),
        "r":  random.uniform(2, 5),
        # white-cyan tint
        "col": random.choice([(255,255,255), (200,240,255), (210,255,230)]),
    })

# ═════════════════════════════════════════════════════════════
#  COLLISION SYSTEM — grid-based for walls, sprite-based for floaters
# ═════════════════════════════════════════════════════════════

# 1) Exact grid-aligned collision rects for ALL solid 'X' tiles (zero gaps)
SOLID_GRID_RECTS = []
for r, row in enumerate(DUNGEON_GRID):
    for c, char in enumerate(row):
        if char == 'X':
            SOLID_GRID_RECTS.append(
                pygame.Rect(c * CELL_W, r * CELL_H, CELL_W, CELL_H)
            )

# 2) Sprite-derived col_rects only for floating 'P' platforms
FLOATER_RECTS = []
for plat in PLATFORMS:
    cr = plat["col_rect"]
    # Only include if it's NOT already covered by a grid rect
    is_grid = False
    for gr in SOLID_GRID_RECTS:
        if gr.contains(cr):
            is_grid = True
            break
    if not is_grid:
        FLOATER_RECTS.append(cr)

# 3) Merge into one master list
ALL_RECTS = SOLID_GRID_RECTS + FLOATER_RECTS

# 4) Build spatial hash for fast lookup (bucket size = CELL_W)
SPATIAL_BUCKET = CELL_W
SPATIAL_HASH = {}
for rect in ALL_RECTS:
    # Which grid buckets does this rect touch?
    x0 = rect.left   // SPATIAL_BUCKET
    x1 = rect.right  // SPATIAL_BUCKET
    y0 = rect.top    // SPATIAL_BUCKET
    y1 = rect.bottom // SPATIAL_BUCKET
    for bx in range(x0, x1 + 1):
        for by in range(y0, y1 + 1):
            key = (bx, by)
            if key not in SPATIAL_HASH:
                SPATIAL_HASH[key] = []
            SPATIAL_HASH[key].append(rect)

def spatial_query(rect):
    """Return all collision rects that could overlap with `rect`."""
    x0 = rect.left   // SPATIAL_BUCKET
    x1 = rect.right  // SPATIAL_BUCKET
    y0 = rect.top    // SPATIAL_BUCKET
    y1 = rect.bottom // SPATIAL_BUCKET
    seen = set()
    result = []
    for bx in range(x0, x1 + 1):
        for by in range(y0, y1 + 1):
            for r in SPATIAL_HASH.get((bx, by), []):
                rid = id(r)
                if rid not in seen:
                    seen.add(rid)
                    if rect.colliderect(r):
                        result.append(r)
    return result

print(f"Collision: {len(SOLID_GRID_RECTS)} grid rects + {len(FLOATER_RECTS)} floater rects = {len(ALL_RECTS)} total")

# ═════════════════════════════════════════════════════════════
#  FRUIT COLLECTIBLES (scattered across all platforms)
# ═════════════════════════════════════════════════════════════
FRUIT_LIST = []    # each: {name, x, y, frames, fc, collected, collect_t}

if FRUIT_FRAMES:
    fruit_names_k = list(FRUIT_FRAMES.keys())
    _frng = random.Random(55)
    for plat in PLATFORMS:
        if _frng.random() < 0.35:   # ~35% of platforms get a fruit
            cr  = plat["col_rect"]
            fx  = cr.left + _frng.randint(10, max(11, cr.width - 40))
            fy  = cr.top  - 36
            fnm = _frng.choice(fruit_names_k)
            FRUIT_LIST.append({
                "name":      fnm,
                "x": float(fx), "y": float(fy),
                "frames":    FRUIT_FRAMES[fnm],
                "fc":        _frng.uniform(0, 16),
                "collected": False,
                "collect_t": 0.0,
            })
print(f"Spawned {len(FRUIT_LIST)} fruit collectibles.")

# ═════════════════════════════════════════════════════════════
#  PLAYER
# ═════════════════════════════════════════════════════════════
class Player:
    W, H = 28, 44    # hitbox

    def __init__(self, x, y):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.facing_right = True
        self.on_ground    = False
        self.jump_count   = 0
        self.rect         = pygame.Rect(int(x), int(y), self.W, self.H)
        self.state        = 'idle'
        self.frame_idx    = 0.0
        # ── game stats ────────────────────────────────────────
        self.health       = 3        # hearts (max 3)
        self.score        = 0
        self.distance     = 0        # rightmost x reached
        self.invincible   = 0.0      # seconds of iframes after hurt
        self.spawn_x      = float(x)
        self.spawn_y      = float(y)

    def _hits(self, rect):
        return spatial_query(rect)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.vx = -SPEED; self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx =  SPEED; self.facing_right = True
        else:
            self.vx = 0

        self.vy = min(self.vy + GRAVITY * dt, 1200)

        # X
        self.x += self.vx * dt
        self.rect.x = int(self.x)
        for h in self._hits(self.rect):
            if self.vx > 0: self.rect.right = h.left
            else:           self.rect.left  = h.right
            self.x = float(self.rect.x)

        # Y
        self.y += self.vy * dt
        self.rect.y = int(self.y)
        for h in self._hits(self.rect):
            if self.vy > 0: self.rect.bottom = h.top;  self.vy = 0
            else:           self.rect.top    = h.bottom; self.vy = 0
            self.y = float(self.rect.y)

        # Ground probe
        self.rect.y += 3
        self.on_ground = bool(self._hits(self.rect))
        self.rect.y -= 3
        if self.on_ground:
            self.jump_count = 0

        # Clamp to world
        self.rect.x = max(0, min(self.rect.x, WORLD_W - self.W))
        if self.rect.y > WORLD_H + 400:
            self.health = max(0, self.health - 1)
            self.x = self.spawn_x
            self.y = self.spawn_y
            self.vy = 0
            self.invincible = 2.0
        # Track distance
        self.distance = max(self.distance, self.rect.x)
        # Iframes countdown
        if self.invincible > 0:
            self.invincible -= dt

        # Anim state
        ns = self.state
        if not self.on_ground:
            ns = 'double_jump' if self.jump_count==2 else ('jump' if self.vy<0 else 'fall')
        else:
            ns = 'run' if self.vx!=0 else 'idle'
        if ns != self.state:
            self.state, self.frame_idx = ns, 0.0
        spd = 20 if self.state == 'run' else 12
        self.frame_idx += spd * dt

    def jump(self):
        if self.jump_count < 2:
            self.vy = JUMP_FORCE
            self.jump_count += 1
            self.on_ground = False
            self.frame_idx = 0.0

    def draw(self, surf, sx, sy):
        frames = PLAYER_ANIMS[self.state]
        if not frames: return
        if self.state in ('jump','fall','double_jump'):
            idx = min(int(self.frame_idx), len(frames)-1)
        else:
            idx = int(self.frame_idx) % len(frames)
        img = frames[idx]
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        bx = self.rect.centerx - img.get_width()//2 - sx
        by = self.rect.bottom   - img.get_height()   - sy
        surf.blit(img, (bx, by))

# ═════════════════════════════════════════════════════════════
#  ATMOSPHERIC GLOW (radial soft-light circles in bg)
# ═════════════════════════════════════════════════════════════
GLOW_SPOTS = []
random.seed(12)
for _ in range(14):
    GLOW_SPOTS.append({
        "x": random.uniform(0, WORLD_W),
        "y": random.uniform(200, WORLD_H - 300),
        "r": random.randint(120, 280),
        "col": random.choice([(40,120,140), (30,100,120), (50,130,100)]),
        "phase": random.uniform(0, math.pi*2),
    })

def draw_glow(surf, cx, cy, radius, color, alpha):
    """Draw a soft radial glow circle."""
    gsurf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for ri in range(radius, 0, -4):
        a = int(alpha * (1 - ri/radius)**1.5)
        pygame.draw.circle(gsurf, (*color, a), (radius, radius), ri)
    surf.blit(gsurf, (cx - radius, cy - radius), special_flags=pygame.BLEND_RGBA_ADD)

# ═════════════════════════════════════════════════════════════
#  UI DRAWING HELPERS
# ═════════════════════════════════════════════════════════════

def draw_panel(surf, rect, radius=10):
    """Glassmorphism panel: dark translucent rounded rect + subtle border."""
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, UI_PANEL, (0,0,*rect.size), border_radius=radius)
    pygame.draw.rect(panel, (*UI_TEAL, 80), (0,0,*rect.size), 2, border_radius=radius)
    surf.blit(panel, rect.topleft)

def draw_health_orbs(surf, health, max_health=3, x=18, y=18):
    """Draw glowing heart orbs for health."""
    orb_r   = 13
    spacing = 34
    for i in range(max_health):
        cx = x + i * spacing + orb_r
        cy = y + orb_r
        filled = i < health
        # Glow ring
        if filled:
            gc = pygame.Surface((orb_r*4, orb_r*4), pygame.SRCALPHA)
            pygame.draw.circle(gc, (80,220,160,60), (orb_r*2,orb_r*2), orb_r*2)
            surf.blit(gc, (cx-orb_r*2, cy-orb_r*2))
        # Outer ring
        pygame.draw.circle(surf, UI_TEAL if filled else UI_TEAL_DIM, (cx,cy), orb_r, 2)
        # Inner fill
        col_in = (60,200,140) if filled else (20,55,50)
        pygame.draw.circle(surf, col_in, (cx,cy), orb_r-3)
        # Highlight
        if filled:
            pygame.draw.circle(surf, (180,255,220), (cx-4, cy-4), 4)

def draw_score(surf, score, x, y):
    """Score badge."""
    lbl  = FONT_HUD.render(f"✦ {score:05d}", True, UI_GOLD)
    r    = pygame.Rect(x, y, lbl.get_width()+20, lbl.get_height()+10)
    draw_panel(surf, r)
    surf.blit(lbl, (x+10, y+5))

def draw_jump_indicator(surf, jump_count, x, y):
    """Show remaining jumps as small glowing dots."""
    for i in range(2):
        cx = x + i*20
        avail = i < (2 - jump_count)
        col = UI_ACCENT if avail else (30,60,55)
        pygame.draw.circle(surf, col, (cx, y), 7)
        if avail:
            pygame.draw.circle(surf, (200,255,240), (cx-2, y-2), 3)
        pygame.draw.circle(surf, UI_TEAL, (cx, y), 7, 2)

def draw_minimap(surf, player, platforms, isx, isy,
                 mm_x=None, mm_y=None, mm_w=160, mm_h=80):
    """Draw a small minimap in the bottom-right corner."""
    if mm_x is None: mm_x = surf.get_width()  - mm_w - 14
    if mm_y is None: mm_y = surf.get_height() - mm_h - 14

    draw_panel(surf, pygame.Rect(mm_x-4, mm_y-4, mm_w+8, mm_h+8), radius=8)

    scale_x = mm_w / WORLD_W
    scale_y = mm_h / WORLD_H

    # Platform dots
    for plat in platforms:
        cr  = plat["col_rect"]
        px  = int(cr.centerx * scale_x)
        py  = int(cr.centery * scale_y)
        pw  = max(2, int(cr.width * scale_x))
        pygame.draw.rect(surf, (60,140,100), (mm_x+px-pw//2, mm_y+py-1, pw, 2))

    # Viewport rect
    vx = int(isx * scale_x)
    vy = int(isy * scale_y)
    vw = int(SCREEN_W * scale_x)
    vh = int(SCREEN_H * scale_y)
    pygame.draw.rect(surf, (*UI_TEAL, 80), (mm_x+vx, mm_y+vy, vw, vh))
    pygame.draw.rect(surf, UI_TEAL, (mm_x+vx, mm_y+vy, vw, vh), 1)

    # Player dot
    ppx = int(player.rect.centerx * scale_x)
    ppy = int(player.rect.centery * scale_y)
    pygame.draw.circle(surf, UI_GOLD, (mm_x+ppx, mm_y+ppy), 3)

    lbl = FONT_SMALL.render("MAP", True, UI_TEAL)
    surf.blit(lbl, (mm_x, mm_y - 16))

def draw_controls_hint(surf, y):
    """Compact control hints at the bottom."""
    hints = [
        ("A / D",     "Move"),
        ("Space / W", "Jump ×2"),
        ("P",         "Pause"),
        ("ESC",       "Quit"),
    ]
    total_w = sum(FONT_HINT.size(f"{k}  {v}")[0] + 32 for k,v in hints)
    xc = (surf.get_width() - total_w) // 2
    pad = 5
    for key, act in hints:
        k_surf = FONT_HINT.render(key, True, UI_TEAL)
        a_surf = FONT_HINT.render(act, True, UI_WHITE)
        w = k_surf.get_width() + a_surf.get_width() + 20
        bg = pygame.Surface((w+pad*2, 20), pygame.SRCALPHA)
        bg.fill((10,30,35,160))
        pygame.draw.rect(bg, (*UI_TEAL,100), (0,0,w+pad*2,20), 1, border_radius=4)
        surf.blit(bg, (xc, y))
        surf.blit(k_surf, (xc+pad, y+2))
        surf.blit(a_surf, (xc+pad+k_surf.get_width()+6, y+2))
        xc += w + pad*2 + 10

def draw_pause_menu(surf):
    """Full pause overlay."""
    # Dim
    dim = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    dim.fill((5, 20, 25, 160))
    surf.blit(dim, (0,0))

    # Panel
    pw, ph = 360, 260
    px = (surf.get_width()  - pw) // 2
    py = (surf.get_height() - ph) // 2
    draw_panel(surf, pygame.Rect(px, py, pw, ph), radius=16)

    # Title
    title = FONT_TITLE.render("⏸  Paused", True, UI_TEAL)
    surf.blit(title, (px + (pw - title.get_width())//2, py + 24))

    # Divider
    pygame.draw.line(surf, (*UI_TEAL, 80),
                     (px+20, py+74), (px+pw-20, py+74), 1)

    items = [
        ("R  –  Resume",  UI_WHITE),
        ("K  –  Restart", UI_ACCENT),
        ("ESC – Quit",    (200, 120, 120)),
    ]
    for i, (text, col) in enumerate(items):
        lbl = FONT_PAUSE.render(text, True, col)
        surf.blit(lbl, (px + (pw - lbl.get_width())//2, py + 96 + i * 54))

def draw_title_card(surf, alpha):
    """Cinematic intro title with fade."""
    if alpha <= 0: return
    overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    overlay.fill((8, 25, 30, alpha))
    surf.blit(overlay, (0,0))

    if alpha > 60:
        t_alpha = min(255, alpha)
        title = FONT_TITLE.render("🌿  Mossy Forest", True, (*UI_TEAL, t_alpha))
        sub   = FONT_HUD.render("Explore the enchanted grove", True, (*UI_WHITE, t_alpha))
        tx = (surf.get_width()  - title.get_width())  // 2
        ty = (surf.get_height() - title.get_height()) // 2 - 20
        surf.blit(title, (tx, ty))
        surf.blit(sub,   ((surf.get_width()-sub.get_width())//2, ty+52))

def collect_near_fruits(player_rect, score_ref):
    """Check fruit pickup — returns new score."""
    score = score_ref
    prect = player_rect.inflate(16, 16)
    for fr in FRUIT_LIST:
        if fr["collected"]: continue
        frect = pygame.Rect(int(fr["x"])-14, int(fr["y"])-14, 28, 28)
        if prect.colliderect(frect):
            fr["collected"]  = True
            fr["collect_t"]  = 0.0
            score += 100
    return score

# ═════════════════════════════════════════════════════════════
def run_level(surface, game_state=None):
    global SCREEN_W, SCREEN_H, BG_GRAD
    
    if game_state is None:
        game_state = {"health": 3, "max_health": 3, "score": 0, "lives": 3}
    
    # Fix coordinate so we don't accidentally spawn too far left and re-trigger portal
    spawn_x = max(100.0, float(spawn_cord[0]))
    
    player = Player(spawn_x, spawn_cord[1])
    player.spawn_x = spawn_x
    player.spawn_y = float(player.rect.y)
    player.health = game_state["health"]
    player.score  = game_state["score"]
    
    clock  = pygame.time.Clock()
    sx, sy = 0.0, 0.0   # camera
    t      = 0.0
    paused = False
    title_alpha = 255.0   # fade-in title counter (255→0)
    
    run = True
    while run:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        if not paused: t += dt

        # ── events ────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_r and paused:
                    paused = False
                elif event.key == pygame.K_k and paused:
                    # Restart
                    for fr in FRUIT_LIST: fr["collected"] = False
                    player = Player(player.spawn_x, player.spawn_y)
                    player.spawn_x = player.x
                    player.spawn_y = player.y
                    sx, sy = 0.0, 0.0
                    t = 0.0
                    title_alpha = 200.0
                    paused = False
                elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    if not paused: player.jump()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = event.w, event.h
                surface = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
                BG_GRAD = make_gradient_bg(SCREEN_W, SCREEN_H)

        # ── update ────────────────────────────────────────────────
        if not paused:
            player.update(dt)
            player.score = collect_near_fruits(player.rect, player.score)
            # Score ticks up based on distance
            player.score += int(player.vx * dt * 0.5) if player.vx > 0 else 0
            # Title fade
            if title_alpha > 0:
                title_alpha = max(0, title_alpha - 120 * dt)
                
            # Transition conditions for the diagonal dungeon route:
            # moving into the top chamber means climbing out,
            # while the lower-right chamber means descending deeper.
            if up_exit_rect and player.rect.colliderect(up_exit_rect):
                game_state["health"] = player.health
                game_state["score"]  = player.score
                return "kenney"
            if down_exit_rect and player.rect.colliderect(down_exit_rect):
                game_state["health"] = player.health
                game_state["score"]  = player.score
                return "exclusion"

        # ── camera ────────────────────────────────────────────────
        tx = player.rect.centerx - SCREEN_W//2
        ty = player.rect.centery - SCREEN_H//2
        sy += (ty - sy) * 5 * dt
        sx += (tx - sx) * 5 * dt
        sx = max(0, min(sx, WORLD_W - SCREEN_W))
        sy = min(sy, WORLD_H - SCREEN_H)
        isx, isy = int(sx), int(sy)

        # ── update spark particles ────────────────────────────────
        for sp in SPARKS:
            sp["x"]    += sp["vx"] * dt
            sp["y"]    += sp["vy"] * dt
            sp["phase"] += 1.5 * dt
            if sp["x"] < 0:        sp["x"] += WORLD_W
            if sp["x"] > WORLD_W:  sp["x"] -= WORLD_W
            if sp["y"] < 0:        sp["y"] = 0;  sp["vy"] *= -1
            if sp["y"] > WORLD_H - 200: sp["y"] = WORLD_H - 200; sp["vy"] *= -1

        # Sync shared state every frame
        game_state["health"] = player.health
        game_state["score"]  = player.score

        # ══════ DRAW ══════════════════════════════════════════════

        # 1) Gradient background (full screen, static — teal sky)
        surface.blit(BG_GRAD, (0, 0))

        # 2) Atmospheric glow spots (subtle big circles)
        for gs in GLOW_SPOTS:
            gx = gs["x"] - isx
            gy = gs["y"] - isy
            if -gs["r"] < gx < SCREEN_W+gs["r"] and -gs["r"] < gy < SCREEN_H+gs["r"]:
                pulse = 0.7 + 0.3 * math.sin(t * 0.4 + gs["phase"])
                draw_glow(surface, int(gx), int(gy), int(gs["r"]*pulse),
                          gs["col"], int(50 * pulse))

        # 3) Parallax backgrounds (very subtle, avoid overwhelming the teal sky)
        if BG_DECO:
            px = -(isx * 0.12) % BG_DECO.get_width()
            py = -(isy * 0.06)
            for ox in range(-1, SCREEN_W // BG_DECO.get_width() + 2):
                surface.blit(BG_DECO, (int(px + ox * BG_DECO.get_width()), int(py)))

        if BG_HILLS:
            px = -(isx * 0.25) % BG_HILLS.get_width()
            py = -(isy * 0.12)
            for ox in range(-1, SCREEN_W // BG_HILLS.get_width() + 2):
                surface.blit(BG_HILLS, (int(px + ox * BG_HILLS.get_width()), int(py)))

        # 4) Platforms + their plants/decorations
        for plat in PLATFORMS:
            spr = PLATFORM_SPRITES[plat["sprite_idx"]]
            sw, sh = spr.get_size()
            px = plat["wx"] - isx
            py = plat["wy"] - isy

            # Gentle vertical float for sky-level platforms
            bob = math.sin(t * 0.5 + plat["wx"] * 0.002) * 3 if plat["wy"] < 700 else 0

            # Draw hanging vines first (so they are "behind" or flush with bottom)
            for hv in plat["hanging"]:
                vx, vy = hv["wx"] - isx, hv["wy"] - isy + bob
                if -180 < vx < SCREEN_W + 180 and -180 < vy < SCREEN_H + 180:
                    surface.blit(hv["img"], (int(vx), int(vy)))

            # Skip platform if off-screen
            if px > SCREEN_W + sw or px + sw < -sw: continue
            if py > SCREEN_H + sh or py + sh < -sh: continue

            # Draw environment objects (spikes, chompers)
            for eo in plat["env_objs"]:
                ex, ey = eo["wx"] - isx, eo["wy"] - isy + bob
                surface.blit(eo["img"], (int(ex), int(ey)))

            # Draw platform sprite
            surface.blit(spr, (px, int(py + bob)))

            # Plants on this platform
            for dec in plat["plants"]:
                dpx = dec["wx"] - isx
                dpy = dec["wy"] - isy + (bob if plat["wy"] < 700 else 0)
                if -60 < dpx < SCREEN_W + 60:
                    dec["fc"] += dec["spd"] * dt
                    fi = int(dec["fc"]) % len(dec["frames"])
                    plant_bob = math.sin(t * 1.0 + dec["bob_phase"]) * 1.5
                    surface.blit(dec["frames"][fi], (int(dpx), int(dpy + plant_bob)))

        # 5) Player (flicker when invincible)
        if player.invincible <= 0 or int(t * 10) % 2 == 0:
            player.draw(surface, isx, isy)

        # 6) Fruit collectibles
        for fr in FRUIT_LIST:
            if fr["collected"]:
                fr["collect_t"] += dt
                continue
            fx = fr["x"] - isx
            fy = fr["y"] - isy
            if not (-40 < fx < SCREEN_W+40 and -40 < fy < SCREEN_H+40): continue
            fr["fc"] += 14 * dt
            fi = int(fr["fc"]) % len(fr["frames"])
            bob = math.sin(t * 2.0 + fr["x"] * 0.01) * 4
            # Soft glow under fruit
            gs = pygame.Surface((34,34), pygame.SRCALPHA)
            pygame.draw.ellipse(gs, (UI_GOLD[0], UI_GOLD[1], UI_GOLD[2], 40), (0,22,34,10))
            surface.blit(gs, (int(fx)-3, int(fy+bob)+4))
            surface.blit(fr["frames"][fi], (int(fx), int(fy+bob)))

        # 7) White sparkle particles
        for sp in SPARKS:
            gx = sp["x"] - isx
            gy = sp["y"] - isy
            if not (-10 < gx < SCREEN_W+10 and -10 < gy < SCREEN_H+10): continue
            alpha_v = int((math.sin(sp["phase"]) * 0.5 + 0.5) * 200 + 30)
            r = int(sp["r"])
            hsurf = pygame.Surface((r*6, r*6), pygame.SRCALPHA)
            pygame.draw.circle(hsurf, (*sp["col"], alpha_v//5), (r*3, r*3), r*3)
            pygame.draw.circle(hsurf, (*sp["col"], alpha_v//2), (r*3, r*3), r*2)
            pygame.draw.circle(hsurf, (*sp["col"], alpha_v),    (r*3, r*3), r)
            surface.blit(hsurf, (int(gx-r*3), int(gy-r*3)))

        # 8) Vignette (dark edges)
        vig = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for i in range(5):
            inset = i * 50
            a = int(80 * (1 - i/5) ** 2)
            pygame.draw.rect(vig, (5, 18, 24, a),
                             (inset, inset, SCREEN_W-inset*2, SCREEN_H-inset*2), 50)
        surface.blit(vig, (0, 0))

        # ── 9)  HUD ───────────────────────────────────────────────
        # Top-left: health orbs
        draw_panel(surface, pygame.Rect(10, 10, 130, 50), radius=10)
        draw_health_orbs(surface, player.health, x=18, y=18)

        # Top-left below health: jump indicator
        draw_panel(surface, pygame.Rect(10, 68, 70, 32), radius=8)
        jlbl = FONT_SMALL.render("JUMP", True, UI_TEAL_DIM)
        surface.blit(jlbl, (18, 73))
        draw_jump_indicator(surface, player.jump_count, x=54, y=84)

        # Top-right: score
        draw_score(surface, player.score, SCREEN_W - 180, 10)

        # Distance bar (below score)
        dist_pct = min(1.0, player.distance / (WORLD_W - SCREEN_W))
        bar_rect = pygame.Rect(SCREEN_W-180, 50, 160, 10)
        draw_panel(surface, bar_rect.inflate(4,4), radius=5)
        filled_w = int(dist_pct * 160)
        if filled_w > 0:
            pygame.draw.rect(surface, UI_TEAL, (*bar_rect.topleft, filled_w, 10), border_radius=5)
        prog_lbl = FONT_SMALL.render(f"{int(dist_pct*100)}%  explored", True, UI_TEAL if dist_pct<1 else UI_GOLD)
        surface.blit(prog_lbl, (SCREEN_W-180, 64))

        # Bottom: minimap
        draw_minimap(surface, player, PLATFORMS, isx, isy)

        # Bottom-center: controls hint (subtle)
        draw_controls_hint(surface, SCREEN_H - 28)

        # Pause overlay
        if paused:
            draw_pause_menu(surface)

        # Cinematic title fade-in
        draw_title_card(surface, int(title_alpha))

        pygame.display.flip()

    game_state["health"] = player.health
    game_state["score"]  = player.score
    return "quit"

if __name__ == "__main__":
    run_level(screen)
    pygame.quit()
    sys.exit()
