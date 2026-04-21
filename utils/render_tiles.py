import os, pygame

# Paths
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
BASE = os.path.join(PARENT_DIR, "assets", "craftpix-net-924041-power-station-free-tileset-pixel-art")
TILES_DIR = os.path.join(BASE, "1 Tiles")

pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)
COLS = 10
TILE = 32
PAD  = 4
FONT_SIZE = 12

tiles = sorted([f for f in os.listdir(TILES_DIR) if f.endswith('.png') and 'Tileset' not in f])
ROWS = (len(tiles) + COLS - 1) // COLS
W = COLS * (TILE + PAD) + PAD
H = ROWS * (TILE + PAD + FONT_SIZE + 2) + PAD

surface = pygame.Surface((W, H))
font = pygame.font.SysFont("consolas", FONT_SIZE)

surface.fill((30, 28, 40))
for i, fname in enumerate(tiles):
    img = pygame.image.load(os.path.join(TILES_DIR, fname)).convert_alpha()
    img = pygame.transform.scale(img, (TILE, TILE))
    col = i % COLS
    row = i // COLS
    x = PAD + col * (TILE + PAD)
    y = PAD + row * (TILE + PAD + FONT_SIZE + 2)
    surface.blit(img, (x, y))
    
    num = fname.replace("Tile_", "").replace(".png", "")
    lbl = font.render(num, True, (255, 220, 100))
    surface.blit(lbl, (x, y + TILE + 1))

pygame.image.save(surface, "power_station_tiles_numbered.png")
