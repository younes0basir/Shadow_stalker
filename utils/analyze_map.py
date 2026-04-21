import pygame
import sys
pygame.init()
img = pygame.image.load("ref_map.png")
# The actual image size is 1233x611. It seems cropped. Let's assume standard 32x32 tiles.
w, h = img.get_size()
tile_size = 32

cols = w // tile_size
rows = h // tile_size

for r in range(rows):
    line = f"{r:02d} "
    for c in range(cols):
        # sample a 20x20 box in the center of the 32x32 tile
        r_sum, g_sum, b_sum = 0, 0, 0
        samples = 0
        for i in range(c*tile_size + 6, c*tile_size + 26):
            for j in range(r*tile_size + 6, r*tile_size + 26):
                if i < w and j < h:
                    color = img.get_at((i, j))
                    r_sum += color.r
                    g_sum += color.g
                    b_sum += color.b
                    samples += 1
        
        if samples == 0:
            line += "  "
            continue
            
        r_avg = r_sum // samples
        g_avg = g_sum // samples
        b_avg = b_sum // samples
        
        # print ANSI colored block
        line += f"\033[48;2;{r_avg};{g_avg};{b_avg}m  \033[0m"
    print(line)
