import os
import sys
import pygame

# Add paths
ROOT = os.path.dirname(__file__)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "maps"))
sys.path.insert(0, os.path.join(ROOT, "ai"))

# Import AI bot
try:
    from ai.mask_dude_bot import MaskDudeBot
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: AI bot not available")

pygame.init()
SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
pygame.display.set_caption("Shadow Stalker - Merged Zones")

# Import map modules
try:
    from maps.industrial_zone_map import (
        MAP_LAYOUT as IND_LAYOUT, TILE_MAPPING as IND_MAPPING, 
        SOLID_TILES as IND_SOLID, loaded_tiles as IND_TILES,
        decorations as IND_DECOR, ANIM_DECOR as IND_ANIM,
        coin_frames as IND_COINS, platform_frames as IND_PLATFORM,
        CONV_L_COL_S, CONV_L_COL_E, bg_img as IND_BG,
        COIN_COORDS as IND_COINS_COORDS, TILE_SIZE
    )
    IND_AVAILABLE = True
except ImportError:
    IND_AVAILABLE = False
    print("Warning: Industrial zone map not available")

try:
    from maps.green_zone_map import (
        MAP_LAYOUT as GREEN_LAYOUT, TILE_MAPPING as GREEN_MAPPING,
        SOLID_TILES as GREEN_SOLID, loaded_tiles as GREEN_TILES,
        decorations as GREEN_DECOR, coin_frames as GREEN_COINS,
        CHEST_COORDS as GREEN_CHESTS, bg_layers as GREEN_BG,
        fountain_frames as GREEN_FOUNTAIN
    )
    GREEN_AVAILABLE = True
except ImportError:
    GREEN_AVAILABLE = False
    print("Warning: Green zone map not available")

try:
    from maps.exclusion_zone_map import (
        MAP_LAYOUT as EXCL_LAYOUT, TILE_MAPPING as EXCL_MAPPING,
        SOLID_TILES as EXCL_SOLID, loaded_tiles as EXCL_TILES,
        decorations as EXCL_DECOR, coin_frames as EXCL_COINS,
        COIN_COORDS as EXCL_COINS_COORDS, bg_layers as EXCL_BG,
        card_frames as EXCL_CARDS
    )
    EXCL_AVAILABLE = True
except ImportError:
    EXCL_AVAILABLE = False
    print("Warning: Exclusion zone map not available")

# Player path
PLAYER_PATH = os.path.join(ROOT, "assets", "MainCharacters", "VirtualGuy")

class Player:
    def __init__(self, x, y):
        scale = 1.5
        self.anims = self._load_anims(scale)
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

    def _load_anims(self, scale):
        def load_ss(path, fw, fh, sc):
            try:
                sheet = pygame.image.load(path).convert_alpha()
                frames = []
                for x in range(0, sheet.get_width(), fw):
                    surf = pygame.Surface((fw, fh), pygame.SRCALPHA)
                    surf.blit(sheet, (0, 0), (x, 0, fw, fh))
                    if sc != 1:
                        surf = pygame.transform.scale(surf, (int(fw * sc), int(fh * sc)))
                    frames.append(surf)
                return frames if frames else [pygame.Surface((int(fw * sc), int(fh * sc)), pygame.SRCALPHA)]
            except Exception:
                return [pygame.Surface((int(fw * scale), int(fh * scale)), pygame.SRCALPHA)]
        
        return {
            'idle': load_ss(os.path.join(PLAYER_PATH, "idle.png"), 32, 32, scale),
            'run': load_ss(os.path.join(PLAYER_PATH, "run.png"), 32, 32, scale),
            'jump': load_ss(os.path.join(PLAYER_PATH, "jump.png"), 32, 32, scale),
            'double_jump': load_ss(os.path.join(PLAYER_PATH, "double_jump.png"), 32, 32, scale),
            'fall': load_ss(os.path.join(PLAYER_PATH, "fall.png"), 32, 32, scale),
        }

    def _tiles_for(self, rect, map_layout, solid_tiles):
        hits = []
        sc = max(0, rect.left // TILE_SIZE)
        sr = max(0, rect.top // TILE_SIZE)
        er = min(len(map_layout) - 1, (rect.bottom - 1) // TILE_SIZE)
        for row in range(sr, er + 1):
            row_str = map_layout[row]
            ec = min(len(row_str) - 1, (rect.right - 1) // TILE_SIZE)
            for col in range(sc, ec + 1):
                if 0 <= col < len(row_str) and row_str[col] in solid_tiles:
                    hits.append(pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return hits

    def _check_wall(self, direction, map_layout, solid_tiles):
        probe = self.rect.copy()
        probe.x += -2 if direction == 'left' else 2
        return any(True for _ in self._tiles_for(probe, map_layout, solid_tiles))

    def jump(self):
        if self.on_wall_left and not self.on_ground:
            self.vy = self.jump_force
            self.vx = self.speed * 1.2
            self.wall_jump_cd = 0.15
            self.facing_right = True
            return
        if self.on_wall_right and not self.on_ground:
            self.vy = self.jump_force
            self.vx = -self.speed * 1.2
            self.wall_jump_cd = 0.15
            self.facing_right = False
            return
        if self.jump_count < 2:
            self.vy = self.jump_force
            self.jump_count += 1
            self.on_ground = False
            self.frame_idx = 0

    def update(self, dt, map_layout, solid_tiles, map_height):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.facing_right = True
        else:
            self.vx = 0

        if self.x < 0:
            self.x = 0
            self.vx = max(0, self.vx)

        if not self.on_ground and self.wall_jump_cd <= 0:
            self.on_wall_left = self._check_wall('left', map_layout, solid_tiles)
            self.on_wall_right = self._check_wall('right', map_layout, solid_tiles)
            self.wall_slide = (self.on_wall_left or self.on_wall_right) and self.vy > 0
        else:
            self.on_wall_left = self.on_wall_right = self.wall_slide = False
        if self.wall_jump_cd > 0:
            self.wall_jump_cd = max(0, self.wall_jump_cd - dt)

        self.vy += (self.gravity * 0.3 if self.wall_slide else self.gravity) * dt
        if self.wall_slide:
            self.vy = min(self.vy, 150)

        self.x += self.vx * dt
        self.rect.x = int(self.x)
        for h in self._tiles_for(self.rect, map_layout, solid_tiles):
            if self.vx > 0:
                self.rect.right = h.left
                self.x = float(self.rect.x)
            elif self.vx < 0:
                self.rect.left = h.right
                self.x = float(self.rect.x)

        self.y += self.vy * dt
        self.rect.y = int(self.y)
        for h in self._tiles_for(self.rect, map_layout, solid_tiles):
            if self.vy > 0:
                self.rect.bottom = h.top
                self.y = float(self.rect.y)
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = h.bottom
                self.y = float(self.rect.y)
                self.vy = 0

        probe = self.rect.copy()
        probe.y += 1
        self.on_ground = bool(self._tiles_for(probe, map_layout, solid_tiles)) and self.vy >= 0
        if self.on_ground:
            self.jump_count = 0

        if self.rect.y > map_height:
            return True  # fell off map
        return False

    def update_animation(self, dt):
        new_state = 'idle'
        if not self.on_ground:
            new_state = 'double_jump' if self.jump_count == 2 else ('jump' if self.vy < 0 else 'fall')
        elif self.vx != 0:
            new_state = 'run'
        
        if new_state != self.state:
            self.state = new_state
            self.frame_idx = 0
        
        spd = 20 if self.state == 'run' else 12
        self.frame_idx += spd * dt

    def draw(self, surface, sx, sy):
        frames = self.anims[self.state]
        if not frames:
            return
        idx = (int(self.frame_idx) % len(frames)) if self.state not in ('jump', 'fall', 'double_jump') else min(int(self.frame_idx), len(frames) - 1)
        img = frames[idx]
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        bx = self.rect.centerx - img.get_width() // 2 - sx
        by = self.rect.bottom - img.get_height() - sy
        surface.blit(img, (bx, by))

class MapManager:
    def __init__(self):
        self.current_map = 0
        self.maps = []
        
        if IND_AVAILABLE:
            self.maps.append({
                'name': 'Industrial Zone',
                'layout': IND_LAYOUT,
                'tiles': IND_TILES,
                'solid': IND_SOLID,
                'decor': IND_DECOR,
                'anim_decor': IND_ANIM if IND_AVAILABLE else [],
                'coins': IND_COINS_COORDS.copy() if IND_AVAILABLE else [],
                'coin_frames': IND_COINS if IND_AVAILABLE else None,
                'platform_frames': IND_PLATFORM if IND_AVAILABLE else None,
                'bg': IND_BG if IND_AVAILABLE else None,
                'conv_start': CONV_L_COL_S if IND_AVAILABLE else 0,
                'conv_end': CONV_L_COL_E if IND_AVAILABLE else 0,
                'spawn': (4 * TILE_SIZE, 2 * TILE_SIZE),
                'width': max(len(r) for r in IND_LAYOUT) * TILE_SIZE,
                'height': len(IND_LAYOUT) * TILE_SIZE
            })
        
        if GREEN_AVAILABLE:
            self.maps.append({
                'name': 'Green Zone',
                'layout': GREEN_LAYOUT,
                'tiles': GREEN_TILES,
                'solid': GREEN_SOLID,
                'decor': GREEN_DECOR,
                'anim_decor': [],
                'coins': GREEN_CHESTS.copy() if GREEN_AVAILABLE else [],
                'coin_frames': GREEN_COINS if GREEN_AVAILABLE else None,
                'platform_frames': None,
                'bg': GREEN_BG if GREEN_AVAILABLE else [],
                'conv_start': 0,
                'conv_end': 0,
                'spawn': (120, 200),
                'width': max(len(r) for r in GREEN_LAYOUT) * TILE_SIZE,
                'height': len(GREEN_LAYOUT) * TILE_SIZE,
                'fountain_frames': GREEN_FOUNTAIN if GREEN_AVAILABLE else None
            })
        
        if EXCL_AVAILABLE:
            self.maps.append({
                'name': 'Exclusion Zone',
                'layout': EXCL_LAYOUT,
                'tiles': EXCL_TILES,
                'solid': EXCL_SOLID,
                'decor': EXCL_DECOR,
                'anim_decor': [],
                'coins': EXCL_COINS_COORDS.copy() if EXCL_AVAILABLE else [],
                'coin_frames': EXCL_COINS if EXCL_AVAILABLE else None,
                'platform_frames': None,
                'bg': EXCL_BG if EXCL_AVAILABLE else [],
                'conv_start': 0,
                'conv_end': 0,
                'spawn': (120, 340),
                'width': max(len(r) for r in EXCL_LAYOUT) * TILE_SIZE,
                'height': len(EXCL_LAYOUT) * TILE_SIZE,
                'card_frames': EXCL_CARDS if EXCL_AVAILABLE else None
            })

    def get_current_map(self):
        return self.maps[self.current_map]

    def switch_map(self, direction):
        if direction == 'next':
            self.current_map = (self.current_map + 1) % len(self.maps)
        elif direction == 'prev':
            self.current_map = (self.current_map - 1) % len(self.maps)
        return self.get_current_map()

    def check_transition(self, player):
        current = self.get_current_map()
        map_w = current['width']
        
        # Check right edge - go to next map
        if player.rect.right >= map_w - 10:
            return 'next'
        # Check left edge - go to previous map
        if player.rect.left <= 10:
            return 'prev'
        return None

def draw_hud(surface, game_state, map_name):
    try:
        f_big = pygame.font.SysFont("segoeui", 18, bold=True)
        f_sm = pygame.font.SysFont("consolas", 13)
    except Exception:
        f_big = f_sm = pygame.font.Font(None, 20)

    # Health panel
    panel = pygame.Surface((170, 50), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 12, 5, 215), (0, 0, 170, 50), border_radius=10)
    pygame.draw.rect(panel, (220, 100, 30, 120), (0, 0, 170, 50), 2, border_radius=10)
    surface.blit(panel, (10, 10))
    for i in range(game_state["max_health"]):
        cx = 28 + i * 34
        cy = 35
        filled = i < game_state["health"]
        pygame.draw.circle(surface, (255, 140, 20) if filled else (80, 50, 20), (cx, cy), 13, 2)
        pygame.draw.circle(surface, (220, 110, 15) if filled else (50, 30, 10), (cx, cy), 10)
        if filled:
            pygame.draw.circle(surface, (255, 220, 130), (cx - 4, cy - 4), 4)

    # Score panel
    sp = pygame.Surface((170, 44), pygame.SRCALPHA)
    pygame.draw.rect(sp, (20, 12, 5, 215), (0, 0, 170, 44), border_radius=10)
    pygame.draw.rect(sp, (220, 100, 30, 120), (0, 0, 170, 44), 2, border_radius=10)
    surface.blit(sp, (SCREEN_W - 180, 10))
    score_lbl = f_big.render(f"SCORE  {game_state['score']}", True, (255, 180, 60))
    surface.blit(score_lbl, (SCREEN_W - 178, 22))

    # Map name
    lvl = f_sm.render(map_name.upper(), True, (255, 150, 50))
    surface.blit(lvl, (SCREEN_W // 2 - lvl.get_width() // 2, 8))

    # Controls
    controls = [("[A]/[D]", "Move"), ("[Space]/[W]", "Double Jump"), ("[ESC]", "Quit")]
    py = SCREEN_H - 20 - len(controls) * 20
    for i, (k, a) in enumerate(controls):
        surface.blit(f_sm.render(k, True, (255, 190, 110)), (20, py + i * 20))
        surface.blit(f_sm.render(a, True, (200, 140, 70)), (120, py + i * 20))

def main():
    global SCREEN_W, SCREEN_H, screen
    
    if len(sys.argv) > 1 and sys.argv[1] == '--module':
        return "merged_game"

    game_state = {"health": 3, "max_health": 3, "score": 0, "lives": 3}
    map_manager = MapManager()
    
    if not map_manager.maps:
        print("No maps available!")
        return
    
    current_map = map_manager.get_current_map()
    player = Player(*current_map['spawn'])
    
    # Spawn AI enemy at a distance from player
    if AI_AVAILABLE:
        enemy_spawn_x = min(current_map['width'] - 100, player.x + 300)
        enemy = MaskDudeBot(enemy_spawn_x, player.y, tile_size=TILE_SIZE, 
                           map_layout=current_map['layout'], 
                           solid_tiles=current_map['solid'])
        enemy.set_target(player)
    else:
        # Fallback to simple enemy if AI not available
        enemy_spawn_x = min(current_map['width'] - 100, player.x + 300)
        enemy = None
    
    clock = pygame.time.Clock()
    t = sx = sy = 0.0
    running = True
    transition_cooldown = 0.0
    game_over = False
    in_transition = False

    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if game_over and not in_transition:
                        # Restart game (only if not in transition)
                        game_over = False
                        game_state = {"health": 3, "max_health": 3, "score": 0, "lives": 3}
                        current_map = map_manager.get_current_map()
                        player = Player(*current_map['spawn'])
                        if AI_AVAILABLE:
                            enemy_spawn_x = min(current_map['width'] - 100, player.x + 300)
                            enemy = MaskDudeBot(enemy_spawn_x, player.y, tile_size=TILE_SIZE, 
                                               map_layout=current_map['layout'], 
                                               solid_tiles=current_map['solid'])
                            enemy.set_target(player)
                        else:
                            enemy = None
                        sx = sy = 0.0
                    else:
                        player.jump()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)

        # Update player
        fell_off = player.update(dt, current_map['layout'], current_map['solid'], current_map['height'])
        # Check if player fell off map (only if not on transition cooldown)
        if fell_off and transition_cooldown <= 0:
            if game_state["health"] > 0:
                game_state["health"] -= 1
            if game_state["health"] <= 0:
                game_state["health"] = game_state["max_health"]
                game_state["lives"] = max(0, game_state["lives"] - 1)
            # Respawn at current map spawn
            player.x, player.y = current_map['spawn']
            player.rect.x = int(player.x)
            player.rect.y = int(player.y)
            player.vx = 0
            player.vy = 0

        # Update enemy if game is not over and AI is available and not on transition cooldown
        if not game_over and enemy and AI_AVAILABLE and transition_cooldown <= 0:
            enemy.update(dt, current_map['height'])
            
            # Check if enemy caught player
            if enemy.get_rect().colliderect(player.rect):
                game_over = True
            
            # Check if enemy fell off map - respawn behind player
            if enemy.rect.y > current_map['height']:
                offset = -200 if player.facing_right else 200
                enemy.x = float(player.rect.centerx + offset)
                enemy.y = float(player.rect.y - 100)
                enemy.rect.x = int(enemy.x)
                enemy.rect.y = int(enemy.y)
                enemy.vx = 0
                enemy.vy = 0

        # Coin collection
        for entry in current_map['coins'][:]:
            cr = pygame.Rect(entry[0] * TILE_SIZE, entry[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if player.rect.colliderect(cr):
                game_state["score"] += 10
                current_map['coins'].remove(entry)

        # Update transition cooldown
        if transition_cooldown > 0:
            transition_cooldown -= dt
        else:
            in_transition = False

        # Check map transition (only if not on cooldown)
        transition = None
        if transition_cooldown <= 0:
            transition = map_manager.check_transition(player)
        
        if transition:
            in_transition = True
            current_map = map_manager.switch_map(transition)
            # Position player at opposite edge
            if transition == 'next':
                player.x = 50.0
            else:
                player.x = current_map['width'] - 50.0 - player.rect.width
            
            # Find safe Y position (on solid ground)
            spawn_x = int(player.x)
            spawn_y = current_map['spawn'][1]  # Use map's default spawn Y
            player.y = float(spawn_y)
            
            player.rect.x = int(player.x)
            player.rect.y = int(player.y)
            player.vx = 0
            player.vy = 0
            player.on_ground = False
            player.jump_count = 0
            
            # Reposition bot on new map behind the player (chasing game logic)
            if enemy and AI_AVAILABLE:
                enemy.map_layout = current_map['layout']
                enemy.solid_tiles = current_map['solid']
                # Spawn bot behind player on new map so chase continues
                offset = -250 if player.facing_right else 250
                enemy.x = float(player.rect.centerx + offset)
                enemy.y = float(player.rect.y)
                enemy.rect.x = int(enemy.x)
                enemy.rect.y = int(enemy.y)
                enemy.vx = 0
                enemy.vy = 0
                enemy.on_ground = False
                enemy.jump_count = 0
                enemy.on_wall_l = False
                enemy.on_wall_r = False
                enemy.wall_slide = False
            
            # Reset camera with smooth transition
            sx = player.rect.centerx - SCREEN_W // 2
            sy = player.rect.centery - SCREEN_H // 2
            sx = max(0, min(sx, current_map['width'] - SCREEN_W))
            sy = max(0, min(sy, current_map['height'] - SCREEN_H))
            
            # Add cooldown to prevent immediate re-transition and game over
            transition_cooldown = 1.0

        # Camera
        tx = player.rect.centerx - SCREEN_W // 2
        ty = player.rect.centery - SCREEN_H // 2
        sx += (tx - sx) * 8 * dt
        sy += (ty - sy) * 8 * dt
        sx = max(0, min(sx, current_map['width'] - SCREEN_W))
        sy = max(0, min(sy, current_map['height'] - SCREEN_H))
        isx, isy = int(sx), int(sy)

        # Draw
        screen.fill((18, 14, 22))

        # Background
        if current_map['bg']:
            if isinstance(current_map['bg'], list):
                # Parallax for layered backgrounds
                for i, bg in enumerate(current_map['bg']):
                    px = (sx * 0.06 * i) % bg.get_width()
                    py = SCREEN_H - bg.get_height() + sy * 0.02 * i
                    screen.blit(bg, (-px, py))
                    if px > 0:
                        screen.blit(bg, (bg.get_width() - px, py))
            else:
                screen.blit(current_map['bg'], (0, 0))

        # Animated platform (industrial)
        if current_map['platform_frames']:
            pf = current_map['platform_frames'][int(t * 10) % len(current_map['platform_frames'])]
            row_y = 10 * TILE_SIZE - isy
            if -TILE_SIZE < row_y < SCREEN_H + TILE_SIZE:
                for col in range(current_map['conv_start'], current_map['conv_end']):
                    bx = col * TILE_SIZE - isx
                    if -TILE_SIZE < bx < SCREEN_W:
                        screen.blit(pf, (bx, row_y))

        # Static decorations
        for img, ox, oy in current_map['decor']:
            bx = ox - isx
            by = oy - isy
            if -img.get_width() < bx < SCREEN_W and -img.get_height() < by < SCREEN_H:
                screen.blit(img, (bx, by))

        # Animated decorations
        for frames, wx, wy in current_map['anim_decor']:
            if frames:
                fi = int(t * 6) % len(frames)
                img = frames[fi]
                bx = wx - isx
                by = wy - isy
                if -64 < bx < SCREEN_W and -64 < by < SCREEN_H:
                    screen.blit(img, (bx, by))

        # Tiles
        for ri, row in enumerate(current_map['layout']):
            ry = ri * TILE_SIZE - isy
            if ry < -TILE_SIZE or ry > SCREEN_H + TILE_SIZE:
                continue
            for ci, sym in enumerate(row):
                if sym in (' ', 'c', 'C'):
                    continue
                rx = ci * TILE_SIZE - isx
                if rx < -TILE_SIZE or rx > SCREEN_W + TILE_SIZE:
                    continue
                if sym in current_map['tiles']:
                    screen.blit(current_map['tiles'][sym], (rx, ry))

        # Coins
        if current_map['coin_frames']:
            cf = current_map['coin_frames'][int(t * 8) % len(current_map['coin_frames'])]
            for cx, cy in current_map['coins']:
                bx = cx * TILE_SIZE - isx + (TILE_SIZE - cf.get_width()) // 2
                by = cy * TILE_SIZE - isy + (TILE_SIZE - cf.get_height()) // 2
                if -32 < bx < SCREEN_W and -32 < by < SCREEN_H:
                    screen.blit(cf, (bx, by + int(math.sin(t * 4 + cx) * 3)))

        # Fountain (green zone)
        if current_map.get('fountain_frames'):
            ff = current_map['fountain_frames'][int(t * 6) % len(current_map['fountain_frames'])]
            fx, fy = 59 * TILE_SIZE - isx, 10 * TILE_SIZE - ff.get_height() - isy
            if -100 < fx < SCREEN_W and -100 < fy < SCREEN_H:
                screen.blit(ff, (fx, fy))

        # Cards (exclusion zone)
        if current_map.get('card_frames'):
            kf = current_map['card_frames'][int(t * 5) % len(current_map['card_frames'])]
            for cpx, cpy in [(62 * TILE_SIZE, 6), (64 * TILE_SIZE, 6)]:
                bx = cpx - isx
                by = cpy * TILE_SIZE - kf.get_height() - isy
                if -64 < bx < SCREEN_W and -64 < by < SCREEN_H:
                    screen.blit(kf, (bx, by + int(math.sin(t * 3 + cpx) * 3)))

        draw_hud(screen, game_state, current_map['name'])
        player.draw(screen, isx, isy)
        
        # Draw enemy
        if not game_over and enemy and AI_AVAILABLE:
            enemy.draw(screen, isx, isy)
        
        # Game over screen
        if game_over:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            font_large = pygame.font.SysFont("segoeui", 48, bold=True)
            font_small = pygame.font.SysFont("segoeui", 24)
            
            game_over_text = font_large.render("GAME OVER", True, (255, 50, 50))
            caught_text = font_small.render("You were caught by the Shadow Stalker!", True, (255, 255, 255))
            restart_text = font_small.render("Press SPACE to restart", True, (200, 200, 200))
            
            screen.blit(game_over_text, (SCREEN_W // 2 - game_over_text.get_width() // 2, SCREEN_H // 2 - 50))
            screen.blit(caught_text, (SCREEN_W // 2 - caught_text.get_width() // 2, SCREEN_H // 2 + 10))
            screen.blit(restart_text, (SCREEN_W // 2 - restart_text.get_width() // 2, SCREEN_H // 2 + 50))
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    import math
    main()
