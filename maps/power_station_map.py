import os, sys, pygame, math

ROOT        = os.path.dirname(__file__)
PARENT_DIR  = os.path.dirname(ROOT)
BASE        = os.path.join(PARENT_DIR, "assets", "craftpix-net-924041-power-station-free-tileset-pixel-art")
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
pygame.display.set_caption("Power Station – Facility Interior")

PFX = "Tile_"

TILE_MAPPING = {
    '1': f"{PFX}01.png", '2': f"{PFX}02.png", '3': f"{PFX}03.png",
    'l': f"{PFX}09.png", 'p': f"{PFX}09.png",
    'm': f"{PFX}10.png",
    'q': f"{PFX}14.png", 'r': f"{PFX}14.png",
    '7': f"{PFX}17.png", '8': f"{PFX}18.png", '9': f"{PFX}19.png",
    '/': f"{PFX}33.png", '\\': f"{PFX}34.png",
    'u': f"{PFX}25.png", 'v': f"{PFX}26.png", 'x': f"{PFX}27.png", 'w': f"{PFX}28.png",
    'a': f"{PFX}51.png", 'b': f"{PFX}52.png", 'c': f"{PFX}53.png",
    'd': f"{PFX}54.png", 'f': f"{PFX}56.png", 'g': f"{PFX}57.png",
    'h': f"{PFX}58.png", 'e': f"{PFX}60.png", 'i': f"{PFX}63.png", 'j': f"{PFX}64.png",
    'k': f"{PFX}46.png", # solid dark for gap background
}

SOLID_TILES = set('123456789lpqrm/\\uvxw')
BG_TILES = set('abcdefghijk')

MAP_LAYOUT = [
    (' '*40)[:40],
    (' '*7 + '1' + '2' + '3' + ' '*10 + '1' + '2'*8 + '3' + ' '*5 + '1' + '2'*4)[:40],
    (' '*7 + '7' + '8' + '9' + ' '*10 + '7' + '8'*8 + '9' + ' '*5 + '7' + '8'*4)[:40],
    (' '*40)[:40],
    (' '*40)[:40],
    (' '*15 + '1' + '3' + ' '*4 + '1' + '3' + ' '*18)[:40],
    (' '*14 + '/' + 'm' + 'q' + 'kkkk' + 'p' + 'm' + '\\' + ' '*14)[:40],
    (' '*13 + '/' + 'm'*2 + 'q' + 'kkkk' + 'p' + 'm'*2 + '\\' + ' '*13)[:40],
    (' '*12 + '/' + 'm'*3 + 'q' + 'kkkk' + 'p' + 'm'*3 + '\\' + ' '*12)[:40],
    (' '*11 + '/' + 'm'*4 + 'q' + 'kkkk' + 'p' + 'm'*4 + '\\' + ' '*11)[:40],
    (' '*10 + '/' + 'm'*5 + 'q' + 'k' + '1' + '3' + 'k' + 'p' + 'm'*5 + '\\' + ' '*10)[:40],
    (' '*9 + '/' + 'm'*6 + 'q' + 'k' + '7' + '9' + 'k' + 'p' + 'm'*6 + '\\' + ' '*9)[:40],
    ('1' + '2'*7 + '/' + 'm'*7 + 'q' + 'uvxw' + 'p' + 'm'*7 + '\\' + '2'*9 + '3')[:40],
    ('l' + 'aaebfgaaaaa' + 'p' + 'm'*3 + 'q' + 'kkkk' + 'p' + 'm'*3 + 'q' + 'aaaeaaidjiaaa' + 'r')[:40],
    ('l' + 'aaebhhaaaaa' + 'p' + 'm'*3 + 'q' + 'kkkk' + 'p' + 'm'*3 + 'q' + 'aaaeaaidjiaaa' + 'r')[:40],
    ('l' + 'aaeaaaaaaca' + 'p' + 'm'*3 + 'q' + 'k'*4 + 'p' + 'm'*3 + 'q' + 'aaaaaaggggaaa' + 'r')[:40],
    ('l' + 'aaeaaaaaada' + 'p' + 'm'*3 + 'q' + 'k'*4 + 'p' + 'm'*3 + 'q' + 'aaafaaadddaaa' + 'r')[:40],
    ('1' + '2'*15 + '3' + ' '*4 + '1' + '2'*17 + '3')[:40],
    ('l' + 'm'*15 + 'q' + 'k'*4 + 'p' + 'm'*17 + 'r')[:40],
    ('l' + 'm'*15 + 'q' + 'k'*4 + 'p' + 'm'*17 + 'r')[:40],
    ('l' + 'm'*15 + 'q' + 'k'*4 + 'p' + 'm'*17 + 'r')[:40],
    ('l' + 'm'*15 + 'q' + 'k'*4 + 'p' + 'm'*17 + 'r')[:40],
]

COIN_COORDS = [
    [15, 4], [16, 4],
    [17, 8], [18, 8], [19, 8], [20, 8],
    [7, 10], [32, 10]
]

def load_img(p, scale=1):
    try:
        i = pygame.image.load(p).convert_alpha()
        if scale != 1: i = pygame.transform.scale(i, (int(i.get_width() * scale), int(i.get_height() * scale)))
        return i
    except Exception:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        s.fill((90, 70, 50, 200)); return s

def load_ss(p, fw, fh, scale=1.0):
    try:
        sh = pygame.image.load(p).convert_alpha()
        fr = []
        for x in range(0, sh.get_width(), fw):
            s = pygame.Surface((fw, fh), pygame.SRCALPHA)
            s.blit(sh, (0, 0), (x, 0, fw, fh))
            if scale != 1: s = pygame.transform.scale(s, (int(fw * scale), int(fh * scale)))
            fr.append(s)
        return fr if fr else [pygame.Surface((int(fw * scale), int(fh * scale)))]
    except Exception:
        return [pygame.Surface((int(fw * scale), int(fh * scale)))]

tiles_d = os.path.join(BASE, "1 Tiles")
loaded_tiles = {k: load_img(os.path.join(tiles_d, v)) for k, v in TILE_MAPPING.items()}
bg_img = load_img(os.path.join(BASE, "2 Background", "Background.png"))
if bg_img.get_width() > 1: bg_img = pygame.transform.scale(bg_img, (SCREEN_W, SCREEN_H))

# Objects
tub_d = os.path.join(BASE, "3 Objects", "1 Tube")
dec_d = os.path.join(BASE, "3 Objects", "2 Decoration")
pow_d = os.path.join(BASE, "3 Objects", "3 Power lines")

DECOR_RAW = [
    (load_img(os.path.join(tub_d, "4.png")), 1*TILE_SIZE, 17), # big blue machine
    (load_img(os.path.join(tub_d, "11.png")), 4*TILE_SIZE+16, 17), # small container
    (load_img(os.path.join(dec_d, "24.png")), 6*TILE_SIZE, 17), # AC-3
    (load_img(os.path.join(dec_d, "25.png")), 9*TILE_SIZE, 17), # EFG-2
    (load_img(os.path.join(tub_d, "2.png")), 12*TILE_SIZE+16, 17), # green tube
    (load_img(os.path.join(dec_d, "22.png")), 23*TILE_SIZE+16, 1), # top yellow monitors
    (load_img(os.path.join(dec_d, "22.png")), 25*TILE_SIZE+16, 1),
    (load_img(os.path.join(dec_d, "22.png")), 27*TILE_SIZE+16, 1),
    
    # Gap walls panels
    (load_img(os.path.join(dec_d, "7.png")),  15*TILE_SIZE+16, 9), # Green locker left wall
    (load_img(os.path.join(dec_d, "6.png")),  16*TILE_SIZE+16, 9), # Blue panel gap left wall
    (load_img(os.path.join(dec_d, "11.png")), 21*TILE_SIZE,    9), # Electric blue box gap right wall
    
    (load_img(os.path.join(dec_d, "8.png")), 15*TILE_SIZE, 13), # Server racks moved right
    (load_img(os.path.join(dec_d, "9.png")), 20*TILE_SIZE, 10),
    (load_img(os.path.join(dec_d, "10.png")), 21*TILE_SIZE, 10),
    (load_img(os.path.join(pow_d, "1.png")), 32*TILE_SIZE, 12), # Tower right
    (load_img(os.path.join(pow_d, "2.png")), 2*TILE_SIZE, 12), # Tower left
    
    # Desks and monitors right room
    (load_img(os.path.join(dec_d, "18.png")), 24*TILE_SIZE, 17),
    (load_img(os.path.join(dec_d, "18.png")), 27*TILE_SIZE, 17),
    (load_img(os.path.join(dec_d, "13.png")), 24*TILE_SIZE, 15),
    (load_img(os.path.join(dec_d, "16.png")), 27*TILE_SIZE, 15),
]

decorations = []
for img, px, row in DECOR_RAW:
    if img and img.get_width() > 1:
        decorations.append((img, px, row * TILE_SIZE - img.get_height()))

ANIM_DECOR = [
    # Glowing electric trap (on the floor right room)
    (load_ss(os.path.join(BASE, "4 Animated objects", "Trap.png"), 32, 48), 35*TILE_SIZE, 17*TILE_SIZE - 48),
]

def load_player(p, w, h):
    d = {}
    for a in ["Idle", "Run", "Jump", "Fall"]:
        path = os.path.join(p, f"{a} (32x32).png")
        d[a.lower()] = load_ss(path, w, h)
    return d

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 26)
        self.vx = self.vy = 0.0
        self.speed = 180.0
        self.jump_power = -380.0
        self.gravity = 900.0
        self.grounded = False
        self.anims = load_player(PLAYER_PATH, 32, 32)
        self.state = "idle"
        self.frame = 0.0
        self.facing_right = True
    
    def update(self, dt, solid_rects):
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_LEFT]:  self.vx = -self.speed; self.facing_right = False
        if keys[pygame.K_RIGHT]: self.vx =  self.speed; self.facing_right = True
        
        self.vy += self.gravity * dt
        if keys[pygame.K_UP] and self.grounded:
            self.vy = self.jump_power
            self.grounded = False

        self.rect.x += int(self.vx * dt)
        for r in solid_rects:
            if self.rect.colliderect(r):
                if self.vx > 0: self.rect.right = r.left
                elif self.vx < 0: self.rect.left = r.right
        
        self.rect.y += int(self.vy * dt)
        self.grounded = False
        for r in solid_rects:
            if self.rect.colliderect(r):
                if self.vy > 0:
                    self.rect.bottom = r.top
                    self.vy = 0
                    self.grounded = True
                elif self.vy < 0:
                    self.rect.top = r.bottom
                    self.vy = 0

        if not self.grounded: self.state = "jump" if self.vy < 0 else "fall"
        elif self.vx != 0: self.state = "run"
        else: self.state = "idle"
        
        self.frame += dt * 10
        if self.state not in self.anims: self.state = "idle"

    def draw(self, surf, cx, cy):
        f_list = self.anims[self.state]
        if not f_list: return
        f = f_list[int(self.frame) % len(f_list)]
        if not self.facing_right: f = pygame.transform.flip(f, True, False)
        surf.blit(f, (self.rect.x - 6 - cx, self.rect.y - 6 - cy))

def build_rects(layout):
    rs = []
    bz = []
    for r, row in enumerate(layout):
        for c, ch in enumerate(row):
            if ch in SOLID_TILES:
                rs.append(pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            if ch in BG_TILES:
                bz.append((ch, c*TILE_SIZE, r*TILE_SIZE))
    return rs, bz

def main():
    player = Player(4 * TILE_SIZE, 10 * TILE_SIZE)
    clock = pygame.time.Clock()
    solids, bg_rects = build_rects(MAP_LAYOUT)
    
    money_frames = load_ss(os.path.join(PARENT_DIR, "assets", "craftpix-net-924041-power-station-free-tileset-pixel-art", "4 Animated objects", "Money.png"), 24, 24)
    # Filter coins that are exactly where blocks are
    actual_coins = []
    for ci, rj in COIN_COORDS:
        r = pygame.Rect(ci*TILE_SIZE + 4, rj*TILE_SIZE + 4, 16, 16)
        if r.collidelist(solids) == -1:
            actual_coins.append(r)
    
    t = cx = cy = 0.0
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        t += dt
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                running = False
        
        player.update(dt, solids)
        
        # Camera
        tcx = player.rect.centerx - SCREEN_W / 2
        tcy = player.rect.centery - SCREEN_H / 2
        cx += (tcx - cx) * 5 * dt
        cy += (tcy - cy) * 5 * dt
        cx = max(0, min(cx, len(MAP_LAYOUT[0]) * TILE_SIZE - SCREEN_W))
        if cy > len(MAP_LAYOUT)*TILE_SIZE - SCREEN_H: cy = len(MAP_LAYOUT)*TILE_SIZE - SCREEN_H
        
        icx, icy = int(cx), int(cy)
        
        screen.fill((30, 28, 40))
        if bg_img: screen.blit(bg_img, (0, 0))
        
        # Draw background tiles
        for ch, bx, by in bg_rects:
            if -TILE_SIZE < bx - icx < SCREEN_W and -TILE_SIZE < by - icy < SCREEN_H:
                screen.blit(loaded_tiles[ch], (bx - icx, by - icy))
        
        for img, px, py in decorations:
            if -img.get_width() < px - icx < SCREEN_W and -img.get_height() < py - icy < SCREEN_H:
                screen.blit(img, (px - icx, py - icy))
        
        for fr, px, py in ANIM_DECOR:
            f = fr[int(t * 10) % len(fr)]
            screen.blit(f, (px - icx, py - icy))
        
        # Draw solid tiles
        for r, row in enumerate(MAP_LAYOUT):
            by = r * TILE_SIZE - icy
            if by < -TILE_SIZE or by > SCREEN_H: continue
            for c, ch in enumerate(row):
                if ch in SOLID_TILES:
                    bx = c * TILE_SIZE - icx
                    if -TILE_SIZE < bx < SCREEN_W:
                        screen.blit(loaded_tiles[ch], (bx, by))
        
        # Coins
        if money_frames:
            mf = money_frames[int(t * 10) % len(money_frames)]
        for r in actual_coins[:]:
            if r.colliderect(player.rect):
                actual_coins.remove(r)
            elif money_frames:
                screen.blit(mf, (r.x - 4 - icx, r.y - 4 - icy))
                
        player.draw(screen, icx, icy)
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main()
