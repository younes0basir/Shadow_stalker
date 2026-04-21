"""Tile viewer — renders all IndustrialTile_XX.png in a grid so we can identify each tile visually."""
import os, sys, pygame

# Paths
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
BASE = os.path.join(PARENT_DIR, "assets", "craftpix-net-314143-free-industrial-zone-tileset-pixel-art")
TILES_DIR = os.path.join(BASE, "1 Tiles")

pygame.init()
COLS = 9
TILE = 32
PAD  = 4
FONT_SIZE = 10

tiles = sorted([f for f in os.listdir(TILES_DIR) if f.endswith('.png') and 'Tileset' not in f])
ROWS = (len(tiles) + COLS - 1) // COLS
W = COLS * (TILE + PAD) + PAD
H = ROWS * (TILE + PAD + FONT_SIZE + 2) + PAD + 30

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Industrial Tile Viewer – press ESC to quit")
font = pygame.font.SysFont("consolas", FONT_SIZE)

imgs = []
for fname in tiles:
    img = pygame.image.load(os.path.join(TILES_DIR, fname)).convert_alpha()
    img = pygame.transform.scale(img, (TILE, TILE))
    imgs.append((fname, img))

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            running = False

    screen.fill((30, 28, 40))
    for i, (fname, img) in enumerate(imgs):
        col = i % COLS
        row = i // COLS
        x = PAD + col * (TILE + PAD)
        y = PAD + row * (TILE + PAD + FONT_SIZE + 2)
        screen.blit(img, (x, y))
        # draw number label
        num = fname.replace("IndustrialTile_", "").replace(".png", "")
        lbl = font.render(num, True, (255, 220, 100))
        screen.blit(lbl, (x, y + TILE + 1))

    pygame.display.flip()

pygame.quit()
sys.exit()
