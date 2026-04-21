import os, pygame, glob

# Paths
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
BASE = os.path.join(PARENT_DIR, "assets", "craftpix-net-924041-power-station-free-tileset-pixel-art")
OBJ_DIR = os.path.join(BASE, "3 Objects")

pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

# Find all png files
obj_files = []
for root, _, files in os.walk(OBJ_DIR):
    for f in files:
        if f.endswith(".png"):
            obj_files.append(os.path.join(root, f))

# Read images
imgs = []
max_h = 0
for path in obj_files:
    img = pygame.image.load(path).convert_alpha()
    imgs.append((path.replace(OBJ_DIR + os.sep, ""), img))
    if img.get_height() > max_h:
        max_h = img.get_height()

PAD = 10
W = 1200
H = 1500
surface = pygame.Surface((W, H))
surface.fill((40, 40, 50))
font = pygame.font.SysFont("consolas", 12)

x, y = PAD, PAD
row_h = max_h + 30
for name, img in imgs:
    if x + img.get_width() > W - PAD:
        x = PAD
        y += row_h
    surface.blit(img, (x, y))
    lbl = font.render(name, True, (255, 255, 255))
    surface.blit(lbl, (x, y + img.get_height() + 2))
    x += img.get_width() + PAD

pygame.image.save(surface, "power_station_objects.png")
