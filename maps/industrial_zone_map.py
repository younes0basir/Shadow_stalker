import os, sys, pygame, math

ROOT        = os.path.dirname(__file__)
PARENT_DIR  = os.path.dirname(ROOT)
BASE        = os.path.join(PARENT_DIR, "assets", "craftpix-net-314143-free-industrial-zone-tileset-pixel-art")
PLAYER_PATH = os.path.join(PARENT_DIR, "assets", "MainCharacters", "VirtualGuy")

pygame.init()
SCREEN_W, SCREEN_H = 1280, 720
TILE_SIZE = 32

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
else:
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    else:
        SCREEN_W, SCREEN_H = screen.get_size()
pygame.display.set_caption("Industrial Zone – Factory Interior")

PFX = "IndustrialTile_"

# ── Verified tile mapping (from tile viewer) ─────────────────────────────────
TILE_MAPPING = {
    '1': f"{PFX}04.png", '2': f"{PFX}05.png", '3': f"{PFX}06.png",
    '4': f"{PFX}13.png", '5': f"{PFX}14.png", '6': f"{PFX}15.png",
    '7': f"{PFX}22.png", '8': f"{PFX}23.png", '9': f"{PFX}24.png",
    '+': f"{PFX}08.png", 'x': f"{PFX}16.png", 'y': f"{PFX}17.png",
    's': f"{PFX}36.png", 't': f"{PFX}71.png",
    'u': f"{PFX}77.png", 'v': f"{PFX}78.png", 'w': f"{PFX}79.png",
    '_': f"{PFX}72.png",
    
    'H': f"{PFX}49.png", 'I': f"{PFX}50.png", 'J': f"{PFX}51.png",
    'K': f"{PFX}58.png", 'L': f"{PFX}59.png", 'M': f"{PFX}60.png",
    
    'A': f"{PFX}74.png", 'B': f"{PFX}75.png", 'C': f"{PFX}76.png",
    
    'S': f"{PFX}45.png", 'T': f"{PFX}54.png", 'W': f"{PFX}63.png",
    'p': f"{PFX}61.png", 'q': f"{PFX}70.png",
    'z': f"{PFX}27.png",
    'U': f"{PFX}70.png",
    'Q': f"{PFX}08.png", 'E': f"{PFX}16.png",
}

SOLID_TILES = set('123456789+xysuvw_HIJKLMABCSTWpqzQE')

# ── Map layout ───────────────────────────────────────────────────────────────
# W = 40 tiles × 32px = 1280px  →  fills the screen exactly, no scrolling needed
#
# Columns breakdown (total 40):
#   0-1   : left wall  (Q E)
#   2     : left shaft (ladder, open)
#   3-10  : left platform  (8 wide)
#   11-12 : gap
#   13-16 : center pillar  (4 wide, tall — runs from ceiling to floor)
#   17-18 : gap
#   19-30 : right platform section  (12 wide)
#   31-32 : gap before chimney
#   33-35 : chimney  (3 wide)
#   36-39 : right wall / entry  (4 wide)

W = 40

MAP_LAYOUT = [
    (' '*29 + 'S' + ' '*4 + 'S' + ' '*5)[:40],
    (' '*29 + 'W' + ' '*4 + 'W' + ' '*5)[:40],
    (' '*29 + 'T' + ' '*4 + 'T' + ' '*5)[:40],
    (' '*29 + 'T' + ' '*4 + 'T' + ' '*5)[:40],
    ('2'*16 + '3' + ' ' + ' '*8 + '  ' + '1' + '2'*10 + '3')[:40],
    ('y'*7 + 's'*5 + '+'*4 + '6' + ' '*10 + '4' + '+'*10 + '6')[:40],
    ('8'*16 + '9' + ' '*10 + '7' + '8'*10 + '9')[:40],
    (' '*13 + 'p' + ' '*10 + 'p' + ' '*8 + 'p' + ' '*15)[:40],
    (' '*13 + 'p' + ' '*10 + 'p' + ' '*8 + 'p' + ' '*15)[:40],
    (' '*13 + 'q' + ' '*10 + 'q' + ' '*8 + 'q' + ' '*15)[:40],
    (' '*15 + 'A' + 'B'*14 + 'C' + ' ' + 'u' + 'v' + 'w' + ' '*5)[:40],
    (' '*32 + '_' * 3 + ' '*5)[:40],
    (' '*40)[:40],
    (' '*5 + '2'*5 + 's'*3 + '+' + '3' + ' '*6 + '1' + '2'*3 + '3')[:40],
    (' '*5 + '5'*6 + '+'*3 + '6' + ' '*6 + '4' + '5'*3 + '6')[:40],
    (' '*5 + '5'*6 + '+'*3 + '6' + ' '*6 + '4' + '5'*3 + '6')[:40],
    (' '*5 + '8'*10 + ' '*6 + '7' + '8'*3 + '9')[:40],
    (' '*8 + 'A' + 'B'*6 + 'C' + ' '*18 + 'A' + 'B'*3 + 'C')[:40],
    'I'*40,
]
# Ground continuation
for _ in range(8):
    MAP_LAYOUT.append('L'*40)

# ── Coin positions ────────────────────────────────────────────────────────────
COIN_COORDS = [
    [18, 2], [20, 1], [22, 1], [24, 2],
    [15, 9], [18, 9], [21, 9], [24, 9],
    [3, 12], [6, 12],
    # New coins for improved layout
    [8, 14], [11, 14], [14, 14],
    [30, 14], [33, 14], [36, 14],
    [10, 16], [12, 16], [14, 16],
    [28, 16], [30, 16], [32, 16],
]
for ri, row in enumerate(MAP_LAYOUT):
    for ci, ch in enumerate(row):
        if ch == 'c':
            COIN_COORDS.append([ci, ri])

# ── Helpers ──────────────────────────────────────────────────────────────────
def load_image(path, scale=1):
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale != 1:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
        return img
    except Exception:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        s.fill((90, 70, 50, 200)); return s

def load_ss(path, fw, fh, scale=1.0):
    try:
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for x in range(0, sheet.get_width(), fw):
            surf = pygame.Surface((fw, fh), pygame.SRCALPHA)
            surf.blit(sheet, (0, 0), (x, 0, fw, fh))
            if scale != 1:
                surf = pygame.transform.scale(surf, (int(fw * scale), int(fh * scale)))
            frames.append(surf)
        return frames if frames else _ff(fw, fh, scale)
    except Exception:
        return _ff(fw, fh, scale)

def _ff(fw, fh, s):
    surf = pygame.Surface((int(fw * s), int(fh * s)), pygame.SRCALPHA)
    surf.fill((200, 80, 0)); return [surf]

# ── Load tiles & background ───────────────────────────────────────────────────
tiles_dir    = os.path.join(BASE, "1 Tiles")
loaded_tiles = {sym: load_image(os.path.join(tiles_dir, fname))
                for sym, fname in TILE_MAPPING.items()}

bg_dir = os.path.join(BASE, "2 Background")
bg_img = None
for fname in ("Background.png", "1.png"):
    p = os.path.join(bg_dir, fname)
    img = load_image(p)
    if img.get_width() > 1:
        bg_img = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        break

# ── Objects ───────────────────────────────────────────────────────────────────
o  = lambda p: os.path.join(BASE, "3 Objects", p)
an = lambda p: os.path.join(BASE, "4 Animated objects", p)

barrel1 = load_image(o("Barrel1.png"))
barrel2 = load_image(o("Barrel2.png"))
barrel3 = load_image(o("Barrel3.png"))
barrel4 = load_image(o("Barrel4.png"))
box1 = load_image(o("Box1.png")); box2 = load_image(o("Box2.png"))
box3 = load_image(o("Box3.png")); box4 = load_image(o("Box4.png"))
box5 = load_image(o("Box5.png")); box6 = load_image(o("Box6.png"))
bench    = load_image(o("Bench.png"))
locker1  = load_image(o("Locker1.png")); locker2 = load_image(o("Locker2.png"))
locker3  = load_image(o("Locker3.png")); locker4 = load_image(o("Locker4.png"))
fence1   = load_image(o("Fence1.png"));  fence2  = load_image(o("Fence2.png"))
fence3   = load_image(o("Fence3.png"))
ladder1  = load_image(o("Ladder1.png")); ladder2 = load_image(o("Ladder2.png"))
fire1    = load_image(o("Fire-extinguisher1.png"))
ptr1     = load_image(o("Pointer1.png")); ptr2 = load_image(o("Pointer2.png"))
board1   = load_image(o("Board1.png")); board2 = load_image(o("Board2.png"))
board3   = load_image(o("Board3.png"))
bucket   = load_image(o("Bucket.png")); mop = load_image(o("Mop.png"))
sign3    = load_image(o("3.png")); sign4 = load_image(o("4.png"))
flag     = load_image(o("Flag.png"))

coin_frames    = load_ss(an("Money.png"),    24, 24, 1.0)
chest_frames   = load_ss(an("Chest.png"),    32, 32, 1.0)
hammer_frames  = load_ss(an("Hammer.png"),   32, 32, 1.0)
entry_frames   = load_ss(an("Entry.png"),    32, 32, 1.0)
screen1_frames = load_ss(an("Screen1.png"),  32, 32, 1.0)
platform_frames= load_ss(an("Platform.png"), 32, 32, 1.0)

# ── Decorations (pixel_x, tile_row) ──────────────────────────────────────────
# Column reference constants (in tiles):
L_PLAT = 3    # left platform starts at col 3
C_PIL  = 13   # center pillar starts at col 13
R_PLAT = 19   # right platform starts at col 19
CHIM   = 33   # chimney starts at col 33

DECOR_RAW = [
    # Ladder spanning the full visible left bounding shaft
    (ladder2, 1*TILE_SIZE, 0), (ladder2, 1*TILE_SIZE, 1), (ladder2, 1*TILE_SIZE, 2), (ladder2, 1*TILE_SIZE, 3), 
    (ladder2, 1*TILE_SIZE, 4), (ladder2, 1*TILE_SIZE, 5), (ladder2, 1*TILE_SIZE, 6), (ladder2, 1*TILE_SIZE, 7), 
    (ladder2, 1*TILE_SIZE, 8), (ladder2, 1*TILE_SIZE, 9), (ladder2, 1*TILE_SIZE, 10), (ladder2, 1*TILE_SIZE, 11),
    (ladder2, 1*TILE_SIZE, 12), (ladder1, 1*TILE_SIZE, 13),

    # Top Left platform
    (barrel3, 11*TILE_SIZE, 4), (barrel4, 12*TILE_SIZE, 4),
    (ptr1, 15*TILE_SIZE, 4),  # Warning sign

    # Top Bridge (railings/fences) exactly matching visual gap structure
    (fence1, 18*TILE_SIZE, 4), (fence2, 19*TILE_SIZE, 4), (fence2, 20*TILE_SIZE, 4), (fence2, 21*TILE_SIZE, 4),
    (fence2, 22*TILE_SIZE, 4), (fence2, 23*TILE_SIZE, 4), (fence2, 24*TILE_SIZE, 4), (fence3, 25*TILE_SIZE, 4),

    # Conveyor belt (Row 10) 
    (box4, 20*TILE_SIZE, 10),

    # Mid ledge (Row 10)
    (box1, 33*TILE_SIZE, 10),

    # Ground floor (Row 17)
    (mop, 9*TILE_SIZE, 17), (bucket, 10*TILE_SIZE, 17),
    (barrel1, 12*TILE_SIZE, 17), (barrel2, 13*TILE_SIZE, 17),
    (fire1, 15*TILE_SIZE, 17),
    (board1, 10*TILE_SIZE, 14),
    (board2, 22*TILE_SIZE, 14),
    (board3, 26*TILE_SIZE, 14),
    (locker1, 23*TILE_SIZE, 17), (locker2, 24*TILE_SIZE, 17), (locker3, 27*TILE_SIZE, 17), (locker4, 28*TILE_SIZE, 17),
    (bench, 25*TILE_SIZE, 17),
    (box1, 32*TILE_SIZE, 17), (box2, 33*TILE_SIZE, 17), (box3, 33*TILE_SIZE+8, 15),
    (box4, 34*TILE_SIZE, 17),
]

decorations = []
for img, px, row in DECOR_RAW:
    if img and img.get_width() > 1:
        if img in (board1, board2, board3):
            decorations.append((img, px, row * TILE_SIZE))
        elif img in (ladder1, ladder2):
            decorations.append((img, px, row * TILE_SIZE))
        else:
            decorations.append((img, px, row * TILE_SIZE - img.get_height()))

# Animated world objects: (frames, pixel_x, pixel_y)
ANIM_DECOR = [
    (screen1_frames, 7*TILE_SIZE,  6*TILE_SIZE),      # monitor hovering off platform edge
    (entry_frames,   37*TILE_SIZE, 17*TILE_SIZE-32),  # entry door on ground floor
]

# Conveyor animated ranges (tile columns)
CONV_L_COL_S = 15   # conveyor starts precisely after left plat
CONV_L_COL_E = 31
CONV_R_COL_S = 0
CONV_R_COL_E = 0

map_width  = max(len(r) for r in MAP_LAYOUT) * TILE_SIZE
map_height = len(MAP_LAYOUT) * TILE_SIZE

# ── Player ─────────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        sc = 1.5
        self.anims = {s: load_ss(os.path.join(PLAYER_PATH, f"{s}.png"), 32, 32, sc)
                      for s in ('idle', 'run', 'jump', 'double_jump', 'fall')}
        self.state = 'idle'; self.frame_idx = 0.0; self.facing_right = True
        self.x = float(x); self.y = float(y)
        self.rect = pygame.Rect(x, y, int(16 * sc), int(24 * sc))
        self.vx = 0.0; self.vy = 0.0
        self.speed = 260; self.jump_force = -460; self.gravity = 1200
        self.on_ground = False; self.jump_count = 0
        self.on_wall_l = self.on_wall_r = self.wall_slide = False
        self.wall_cd = 0.0

    def _tiles(self, rect):
        hits = []
        sc = max(0, rect.left // TILE_SIZE); sr = max(0, rect.top // TILE_SIZE)
        er = min(len(MAP_LAYOUT) - 1, (rect.bottom - 1) // TILE_SIZE)
        for row in range(sr, er + 1):
            rs = MAP_LAYOUT[row]
            ec = min(len(rs) - 1, (rect.right - 1) // TILE_SIZE)
            for col in range(sc, ec + 1):
                if 0 <= col < len(rs) and rs[col] in SOLID_TILES:
                    hits.append(pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return hits

    def _wall(self, d):
        p = self.rect.copy(); p.x += -2 if d == 'l' else 2
        return bool(self._tiles(p))

    def jump(self):
        if self.on_wall_l and not self.on_ground:
            self.vy = self.jump_force; self.vx = self.speed * 1.2
            self.wall_cd = 0.15; self.facing_right = True; return
        if self.on_wall_r and not self.on_ground:
            self.vy = self.jump_force; self.vx = -self.speed * 1.2
            self.wall_cd = 0.15; self.facing_right = False; return
        if self.jump_count < 2:
            self.vy = self.jump_force; self.jump_count += 1
            self.on_ground = False; self.frame_idx = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if   keys[pygame.K_LEFT] or keys[pygame.K_a]: self.vx = -self.speed; self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx =  self.speed; self.facing_right = True
        else: self.vx = 0

        # Clamp inside room walls
        if self.x < 2 * TILE_SIZE: self.x = float(2 * TILE_SIZE); self.vx = max(0, self.vx)

        if not self.on_ground and self.wall_cd <= 0:
            self.on_wall_l = self._wall('l'); self.on_wall_r = self._wall('r')
            self.wall_slide = (self.on_wall_l or self.on_wall_r) and self.vy > 0
        else: self.on_wall_l = self.on_wall_r = self.wall_slide = False
        if self.wall_cd > 0: self.wall_cd = max(0, self.wall_cd - dt)

        self.vy += (self.gravity * 0.3 if self.wall_slide else self.gravity) * dt
        if self.wall_slide: self.vy = min(self.vy, 150)

        self.x += self.vx * dt; self.rect.x = int(self.x)
        for h in self._tiles(self.rect):
            if self.vx > 0:  self.rect.right = h.left;  self.x = float(self.rect.x)
            elif self.vx < 0: self.rect.left = h.right; self.x = float(self.rect.x)

        self.y += self.vy * dt; self.rect.y = int(self.y)
        for h in self._tiles(self.rect):
            if self.vy > 0:  self.rect.bottom = h.top;  self.y = float(self.rect.y); self.vy = 0
            elif self.vy < 0: self.rect.top = h.bottom; self.y = float(self.rect.y); self.vy = 0

        probe = self.rect.copy(); probe.y += 1
        self.on_ground = bool(self._tiles(probe)) and self.vy >= 0
        if self.on_ground: self.jump_count = 0
        if self.rect.y > map_height:
            self.x, self.y = float(2 * TILE_SIZE + 10), float(3 * TILE_SIZE); self.vy = 0

        ns = 'idle'
        if not self.on_ground: ns = 'double_jump' if self.jump_count == 2 else ('jump' if self.vy < 0 else 'fall')
        elif self.vx != 0: ns = 'run'
        if ns != self.state: self.state = ns; self.frame_idx = 0
        self.frame_idx += (20 if self.state == 'run' else 12) * dt

    def draw(self, surface, sx, sy):
        frames = self.anims[self.state]
        idx = (int(self.frame_idx) % len(frames)) if self.state not in ('jump', 'fall', 'double_jump') \
              else min(int(self.frame_idx), len(frames) - 1)
        img = frames[idx]
        if not self.facing_right: img = pygame.transform.flip(img, True, False)
        surface.blit(img, (self.rect.centerx - img.get_width() // 2 - sx,
                           self.rect.bottom  - img.get_height()       - sy))

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
    lbl = fs.render("INDUSTRIAL  ZONE", True, (255, 150, 50))
    surface.blit(lbl, (SCREEN_W // 2 - lbl.get_width() // 2, 8))
    ctrls = [("[A]/[D]", "Move"), ("[Space]/[W]", "Double Jump"), ("[ESC]", "Quit")]
    py = SCREEN_H - 20 - len(ctrls) * 20
    for i, (k, a) in enumerate(ctrls):
        surface.blit(fs.render(k, True, (255, 190, 110)), (20, py + i * 20))
        surface.blit(fs.render(a, True, (200, 140, 70)), (120, py + i * 20))

# ── Level loop ─────────────────────────────────────────────────────────────────
def run_level(surface, game_state=None):
    global SCREEN_W, SCREEN_H, bg_img
    if game_state is None:
        game_state = {"health": 3, "max_health": 3, "score": 0, "lives": 3}

    player  = Player(4 * TILE_SIZE, 2 * TILE_SIZE)
    clock   = pygame.time.Clock()
    t = sx = sy = 0.0; running = True

    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05); t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w): player.jump()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = event.w, event.h
                surface = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
                for fname in ("Background.png", "1.png"):
                    p = os.path.join(bg_dir, fname)
                    img = load_image(p)
                    if img.get_width() > 1:
                        bg_img = pygame.transform.scale(img, (SCREEN_W, SCREEN_H)); break

        player.update(dt)

        for entry in COIN_COORDS[:]:
            cr = pygame.Rect(entry[0]*TILE_SIZE, entry[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if player.rect.colliderect(cr):
                game_state["score"] += 10; COIN_COORDS.remove(entry)

        # Camera: lock at 0,0 since map fills the screen exactly
        # Room height: rows 0-9 = 10×32 = 320px; centre vertically in 720px window
        room_h = 10 * TILE_SIZE  # 320px
        sy_fixed = -(SCREEN_H - room_h) // 2  # offset so room is centred vertically
        # Actually start at 0 so ceiling is at top; let camera follow player vertically
        tx = 0   # no horizontal camera needed (map is exactly screen-wide)
        ty = player.rect.centery - SCREEN_H // 2
        sx += (tx - sx) * 8 * dt
        sy += (ty - sy) * 8 * dt
        sx = max(0, min(sx, map_width  - SCREEN_W))
        sy = max(0, min(sy, map_height - SCREEN_H))
        isx, isy = int(sx), int(sy)

        # ── Draw ─────────────────────────────────────────────────────────────
        surface.fill((18, 14, 22))

        if bg_img:
            surface.blit(bg_img, (0, 0))

        # Animated conveyor belt overlay (drawn at row 10, over the A/B/C tiles)
        if platform_frames:
            pf    = platform_frames[int(t * 10) % len(platform_frames)]
            row_y = 10 * TILE_SIZE - isy
            if -TILE_SIZE < row_y < SCREEN_H + TILE_SIZE:
                for col in range(CONV_L_COL_S, CONV_L_COL_E):
                    bx = col * TILE_SIZE - isx
                    if -TILE_SIZE < bx < SCREEN_W: surface.blit(pf, (bx, row_y))

        # Static decorations
        for img, ox, oy in decorations:
            bx = ox - isx; by = oy - isy
            if -img.get_width() < bx < SCREEN_W and -img.get_height() < by < SCREEN_H:
                surface.blit(img, (bx, by))

        # Animated decorations
        for frames, wx, wy in ANIM_DECOR:
            if frames:
                fi = int(t * 6) % len(frames); img = frames[fi]
                bx = wx - isx; by = wy - isy
                if -64 < bx < SCREEN_W and -64 < by < SCREEN_H:
                    surface.blit(img, (bx, by))

        # Tiles (drawn last so walls appear on top of decorations near edges)
        for ri, row in enumerate(MAP_LAYOUT):
            ry = ri * TILE_SIZE - isy
            if ry < -TILE_SIZE or ry > SCREEN_H + TILE_SIZE: continue
            for ci, sym in enumerate(row):
                if sym in (' ', 'c'): continue
                rx = ci * TILE_SIZE - isx
                if rx < -TILE_SIZE or rx > SCREEN_W + TILE_SIZE: continue
                if sym in loaded_tiles: surface.blit(loaded_tiles[sym], (rx, ry))

        # Coins
        if coin_frames:
            cf = coin_frames[int(t * 8) % len(coin_frames)]
            for cx, cy in COIN_COORDS:
                bx = cx * TILE_SIZE - isx + (TILE_SIZE - cf.get_width())  // 2
                by = cy * TILE_SIZE - isy + (TILE_SIZE - cf.get_height()) // 2
                if -32 < bx < SCREEN_W and -32 < by < SCREEN_H:
                    surface.blit(cf, (bx, by + int(math.sin(t * 4 + cx) * 3)))

        draw_hud(surface, game_state)
        player.draw(surface, isx, isy)
        pygame.display.flip()

    return "quit"

if __name__ == "__main__":
    run_level(screen)
    pygame.quit()
    sys.exit()
