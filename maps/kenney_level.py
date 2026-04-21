"""
kenney_level.py  ·  Sunny Grassland Adventure
=========================================================
A bright outdoor platformer level using Kenney Pixel Platformer assets.
Features: grass platforms, trees, coins, clouds, enemies, checkpoints.
"""

import os
import sys
import pygame
import random
import math

pygame.init()
pygame.display.init()  # Required for convert_alpha() when running directly

# Screen dimensions
SCREEN_W, SCREEN_H = 1280, 720
TILE_SIZE = 36  # Scale 18x18 tiles up to 36x36 for visibility

# Paths
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
KENNEY_TILES = os.path.join(PARENT_DIR, "assets", "kenney_pixel-platformer", "Tiles")
KENNEY_CHARS = os.path.join(PARENT_DIR, "assets", "kenney_pixel-platformer", "Tiles", "Characters")
KENNEY_BG = os.path.join(PARENT_DIR, "assets", "kenney_pixel-platformer", "Tiles", "Backgrounds")
PLAYER_PATH = os.path.join(PARENT_DIR, "assets", "MainCharacters", "VirtualGuy")

# Physics
GRAVITY = 1400
JUMP_FORCE = -520
SPEED = 270

# Colors
SKY_TOP = (135, 206, 235)      # Light blue
SKY_BOTTOM = (255, 255, 255)    # White-ish at horizon
CLOUD_COLOR = (255, 255, 255)

# ═════════════════════════════════════════════════════════════
#  ASSET LOADING
# ═════════════════════════════════════════════════════════════

def load_img(path, scale=1):
    """Load and optionally scale an image."""
    try:
        img = pygame.image.load(path)
        # Only convert if display is initialized
        if pygame.display.get_surface():
            img = img.convert_alpha()
        if scale != 1:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (max(1,int(w*scale)), max(1,int(h*scale))))
        return img
    except Exception as e:
        print(f"  FAILED to load: {path} - {e}")
        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        s.fill((255, 0, 255))  # Magenta for missing assets
        return s

def load_sheet_frames(path, fw, fh, scale=1):
    """Load animation frames from a spritesheet."""
    try:
        sheet = pygame.image.load(path)
        if pygame.display.get_surface():
            sheet = sheet.convert_alpha()
        frames = []
        for x in range(0, sheet.get_width(), fw):
            rect = pygame.Rect(x, 0, fw, fh)
            surf = sheet.subsurface(rect).copy()
            if scale != 1:
                surf = pygame.transform.scale(surf, (int(fw * scale), int(fh * scale)))
            frames.append(surf)
        return frames
    except Exception:
        s = pygame.Surface((int(fw * scale), int(fh * scale)), pygame.SRCALPHA)
        s.fill((255, 0, 255))
        return [s]

print("Loading Kenney assets...")

# ── Terrain Tiles ────────────────────────────────────────────
# Kenney tiles are 18x18, we scale to TILE_SIZE (36 = 2x)
TILE_SCALE = TILE_SIZE / 18

TILE_MAPPING = {
    # Row 1: Grass tops (0020-0039)
    'G': "tile_0021.png",   # Grass center top
    '1': "tile_0020.png",   # Grass left edge
    '2': "tile_0022.png",   # Grass right edge
    '3': "tile_0030.png",   # Dirt below grass (center)
    '4': "tile_0031.png",   # Dirt below grass (variation)
    # Row 2: Dirt fill (0040-0059)
    'D': "tile_0041.png",   # Dirt center A
    'd': "tile_0051.png",   # Dirt center B
    'E': "tile_0040.png",   # Dirt left
    'e': "tile_0042.png",   # Dirt right
    # Row 3: Deep dirt/stone (0060-0079)
    '5': "tile_0061.png",   # Stone/dirt deep
    '6': "tile_0062.png",   # Stone/dirt variation
    '7': "tile_0071.png",   # Deep ground
    '8': "tile_0072.png",   # Deep ground variation
    # Row 4: Platforms (0080-0099)
    'P': "tile_0080.png",   # Wood platform left
    'p': "tile_0081.png",   # Wood platform center
    'O': "tile_0082.png",   # Wood platform right
    'L': "tile_0096.png",   # Ladder top
    'l': "tile_0097.png",   # Ladder
    # Row 5: Hazards (0100-0119)
    'S': "tile_0112.png",   # Spikes up
    's': "tile_0113.png",   # Spikes down
    # Row 6: Interactive blocks (0120-0139)
    '?': "tile_0120.png",   # Question block
    '!': "tile_0121.png",   # Exclamation block
    '[': "tile_0122.png",   # Sign left
    ']': "tile_0123.png",   # Sign right
    # Row 7: Collectibles (0140-0159)
    'C': "tile_0148.png",   # Coin gold
    'c': "tile_0149.png",   # Coin silver
    'y': "tile_0152.png",   # Key
    'B': "tile_0156.png",   # Gem blue
    'R': "tile_0157.png",   # Gem red
    'g': "tile_0158.png",   # Gem green
    # Row 8: Doors/flags (0160-0179)
    'F': "tile_0166.png",   # Flag checkpoint
    'f': "tile_0167.png",   # Flag pole
    'V': "tile_0164.png",   # Door closed
    'v': "tile_0165.png",   # Door open
}

# Load all terrain tiles
loaded_tiles = {}
for symbol, filename in TILE_MAPPING.items():
    path = os.path.join(KENNEY_TILES, filename)
    loaded_tiles[symbol] = load_img(path, TILE_SCALE)

# Characters/Enemies (24x24 scaled to 32x32)
CHAR_SCALE = 32 / 24
ENEMY_FRAMES = {}
enemy_types = [
    ("slime", "tile_0000.png", 24, 24),
    ("slime_blue", "tile_0001.png", 24, 24),
    ("slime_red", "tile_0002.png", 24, 24),
    ("barnacle", "tile_0011.png", 24, 24),
    ("bee", "tile_0012.png", 24, 24),
    ("snail", "tile_0021.png", 24, 24),
    ("worm", "tile_0022.png", 24, 24),
    ("fly", "tile_0023.png", 24, 24),
]
for name, fname, fw, fh in enemy_types:
    path = os.path.join(KENNEY_CHARS, fname)
    ENEMY_FRAMES[name] = load_img(path, CHAR_SCALE)

# Background clouds (24x24 scaled up significantly)
CLOUD_SCALE = 3.0  # Scale 24x24 to 72x72
cloud_files = ["tile_0008.png", "tile_0009.png", "tile_0010.png"]
cloud_images = [load_img(os.path.join(KENNEY_BG, f), CLOUD_SCALE) for f in cloud_files]

# Decoration tile types that sit ON TOP of grass
DECORATION_TILES = {
    'T': "tile_0098.png",   # Tree small
    't': "tile_0099.png",   # Tree large  
    'M': "tile_0100.png",   # Mushroom red
    'm': "tile_0101.png",   # Mushroom brown
    'U': "tile_0102.png",   # Bush small
    'u': "tile_0103.png",   # Bush large
    'R': "tile_0094.png",   # Rock
    'r': "tile_0095.png",   # Rock mossy
    'F': "tile_0092.png",   # Flower red
    'W': "tile_0093.png",   # Flower blue
}

# Load decoration tiles
for symbol, filename in DECORATION_TILES.items():
    path = os.path.join(KENNEY_TILES, filename)
    loaded_tiles[symbol] = load_img(path, TILE_SCALE)

# Player animations (using existing VirtualGuy)
PLAYER_ANIMS = {}
for state, fname in [
    ('idle', 'idle.png'),
    ('run', 'run.png'),
    ('jump', 'jump.png'),
    ('double_jump', 'double_jump.png'),
    ('fall', 'fall.png')
]:
    PLAYER_ANIMS[state] = load_sheet_frames(os.path.join(PLAYER_PATH, fname), 32, 32, scale=2.0)

print(f"Loaded {len(loaded_tiles)} tiles, {len(ENEMY_FRAMES)} enemies")

# ═════════════════════════════════════════════════════════════
#  LEVEL DESIGN - Sunny Grassland
# ═════════════════════════════════════════════════════════════

SOLID_TILES = set('GDdEe1234PL?S[]')  # Solid tiles

# Level Design: 15% surface (cols 0-18) -> forced shaft -> two paths at bottom
MAP_LAYOUT = [
    # 0         10        20        30        40        50        60        70        80        90       100       110       120
    # ========= SURFACE AREA (cols 0-18, ~15% of 120 cols) =========
    "                                                                                                                                                                                           ",  # 0
    "   C  C  C                                                                                                                                                                                  ",  # 1
    " 1GGGGGGGG2                                                                                                                                                                                ",  # 2
    "33333333333                                    C   C       C                                                                                                                                ",  # 3
    "33333333333                                   1GGG2     C 1GG2                                                                                                                             ",  # 4
    "33333333333                                  333333    1G23333                                                                                                                              ",  # 5
    "           S                      S          33333333  33333333                       S                                                                                                    ",  # 6
    "F                              1GG2        3333333333333333333               3333333333333                     1GG2                  C   C       1GGG2                                  ",  # 7
    "fGG2                          3333      S 33333333333333333333              S 333333333333                     3333                1GGGGGGGG2  3333                                  ",  # 8
    "333333                         333       1GG2   3333333333333333333333333     1GG2   3333333333                        333                  3333333333   333                            ",  # 9
    "3333333       S        333       S         333333333333       S                   S  333       S         3333333333   333       S        3333333     S    S    S                           ",  # 10
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",  # 11 - Surface solid
    # ========= FORCED SHAFT (narrow gap at col 18, only one way down) =========
    "DDDDDDDDDDDDDDDDDD  DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",  # 12 - GAP at col 18 only
    "DDDDDDDDDDDDDDDDDD  DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",  # 13
    "                  3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333",  # 14 - Landing platform after drop
    "                  3C                                                                                                                                                                        ",  # 15
    "                  31GGG2                                                                                                                                                                   ",  # 16
    "                  3333333              C     C                                                                                                                                             ",  # 17
    "                  33333333            1GGG2 1GGG2                                                                                                                                          ",  # 18
    "                  333333333           33333333333333                                    S                                                                                                  ",  # 19
    "                  3333333333          333333333333333          C  C  C                  1GG2                                                                                               ",  # 20
    "                  33333333333         3333333333333333         1GGGGGGGG2               3333333                                                                                            ",  # 21
    "                  333333333333        33333333333333333        333333333              33333333                              S                                                              ",  # 22
    "                  3333333333333       333333333333333333       3333333333             333333333                            1GG2                                                            ",  # 23
    "                  33333333333333      3333333333333333333      333333333              3333333333                           333333                                                          ",  # 24
    "                  333333333333333     33333333333333333333     33333333               33333333333                          33333333                              S                       ",  # 25
    "                  3333333333333333    333333333333333333333    3333333               333333333333                        333333333                            1GG2                        ",  # 26
    "                  33333333333333333   3333333333333333333333   333333                3333333333333                       3333333333                           3333333                     ",  # 27
    "                  333333333333333333  33333333333333333333333  33333                 33333333333333                      33333333333        C   C   C        33333333          C   C      ",  # 28
    # ========= TWO PATHS FORK (left = continue to exit, right = go back up) =========
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",  # 29 - Fork bottom
    "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",  # 30
    "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",  # 31
    "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",  # 32
    "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",  # 33
    # ========= PATH TO EXIT (left side, cols 18-60) =========
    "                                                                                                                                                                                           ",  # 34
    "                                                                                                                                                                                           ",  # 35
    "                                    1GGGGGGGGGGGGGG2                                              C  C  C                                                                               ",  # 36
    "                                   333333333333333333                   S                  1GGGGGGGGGGGGGG2                                                                                  ",  # 37
    "                                  3333333333333333333             1GGGGGGGGGG2          33333333333333333                    F                                                          ",  # 38
    "                                 333333333333333333333             3333333333333         33333333333333333                  fGG2                                                         ",  # 39
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",  # 40 - Exit path ground
    # ========= PATH BACK UP (right side, elevator shaft) =========
    "                                                                                                                                                                                           ",  # 41
    "                                                                                                                                                                                           ",  # 42
    "                                                                                                                                                                                           ",  # 43
    "                                                                                                                                                                                           ",  # 44
    "                                                                                                           L                                                                               ",  # 45 - Ladder base
    "                                                                                                           L                                                                               ",  # 46
    "                                                                                                           L                                                                               ",  # 47
    "                                                                                                           L                                                                               ",  # 48
    "                                                                                                           L                                                                               ",  # 49
    "                                                                                                           L                                                                               ",  # 50
    "                                                                                                           L                                                                               ",  # 51
    "                                                                                                           L                                                                               ",  # 52
    "                                                                                                           L                                                                               ",  # 53
    "                                                                                                           L                                                                               ",  # 54
    "                                                                                                           L                                                                               ",  # 55
    "                                                                                                           L                                                                               ",  # 56
    "                                                                                                           L                                                                               ",  # 57
    "                                                                                                           L                                                                               ",  # 58
    "                                                                                                           L                                                                               ",  # 59
    "                                                                                                           L                                                                               ",  # 60
    "                                                                                                           L                                                                               ",  # 61
    "                                                                                                           L                                                                               ",  # 62
    "                                                                                                           L                                                                               ",  # 63
    "                                                                                                           L                                                                               ",  # 64
    "                                                                                                           L                                                                               ",  # 65
    "                                                                                                           L                                                                               ",  # 66
    "                                                                                                           L                                                                               ",  # 67
    "                                                                                                           L                                                                               ",  # 68
    "                                                                                                           L                                                                               ",  # 69
    "                                                                                                           L                                                                               ",  # 70
    "                                                                                                           L                                                                               ",  # 71
    "                                                                                                           L                                                                               ",  # 72
    "                                                                                                           L                                                                               ",  # 73
    "                                                                                                           L                                                                               ",  # 74
    "                                                                                                           L                                                                               ",  # 75
    "                                                                                                           L                                                                               ",  # 76
    "                                                                                                           L                                                                               ",  # 77
    "                                                                                                           L                                                                               ",  # 78
    "                                                                                                           L                                                                               ",  # 79
    "                                                                                                           L                                                                               ",  # 80
    "                                                                                                           L                                                                               ",  # 81
    "                                                                                                           L                                                                               ",  # 82
    "                                                                                                           L                                                                               ",  # 83
    "                                                                                                           L                                                                               ",  # 84
    "                                                                                                           L                                                                               ",  # 85
    "                                                                                                           L                                                                               ",  # 86
    "                                                                                                           L                                                                               ",  # 87
    "                                                                                                           L                                                                               ",  # 88
    "                                                                                                           L                                                                               ",  # 89
    "                                                                                                           L                                                                               ",  # 90
    "                                                                                                           L                                                                               ",  # 91
    "                                                                                                           L                                                                               ",  # 92
    "                                                                                                           L                                                                               ",  # 93
    "                                                                                                           L                                                                               ",  # 94
    "                                                                                                           L                                                                               ",  # 95
    "                                                                                                           L                                                                               ",  # 96
    "                                                                                                           L                                                                               ",  # 97
    "                                                                                                           L                                                                               ",  # 98
    "                                                                                                           L                                                                               ",  # 99
    "                                                                                                           L                                                                               ",  # 100
    "                                                                                                           L                                                                               ",  # 101
    "                                                                                                           L                                                                               ",  # 102
    "                                                                                                           L                                                                               ",  # 103
    "                                                                                                           L                                                                               ",  # 104
    "                                                                                                           L                                                                               ",  # 105
    "                                                                                                           L                                                                               ",  # 106
    "                                                                                                           L                                                                               ",  # 107
    "                                                                                                           L                                                                               ",  # 108
    "                                                                                                           L                                                                               ",  # 109
    "                                                                                                           L                                                                               ",  # 110
    "                                                                                                           L                                                                               ",  # 111
    "                                                                                                           L                                                                               ",  # 112
    "                                                                                                           L                                                                               ",  # 113
    "                                                                                                           L                                                                               ",  # 114
    "                                                                                                           L                                                                               ",  # 115
    "                                                                                                           L                                                                               ",  # 116
    "                                                                                                           L                                                                               ",  # 117
    "                                                                                                           L                                                                               ",  # 118
    "                                                                                                           L                                                                               ",  # 119
    "                                                                                                           L                                                                               ",  # 120
    "                                                                                                           L                                                                               ",  # 121
    "                                                                                                           L                                                                               ",  # 122
    "                                                                                                           L                                                                               ",  # 123
    "                                                                                                           L                                                                               ",  # 124
    "                                                                                                           L                                                                               ",  # 125
    "                                                                                                           L                                                                               ",  # 126
    "                                                                                                           L                                                                               ",  # 127
    "                                                                                                           L                                                                               ",  # 128
    "                                                                                                           L                                                                               ",  # 129
    "                                                                                                           L                                                                               ",  # 130
    "                                                                                                           L                                                                               ",  # 131
    "                                                                                                           L                                                                               ",  # 132
    "                                                                                                           L                                                                               ",  # 133
    "                                                                                                           L                                                                               ",  # 134
    "                                                                                                           L                                                                               ",  # 135
    "                                                                                                           L                                                                               ",  # 136
    "                                                                                                           L                                                                               ",  # 137
    "                                                                                                           L                                                                               ",  # 138
    "                                                                                                           L                                                                               ",  # 139
    "                                                                                                           L                                                                               ",  # 140
    "                                                                                                           L                                                                               ",  # 141
    "                                                                                                           L                                                                               ",  # 142
    "                                                                                                           L                                                                               ",  # 143
    "                                                                                                           L                                                                               ",  # 144
    "                                                                                                           L                                                                               ",  # 145
    "                                                                                                           L                                                                               ",  # 146
    "                                                                                                           L                                                                               ",  # 147
    "                                                                                                           L                                                                               ",  # 148
    "                                                                                                           L                                                                               ",  # 149
    "                                                                                                           L                                                                               ",  # 150
    "                                                                                                           L                                                                               ",  # 151
    "                                                                                                           L                                                                               ",  # 152
    "                                                                                                           L                                                                               ",  # 153
    "                                                                                                           L                                                                               ",  # 154
    "                                                                                                           L                                                                               ",  # 155
    "                                                                                                           L                                                                               ",  # 156
    "                                                                                                           L                                                                               ",  # 157
    "                                                                                                           L                                                                               ",  # 158
    "                                                                                                           L                                                                               ",  # 159
    "                                                                                                           L                                                                               ",  # 160
    "                                                                                                           L                                                                               ",  # 161
    "                                                                                                           L                                                                               ",  # 162
    "                                                                                                           L                                                                               ",  # 163
    "                                                                                                           L                                                                               ",  # 164
    "                                                                                                           L                                                                               ",  # 165
    "                                                                                                           L                                                                               ",  # 166
    "                                                                                                           L                                                                               ",  # 167
    "                                                                                                           L                                                                               ",  # 168
    "                                                                                                           L                                                                               ",  # 169
    "                                                                                                           L                                                                               ",  # 170
    "                                                                                                           L                                                                               ",  # 171
    "                                                                                                           L                                                                               ",  # 172
    "                                                                                                           L                                                                               ",  # 173
    "                                                                                                           L                                                                               ",  # 174
    "                                                                                                           L                                                                               ",  # 175
    "                                                                                                           L                                                                               ",  # 176
    "                                                                                                           L                                                                               ",  # 177
    "                                                                                                           L                                                                               ",  # 178
    "                                                                                                           L                                                                               ",  # 179
    "                                                                                                           L                                                                               ",  # 180
    "                                                                                                           L                                                                               ",  # 181
    "                                                                                                           L                                                                               ",  # 182
    "                                                                                                           L                                                                               ",  # 183
    "                                                                                                           L                                                                               ",  # 184
    "                                                                                                           L                                                                               ",  # 185
    "                                                                                                           L                                                                               ",  # 186
    "                                                                                                           L                                                                               ",  # 187
    "                                                                                                           L                                                                               ",  # 188
    "                                                                                                           L                                                                               ",  # 189
    "                                                                                                           L                                                                               ",  # 190
    "                                                                                                           L                                                                               ",  # 191
    "                                                                                                           L                                                                               ",  # 192
    "                                                                                                           L                                                                               ",  # 193
    "                                                                                                           L                                                                               ",  # 194
    "                                                                                                           L                                                                               ",  # 195
    "                                                                                                           L                                                                               ",  # 196
    "                                                                                                           L                                                                               ",  # 197
    "                                                                                                           L                                                                               ",  # 198
    "                                                                                                           L                                                                               ",  # 199
    "                                                                                                           L                                                                               ",  # 200
    "                                                                                                           L                                                                               ",  # 201
    "                                                                                                           L                                                                               ",  # 202
    "                                                                                                           L                                                                               ",  # 203
    "                                                                                                           L                                                                               ",  # 204
    "                                                                                                           L                                                                               ",  # 205
    "                                                                                                           L                                                                               ",  # 206
    "                                                                                                           L                                                                               ",  # 207
    "                                                                                                           L                                                                               ",  # 208
    "                                                                                                           L                                                                               ",  # 209
    "                                                                                                           L                                                                               ",  # 210
    "                                                                                                           L                                                                               ",  # 211
    "                                                                                                           L                                                                               ",  # 212
    "                                                                                                           L                                                                               ",  # 213
    "                                                                                                           L                                                                               ",  # 214
    "                                                                                                           L                                                                               ",  # 215
    "                                                                                                           L                                                                               ",  # 216
    "                                                                                                           L                                                                               ",  # 217
    "                                                                                                           L                                                                               ",  # 218
    "                                                                                                           L                                                                               ",  # 219
    "                                                                                                           L                                                                               ",  # 220
    "                                                                                                           L                                                                               ",  # 221
    "                                                                                                           L                                                                               ",  # 222
    "                                                                                                           L                                                                               ",  # 223
    "                                                                                                           L                                                                               ",  # 224
    "                                                                                                           L                                                                               ",  # 225
    "                                                                                                           L                                                                               ",  # 226
    "                                                                                                           L                                                                               ",  # 227
    "                                                                                                           L                                                                               ",  # 228
    "                                                                                                           L                                                                               ",  # 229
    "                                                                                                           L                                                                               ",  # 230
    "                                                                                                           L                                                                               ",  # 231
    "                                                                                                           L                                                                               ",  # 232
    "                                                                                                           L                                                                               ",  # 233
    "                                                                                                           L                                                                               ",  # 234
    "                                                                                                           L                                                                               ",  # 235
    "                                                                                                           L                                                                               ",  # 236
    "                                                                                                           L                                                                               ",  # 237
    "                                                                                                           L                                                                               ",  # 238
    "                                                                                                           L                                                                               ",  # 239
    "                                                                                                           L                                                                               ",  # 240
    "                                                                                                           L                                                                               ",  # 241
    "                                                                                                           L                                                                               ",  # 242
    "                                                                                                           L                                                                               ",  # 243
    "                                                                                                           L                                                                               ",  # 244
    "                                                                                                           L                                                                               ",  # 245
    "                                                                                                           L                                                                               ",  # 246
    "                                                                                                           L                                                                               ",  # 247
    "                                                                                                           L                                                                               ",  # 248
    "                                                                                                           L                                                                               ",  # 249
    "                                                                                                           L                                                                               ",  # 250
    "                                                                                                           L                                                                               ",  # 251
    "                                                                                                           L                                                                               ",  # 252
    "                                                                                                           L                                                                               ",  # 253
    "                                                                                                           L                                                                               ",  # 254
    "                                                                                                           L                                                                               ",  # 255
    "                                                                                                           L                                                                               ",  # 256
    "                                                                                                           L                                                                               ",  # 257
    "                                                                                                           L                                                                               ",  # 258
    "                                                                                                           L                                                                               ",  # 259
    "                                                                                                           L                                                                               ",  # 260
    "                                                                                                           L                                                                               ",  # 261
    "                                                                                                           L                                                                               ",  # 262
    "                                                                                                           L                                                                               ",  # 263
    "                                                                                                           L                                                                               ",  # 264
    "                                                                                                           L                                                                               ",  # 265
    "                                                                                                           L                                                                               ",  # 266
    "                                                                                                           L                                                                               ",  # 267
    "                                                                                                           L                                                                               ",  # 268
    "                                                                                                           L                                                                               ",  # 269
    "                                                                                                           L                                                                               ",  # 270
    "                                                                                                           L                                                                               ",  # 271
    "                                                                                                           L                                                                               ",  # 272
    "                                                                                                           L                                                                               ",  # 273
    "                                                                                                           L                                                                               ",  # 274
    "                                                                                                           L                                                                               ",  # 275
    "                                                                                                           L                                                                               ",  # 276
    "                                                                                                           L                                                                               ",  # 277
    "                                                                                                           L                                                                               ",  # 278
    "                                                                                                           L                                                                               ",  # 279
    "                                                                                                           L                                                                               ",  # 280
    "                                                                                                           L                                                                               ",  # 281
    "                                                                                                           L                                                                               ",  # 282
    "                                                                                                           L                                                                               ",  # 283
    "                                                                                                           L                                                                               ",  # 284
    "                                                                                                           L                                                                               ",  # 285
    "                                                                                                           L                                                                               ",  # 286
    "                                                                                                           L                                                                               ",  # 287
    "                                                                                                           L                                                                               ",  # 288
    "                                                                                                           L                                                                               ",  # 289
    "                                                                                                           L                                                                               ",  # 290
    "                                                                                                           L                                                                               ",  # 291
    "                                                                                                           L                                                                               ",  # 292
    "                                                                                                           L                                                                               ",  # 293
    "                                                                                                           L                                                                               ",  # 294
    "                                                                                                           L                                                                               ",  # 295
    "                                                                                                           L                                                                               ",  # 296
    "                                                                                                           L                                                                               ",  # 297
    "                                                                                                           L                                                                               ",  # 298
    "                                                                                                           L                                                                               ",  # 299
    "                                                                                                           L                                                                               ",  # 300
    "                                                                                                           L                                                                               ",  # 301
    "                                                                                                           L                                                                               ",  # 302
    "                                                                                                           L                                                                               ",  # 303
    "                                                                                                           L                                                                               ",  # 304
    "                                                                                                           L                                                                               ",  # 305
    "                                                                                                           L                                                                               ",  # 306
    "                                                                                                           L                                                                               ",  # 307
    "                                                                                                           L                                                                               ",  # 308
    "                                                                                                           L                                                                               ",  # 309
    "                                                                                                           L                                                                               ",  # 310
    "                                                                                                           L                                                                               ",  # 311
    "                                                                                                           L                                                                               ",  # 312
    "                                                                                                           L                                                                               ",  # 313
    "                                                                                                           L                                                                               ",  # 314
    "                                                                                                           L                                                                               ",  # 315
    "                                                                                                           L                                                                               ",  # 316
    "                                                                                                           L                                                                               ",  # 317
    "                                                                                                           L                                                                               ",  # 318
    "                                                                                                           L                                                                               ",  # 319
    "                                                                                                           L                                                                               ",  # 320
    "                                                                                                           L                                                                               ",  # 321
    "                                                                                                           L                                                                               ",  # 322
    "                                                                                                           L                                                                               ",  # 323
    "                                                                                                           L                                                                               ",  # 324
    "                                                                                                           L                                                                               ",  # 325
    "                                                                                                           L                                                                               ",  # 326
    "                                                                                                           L                                                                               ",  # 327
    "                                                                                                           L                                                                               ",  # 328
    "                                                                                                           L                                                                               ",  # 329
    "                                                                                                           L                                                                               ",  # 330
    "                                                                                                           L                                                                               ",  # 331
    "                                                                                                           L                                                                               ",  # 332
    "                                                                                                           L                                                                               ",  # 333
    "                                                                                                           L                                                                               ",  # 334
    "                                                                                                           L                                                                               ",  # 335
    "                                                                                                           L                                                                               ",  # 336
    "                                                                                                           L                                                                               ",  # 337
    "                                                                                                           L                                                                               ",  # 338
    "                                                                                                           L                                                                               ",  # 339
    "                                                                                                           L                                                                               ",  # 340
    "                                                                                                           L                                                                               ",  # 341
    "                                                                                                           L                                                                               ",  # 342
    "                                                                                                           L                                                                               ",  # 343
    "                                                                                                           L                                                                               ",  # 344
    "                                                                                                           L                                                                               ",  # 345
    "                                                                                                           L                                                                               ",  # 346
    "                                                                                                           L                                                                               ",  # 347
    "                                                                                                           L                                                                               ",  # 348
    "                                                                                                           L                                                                               ",  # 349
    "                                                                                                           L                                                                               ",  # 350
    "                                                                                                           L                                                                               ",  # 351
    "                                                                                                           L                                                                               ",  # 352
    "                                                                                                           L                                                                               ",  # 353
    "                                                                                                           L                                                                               ",  # 354
    "                                                                                                           L                                                                               ",  # 355
    "                                                                                                           L                                                                               ",  # 356
    "                                                                                                           L                                                                               ",  # 357
    "                                                                                                           L                                                                               ",  # 358
    "                                                                                                           L                                                                               ",  # 359
    "                                                                                                           L                                                                               ",  # 360
    "                                                                                                           L                                                                               ",  # 361
    "                                                                                                           L                                                                               ",  # 362
    "                                                                                                           L                                                                               ",  # 363
    "                                                                                                           L                                                                               ",  # 364
    "                                                                                                           L                                                                               ",  # 365
    "                                                                                                           L                                                                               ",  # 366
    "                                                                                                           L                                                                               ",  # 367
    "                                                                                                           L                                                                               ",  # 368
    "                                                                                                           L                                                                               ",  # 369
    "                                                                                                           L                                                                               ",  # 370
    "                                                                                                           L                                                                               ",  # 371
    "                                                                                                           L                                                                               ",  # 372
    "                                                                                                           L                                                                               ",  # 373
    "                                                                                                           L                                                                               ",  # 374
    "                                                                                                           L                                                                               ",  # 375
    "                                                                                                           L                                                                               ",  # 376
    "                                                                                                           L                                                                               ",  # 377
    "                                                                                                           L                                                                               ",  # 378
    "                                                                                                           L                                                                               ",  # 379
    "                                                                                                           L                                                                               ",  # 380
    "                                                                                                           L                                                                               ",  # 381
    "                                                                                                           L                                                                               ",  # 382
    "                                                                                                           L                                                                               ",  # 383
    "                                                                                                           L                                                                               ",  # 384
    "                                                                                                           L                                                                               ",  # 385
    "                                                                                                           L                                                                               ",  # 386
    "                                                                                                           L                                                                               ",  # 387
    "                                                                                                           L                                                                               ",  # 388
    "                                                                                                           L                                                                               ",  # 389
    "                                                                                                           L                                                                               ",  # 390
    "                                                                                                           L                                                                               ",  # 391
    "                                                                                                           L                                                                               ",  # 392
    "                                                                                                           L                                                                               ",  # 393
    "                                                                                                           L                                                                               ",  # 394
    "                                                                                                           L                                                                               ",  # 395
    "                                                                                                           L                                                                               ",  # 396
    "                                                                                                           L                                                                               ",  # 397
    "                                                                                                           L                                                                               ",  # 398
    "                                                                                                           L                                                                               ",  # 399
    "                                                                                                           L                                                                               ",  # 400
    "                                                                                                           L                                                                               ",  # 401
    "                                                                                                           L                                                                               ",  # 402
    "                                                                                                           L                                                                               ",  # 403
    "                                                                                                           L                                                                               ",  # 404
    "                                                                                                           L                                                                               ",  # 405
    "                                                                                                           L                                                                               ",  # 406
    "                                                                                                           L                                                                               ",  # 407
    "                                                                                                           L                                                                               ",  # 408
    "                                                                                                           L                                                                               ",  # 409
    "                                                                                                           L                                                                               ",  # 410
    "                                                                                                           L                                                                               ",  # 411
    "                                                                                                           L                                                                               ",  # 412
    "                                                                                                           L                                                                               ",  # 413
    "                                                                                                           L                                                                               ",  # 414
    "                                                                                                           L                                                                               ",  # 415
    "                                                                                                           L                                                                               ",  # 416
    "                                                                                                           L                                                                               ",  # 417
    "                                                                                                           L                                                                               ",  # 418
    "                                                                                                           L                                                                               ",  # 419
    "                                                                                                           L                                                                               ",  # 420
    "                                                                                                           L                                                                               ",  # 421
    "                                                                                                           L                                                                               ",  # 422
    "                                                                                                           L                                                                               ",  # 423
    "                                                                                                           L                                                                               ",  # 424
    "                                                                                                           L                                                                               ",  # 425
    "                                                                                                           L                                                                               ",  # 426
    "                                                                                                           L                                                                               ",  # 427
    "                                                                                                           L                                                                               ",  # 428
    "                                                                                                           L                                                                               ",  # 429
    "                                                                                                           L                                                                               ",  # 430
    "                                                                                                           L                                                                               ",  # 431
    "                                                                                                           L                                                                               ",  # 432
    "                                                                                                           L                                                                               ",  # 433
    "                                                                                                           L                                                                               ",  # 434
    "                                                                                                           L                                                                               ",  # 435
    "                                                                                                           L                                                                               ",  # 436
    "                                                                                                           L                                                                               ",  # 437
    "                                                                                                           L                                                                               ",  # 438
    "                                                                                                           L                                                                               ",  # 439
    "                                                                                                           L                                                                               ",  # 440
    "                                                                                                           L                                                                               ",  # 441
    "                                                                                                           L                                                                               ",  # 442
    "                                                                                                           L                                                                               ",  # 443
    "                                                                                                           L                                                                               ",  # 444
    "                                                                                                           L                                                                               ",  # 445
    "                                                                                                           L                                                                               ",  # 446
    "                                                                                                           L                                                                               ",  # 447
    "                                                                                                           L                                                                               ",  # 448
    "                                                                                                           L                                                                               ",  # 449
    "                                                                                                           L                                                                               ",  # 450
    "                                                                                                           L                                                                               ",  # 451
    "                                                                                                           L                                                                               ",  # 452
    "                                                                                                           L                                                                               ",  # 453
    "                                                                                                           L                                                                               ",  # 454
    "                                                                                                           L                                                                               ",  # 455
    "                                                                                                           L                                                                               ",  # 456
    "                                                                                                           L                                                                               ",  # 457
    "                                                                                                           L                                                                               ",  # 458
    "                                                                                                           L                                                                               ",  # 459
    "                                                                                                           L                                                                               ",  # 460
    "                                                                                                           L                                                                               ",  # 461
    "                                                                                                           L                                                                               ",  # 462
    "                                                                                                           L                                                                               ",  # 463
    "                                                                                                           L                                                                               ",  # 464
    "                                                                                                           L                                                                               ",  # 465
    "                                                                                                           L                                                                               ",  # 466
    "                                                                                                           L                                                                               ",  # 467
    "                                                                                                           L                                                                               ",  # 468
    "                                                                                                           L                                                                               ",  # 469
    "                                                                                                           L                                                                               ",  # 470
    "                                                                                                           L                                                                               ",  # 471
    "                                                                                                           L                                                                               ",  # 472
    "                                                                                                           L                                                                               ",  # 473
    "                                                                                                           L                                                                               ",  # 474
    "                                                                                                           L                                                                               ",  # 475
    "                                                                                                           L                                                                               ",  # 476
    "                                                                                                           L                                                                               ",  # 477
    "                                                                                                           L                                                                               ",  # 478
    "                                                                                                           L                                                                               ",  # 479
    "                                                                                                           L                                                                               ",  # 480
    "                                                                                                           L                                                                               ",  # 481
    "                                                                                                           L                                                                               ",  # 482
    "                                                                                                           L                                                                               ",  # 483
    "                                                                                                           L                                                                               ",  # 484
    "                                                                                                           L                                                                               ",  # 485
    "                                                                                                           L                                                                               ",  # 486
    "                                                                                                           L                                                                               ",  # 487
    "                                                                                                           L                                                                               ",  # 488
    "                                                                                                           L                                                                               ",  # 489
    "                                                                                                           L                                                                               ",  # 490
    "                                                                                                           L                                                                               ",  # 491
    "                                                                                                           L                                                                               ",  # 492
    "                                                                                                           L                                                                               ",  # 493
    "                                                                                                           L                                                                               ",  # 494
    "                                                                                                           L                                                                               ",  # 495
    "                                                                                                           L                                                                               ",  # 496
    "                                                                                                           L                                                                               ",  # 497
    "                                                                                                           L                                                                               ",  # 498
    "                                                                                                           L                                                                               ",  # 499
    "                                                                                                           L                                                                               ",  # 500
    "                                                                                                           L                                                                               ",  # 501
    "                                                                                                           L                                                                               ",  # 502
    "                                                                                                           L                                                                               ",  # 503
    "                                                                                                           L                                                                               ",  # 504
    "                                                                                                           L                                                                               ",  # 505
    "                                                                                                           L                                                                               ",  # 506
    "                                                                                                           L                                                                               ",  # 507
    "                                                                                                           L                                                                               ",  # 508
    "                                                                                                           L                                                                               ",  # 509
    "                                                                                                           L                                                                               ",  # 510
    "                                                                                                           L                                                                               ",  # 511
    "                                                                                                           L                                                                               ",  # 512
    "                                                                                                           L                                                                               ",  # 513
    "                                                                                                           L                                                                               ",  # 514
    "                                                                                                           L                                                                               ",  # 515
    "                                                                                                           L                                                                               ",  # 516
    "                                                                                                           L                                                                               ",  # 517
    "                                                                                                           L                                                                               ",  # 518
    "                                                                                                           L                                                                               ",  # 519
    "                                                                                                           L                                                                               ",  # 520
    "                                                                                                           L                                                                               ",  # 521
    "                                                                                                           L                                                                               ",  # 522
    "                                                                                                           L                                                                               ",  # 523
    "                                                                                                           L                                                                               ",  # 524
    "                                                                                                           L                                                                               ",  # 525
    "                                                                                                           L                                                                               ",  # 526
    "                                                                                                           L                                                                               ",  # 527
    "                                                                                                           L                                                                               ",  # 528
    "                                                                                                           L                                                                               ",  # 529
    "                                                                                                           L                                                                               ",  # 530
    "                                                                                                           L                                                                               ",  # 531
    "                                                                                                           L                                                                               ",  # 532
    "                                                                                                           L                                                                               ",  # 533
    "                                                                                                           L                                                                               ",  # 534
    "                                                                                                           L                                                                               ",  # 535
    "                                                                                                           L                                                                               ",  # 536
    "                                                                                                           L                                                                               ",  # 537
    "                                                                                                           L                                                                               ",  # 538
    "                                                                                                           L                                                                               ",  # 539
    "                                                                                                           L                                                                               ",  # 540
    "                                                                                                           L                                                                               ",  # 541
    "                                                                                                           L                                                                               ",  # 542
    "                                                                                                           L                                                                               ",  # 543
    "                                                                                                           L                                                                               ",  # 544
    "                                                                                                           L                                                                               ",  # 545
    "                                                                                                           L                                                                               ",  # 546
    "                                                                                                           L                                                                               ",  # 547
    "                                                                                                           L                                                                               ",  # 548
    "                                                                                                           L                                                                               ",  # 549
    "                                                                                                           L                                                                               ",  # 550
    "                                                                                                           L                                                                               ",  # 551
    "                                                                                                           L                                                                               ",  # 552
    "                                                                                                           L                                                                               ",  # 553
    "                                                                                                           L                                                                               ",  # 554
    "                                                                                                           L                                                                               ",  # 555
    "                                                                                                           L                                                                               ",  # 556
    "                                                                                                           L                                                                               ",  # 557
    "                                                                                                           L                                                                               ",  # 558
    "                                                                                                           L                                                                               ",  # 559
    "                                                                                                           L                                                                               ",  # 560
    "                                                                                                           L                                                                               ",  # 561
    "                                                                                                           L                                                                               ",  # 562
    "                                                                                                           L                                                                               ",  # 563
    "                                                                                                           L                                                                               ",  # 564
    "                                                                                                           L                                                                               ",  # 565
    "                                                                                                           L                                                                               ",  # 566
    "                                                                                                           L                                                                               ",  # 567
    "                                                                                                           L                                                                               ",  # 568
    "                                                                                                           L                                                                               ",  # 569
    "                                                                                                           L                                                                               ",  # 570
    "                                                                                                           L                                                                               ",  # 571
    "                                                                                                           L                                                                               ",  # 572
    "                                                                                                           L                                                                               ",  # 573
    "                                                                                                           L                                                                               ",  # 574
    "                                                                                                           L                                                                               ",  # 575
    "                                                                                                           L                                                                               ",  # 576
    "                                                                                                           L                                                                               ",  # 577
    "                                                                                                           L                                                                               ",  # 578
    "                                                                                                           L                                                                               ",  # 579
    "                                                                                                           L                                                                               ",  # 580
    "                                                                                                           L                                                                               ",  # 581
    "                                                                                                           L                                                                               ",  # 582
    "                                                                                                           L                                                                               ",  # 583
    "                                                                                                           L                                                                               ",  # 584
    "                                                                                                           L                                                                               ",  # 585
    "                                                                                                           L                                                                               ",  # 586
    "                                                                                                           L                                                                               ",  # 587
    "                                                                                                           L                                                                               ",  # 588
    "                                                                                                           L                                                                               ",  # 589
    "                                                                                                           L                                                                               ",  # 590
    "                                                                                                           L                                                                               ",  # 591
    "                                                                                                           L                                                                               ",  # 592
    "                                                                                                           L                                                                               ",  # 593
    "                                                                                                           L                                                                               ",  # 594
    "                                                                                                           L                                                                               ",  # 595
    "                                                                                                           L                                                                               ",  # 596
    "                                                                                                           L                                                                               ",  # 597
    "                                                                                                           L                                                                               ",  # 598
    "                                                                                                           L                                                                               ",  # 599
    "                                                                                                           L                                                                               ",  # 600
    "                                                                                                           L                                                                               ",  # 601
    "                                                                                                           L                                                                               ",  # 602
    "                                                                                                           L                                                                               ",  # 603
    "                                                                                                           L                                                                               ",  # 604
    "                                                                                                           L                                                                               ",  # 605
    "                                                                                                           L                                                                               ",  # 606
    "                                                                                                           L                                                                               ",  # 607
    "                                                                                                           L                                                                               ",  # 608
    "                                                                                                           L                                                                               ",  # 609
    "                                                                                                           L                                                                               ",  # 610
    "                                                                                                           L                                                                               ",  # 611
    "                                                                                                           L                                                                               ",  # 612
    "                                                                                                           L                                                                               ",  # 613
    "                                                                                                           L                                                                               ",  # 614
    "                                                                                                           L                                                                               ",  # 615
    "                                                                                                           L                                                                               ",  # 616
    "                                                                                                           L                                                                               ",  # 617
    "                                                                                                           L                                                                               ",  # 618
    "                                                                                                           L                                                                               ",  # 619
    "                                                                                                           L                                                                               ",  # 620
    "                                                                                                           L                                                                               ",  # 621
    "                                                                                                           L                                                                               ",  # 622
    "                                                                                                           L                                                                               ",  # 623
    "                                                                                                           L                                                                               ",  # 624
    "                                                                                                           L                                                                               ",  # 625
    "                                                                                                           L                                                                               ",  # 626
    "                                                                                                           L                                                                               ",  # 627
    "                                                                                                           L                                                                               ",  # 628
    "                                                                                                           L                                                                               ",  # 629
    "                                                                                                           L                                                                               ",  # 630
    "                                                                                                           L                                                                               ",  # 631
    "                                                                                                           L                                                                               ",  # 632
    "                                                                                                           L                                                                               ",  # 633
    "                                                                                                           L                                                                               ",  # 634
    "                                                                                                           L                                                                               ",  # 635
    "                                                                                                           L                                                                               ",  # 636
    "                                                                                                           L                                                                               ",  # 637
    "                                                                                                           L                                                                               ",  # 638
    "                                                                                                           L                                                                               ",  # 639
    "                                                                                                           L                                                                               ",  # 640
    "                                                                                                           L                                                                               ",  # 641
    "                                                                                                           L                                                                               ",  # 642
    "                                                                                                           L                                                                               ",  # 643
    "                                                                                                           L                                                                               ",  # 644
    "                                                                                                           L                                                                               ",  # 645
    "                                                                                                           L                                                                               ",  # 646
    "                                                                                                           L                                                                               ",  # 647
    "                                                                                                           L                                                                               ",  # 648
    "                                                                                                           L                                                                               ",  # 649
    "                                                                                                           L                                                                               ",  # 650
    "                                                                                                           L                                                                               ",  # 651
    "                                                                                                           L                                                                               ",  # 652
    "                                                                                                           L                                                                               ",  # 653
    "                                                                                                           L                                                                               ",  # 654
    "                                                                                                           L                                                                               ",  # 655
    "                                                                                                           L                                                                               ",  # 656
    "                                                                                                           L                                                                               ",  # 657
    "                                                                                                           L                                                                               ",  # 658
    "                                                                                                           L                                                                               ",  # 659
    "                                                                                                           L                                                                               ",  # 660
    "                                                                                                           L                                                                               ",  # 661
    "                                                                                                           L                                                                               ",  # 662
    "                                                                                                           L                                                                               ",  # 663
    "                                                                                                           L                                                                               ",  # 664
    "                                                                                                           L                                                                               ",  # 665
    "                                                                                                           L                                                                               ",  # 666
    "                                                                                                           L                                                                               ",  # 667
    "                                                                                                           L                                                                               ",  # 668
    "                                                                                                           L                                                                               ",  # 669
    "                                                                                                           L                                                                               ",  # 670
    "                                                                                                           L                                                                               ",  # 671
    "                                                                                                           L                                                                               ",  # 672
    "                                                                                                           L                                                                               ",  # 673
    "                                                                                                           L                                                                               ",  # 674
    "                                                                                                           L                                                                               ",  # 675
    "                                                                                                           L                                                                               ",  # 676
    "                                                                                                           L                                                                               ",  # 677
    "                                                                                                           L                                                                               ",  # 678
    "                                                                                                           L                                                                               ",  # 679
    "                                                                                                           L                                                                               ",  # 680
    "                                                                                                           L                                                                               ",  # 681
    "                                                                                                           L                                                                               ",  # 682
    "                                                                                                           L                                                                               ",  # 683
    "                                                                                                           L                                                                               ",  # 684
    "                                                                                                           L                                                                               ",  # 685
    "                                                                                                           L                                                                               ",  # 686
    "                                                                                                           L                                                                               ",  # 687
    "                                                                                                           L                                                                               ",  # 688
    "                                                                                                           L                                                                               ",  # 689
    "                                                                                                           L                                                                               ",  # 690
    "                                                                                                           L                                                                               ",  # 691
    "                                                                                                           L                                                                               ",  # 692
    "                                                                                                           L                                                                               ",  # 693
    "                                                                                                           L                                                                               ",  # 694
    "                                                                                                           L                                                                               ",  # 695
    "                                                                                                           L                                                                               ",  # 696
    "                                                                                                           L                                                                               ",  # 697
    "                                                                                                           L                                                                               ",  # 698
    "                                                                                                           L                                                                               ",  # 699
    "                                                                                                           L                                                                               ",  # 700
    "                                                                                                           L                                                                               ",  # 701
    "                                                                                                           L                                                                               ",  # 702
    "                                                                                                           L                                                                               ",  # 703
    "                                                                                                           L                                                                               ",  # 704
    "                                                                                                           L                                                                               ",  # 705
    "                                                                                                           L                                                                               ",  # 706
    "                                                                                                           L                                                                               ",  # 707
    "                                                                                                           L                                                                               ",  # 708
    "                                                                                                           L                                                                               ",  # 709
    "                                                                                                           L                                                                               ",  # 710
    "                                                                                                           L                                                                               ",  # 711
    "                                                                                                           L                                                                               ",  # 712
    "                                                                                                           L                                                                               ",  # 713
    "                                                                                                           L                                                                               ",  # 714
    "                                                                                                           L                                                                               ",  # 715
    "                                                                                                           L                                                                               ",  # 716
    "                                                                                                           L                                                                               ",  # 717
    "                                                                                                           L                                                                               ",  # 718
    "                                                                                                           L                                                                               ",  # 719
    "                                                                                                           L                                                                               ",  # 720
    "                                                                                                           L                                                                               ",  # 721
    "                                                                                                           L                                                                               ",  # 722
    "                                                                                                           L                                                                               ",  # 723
    "                                                                                                           L                                                                               ",  # 724
    "                                                                                                           L                                                                               ",  # 725
    "                                                                                                           L                                                                               ",  # 726
    "                                                                                                           L                                                                               ",  # 727
    "                                                                                                           L                                                                               ",  # 728
    "                                                                                                           L                                                                               ",  # 729
    "                                                                                                           L                                                                               ",  # 730
    "                                                                                                           L                                                                               ",  # 731
    "                                                                                                           L                                                                               ",  # 732
    "                                                                                                           L                                                                               ",  # 733
    "                                                                                                           L                                                                               ",  # 734
    "                                                                                                           L                                                                               ",  # 735
    "                                                                                                           L                                                                               ",  # 736
    "                                                                                                           L                                                                               ",  # 737
    "                                                                                                           L                                                                               ",  # 738
    "                                                                                                           L                                                                               ",  # 739
    "                                                                                                           L                                                                               ",  # 740
    "                                                                                                           L                                                                               ",  # 741
    "                                                                                                           L                                                                               ",  # 742
    "                                                                                                           L                                                                               ",  # 743
    "                                                                                                           L                                                                               ",  # 744
    "                                                                                                           L                                                                               ",  # 745
    "                                                                                                           L                                                                               ",  # 746
    "                                                                                                           L                                                                               ",  # 747
    "                                                                                                           L                                                                               ",  # 748
    "                                                                                                           L                                                                               ",  # 749
    "                                                                                                           L                                                                               ",  # 750
    "                                                                                                           L                                                                               ",  # 751
    "                                                                                                           L                                                                               ",  # 752
    "                                                                                                           L                                                                               ",  # 753
    "                                                                                                           L                                                                               ",  # 754
    "                                                                                                           L                                                                               ",  # 755
    "                                                                                                           L                                                                               ",  # 756
    "                                                                                                           L                                                                               ",  # 757
    "                                                                                                           L                                                                               ",  # 758
    "                                                                                                           L                                                                               ",  # 759
    "                                                                                                           L                                                                               ",  # 760
    "                                                                                                           L                                                                               ",  # 761
    "                                                                                                           L                                                                               ",  # 762
    "                                                                                                           L                                                                               ",  # 763
    "                                                                                                           L                                                                               ",  # 764
    "                                                                                                           L                                                                               ",  # 765
    "                                                                                                           L                                                                               ",  # 766
    "                                                                                                           L                                                                               ",  # 767
    "                                                                                                           L                                                                               ",  # 768
    "                                                                                                           L                                                                               ",  # 769
    "                                                                                                           L                                                                               ",  # 770
    "                                                                                                           L                                                                               ",  # 771
    "                                                                                                           L                                                                               ",  # 772
    "                                                                                                           L                                                                               ",  # 773
    "                                                                                                           L                                                                               ",  # 774
    "                                                                                                           L                                                                               ",  # 775
    "                                                                                                           L                                                                               ",  # 776
    "                                                                                                           L                                                                               ",  # 777
    "                                                                                                           L                                                                               ",  # 778
    "                                                                                                           L                                                                               ",  # 779
    "                                                                                                           L                                                                               ",  # 780
    "                                                                                                           L                                                                               ",  # 781
    "                                                                                                           L                                                                               ",  # 782
    "                                                                                                           L                                                                               ",  # 783
    "                                                                                                           L                                                                               ",  # 784
    "                                                                                                           L                                                                               ",  # 785
    "                                                                                                           L                                                                               ",  # 786
    "                                                                                                           L                                                                               ",  # 787
    "                                                                                                           L                                                                               ",  # 788
    "                                                                                                           L                                                                               ",  # 789
    "                                                                                                           L                                                                               ",  # 790
    "                                                                                                           L                                                                               ",  # 791
    "                                                                                                           L                                                                               ",  # 792
    "                                                                                                           L                                                                               ",  # 793
    "                                                                                                           L                                                                               ",  # 794
    "                                                                                                           L                                                                               ",  # 795
    "                                                                                                           L                                                                               ",  # 796
    "                                                                                                           L                                                                               ",  # 797
    "                                                                                                           L                                                                               ",  # 798
    "                                                                                                           L                                                                               ",  # 799
    "                                                                                                           L                                                                               ",  # 800
    "                                                                                                           L                                                                               ",  # 801
    "                                                                                                           L                                                                               ",  # 802
    "                                                                                                           L                                                                               ",  # 803
    "                                                                                                           L                                                                               ",  # 804
    "                                                                                                           L                                                                               ",  # 805
    "                                                                                                           L                                                                               ",  # 806
    "                                                                                                           L                                                                               ",  # 807
    "                                                                                                           L                                                                               ",  # 808
    "                                                                                                           L                                                                               ",  # 809
    "                                                                                                           L                                                                               ",  # 810
    "                                                                                                           L                                                                               ",  # 811
    "                                                                                                           L                                                                               ",  # 812
    "                                                                                                           L                                                                               ",  # 813
    "                                                                                                           L                                                                               ",  # 814
    "                                                                                                           L                                                                               ",  # 815
    "                                                                                                           L                                                                               ",  # 816
    "                                                                                                           L                                                                               ",  # 817
    "                                                                                                           L                                                                               ",  # 818
    "                                                                                                           L                                                                               ",  # 819
    "                                                                                                           L                                                                               ",  # 820
    "                                                                                                           L                                                                               ",  # 821
    "                                                                                                           L                                                                               ",  # 822
    "                                                                                                           L                                                                               ",  # 823
    "                                                                                                           L                                                                               ",  # 824
    "                                                                                                           L                                                                               ",  # 825
    "                                                                                                           L                                                                               ",  # 826
    "                                                                                                           L                                                                               ",  # 827
    "                                                                                                           L                                                                               ",  # 828
    "                                                                                                           L                                                                               ",  # 829
    "                                                                                                           L                                                                               ",  # 830
    "                                                                                                           L                                                                               ",  # 831
    "                                                                                                           L                                                                               ",  # 832
    "                                                                                                           L                                                                               ",  # 833
    "                                                                                                           L                                                                               ",  # 834
    "                                                                                                           L                                                                               ",  # 835
    "                                                                                                           L                                                                               ",  # 836
    "                                                                                                           L                                                                               ",  # 837
    "                                                                                                           L                                                                               ",  # 838
    "                                                                                                           L                                                                               ",  # 839
    "                                                                                                           L                                                                               ",  # 840
    "                                                                                                           L                                                                               ",  # 841
    "                                                                                                           L                                                                               ",  # 842
    "                                                                                                           L                                                                               ",  # 843
    "                                                                                                           L                                                                               ",  # 844
    "                                                                                                           L                                                                               ",  # 845
    "                                                                                                           L                                                                               ",  # 846
    "                                                                                                           L                                                                               ",  # 847
    "                                                                                                           L                                                                               ",  # 848
    "                                                                                                           L                                                                               ",  # 849
    "                                                                                                           L                                                                               ",  # 850
    "                                                                                                           L                                                                               ",  # 851
    "                                                                                                           L                                                                               ",  # 852
    "                                                                                                           L                                                                               ",  # 853
    "                                                                                                           L                                                                               ",  # 854
    "                                                                                                           L                                                                               ",  # 855
    "                                                                                                           L                                                                               ",  # 856
    "                                                                                                           L                                                                               ",  # 857
    "                                                                                                           L                                                                               ",  # 858
    "                                                                                                           L                                                                               ",  # 859
    "                                                                                                           L                                                                               ",  # 860
    "                                                                                                           L                                                                               ",  # 861
    "                                                                                                           L                                                                               ",  # 862
    "                                                                                                           L                                                                               ",  # 863
    "                                                                                                           L                                                                               ",  # 864
    "                                                                                                           L                                                                               ",  # 865
    "                                                                                                           L                                                                               ",  # 866
    "                                                                                                           L                                                                               ",  # 867
    "                                                                                                           L                                                                               ",  # 868
    "                                                                                                           L                                                                               ",  # 869
    "                                                                                                           L                                                                               ",  # 870
    "                                                                                                           L                                                                               ",  # 871
    "                                                                                                           L                                                                               ",  # 872
    "                                                                                                           L                                                                               ",  # 873
    "                                                                                                           L                                                                               ",  # 874
    "                                                                                                           L                                                                               ",  # 875
    "                                                                                                           L                                                                               ",  # 876
    "                                                                                                           L                                                                               ",  # 877
    "                                                                                                           L                                                                               ",  # 878
    "                                                                                                           L                                                                               ",  # 879
    "                                                                                                           L                                                                               ",  # 880
    "                                                                                                           L                                                                               ",  # 881
    "                                                                                                           L                                                                               ",  # 882
    "                                                                                                           L                                                                               ",  # 883
    "                                                                                                           L                                                                               ",  # 884
    "                                                                                                           L                                                                               ",  # 885
    "                                                                                                           L                                                                               ",  # 886
    "                                                                                                           L                                                                               ",  # 887
    "                                                                                                           L                                                                               ",  # 888
    "                                                                                                           L                                                                               ",  # 889
    "                                                                                                           L                                                                               ",  # 890
    "                                                                                                           L                                                                               ",  # 891
    "                                                                                                           L                                                                               ",  # 892
    "                                                                                                           L                                                                               ",  # 893
    "                                                                                                           L                                                                               ",  # 894
    "                                                                                                           L                                                                               ",  # 895
    "                                                                                                           L                                                                               ",  # 896
    "                                                                                                           L                                                                               ",  # 897
    "                                                                                                           L                                                                               ",  # 898
    "                                                                                                           L                                                                               ",  # 899
    "                                                                                                           L                                                                               ",  # 900
    "                                                                                                           L                                                                               ",  # 901
    "                                                                                                           L                                                                               ",  # 902
    "                                                                                                           L                                                                               ",  # 903
    "                                                                                                           L                                                                               ",  # 904
    "                                                                                                           L                                                                               ",  # 905
    "                                                                                                           L                                                                               ",  # 906
    "                                                                                                           L                                                                               ",  # 907
    "                                                                                                           L                                                                               ",  # 908
    "                                                                                                           L                                                                               ",  # 909
    "                                                                                                           L                                                                               ",  # 910
    "                                                                                                           L                                                                               ",  # 911
    "                                                                                                           L                                                                               ",  # 912
    "                                                                                                           L                                                                               ",  # 913
    "                                                                                                           L                                                                               ",  # 914
    "                                                                                                           L                                                                               ",  # 915
    "                                                                                                           L                                                                               ",  # 916
    "                                                                                                           L                                                                               ",  # 917
    "                                                                                                           L                                                                               ",  # 918
    "                                                                                                           L                                                                               ",  # 919
    "                                                                                                           L                                                                               ",  # 920
    "                                                                                                           L                                                                               ",  # 921
    "                                                                                                           L                                                                               ",  # 922
    "                                                                                                           L                                                                               ",  # 923
    "                                                                                                           L                                                                               ",  # 924
    "                                                                                                           L                                                                               ",  # 925
    "                                                                                                           L                                                                               ",  # 926
    "                                                                                                           L                                                                               ",  # 927
    "                                                                                                           L                                                                               ",  # 928
    "                                                                                                           L                                                                               ",  # 929
    "                                                                                                           L                                                                               ",  # 930
    "                                                                                                           L                                                                               ",  # 931
    "                                                                                                           L                                                                               ",  # 932
    "                                                                                                           L                                                                               ",  # 933
    "                                                                                                           L                                                                               ",  # 934
    "                                                                                                           L                                                                               ",  # 935
    "                                                                                                           L                                                                               ",  # 936
    "                                                                                                           L                                                                               ",  # 937
    "                                                                                                           L                                                                               ",  # 938
    "                                                                                                           L                                                                               ",  # 939
    "                                                                                                           L                                                                               ",  # 940
    "                                                                                                           L                                                                               ",  # 941
    "                                                                                                           L                                                                               ",  # 942
    "                                                                                                           L                                                                               ",  # 943
    "                                                                                                           L                                                                               ",  # 944
    "                                                                                                           L                                                                               ",  # 945
    "                                                                                                           L                                                                               ",  # 946
    "                                                                                                           L                                                                               ",  # 947
    "                                                                                                           L                                                                               ",  # 948
    "                                                                                                           L                                                                               ",  # 949
    "                                                                                                           L                                                                               ",  # 950
    "                                                                                                           L                                                                               ",  # 951
    "                                                                                                           L                                                                               ",  # 952
    "                                                                                                           L                                                                               ",  # 953
    "                                                                                                           L                                                                               ",  # 954
    "                                                                                                           L                                                                               ",  # 955
    "                                                                                                           L                                                                               ",  # 956
    "                                                                                                           L                                                                               ",  # 957
    "                                                                                                           L                                                                               ",  # 958
    "                                                                                                           L                                                                               ",  # 959
    "                                                                                                           L                                                                               ",  # 960
    "                                                                                                           L                                                                               ",  # 961
    "                                                                                                           L                                                                               ",  # 962
    "                                                                                                           L                                                                               ",  # 963
    "                                                                                                           L                                                                               ",  # 964
    "                                                                                                           L                                                                               ",  # 965
    "                                                                                                           L                                                                               ",  # 966
    "                                                                                                           L                                                                               ",  # 967
    "                                                                                                           L                                                                               ",  # 968
    "                                                                                                           L                                                                               ",  # 969
    "                                                                                                           L                                                                               ",  # 970
    "                                                                                                           L                                                                               ",  # 971
    "                                                                                                           L                                                                               ",  # 972
    "                                                                                                           L                                                                               ",  # 973
    "                                                                                                           L                                                                               ",  # 974
    "                                                                                                           L                                                                               ",  # 975
    "                                                                                                           L                                                                               ",  # 976
    "                                                                                                           L                                                                               ",  # 977
    "                                                                                                           L                                                                               ",  # 978
    "                                                                                                           L                                                                               ",  # 979
    "                                                                                                           L                                                                               ",  # 980
    "                                                                                                           L                                                                               ",  # 981
    "                                                                                                           L                                                                               ",  # 982
    "                                                                                                           L                                                                               ",  # 983
    "                                                                                                           L                                                                               ",  # 984
    "                                                                                                           L                                                                               ",  # 985
    "                                                                                                           L                                                                               ",  # 986
    "                                                                                                           L                                                                               ",  # 987
    "                                                                                                           L                                                                               ",  # 988
    "                                                                                                           L                                                                               ",  # 989
    "                                                                                                           L                                                                               ",  # 990
    "                                                                                                           L                                                                               ",  # 991
    "                                                                                                           L                                                                               ",  # 992
    "                                                                                                           L                                                                               ",  # 993
    "                                                                                                           L                                                                               ",  # 994
    "                                                                                                           L                                                                               ",  # 995
    "                                                                                                           L                                                                               ",  # 996
    "                                                                                                           L                                                                               ",  # 997
    "                                                                                                           L                                                                               ",  # 998
    "                                                                                                           L                                                                               ",  # 999
    "                                                                                                           L                                                                               ",  # 1000
    "                                                                                                           L                                                                               ",  # 1001
    "                                                                                                           L                                                                               ",  # 1002
    "                                                                                                           L                                                                               ",  # 1003
    "                                                                                                           L                                                                               ",  # 1004
    "                                                                                                           L                                                                               ",  # 1005
    "                                                                                                           L                                                                               ",  # 1006
    "                                                                                                           L                                                                               ",  # 1007
    "                                                                                                           L                                                                               ",  # 1008
    "                                                                                                           L                                                                               ",  # 1009
    "                                                                                                           L                                                                               ",  # 1010
    "                                                                                                           L                                                                               ",  # 1011
    "                                                                                                           L                                                                               ",  # 1012
    "                                                                                                           L                                                                               ",  # 1013
    "                                                                                                           L                                                                               ",  # 1014
    "                                                                                                           L                                                                               ",  # 1015
    "                                                                                                           L                                                                               ",  # 1016
    "                                                                                                           L                                                                               ",  # 1017
    "                                                                                                           L                                                                               ",  # 1018
    "                                                                                                           L                                                                               ",  # 1019
    "                                                                                                           L                                                                               ",  # 1020
    "                                                                                                           L                                                                               ",  # 1021
    "                                                                                                           L                                                                               ",  # 1022
    "                                                                                                           L                                                                               ",  # 1023
    "                                                                                                           L                                                                               ",  # 1024
    "                                                                                                           L                                                                               ",  # 1025
    "                                                                                                           L                                                                               ",  # 1026
    "                                                                                                           L                                                                               ",  # 1027
    "                                                                                                           L                                                                               ",  # 1028
    "                                                                                                           L                                                                               ",  # 1029
    "                                                                                                           L                                                                               ",  # 1030
    "                                                                                                           L                                                                               ",  # 1031
    "                                                                                                           L                                                                               ",  # 1032
    "                                                                                                           L                                                                               ",  # 1033
    "                                                                                                           L                                                                               ",  # 1034
    "                                                                                                           L                                                                               ",  # 1035
    "                                                                                                           L                                                                               ",  # 1036
    "                                                                                                           L                                                                               ",  # 1037
    "                                                                                                           L                                                                               ",  # 1038
    "                                                                                                           L                                                                               ",  # 1039
    "                                                                                                           L                                                                               ",  # 1040
    "                                                                                                           L                                                                               ",  # 1041
    "                                                                                                           L                                                                               ",  # 1042
    "                                                                                                           L                                                                               ",  # 1043
    "                                                                                                           L                                                                               ",  # 1044
    "                                                                                                           L                                                                               ",  # 1045
    "                                                                                                           L                                                                               ",  # 1046
    "                                                                                                           L                                                                               ",  # 1047
    "                                                                                                           L                                                                               ",  # 1048
    "                                                                                                           L                                                                               ",  # 1049
    "                                                                                                           L                                                                               ",  # 1050
    "                                                                                                           L                                                                               ",  # 1051
    "                                                                                                           L                                                                               ",  # 1052
    "                                                                                                           L                                                                               ",  # 1053
    "                                                                                                           L                                                                               ",  # 1054
    "                                                                                                           L                                                                               ",  # 1055
    "                                                                                                           L                                                                               ",  # 1056
    "                                                                                                           L                                                                               ",  # 1057
    "                                                                                                           L                                                                               ",  # 1058
    "                                                                                                           L                                                                               ",  # 1059
    "                                                                                                           L                                                                               ",  # 1060
    "                                                                                                           L                                                                               ",  # 1061
    "                                                                                                           L                                                                               ",  # 1062
    "                                                                                                           L                                                                               ",  # 1063
    "                                                                                                           L                                                                               ",  # 1064
    "                                                                                                           L                                                                               ",  # 1065
    "                                                                                                           L                                                                               ",  # 1066
    "                                                                                                           L                                                                               ",  # 1067
    "                                                                                                           L                                                                               ",  # 1068
    "                                                                                                           L                                                                               ",  # 1069
    "                                                                                                           L                                                                               ",  # 1070
    "                                                                                                           L                                                                               ",  # 1071
    "                                                                                                           L                                                                               ",  # 1072
    "                                                                                                           L                                                                               ",  # 1073
    "                                                                                                           L                                                                               ",  # 1074
    "                                                                                                           L                                                                               ",  # 1075
    "                                                                                                           L                                                                               ",  # 1076
    "                                                                                                           L                                                                               ",  # 1077
    "                                                                                                           L                                                                               ",  # 1078
    "                                                                                                           L                                                                               ",  # 1079
    "                                                                                                           L                                                                               ",  # 1080
    "                                                                                                           L                                                                               ",  # 1081
    "                                                                                                           L                                                                               ",  # 1082
    "                                                                                                           L                                                                               ",  # 1083
    "                                                                                                           L                                                                               ",  # 1084
    "                                                                                                           L                                                                               ",  # 1085
    "                                                                                                           L                                                                               ",  # 1086
    "                                                                                                           L                                                                               ",  # 1087
    "                                                                                                           L                                                                               ",  # 1088
    "                                                                                                           L                                                                               ",  # 1089
    "                                                                                                           L                                                                               ",  # 1090
    "                                                                                                           L                                                                               ",  # 1091
    "                                                                                                           L                                                                               ",  # 1092
    "                                                                                                           L                                                                               ",  # 1093
    "                                                                                                           L                                                                               ",  # 1094
    "                                                                                                           L                                                                               ",  # 1095
    "                                                                                                           L                                                                               ",  # 1096
    "                                                                                                           L                                                                               ",  # 1097
    "                                                                                                           L                                                                               ",  # 1098
    "                                                                                                           L                                                                               ",  # 1099
    "                                                                                                           L                                                                               ",  # 1100
    "                                                                                                           L                                                                               ",  # 1101
    "                                                                                                           L                                                                               ",  # 1102
    "                                                                                                           L                                                                               ",  # 1103
    "                                                                                                           L                                                                               ",  # 1104
    "                                                                                                           L                                                                               ",  # 1105
    "                                                                                                           L                                                                               ",  # 1106
    "                                                                                                           L                                                                               ",  # 1107
    "                                                                                                           L                                                                               ",  # 1108
    "                                                                                                           L                                                                               ",  # 1109
    "                                                                                                           L                                                                               ",  # 1110
    "                                                                                                           L                                                                               ",  # 1111
    "                                                                                                           L                                                                               ",  # 1112
    "                                                                                                           L                                                                               ",  # 1113
    "                                                                                                           L                                                                               ",  # 1114
    "                                                                                                           L                                                                               ",  # 1115
    "                                                                                                           L                                                                               ",  # 1116
    "                                                                                                           L                                                                               ",  # 1117
    "                                                                                                           L                                                                               ",  # 1118
    "                                                                                                           L                                                                               ",  # 1119
    "                                                                                                           L                                                                               ",  # 1120
    "                                                                                                           L                                                                               ",  # 1121
    "                                                                                                           L                                                                               ",  # 1122
    "                                                                                                           L                                                                               ",  # 1123
    "                                                                                                           L                                                                               ",  # 1124
    "                                                                                                           L                                                                               ",  # 1125
    "                                                                                                           L                                                                               ",  # 1126
    "                                                                                                           L                                                                               ",  # 1127
    "                                                                                                           L                                                                               ",  # 1128
    "                                                                                                           L                                                                               ",  # 1129
    "                                                                                                           L                                                                               ",  # 1130
    "                                                                                                           L                                                                               ",  # 1131
    "                                                                                                           L                                                                               ",  # 1132
    "                                                                                                           L                                                                               ",  # 1133
    "                                                                                                           L                                                                               ",  # 1134
    "                                                                                                           L                                                                               ",  # 1135
    "                                                                                                           L                                                                               ",  # 1136
    "                                                                                                           L                                                                               ",  # 1137
    "                                                                                                           L                                                                               ",  # 1138
    "                                                                                                           L                                                                               ",  # 1139
    "                                                                                                           L                                                                               ",  # 1140
    "                                                                                                           L                                                                               ",  # 1141
    "                                                                                                           L                                                                               ",  # 1142
    "                                                                                                           L                                                                               ",  # 1143
    "                                                                                                           L                                                                               ",  # 1144
    "                                                                                                           L                                                                               ",  # 1145
    "                                                                                                           L                                                                               ",  # 1146
    "                                                                                                           L                                                                               ",  # 1147
    "                                                                                                           L                                                                               ",  # 1148
    "                                                                                                           L                                                                               ",  # 1149
    "                                                                                                           L                                                                               ",  # 1150
    "                                                                                                           L                                                                               ",  # 1151
    "                                                                                                           L                                                                               ",  # 1152
    "                                                                                                           L                                                                               ",  # 1153
    "                                                                                                           L                                                                               ",  # 1154
    "                                                                                                           L                                                                               ",  # 1155
    "                                                                                                           L                                                                               ",  # 1156
    "                                                                                                           L                                                                               ",  # 1157
    "                                                                                                           L                                                                               ",  # 1158
    "                                                                                                           L                                                                               ",  # 1159
    "                                                                                                           L                                                                               ",  # 1160
    "                                                                                                           L                                                                               ",  # 1161
    "                                                                                                           L                                                                               ",  # 1162
    "                                                                                                           L                                                                               ",  # 1163
    "                                                                                                           L                                                                               ",  # 1164
    "                                                                                                           L                                                                               ",  # 1165
    "                                                                                                           L                                                                               ",  # 1166
    "                                                                                                           L                                                                               ",  # 1167
    "                                                                                                           L                                                                               ",  # 1168
    "                                                                                                           L                                                                               ",  # 1169
    "                                                                                                           L                                                                               ",  # 1170
    "                                                                                                           L                                                                               ",  # 1171
    "                                                                                                           L                                                                               ",  # 1172
    "                                                                                                           L                                                                               ",  # 1173
    "                                                                                                           L                                                                               ",  # 1174
    "                                                                                                           L                                                                               ",  # 1175
    "                                                                                                           L                                                                               ",  # 1176
    "                                                                                                           L                                                                               ",  # 1177
    "                                                                                                           L                                                                               ",  # 1178
    "                                                                                                           L                                                                               ",  # 1179
    "                                                                                                           L                                                                               ",  # 1180
    "                                                                                                           L                                                                               ",  # 1181
    "                                                                                                           L                                                                               ",  # 1182
    "                                                                                                           L                                                                               ",  # 1183
    "                                                                                                           L                                                                               ",  # 1184
    "                                                                                                           L                                                                               ",  # 1185
    "                                                                                                           L                                                                               ",  # 1186
    "                                                                                                           L                                                                               ",  # 1187
    "                                                                                                           L                                                                               ",  # 1188
    "                                                                                                           L                                                                               ",  # 1189
    "                                                                                                           L                                                                               ",  # 1190
    "                                                                                                           L                                                                               ",  # 1191
    "                                                                                                           L                                                                               ",  # 1192
    "                                                                                                           L                                                                               ",  # 1193
    "                                                                                                           L                                                                               ",  # 1194
    "                                                                                                           L                                                                               ",  # 1195
    "                                                                                                           L                                                                               ",  # 1196
    "                                                                                                           L                                                                               ",  # 1197
    "                                                                                                           L                                                                               ",  # 1198
    "                                                                                                           L                                                                               ",  # 1199
    "                                                                                                           L                                                                               ",  # 1200
    "                                                                                                           L                                                                               ",  # 1201
    "                                                                                                           L                                                                               ",  # 1202
    "                                                                                                           L                                                                               ",  # 1203
    "                                                                                                           L                                                                               ",  # 1204
    "                                                                                                           L                                                                               ",  # 1205
    "                                                                                                           L                                                                               ",  # 1206
    "                                                                                                           L                                                                               ",  # 1207
    "                                                                                                           L                                                                               ",  # 1208
    "                                                                                                           L                                                                               ",  # 1209
    "                                                                                                           L                                                                               ",  # 1210
    "                                                                                                           L                                                                               ",  # 1211
    "                                                                                                           L                                                                               ",  # 1212
    "                                                                                                           L                                                                               ",  # 1213
    "                                                                                                           L                                                                               ",  # 1214
    "                                                                                                           L                                                                               ",  # 1215
    "                                                                                                           L                                                                               ",  # 1216
    "                                                                                                           L                                                                               ",  # 1217
    "                                                                                                           L                                                                               ",  # 1218
    "                                                                                                           L                                                                               ",  # 1219
    "                                                                                                           L                                                                               ",  # 1220
    "                                                                                                           L                                                                               ",  # 1221
    "                                                                                                           L                                                                               ",  # 1222
    "                                                                                                           L                                                                               ",  # 1223
    "                                                                                                           L                                                                               ",  # 1224
    "                                                                                                           L                                                                               ",  # 1225
    "                                                                                                           L                                                                               ",  # 1226
    "                                                                                                           L                                                                               ",  # 1227
    "                                                                                                           L                                                                               ",  # 1228
    "                                                                                                           L                                                                               ",  # 1229
    "                                                                                                           L                                                                               ",  # 1230
    "                                                                                                           L                                                                               ",  # 1231
    "                                                                                                           L                                                                               ",  # 1232
    "                                                                                                           L                                                                               ",  # 1233
    "                                                                                                           L                                                                               ",  # 1234
    "                                                                                                           L                                                                               ",  # 1235
    "                                                                                                           L                                                                               ",  # 1236
    "                                                                                                           L                                                                               ",  # 1237
    "                                                                                                           L                                                                               ",  # 1238
    "                                                                                                           L                                                                               ",  # 1239
    "                                                                                                           L                                                                               ",  # 1240
    "                                                                                                           L                                                                               ",  # 1241
    "                                                                                                           L                                                                               ",  # 1242
    "                                                                                                           L                                                                               ",  # 1243
    "                                                                                                           L                                                                               ",  # 1244
    "                                                                                                           L                                                                               ",  # 1245
    "                                                                                                           L                                                                               ",  # 1246
    "                                                                                                           L                                                                               ",  # 1247
    "                                                                                                           L                                                                               ",  # 1248
    "                                                                                                           L                                                                               ",  # 1249
    "                                                                                                           L                                                                               ",  # 1250
    "                                                                                                           L                                                                               ",  # 1251
    "                                                                                                           L                                                                               ",  # 1252
    "                                                                                                           L                                                                               ",  # 1253
    "                                                                                                           L                                                                               ",  # 1254
    "                                                                                                           L                                                                               ",  # 1255
    "                                                                                                           L                                                                               ",  # 1256
    "                                                                                                           L                                                                               ",  # 1257
    "                                                                                                           L                                                                               ",  # 1258
    "                                                                                                           L                                                                               ",  # 1259
    "                                                                                                           L                                                                               ",  # 1260
    "                                                                                                           L                                                                               ",  # 1261
    "                                                                                                           L                                                                               ",  # 1262
    "                                                                                                           L                                                                               ",  # 1263
    "                                                                                                           L                                                                               ",  # 1264
    "                                                                                                           L                                                                               ",  # 1265
    "                                                                                                           L                                                                               ",  # 1266
    "                                                                                                           L                                                                               ",  # 1267
    "                                                                                                           L                                                                               ",  # 1268
    "                                                                                                           L                                                                               ",  # 1269
    "                                                                                                           L                                                                               ",  # 1270
    "                                                                                                           L                                                                               ",  # 1271
    "                                                                                                           L                                                                               ",  # 1272
    "                                                                                                           L                                                                               ",  # 1273
    "                                                                                                           L                                                                               ",  # 1274
    "                                                                                                           L                                                                               ",  # 1275
    "                                                                                                           L                                                                               ",  # 1276
    "                                                                                                           L                                                                               ",  # 1277
    "                                                                                                           L                                                                               ",  # 1278
    "                                                                                                           L                                                                               ",  # 1279
    "                                                                                                           L                                                                               ",  # 1280
    "                                                                                                           L                                                                               ",  # 1281
    "                                                                                                           L                                                                               ",  # 1282
    "                                                                                                           L                                                                               ",  # 1283
    "                                                                                                           L                                                                               ",  # 1284
    "                                                                                                           L                                                                               ",  # 1285
    "                                                                                                           L                                                                               ",  # 1286
    "                                                                                                           L                                                                               ",  # 1287
    "                                                                                                           L                                                                               ",  # 1288
    "                                                                                                           L                                                                               ",  # 1289
    "                                                                                                           L                                                                               ",  # 1290
    "                                                                                                           L                                                                               ",  # 1291
    "                                                                                                           L                                                                               ",  # 1292
    "                                                                                                           L                                                                               ",  # 1293
    "                                                                                                           L                                                                               ",  # 1294
    "                                                                                                           L                                                                               ",  # 1295
    "                                                                                                           L                                                                               ",  # 1296
    "                                                                                                           L                                                                               ",  # 1297
    "                                                                                                           L                                                                               ",  # 1298
    "                                                                                                           L                                                                               ",  # 1299
    "                                                                                                           L                                                                               ",  # 1300
    "                                                                                                           L                                                                               ",  # 1301
    "                                                                                                           L                                                                               ",  # 1302
    "                                                                                                           L                                                                               ",  # 1303
    "                                                                                                           L                                                                               ",  # 1304
    "                                                                                                           L                                                                               ",  # 1305
    "                                                                                                           L                                                                               ",  # 1306
    "                                                                                                           L                                                                               ",  # 1307
    "                                                                                                           L                                                                               ",  # 1308
    "                                                                                                           L                                                                               ",  # 1309
    "                                                                                                           L                                                                               ",  # 1310
    "                                                                                                           L                                                                               ",  # 1311
    "                                                                                                           L                                                                               ",  # 1312
    "                                                                                                           L                                                                               ",  # 1313
    "                                                                                                           L                                                                               ",  # 1314
    "                                                                                                           L                                                                               ",  # 1315
    "                                                                                                           L                                                                               ",  # 1316
    "                                                                                                           L                                                                               ",  # 1317
    "                                                                                                           L                                                                               ",  # 1318
    "                                                                                                           L                                                                               ",  # 1319
    "                                                                                                           L                                                                               ",  # 1320
    "                                                                                                           L                                                                               ",  # 1321
    "                                                                                                           L                                                                               ",  # 1322
    "                                                                                                           L                                                                               ",  # 1323
    "                                                                                                           L                                                                               ",  # 1324
    "                                                                                                           L                                                                               ",  # 1325
    "                                                                                                           L                                                                               ",  # 1326
    "                                                                                                           L                                                                               ",  # 1327
    "                                                                                                           L                                                                               ",  # 1328
    "                                                                                                           L                                                                               ",  # 1329
    "                                                                                                           L                                                                               ",  # 1330
    "                                                                                                           L                                                                               ",  # 1331
    "                                                                                                           L                                                                               ",  # 1332
    "                                                                                                           L                                                                               ",  # 1333
    "                                                                                                           L                                                                               ",  # 1334
    "                                                                                                           L                                                                               ",  # 1335
    "                                                                                                           L                                                                               ",  # 1336
    "                                                                                                           L                                                                               ",  # 1337
    "                                                                                                           L                                                                               ",  # 1338
    "                                                                                                           L                                                                               ",  # 1339
    "                                                                                                           L                                                                               ",  # 1340
    "                                                                                                           L                                                                               ",  # 1341
    "                                                                                                           L                                                                               ",  # 1342
    "                                                                                                           L                                                                               ",  # 1343
    "                                                                                                           L                                                                               ",  # 1344
    "                                                                                                           L                                                                               ",  # 1345
    "                                                                                                           L                                                                               ",  # 1346
    "                                                                                                           L                                                                               ",  # 1347
    "                                                                                                           L                                                                               ",  # 1348
    "                                                                                                           L                                                                               ",  # 1349
    "                                                                                                           L                                                                               ",  # 1350
    "                                                                                                           L                                                                               ",  # 1351
    "                                                                                                           L                                                                               ",  # 1352
    "                                                                                                           L                                                                               ",  # 1353
    "                                                                                                           L                                                                               ",  # 1354
    "                                                                                                           L                                                                               ",  # 1355
    "                                                                                                           L                                                                               ",  # 1356
    "                                                                                                           L                                                                               ",  # 1357
    "                                                                                                           L                                                                               ",  # 1358
    "                                                                                                           L                                                                               ",  # 1359
    "                                                                                                           L                                                                               ",  # 1360
    "                                                                                                           L                                                                               ",  # 1361
    "                                                                                                           L                                                                               ",  # 1362
    "                                                                                                           L                                                                               ",  # 1363
    "                                                                                                           L                                                                               ",  # 1364
    "                                                                                                           L                                                                               ",  # 1365
    "                                                                                                           L                                                                               ",  # 1366
    "                                                                                                           L                                                                               ",  # 1367
    "                                                                                                           L                                                                               ",  # 1368
    "                                                                                                           L                                                                               ",  # 1369
    "                                                                                                           L                                                                               ",  # 1370
    "                                                                                                           L                                                                               ",  # 1371
    "                                                                                                           L                                                                               ",  # 1372
    "                                                                                                           L                                                                               ",  # 1373
    "                                                                                                           L                                                                               ",  # 1374
    "                                                                                                           L                                                                               ",  # 1375
    "                                                                                                           L                                                                               ",  # 1376
    "                                                                                                           L                                                                               ",  # 1377
    "                                                                                                           L                                                                               ",  # 1378
    "                                                                                                           L                                                                               ",  # 1379
    "                                                                                                           L                                                                               ",  # 1380
    "                                                                                                           L                                                                               ",  # 1381
    "                                                                                                           L                                                                               ",  # 1382
    "                                                                                                           L                                                                               ",  # 1383
    "                                                                                                           L                                                                               ",  # 1384
    "                                                                                                           L                                                                               ",  # 1385
    "                                                                                                           L                                                                               ",  # 1386
    "                                                                                                           L                                                                               ",  # 1387
    "                                                                                                           L                                                                               ",  # 1388
    "                                                                                                           L                                                                               ",  # 1389
    "                                                                                                           L                                                                               ",  # 1390
    "                                                                                                           L                                                                               ",  # 1391
    "                                                                                                           L                                                                               ",  # 1392
    "                                                                                                           L                                                                               ",  # 1393
    "                                                                                                           L                                                                               ",  # 1394
    "                                                                                                           L                                                                               ",  # 1395
    "                                                                                                           L                                                                               ",  # 1396
    "                                                                                                           L                                                                               ",  # 1397
    "                                                                                                           L                                                                               ",  # 1398
    "                                                                                                           L                                                                               ",  # 1399
    "                                                                                                           L                                                                               ",  # 1400
    "                                                                                                           L                                                                               ",  # 1401
    "                                                                                                           L                                                                               ",  # 1402
    "                                                                                                           L                                                                               ",  # 1403
    "                                                                                                           L                                                                               ",  # 1404
    "                                                                                                           L                                                                               ",  # 1405
    "                                                                                                           L                                                                               ",  # 1406
    "                                                                                                           L                                                                               ",  # 1407
    "                                                                                                           L                                                                               ",  # 1408
    "                                                                                                           L                                                                               ",  # 1409
    "                                                                                                           L                                                                               ",  # 1410
    "                                                                                                           L                                                                               ",  # 1411
    "                                                                                                           L                                                                               ",  # 1412
    "                                                                                                           L                                                                               ",  # 1413
    "                                                                                                           L                                                                               ",  # 1414
    "                                                                                                           L                                                                               ",  # 1415
    "                                                                                                           L                                                                               ",  # 1416
    "                                                                                                           L                                                                               ",  # 1417
    "                                                                                                           L                                                                               ",  # 1418
    "                                                                                                           L                                                                               ",  # 1419
    "                                                                                                           L                                                                               ",  # 1420
    "                                                                                                           L                                                                               ",  # 1421
    "                                                                                                           L                                                                               ",  # 1422
    "                                                                                                           L                                                                               ",  # 1423
    "                                                                                                           L                                                                               ",  # 1424
    "                                                                                                           L                                                                               ",  # 1425
    "                                                                                                           L                                                                               ",  # 1426
    "                                                                                                           L                                                                               ",  # 1427
    "                                                                                                           L                                                                               ",  # 1428
    "                                                                                                           L                                                                               ",  # 1429
    "                                                                                                           L                                                                               ",  # 1430
    "                                                                                                           L                                                                               ",  # 1431
    "                                                                                                           L                                                                               ",  # 1432
    "                                                                                                           L                                                                               ",  # 1433
    "                                                                                                           L                                                                               ",  # 1434
    "                                                                                                           L                                                                               ",  # 1435
    "                                                                                                           L                                                                               ",  # 1436
    "                                                                                                           L                                                                               ",  # 1437
    "                                                                                                           L                                                                               ",  # 1438
    "                                                                                                           L                                                                               ",  # 1439
    "                                                                                                           L                                                                               ",  # 1440
    "                                                                                                           L                                                                               ",  # 1441
    "                                                                                                           L                                                                               ",  # 1442
    "                                                                                                           L                                                                               ",  # 1443
    "                                                                                                           L                                                                               ",  # 1444
    "                                                                                                           L                                                                               ",  # 1445
    "                                                                                                           L                                                                               ",  # 1446
    "                                                                                                           L                                                                               ",  # 1447
    "                                                                                                           L                                                                               ",  # 1448
    "                                                                                                           L                                                                               ",  # 1449
    "                                                                                                           L                                                                               ",  # 1450
    "                                                                                                           L                                                                               ",  # 1451
    "                                                                                                           L                                                                               ",  # 1452
    "                                                                                                           L                                                                               ",  # 1453
    "                                                                                                           L                                                                               ",  # 1454
    "                                                                                                           L                                                                               ",  # 1455
    "                                                                                                           L                                                                               ",  # 1456
    "                                                                                                           L                                                                               ",  # 1457
    "                                                                                                           L                                                                               ",  # 1458
    "                                                                                                           L                                                                               ",  # 1459
    "                                                                                                           L                                                                               ",  # 1460
    "                                                                                                           L                                                                               ",  # 1461
    "                                                                                                           L                                                                               ",  # 1462
    "                                                                                                           L                                                                               ",  # 1463
    "                                                                                                           L                                                                               ",  # 1464
    "                                                                                                           L                                                                               ",  # 1465
    "                                                                                                           L                                                                               ",  # 1466
    "                                                                                                           L                                                                               ",  # 1467
    "                                                                                                           L                                                                               ",  # 1468
    "                                                                                                           L                                                                               ",  # 1469
    "                                                                                                           L                                                                               ",  # 1470
    "                                                                                                           L                                                                               ",  # 1471
    "                                                                                                           L                                                                               ",  # 1472
    "                                                                                                           L                                                                               ",  # 1473
    "                                                                                                           L                                                                               ",  # 1474
    "                                                                                                           L                                                                               ",  # 1475
    "                                                                                                           L                                                                               ",  # 1476
    "                                                                                                           L                                                                               ",  # 1477
    "                                                                                                           L                                                                               ",  # 1478
    "                                                                                                           L                                                                               ",  # 1479
    "                                                                                                           L                                                                               ",  # 1480
    "                                                                                                           L                                                                               ",  # 1481
    "                                                                                                           L                                                                               ",  # 1482
    "                                                                                                           L                                                                               ",  # 1483
    "                                                                                                           L                                                                               ",  # 1484
    "                                                                                                           L                                                                               ",  # 1485
    "                                                                                                           L                                                                               ",  # 1486
    "                                                                                                           L                                                                               ",  # 1487
    "                                                                                                           L                                                                               ",  # 1488
    "                                                                                                           L                                                                               ",  # 1489
    "                                                                                                           L                                                                               ",  # 1490
    "                                                                                                           L                                                                               ",  # 1491
    "                                                                                                           L                                                                               ",  # 1492
    "                                                                                                           L                                                                               ",  # 1493
    "                                                                                                           L                                                                               ",  # 1494
    "                                                                                                           L                                                                               ",  # 1495
    "                                                                                                           L                                                                               ",  # 1496
    "                                                                                                           L                                                                               ",  # 1497
    "                                                                                                           L                                                                               ",  # 1498
    "                                                                                                           L                                                                               ",  # 1499
    "                                                                                                           L                                                                               ",  # 1500
    "                                                                                                           L                                                                               ",  # 1501
    "                                                                                                           L                                                                               ",  # 1502
    "                                                                                                           L                                                                               ",  # 1503
    "                                                                                                           L                                                                               ",  # 1504
    "                                                                                                           L                                                                               ",  # 1505
    "                                                                                                           L                                                                               ",  # 1506
    "                                                                                                           L                                                                               ",  # 1507
    "                                                                                                           L                                                                               ",  # 1508
    "                                                                                                           L                                                                               ",  # 1509
    "                                                                                                           L                                                                               ",  # 1510
    "                                                                                                           L                                                                               ",  # 1511
    "                                                                                                           L                                                                               ",  # 1512
    "                                                                                                           L                                                                               ",  # 1513
    "                                                                                                           L                                                                               ",  # 1514
    "                                                                                                           L                                                                               ",  # 1515
    "                                                                                                           L                                                                               ",  # 1516
    "                                                                                                           L                                                                               ",  # 1517
    "                                                                                                           L                                                                               ",  # 1518
    "                                                                                                           L                                                                               ",  # 1519
    "                                                                                                           L                                                                               ",  # 1520
    "                                                                                                           L                                                                               ",  # 1521
    "                                                                                                           L                                                                               ",  # 1522
    "                                                                                                           L                                                                               ",  # 1523
    "                                                                                                           L                                                                               ",  # 1524
    "                                                                                                           L                                                                               ",  # 1525
    "                                                                                                           L                                                                               ",  # 1526
    "                                                                                                           L                                                                               ",  # 1527
    "                                                                                                           L                                                                               ",  # 1528
    "                                                                                                           L                                                                               ",  # 1529
    "                                                                                                           L                                                                               ",  # 1530
    "                                                                                                           L                                                                               ",  # 1531
    "                                                                                                           L                                                                               ",  # 1532
    "                                                                                                           L                                                                               ",  # 1533
    "                                                                                                           L                                                                               ",  # 1534
    "                                                                                                           L                                                                               ",  # 1535
    "                                                                                                           L                                                                               ",  # 1536
    "                                                                                                           L                                                                               ",  # 1537
    "                                                                                                           L                                                                               ",  # 1538
    "                                                                                                           L                                                                               ",  # 1539
    "                                                                                                           L                                                                               ",  # 1540
    "                                                                                                           L                                                                               ",  # 1541
    "                                                                                                           L                                                                               ",  # 1542
    "                                                                                                           L                                                                               ",  # 1543
    "                                                                                                           L                                                                               ",  # 1544
    "                                                                                                           L                                                                               ",  # 1545
    "                                                                                                           L                                                                               ",  # 1546
    "                                                                                                           L                                                                               ",  # 1547
    "                                                                                                           L                                                                               ",  # 1548
    "                                                                                                           L                                                                               ",  # 1549
    "                                                                                                           L                                                                               ",  # 1550
    "                                                                                                           L                                                                               ",  # 1551
    "                                                                                                           L                                                                               ",  # 1552
    "                                                                                                           L                                                                               ",  # 1553
    "                                                                                                           L                                                                               ",  # 1554
    "                                                                                                           L                                                                               ",  # 1555
    "                                                                                                           L                                                                               ",  # 1556
    "                                                                                                           L                                                                               ",  # 1557
    "                                                                                                           L                                                                               ",  # 1558
    "                                                                                                           L                                                                               ",  # 1559
    "                                                                                                           L                                                                               ",  # 1560
    "                                                                                                           L                                                                               ",  # 1561
    "                                                                                                           L                                                                               ",  # 1562
    "                                                                                                           L                                                                               ",  # 1563
    "                                                                                                           L                                                                               ",  # 1564
    "                                                                                                           L                                                                               ",  # 1565
    "                                                                                                           L                                                                               ",  # 1566
    "                                                                                                           L                                                                               ",  # 1567
    "                                                                                                           L                                                                               ",  # 1568
    "                                                                                                           L                                                                               ",  # 1569
    "                                                                                                           L                                                                               ",  # 1570
    "                                                                                                           L                                                                               ",  # 1571
    "                                                                                                           L                                                                               ",  # 1572
    "                                                                                                           L                                                                               ",  # 1573
    "                                                                                                           L                                                                               ",  # 1574
    "                                                                                                           L                                                                               ",  # 1575
    "                                                                                                           L                                                                               ",  # 1576
    "                                                                                                           L                                                                               ",  # 1577
    "                                                                                                           L                                                                               ",  # 1578
    "                                                                                                           L                                                                               ",  # 1579
    "                                                                                                           L                                                                               ",  # 1580
    "                                                                                                           L                                                                               ",  # 1581
    "                                                                                                           L                                                                               ",  # 1582
    "                                                                                                           L                                                                               ",  # 1583
    "                                                                                                           L                                                                               ",  # 1584
    "                                                                                                           L                                                                               ",  # 1585
    "                                                                                                           L                                                                               ",  # 1586
    "                                                                                                           L                                                                               ",  # 1587
    "                                                                                                           L                                                                               ",  # 1588
    "                                                                                                           L                                                                               ",  # 1589
    "                                                                                                           L                                                                               ",  # 1590
    "                                                                                                           L                                                                               ",  # 1591
    "                                                                                                           L                                                                               ",  # 1592
    "                                                                                                           L                                                                               ",  # 1593
    "                                                                                                           L                                                                               ",  # 1594
    "                                                                                                           L                                                                               ",  # 1595
    "                                                                                                           L                                                                               ",  # 1596
    "                                                                                                           L                                                                               ",  # 1597
    "                                                                                                           L                                                                               ",  # 1598
    "                                                                                                           L                                                                               ",  # 1599
    "                                                                                                           L                                                                               ",  # 1600
    "                                                                                                           L                                                                               ",  # 1601
    "                                                                                                           L                                                                               ",  # 1602
    "                                                                                                           L                                                                               ",  # 1603
    "                                                                                                           L                                                                               ",  # 1604
    "                                                                                                           L                                                                               ",  # 1605
    "                                                                                                           L                                                                               ",  # 1606
    "                                                                                                           L                                                                               ",  # 1607
    "                                                                                                           L                                                                               ",  # 1608
    "                                                                                                           L                                                                               ",  # 1609
    "                                                                                                           L                                                                               ",  # 1610
    "                                                                                                           L                                                                               ",  # 1611
    "                                                                                                           L                                                                               ",  # 1612
    "                                                                                                           L                                                                               ",  # 1613
    "                                                                                                           L                                                                               ",  # 1614
    "                                                                                                           L                                                                               ",  # 1615
    "                                                                                                           L                                                                               ",  # 1616
    "                                                                                                           L                                                                               ",  # 1617
    "                                                                                                           L                                                                               ",  # 1618
    "                                                                                                           L                                                                               ",  # 1619
    "                                                                                                           L                                                                               ",  # 1620
    "                                                                                                           L                                                                               ",  # 1621
    "                                                                                                           L                                                                               ",  # 1622
    "                                                                                                           L                                                                               ",  # 1623
    "                                                                                                           L                                                                               ",  # 1624
    "                                                                                                           L                                                                               ",  # 1625
    "                                                                                                           L                                                                               ",  # 1626
    "                                                                                                           L                                                                               ",  # 1627
    "                                                                                                           L                                                                               ",  # 1628
    "                                                                                                           L                                                                               ",  # 1629
    "                                                                                                           L                                                                               ",  # 1630
    "                                                                                                           L                                                                               ",  # 1631
    "                                                                                                           L                                                                               ",  # 1632
    "                                                                                                           L                                                                               ",  # 1633
    "                                                                                                           L                                                                               ",  # 1634
    "                                                                                                           L                                                                               ",  # 1635
    "                                                                                                           L                                                                               ",  # 1636
    "                                                                                                           L                                                                               ",  # 1637
    "                                                                                                           L                                                                               ",  # 1638
    "                                                                                                           L                                                                               ",  # 1639
    "                                                                                                           L                                                                               ",  # 1640
    "                                                                                                           L                                                                               ",  # 1641
    "                                                                                                           L                                                                               ",  # 1642
    "                                                                                                           L                                                                               ",  # 1643
    "                                                                                                           L                                                                               ",  # 1644
    "                                                                                                           L                                                                               ",  # 1645
    "                                                                                                           L                                                                               ",  # 1646
    "                                                                                                           L                                                                               ",  # 1647
    "                                                                                                           L                                                                               ",  # 1648
    "                                                                                                           L                                                                               ",  # 1649
    "                                                                                                           L                                                                               ",  # 1650
    "                                                                                                           L                                                                               ",  # 1651
    "                                                                                                           L                                                                               ",  # 1652
    "                                                                                                           L                                                                               ",  # 1653
    "                                                                                                           L                                                                               ",  # 1654
    "                                                                                                           L                                                                               ",  # 1655
    "                                                                                                           L                                                                               ",  # 1656
    "                                                                                                           L                                                                               ",  # 1657
    "                                                                                                           L                                                                               ",  # 1658
    "                                                                                                           L                                                                               ",  # 1659
    "                                                                                                           L                                                                               ",  # 1660
    "                                                                                                           L                                                                               ",  # 1661
    "                                                                                                           L                                                                               ",  # 1662
    "                                                                                                           L                                                                               ",  # 1663
    "                                                                                                           L                                                                               ",  # 1664
    "                                                                                                           L                                                                               ",  # 1665
    "                                                                                                           L                                                                               ",  # 1666
    "                                                                                                           L                                                                               ",  # 1667
    "                                                                                                           L                                                                               ",  # 1668
    "                                                                                                           L                                                                               ",  # 1669
    "                                                                                                           L                                                                               ",  # 1670
    "                                                                                                           L                                                                               ",  # 1671
    "                                                                                                           L                                                                               ",  # 1672
    "                                                                                                           L                                                                               ",  # 1673
    "                                                                                                           L                                                                               ",  # 1674
    "                                                                                                           L                                                                               ",  # 1675
    "                                                                                                           L                                                                               ",  # 1676
    "                                                                                                           L                                                                               ",  # 1677
    "                                                                                                           L                                                                               ",  # 1678
    "                                                                                                           L                                                                               ",  # 1679
    "                                                                                                           L                                                                               ",  # 1680
    "                                                                                                           L                                                                               ",  # 1681
    "                                                                                                           L                                                                               ",  # 1682
    "                                                                                                           L                                                                               ",  # 1683
    "                                                                                                           L                                                                               ",  # 1684
    "                                                                                                           L                                                                               ",  # 1685
    "                                                                                                           L                                                                               ",  # 1686
    "                                                                                                           L                                                                               ",  # 1687
    "                                                                                                           L                                                                               ",  # 1688
    "                                                                                                           L                                                                               ",  # 1689
    "                                                                                                           L                                                                               ",  # 1690
    "                                                                                                           L                                                                               ",  # 1691
    "                                                                                                           L                                                                               ",  # 1692
    "                                                                                                           L                                                                               ",  # 1693
    "                                                                                                           L                                                                               ",  # 1694
    "                                                                                                           L                                                                               ",  # 1695
    "                                                                                                           L                                                                               ",  # 1696
    "                                                                                                           L                                                                               ",  # 1697
    "                                                                                                           L                                                                               ",  # 1698
    "                                                                                                           L                                                                               ",  # 1699
    "                                                                                                           L                                                                               ",  # 1700
    "                                                                                                           L                                                                               ",  # 1701
    "                                                                                                           L                                                                               ",  # 1702
    "                                                                                                           L                                                                               ",  # 1703
    "                                                                                                           L                                                                               ",  # 1704
    "                                                                                                           L                                                                               ",  # 1705
    "                                                                                                           L                                                                               ",  # 1706
    "                                                                                                           L                                                                               ",  # 1707
    "                                                                                                           L                                                                               ",  # 1708
    "                                                                                                           L                                                                               ",  # 1709
    "                                                                                                           L                                                                               ",  # 1710
    "                                                                                                           L                                                                               ",  # 1711
    "                                                                                                           L                                                                               ",  # 1712
    "                                                                                                           L                                                                               ",  # 1713
    "                                                                                                           L                                                                               ",  # 1714
    "                                                                                                           L                                                                               ",  # 1715
    "                                                                                                           L                                                                               ",  # 1716
    "                                                                                                           L                                                                               ",  # 1717
    "                                                                                                           L                                                                               ",  # 1718
    "                                                                                                           L                                                                               ",  # 1719
    "                                                                                                           L                                                                               ",  # 1720
    "                                                                                                           L                                                                               ",  # 1721
    "                                                                                                           L                                                                               ",  # 1722
    "                                                                                                           L                                                                               ",  # 1723
    "                                                                                                           L                                                                               ",  # 1724
    "                                                                                                           L                                                                               ",  # 1725
    "                                                                                                           L                                                                               ",  # 1726
    "                                                                                                           L                                                                               ",  # 1727
    "                                                                                                           L                                                                               ",  # 1728
    "                                                                                                           L                                                                               ",  # 1729
    "                                                                                                           L                                                                               ",  # 1730
    "                                                                                                           L                                                                               ",  # 1731
    "                                                                                                           L                                                                               ",  # 1732
    "                                                                                                           L                                                                               ",  # 1733
    "                                                                                                           L                                                                               ",  # 1734
    "                                                                                                           L                                                                               ",  # 1735
    "                                                                                                           L                                                                               ",  # 1736
    "                                                                                                           L                                                                               ",  # 1737
    "                                                                                                           L                                                                               ",  # 1738
    "                                                                                                           L                                                                               ",  # 1739
    "                                                                                                           L                                                                               ",  # 1740
    "                                                                                                           L                                                                               ",  # 1741
    "                                                                                                           L                                                                               ",  # 1742
    "                                                                                                           L                                                                               ",  # 1743
    "                                                                                                           L                                                                               ",  # 1744
    "                                                                                                           L                                                                               ",  # 1745
    "                                                                                                           L                                                                               ",  # 1746
    "                                                                                                           L                                                                               ",  # 1747
    "                                                                                                           L                                                                               ",  # 1748
    "                                                                                                           L                                                                               ",  # 1749
    "                                                                                                           L                                                                               ",  # 1750
    "                                                                                                           L                                                                               ",  # 1751
    "                                                                                                           L                                                                               ",  # 1752
    "                                                                                                           L                                                                               ",  # 1753
    "                                                                                                           L                                                                               ",  # 1754
    "                                                                                                           L                                                                               ",  # 1755
    "                                                                                                           L                                                                               ",  # 1756
    "                                                                                                           L                                                                               ",  # 1757
    "                                                                                                           L                                                                               ",  # 1758
    "                                                                                                           L                                                                               ",  # 1759
    "                                                                                                           L                                                                               ",  # 1760
    "                                                                                                           L                                                                               ",  # 1761
    "                                                                                                           L                                                                               ",  # 1762
    "                                                                                                           L                                                                               ",  # 1763
    "                                                                                                           L                                                                               ",  # 1764
    "                                                                                                           L                                                                               ",  # 1765
    "                                                                                                           L                                                                               ",  # 1766
    "                                                                                                           L                                                                               ",  # 1767
    "                                                                                                           L                                                                               ",  # 1768
    "                                                                                                           L                                                                               ",  # 1769
    "                                                                                                           L                                                                               ",  # 1770
    "                                                                                                           L                                                                               ",  # 1771
    "                                                                                                           L                                                                               ",  # 1772
    "                                                                                                           L                                                                               ",  # 1773
    "                                                                                                           L                                                                               ",  # 1774
    "                                                                                                           L                                                                               ",  # 1775
    "                                                                                                           L                                                                               ",  # 1776
    "                                                                                                           L                                                                               ",  # 1777
    "                                                                                                           L                                                                               ",  # 1778
    "                                                                                                           L                                                                               ",  # 1779
    "                                                                                                           L                                                                               ",  # 1780
    "                                                                                                           L                                                                               ",  # 1781
    "                                                                                                           L                                                                               ",  # 1782
    "                                                                                                           L                                                                               ",  # 1783
    "                                                                                                           L                                                                               ",  # 1784
    "                                                                                                           L                                                                               ",  # 1785
    "                                                                                                           L                                                                               ",  # 1786
    "                                                                                                           L                                                                               ",  # 1787
    "                                                                                                           L                                                                               ",  # 1788
    "                                                                                                           L                                                                               ",  # 1789
    "                                                                                                           L                                                                               ",  # 1790
    "                                                                                                           L                                                                               ",  # 1791
    "                                                                                                           L                                                                               ",  # 1792
    "                                                                                                           L                                                                               ",  # 1793
    "                                                                                                           L                                                                               ",  # 1794
    "                                                                                                           L                                                                               ",  # 1795
    "                                                                                                           L                                                                               ",  # 1796
    "                                                                                                           L                                                                               ",  # 1797
    "                                                                                                           L                                                                               ",  # 1798
    "                                                                                                           L                                                                               ",  # 1799
    "                                                                                                           L                                                                               ",  # 1800
    "                                                                                                           L                                                                               ",  # 1801
    "                                                                                                           L                                                                               ",  # 1802
    "                                                                                                           L                                                                               ",  # 1803
    "                                                                                                           L                                                                               ",  # 1804
    "                                                                                                           L                                                                               ",  # 1805
    "                                                                                                           L                                                                               ",  # 1806
    "                                                                                                           L                                                                               ",  # 1807
    "                                                                                                           L                                                                               ",  # 1808
    "                                                                                                           L                                                                               ",  # 1809
    "                                                                                                           L                                                                               ",  # 1810
    "                                                                                                           L                                                                               ",  # 1811
    "                                                                                                           L                                                                               ",  # 1812
    "                                                                                                           L                                                                               ",  # 1813
    "                                                                                                           L                                                                               ",  # 1814
    "                                                                                                           L                                                                               ",  # 1815
    "                                                                                                           L                                                                               ",  # 1816
    "                                                                                                           L                                                                               ",  # 1817
    "                                                                                                           L                                                                               ",  # 1818
    "                                                                                                           L                                                                               ",  # 1819
    "                                                                                                           L                                                                               ",  # 1820
    "                                                                                                           L                                                                               ",  # 1821
    "                                                                                                           L                                                                               ",  # 1822
    "                                                                                                           L                                                                               ",  # 1823
    "                                                                                                           L                                                                               ",  # 1824
    "                                                                                                           L                                                                               ",  # 1825
    "                                                                                                           L                                                                               ",  # 1826
    "                                                                                                           L                                                                               ",  # 1827
    "                                                                                                           L                                                                               ",  # 1828
    "                                                                                                           L                                                                               ",  # 1829
    "                                                                                                           L                                                                               ",  # 1830
    "                                                                                                           L                                                                               ",  # 1831
    "                                                                                                           L                                                                               ",  # 1832
    "                                                                                                           L                                                                               ",  # 1833
    "                                                                                                           L                                                                               ",  # 1834
    "                                                                                                           L                                                                               ",  # 1835
    "                                                                                                           L                                                                               ",  # 1836
    "                                                                                                           L                                                                               ",  # 1837
    "                                                                                                           L                                                                               ",  # 1838
    "                                                                                                           L                                                                               ",  # 1839
    "                                                                                                           L                                                                               ",  # 1840
    "                                                                                                           L                                                                               ",  # 1841
    "                                                                                                           L                                                                               ",  # 1842
    "                                                                                                           L                                                                               ",  # 1843
    "                                                                                                           L                                                                               ",  # 1844
    "                                                                                                           L                                                                               ",  # 1845
    "                                                                                                           L                                                                               ",  # 1846
    "                                                                                                           L                                                                               ",  # 1847
    "                                                                                                           L                                                                               ",  # 1848
    "                                                                                                           L                                                                               ",  # 1849
    "                                                                                                           L                                                                               ",  # 1850
    "                                                                                                           L                                                                               ",  # 1851
    "                                                                                                           L                                                                               ",  # 1852
    "                                                                                                           L                                                                               ",  # 1853
    "                                                                                                           L                                                                               ",  # 1854
    "                                                                                                           L                                                                               ",  # 1855
    "                                                                                                           L                                                                               ",  # 1856
    "                                                                                                           L                                                                               ",  # 1857
    "                                                                                                           L                                                                               ",  # 1858
    "                                                                                                           L                                                                               ",  # 1859
    "                                                                                                           L                                                                               ",  # 1860
    "                                                                                                           L                                                                               ",  # 1861
    "                                                                                                           L                                                                               ",  # 1862
    "                                                                                                           L                                                                               ",  # 1863
    "                                                                                                           L                                                                               ",  # 1864
    "                                                                                                           L                                                                               ",  # 1865
    "                                                                                                           L                                                                               ",  # 1866
    "                                                                                                           L                                                                               ",  # 1867
    "                                                                                                           L                                                                               ",  # 1868
    "                                                                                                           L                                                                               ",  # 1869
    "                                                                                                           L                                                                               ",  # 1870
    "                                                                                                           L                                                                               ",  # 1871
    "                                                                                                           L                                                                               ",  # 1872
    "                                                                                                           L                                                                               ",  # 1873
    "                                                                                                           L                                                                               ",  # 1874
    "                                                                                                           L                                                                               ",  # 1875
    "                                                                                                           L                                                                               ",  # 1876
    "                                                                                                           L                                                                               ",  # 1877
    "                                                                                                           L                                                                               ",  # 1878
    "                                                                                                           L                                                                               ",  # 1879
    "                                                                                                           L                                                                               ",  # 1880
    "                                                                                                           L                                                                               ",  # 1881
    "                                                                                                           L                                                                               ",  # 1882
    "                                                                                                           L                                                                               ",  # 1883
    "                                                                                                           L                                                                               ",  # 1884
    "                                                                                                           L                                                                               ",  # 1885
    "                                                                                                           L                                                                               ",  # 1886
    "                                                                                                           L                                                                               ",  # 1887
    "                                                                                                           L                                                                               ",  # 1888
    "                                                                                                           L                                                                               ",  # 1889
    "                                                                                                           L                                                                               ",  # 1890
    "                                                                                                           L                                                                               ",  # 1891
    "                                                                                                           L                                                                               ",  # 1892
    "                                                                                                           L                                                                               ",  # 1893
    "                                                                                                           L                                                                               ",  # 1894
    "                                                                                                           L                                                                               ",  # 1895
    "                                                                                                           L                                                                               ",  # 1896
    "                                                                                                           L                                                                               ",  # 1897
    "                                                                                                           L                                                                               ",  # 1898
    "                                                                                                           L                                                                               ",  # 1899
    "                                                                                                           L                                                                               ",  # 1900
    "                                                                                                           L                                                                               ",  # 1901
    "                                                                                                           L                                                                               ",  # 1902
    "                                                                                                           L                                                                               ",  # 1903
    "                                                                                                           L                                                                               ",  # 1904
    "                                                                                                           L                                                                               ",  # 1905
    "                                                                                                           L                                                                               ",  # 1906
    "                                                                                                           L                                                                               ",  # 1907
    "                                                                                                           L                                                                               ",  # 1908
    "                                                                                                           L                                                                               ",  # 1909
    "                                                                                                           L                                                                               ",  # 1910
    "                                                                                                           L                                                                               ",  # 1911
    "                                                                                                           L                                                                               ",  # 1912
    "                                                                                                           L                                                                               ",  # 1913
    "                                                                                                           L                                                                               ",  # 1914
    "                                                                                                           L                                                                               ",  # 1915
    "                                                                                                           L                                                                               ",  # 1916
    "                                                                                                           L                                                                               ",  # 1917
    "                                                                                                           L                                                                               ",  # 1918
    "                                                                                                           L                                                                               ",  # 1919
    "                                                                                                           L                                                                               ",  # 1920
    "                                                                                                           L                                                                               ",  # 1921
    "                                                                                                           L                                                                               ",  # 1922
    "                                                                                                           L                                                                               ",  # 1923
    "                                                                                                           L                                                                               ",  # 1924
    "                                                                                                           L                                                                               ",  # 1925
    "                                                                                                           L                                                                               ",  # 1926
    "                                                                                                           L                                                                               ",  # 1927
    "                                                                                                           L                                                                               ",  # 1928
    "                                                                                                           L                                                                               ",  # 1929
    "                                                                                                           L                                                                               ",  # 1930
    "                                                                                                           L                                                                               ",  # 1931
    "                                                                                                           L                                                                               ",  # 1932
    "                                                                                                           L                                                                               ",  # 1933
    "                                                                                                           L                                                                               ",  # 1934
    "                                                                                                           L                                                                               ",  # 1935
    "                                                                                                           L                                                                               ",  # 1936
    "                                                                                                           L                                                                               ",  # 1937
    "                                                                                                           L                                                                               ",  # 1938
    "                                                                                                           L                                                                               ",  # 1939
    "                                                                                                           L                                                                               ",  # 1940
    "                                                                                                           L                                                                               ",  # 1941
    "                                                                                                           L                                                                               ",  # 1942
    "                                                                                                           L                                                                               ",  # 1943
    "                                                                                                           L                                                                               ",  # 1944
    "                                                                                                           L                                                                               ",  # 1945
    "                                                                                                           L                                                                               ",  # 1946
    "                                                                                                           L                                                                               ",  # 1947
    "                                                                                                           L                                                                               ",  # 1948
    "                                                                                                           L                                                                               ",  # 1949
    "                                                                                                           L                                                                               ",  # 1950
    "                                                                                                           L                                                                               ",  # 1951
    "                                                                                                           L                                                                               ",  # 1952
    "                                                                                                           L                                                                               ",  # 1953
    "                                                                                                           L                                                                               ",  # 1954
    "                                                                                                           L                                                                               ",  # 1955
    "                                                                                                           L                                                                               ",  # 1956
    "                                                                                                           L                                                                               ",  # 1957
    "                                                                                                           L                                                                               ",  # 1958
    "                                                                                                           L                                                                               ",  # 1959
    "                                                                                                           L                                                                               ",  # 1960
    "                                                                                                           L                                                                               ",  # 1961
    "                                                                                                           L                                                                               ",  # 1962
    "                                                                                                           L                                                                               ",  # 1963
    "                                                                                                           L                                                                               ",  # 1964
    "                                                                                                           L                                                                               ",  # 1965
    "                                                                                                           L                                                                               ",  # 1966
    "                                                                                                           L                                                                               ",  # 1967
    "                                                                                                           L                                                                               ",  # 1968
    "                                                                                                           L                                                                               ",  # 1969
    "                                                                                                           L                                                                               ",  # 1970
    "                                                                                                           L                                                                               ",  # 1971
    "                                                                                                           L                                                                               ",  # 1972
    "                                                                                                           L                                                                               ",  # 1973
    "                                                                                                           L                                                                               ",  # 1974
    "                                                                                                           L                                                                               ",  # 1975
    "                                                                                                           L                                                                               ",  # 1976
    "                                                                                                           L                                                                               ",  # 1977
    "                                                                                                           L                                                                               ",  # 1978
    "                                                                                                           L                                                                               ",  # 1979
    "                                                                                                           L                                                                               ",  # 1980
    "                                                                                                           L                                                                               ",  # 1981
    "                                                                                                           L                                                                               ",  # 1982
    "                                                                                                           L                                                                               ",  # 1983
    "                                                                                                           L                                                                               ",  # 1984
    "                                                                                                           L                                                                               ",  # 1985
    "                                                                                                           L                                                                               ",  # 1986
    "                                                                                                           L                                                                               ",  # 1987
    "                                                                                                           L                                                                               ",  # 1988
    "                                                                                                           L                                                                               ",  # 1989
    "                                                                                                           L                                                                               ",  # 1990
    "                                                                                                           L                                                                               ",  # 1991
    "                                                                                                           L                                                                               ",  # 1992
    "                                                                                                           L                                                                               ",  # 1993
    "                                                                                                           L                                                                               ",  # 1994
    "                                                                                                           L                                                                               ",  # 1995
    "                                                                                                           L                                                                               ",  # 1996
    "                                                                                                           L                                                                               ",  # 1997
    "                                                                                                           L                                                                               ",  # 1998
    "                                                                                                           L                                                                               ",  # 1999
    "                                                                                                           L                                                                               ",  # 2000
]

# Enemies placement: (row, col, type, patrol_range)
ENEMIES = [
    # Surface enemies
    (11, 25, "slime", 3),
    (11, 45, "bee", 2),
    (11, 60, "snail", 2),
    (11, 85, "slime_blue", 3),
    (11, 100, "worm", 2),
    (11, 115, "fly", 3),
    # Upper cave layer (rows 15-19)
    (17, 22, "bee", 2),
    (18, 35, "snail", 2),
    (19, 55, "slime", 3),
    # Deep shaft (rows 20-24)
    (21, 40, "slime_blue", 2),
    (22, 65, "fly", 3),
    (23, 25, "worm", 2),
    (24, 80, "bee", 2),
    # Deepest layer (rows 25-28)
    (26, 50, "snail", 3),
    (27, 90, "slime", 3),
    (28, 30, "slime_blue", 2),
    (28, 110, "fly", 2),
]

# Coins placement (additional to map layout)
COINS = [
    # Surface coins
    (4, 36), (4, 38), (4, 40),
    (5, 50), (5, 52), (5, 54),
    (6, 25), (6, 27),
    (7, 80), (7, 82), (7, 84),
    (8, 95), (8, 97), (8, 99),
    # Upper cave coins
    (15, 22), (16, 24), (17, 30), (17, 45),
    # Deep shaft coins (hard to reach)
    (20, 38), (20, 40), (21, 55),
    (23, 70), (24, 85), (25, 95),
    # Deepest treasure
    (26, 52), (27, 100), (28, 115),
]

# Cloud decorations (x, y, type_index, scale)
CLOUDS = [
    (100, 80, 0, 1.5), (300, 120, 1, 2.0), (500, 60, 2, 1.8),
    (700, 100, 0, 1.6), (900, 70, 1, 2.2), (1100, 130, 2, 1.5),
    (1300, 90, 0, 1.7), (1500, 110, 1, 1.9), (1700, 50, 2, 2.0),
]

# Tree decorations (attached to grass tops)
TREES = [
    (9, 8), (9, 10), (9, 65), (9, 72),
    (10, 35), (10, 55),
]

# Level dimensions
WORLD_W = len(MAP_LAYOUT[0]) * TILE_SIZE if MAP_LAYOUT else 120 * TILE_SIZE
WORLD_H = len(MAP_LAYOUT) * TILE_SIZE

# ═════════════════════════════════════════════════════════════
#  PLAYER CLASS
# ═════════════════════════════════════════════════════════════

class Player:
    W, H = 28, 44  # Hitbox size

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.facing_right = True
        self.on_ground = False
        self.jump_count = 0
        self.rect = pygame.Rect(int(x), int(y), self.W, self.H)
        self.state = 'idle'
        self.frame_idx = 0.0
        self.spawn_x = float(x)
        self.spawn_y = float(y)
        self.invincible = 0.0

    def get_collisions(self, dx=0, dy=0):
        """Get list of solid tiles overlapping player rect offset by dx,dy."""
        hits = []
        check_rect = self.rect.move(dx, dy)
        start_col = max(0, int(check_rect.left // TILE_SIZE))
        end_col = min(len(MAP_LAYOUT[0])-1, int(check_rect.right // TILE_SIZE))
        start_row = max(0, int(check_rect.top // TILE_SIZE))
        end_row = min(len(MAP_LAYOUT)-1, int(check_rect.bottom // TILE_SIZE))
        
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                if 0 <= row < len(MAP_LAYOUT) and 0 <= col < len(MAP_LAYOUT[row]):
                    char = MAP_LAYOUT[row][col]
                    if char in SOLID_TILES:
                        tile_rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        if check_rect.colliderect(tile_rect):
                            hits.append(tile_rect)
        return hits

    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -SPEED
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = SPEED
            self.facing_right = True
        else:
            self.vx = 0

        # Gravity
        self.vy = min(self.vy + GRAVITY * dt, 1200)

        # X movement with collision check before moving
        move_x = self.vx * dt
        if move_x != 0:
            # Check if we can move
            test_hits = self.get_collisions(move_x, 0)
            if test_hits:
                # Find the nearest valid position
                if self.vx > 0:  # Moving right
                    nearest_left = min(hit.left for hit in test_hits)
                    self.rect.right = nearest_left - 1  # 1px gap
                else:  # Moving left
                    nearest_right = max(hit.right for hit in test_hits)
                    self.rect.left = nearest_right + 1  # 1px gap
                self.x = float(self.rect.x)
                self.vx = 0
            else:
                self.x += move_x
                self.rect.x = int(self.x)

        # Y movement with collision check before moving
        self.on_ground = False
        move_y = self.vy * dt
        if move_y != 0:
            test_hits = self.get_collisions(0, move_y)
            if test_hits:
                if self.vy > 0:  # Falling
                    nearest_top = min(hit.top for hit in test_hits)
                    self.rect.bottom = nearest_top - 1  # 1px gap
                    self.y = float(self.rect.y)
                    self.vy = 0
                    self.on_ground = True
                    self.jump_count = 0
                else:  # Rising/jumping
                    nearest_bottom = max(hit.bottom for hit in test_hits)
                    self.rect.top = nearest_bottom + 1  # 1px gap
                    self.y = float(self.rect.y)
                    self.vy = 0
            else:
                self.y += move_y
                self.rect.y = int(self.y)
        
        # Final ground check - are we standing on something?
        if not self.on_ground and self.vy >= 0:
            ground_hits = self.get_collisions(0, 2)  # Check 2px below
            if ground_hits:
                self.on_ground = True
                self.jump_count = 0
                # Snap to ground
                nearest_top = min(hit.top for hit in ground_hits)
                self.rect.bottom = nearest_top - 1
                self.y = float(self.rect.y)
                self.vy = 0

        # Fall off world - respawn
        if self.rect.y > WORLD_H + 200:
            self.x = self.spawn_x
            self.y = self.spawn_y
            self.vy = 0
            self.health = max(0, getattr(self, 'health', 3) - 1)
            self.invincible = 2.0

        # Update animation state
        new_state = self.state
        if not self.on_ground:
            if self.jump_count == 2:
                new_state = 'double_jump'
            elif self.vy < 0:
                new_state = 'jump'
            else:
                new_state = 'fall'
        elif self.vx != 0:
            new_state = 'run'
        else:
            new_state = 'idle'

        if new_state != self.state:
            self.state = new_state
            self.frame_idx = 0.0

        # Animation frame progression
        anim_speed = 20 if self.state == 'run' else 12
        self.frame_idx += anim_speed * dt

        # Invincibility countdown
        if self.invincible > 0:
            self.invincible -= dt

    def jump(self):
        if self.jump_count < 2:
            self.vy = JUMP_FORCE
            self.jump_count += 1
            self.on_ground = False
            self.frame_idx = 0.0

    def draw(self, surf, sx, sy):
        frames = PLAYER_ANIMS.get(self.state, PLAYER_ANIMS['idle'])
        if not frames:
            return
        
        if self.state in ('jump', 'fall', 'double_jump'):
            idx = min(int(self.frame_idx), len(frames) - 1)
        else:
            idx = int(self.frame_idx) % len(frames)
        
        img = frames[idx]
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        
        # Center sprite on hitbox
        bx = self.rect.centerx - img.get_width() // 2 - sx
        by = self.rect.bottom - img.get_height() - sy
        
        # Flash when invincible
        if self.invincible > 0 and int(self.invincible * 10) % 2 == 0:
            return
            
        surf.blit(img, (bx, by))


# ═════════════════════════════════════════════════════════════
#  ENEMY CLASS
# ═════════════════════════════════════════════════════════════

class Enemy:
    def __init__(self, row, col, etype, patrol):
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = row * TILE_SIZE
        self.etype = etype
        self.patrol_start = self.x
        self.patrol_range = patrol * TILE_SIZE
        self.direction = 1
        self.speed = 50
        self.rect = pygame.Rect(self.x - 16, self.y, 32, 32)
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return
        
        # Simple patrol AI
        self.x += self.speed * self.direction * dt
        
        # Turn around at patrol limits
        if self.x > self.patrol_start + self.patrol_range:
            self.direction = -1
        elif self.x < self.patrol_start - self.patrol_range:
            self.direction = 1
            
        self.rect.x = int(self.x) - 16
        self.rect.y = int(self.y)

    def draw(self, surf, sx, sy):
        if not self.alive:
            return
        img = ENEMY_FRAMES.get(self.etype, ENEMY_FRAMES.get('slime'))
        if img:
            # Flip based on direction
            if self.direction < 0:
                img = pygame.transform.flip(img, True, False)
            bx = self.rect.centerx - img.get_width() // 2 - sx
            by = self.rect.bottom - img.get_height() - sy
            surf.blit(img, (bx, by))


# ═════════════════════════════════════════════════════════════
#  UI DRAWING
# ═════════════════════════════════════════════════════════════

UI_TEAL = (60, 180, 160)
UI_GOLD = (255, 210, 80)
UI_PANEL = (10, 30, 35, 200)

def draw_panel(surf, rect, radius=10):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, UI_PANEL, (0, 0, *rect.size), border_radius=radius)
    pygame.draw.rect(panel, (*UI_TEAL, 80), (0, 0, *rect.size), 2, border_radius=radius)
    surf.blit(panel, rect.topleft)

def draw_health_orbs(surf, health, max_health=3, x=18, y=18):
    orb_r = 13
    spacing = 34
    for i in range(max_health):
        cx = x + i * spacing + orb_r
        cy = y + orb_r
        filled = i < health
        if filled:
            gc = pygame.Surface((orb_r * 4, orb_r * 4), pygame.SRCALPHA)
            pygame.draw.circle(gc, (80, 220, 160, 60), (orb_r * 2, orb_r * 2), orb_r * 2)
            surf.blit(gc, (cx - orb_r * 2, cy - orb_r * 2))
        pygame.draw.circle(surf, UI_TEAL if filled else (30, 90, 80), (cx, cy), orb_r, 2)
        col_in = (60, 200, 140) if filled else (20, 55, 50)
        pygame.draw.circle(surf, col_in, (cx, cy), orb_r - 3)
        if filled:
            pygame.draw.circle(surf, (180, 255, 220), (cx - 4, cy - 4), 4)

def draw_hud(surf, game_state, collected_coins):
    try:
        font_hud = pygame.font.SysFont("segoeui", 18, bold=True)
        font_sm = pygame.font.SysFont("consolas", 13)
    except Exception:
        font_hud = font_sm = pygame.font.Font(None, 20)

    # Health panel
    draw_panel(surf, pygame.Rect(10, 10, 160, 50))
    draw_health_orbs(surf, game_state.get("health", 3), game_state.get("max_health", 3))

    # Score panel
    draw_panel(surf, pygame.Rect(surf.get_width() - 170, 10, 160, 44))
    score_lbl = font_hud.render(f"SCORE  {game_state.get('score', 0)}", True, UI_GOLD)
    surf.blit(score_lbl, (surf.get_width() - 160, 22))

    # Coins collected
    coin_text = font_hud.render(f"COINS: {collected_coins}", True, UI_GOLD)
    surf.blit(coin_text, (surf.get_width() // 2 - 40, 22))

    # Level name
    lvl = font_sm.render("SUNNY GRASSLAND", True, (100, 180, 160))
    surf.blit(lvl, (surf.get_width() // 2 - lvl.get_width() // 2, 8))

    # Controls hint
    controls = [
        ("[A] [D] / [<] [>]", "Move"),
        ("[SPACE] / [W]", "Double Jump"),
        ("[ESC]", "Quit"),
    ]
    pad_y = surf.get_height() - 20 - len(controls) * 20
    for idx, (keys, action) in enumerate(controls):
        key_lbl = font_sm.render(keys, True, (200, 220, 255))
        act_lbl = font_sm.render(action, True, (120, 140, 160))
        surf.blit(key_lbl, (20, pad_y + idx * 20))
        surf.blit(act_lbl, (150, pad_y + idx * 20))


# ═════════════════════════════════════════════════════════════
#  BACKGROUND DRAWING
# ═════════════════════════════════════════════════════════════

def draw_sky_gradient(surf):
    """Draw a nice sky gradient."""
    w, h = surf.get_size()
    for y in range(h):
        t = y / h
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))


def draw_clouds(surf, scroll_x, scroll_y):
    """Draw parallax clouds with proper scaling."""
    for cx, cy, ctype, extra_scale in CLOUDS:
        # Parallax - clouds move slower than camera
        parallax_x = cx - scroll_x * 0.2
        parallax_y = cy - scroll_y * 0.05
        
        # Wrap around for infinite feel
        while parallax_x < -200:
            parallax_x += WORLD_W + 400
        while parallax_x > surf.get_width() + 200:
            parallax_x -= WORLD_W + 400
            
        if -100 <= parallax_x < surf.get_width() + 100:
            img = cloud_images[ctype % len(cloud_images)]
            # Apply extra scale from CLOUDS definition
            if extra_scale != 1.0:
                w, h = img.get_size()
                final_w = int(w * extra_scale)
                final_h = int(h * extra_scale)
                scaled = pygame.transform.scale(img, (final_w, final_h))
                surf.blit(scaled, (int(parallax_x), int(parallax_y)))
            else:
                surf.blit(img, (int(parallax_x), int(parallax_y)))

def scan_decorations_from_map():
    """Scan map for decoration tiles and return their positions."""
    decorations = []
    for row_idx, row in enumerate(MAP_LAYOUT):
        for col_idx, char in enumerate(row):
            if char in DECORATION_TILES:
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                decorations.append((x, y, char))
    return decorations


# ═════════════════════════════════════════════════════════════
#  MAIN LEVEL LOOP
# ═════════════════════════════════════════════════════════════

def run_level(surface, game_state=None):
    """Main entry point for the level. Returns next level name or 'quit'."""
    global SCREEN_W, SCREEN_H
    
    if game_state is None:
        game_state = {"health": 3, "max_health": 3, "score": 0, "lives": 3}
    
    # Initialize player at start position
    player = Player(3 * TILE_SIZE, 8 * TILE_SIZE)
    
    # Create enemies
    enemies = [Enemy(r, c, t, p) for r, c, t, p in ENEMIES]
    
    # Scan for decorations in map
    decorations = scan_decorations_from_map()
    
    # Track coins
    collected_coins = set()
    
    # Camera
    scroll_x, scroll_y = 0, 0
    
    clock = pygame.time.Clock()
    running = True
    
    print("[Kenney Level] Starting Sunny Grassland...")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
                elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    player.jump()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = event.w, event.h
                surface = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
        
        # Update
        player.update(dt)
        
        for enemy in enemies:
            enemy.update(dt)
            # Check enemy collision with player
            if enemy.alive and enemy.rect.colliderect(player.rect):
                if player.invincible <= 0:
                    # Check if jumping on enemy (Mario style)
                    if player.vy > 0 and player.rect.bottom < enemy.rect.centery:
                        enemy.alive = False
                        player.vy = -300  # Bounce
                        game_state["score"] += 100
                    else:
                        # Take damage
                        game_state["health"] = max(0, game_state.get("health", 3) - 1)
                        player.invincible = 2.0
                        # Knockback
                        player.vx = -300 if player.facing_right else 300
                        player.vy = -200
        
        # Check coin collection
        for row, col in COINS:
            coin_key = (row, col)
            if coin_key not in collected_coins:
                coin_rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player.rect.colliderect(coin_rect):
                    collected_coins.add(coin_key)
                    game_state["score"] += 10
        
        # Check map coin collection (C in map)
        player_row = int(player.rect.centery // TILE_SIZE)
        player_col = int(player.rect.centerx // TILE_SIZE)
        if 0 <= player_row < len(MAP_LAYOUT) and 0 <= player_col < len(MAP_LAYOUT[player_row]):
            if MAP_LAYOUT[player_row][player_col] == 'C':
                coin_key = (player_row, player_col)
                if coin_key not in collected_coins:
                    collected_coins.add(coin_key)
                    game_state["score"] += 10
        
        # Level exit - reach the flag at the end
        if player.rect.x > (len(MAP_LAYOUT[0]) - 5) * TILE_SIZE:
            game_state["score"] += 500  # Level completion bonus
            return "exclusion"  # Go to Exclusion Zone Industrial
        
        # Game over check
        if game_state.get("health", 3) <= 0:
            game_state["health"] = game_state.get("max_health", 3)
            game_state["lives"] = max(0, game_state.get("lives", 3) - 1)
            if game_state["lives"] <= 0:
                return "quit"
            # Respawn
            player.x = player.spawn_x
            player.y = player.spawn_y
            player.vy = 0
        
        # Camera follow
        target_x = player.rect.centerx - SCREEN_W // 2
        target_y = player.rect.centery - SCREEN_H // 2
        scroll_x += (target_x - scroll_x) * 5 * dt
        scroll_y += (target_y - scroll_y) * 5 * dt
        
        # Clamp camera
        max_scroll_x = max(0, len(MAP_LAYOUT[0]) * TILE_SIZE - SCREEN_W)
        max_scroll_y = max(0, len(MAP_LAYOUT) * TILE_SIZE - SCREEN_H)
        scroll_x = max(0, min(scroll_x, max_scroll_x))
        scroll_y = max(0, min(scroll_y, max_scroll_y))
        
        # Draw
        draw_sky_gradient(surface)
        draw_clouds(surface, scroll_x, scroll_y)
        
        # Draw map tiles (ground, dirt)
        start_col = max(0, int(scroll_x // TILE_SIZE))
        end_col = min(len(MAP_LAYOUT[0]), int((scroll_x + SCREEN_W) // TILE_SIZE) + 1)
        start_row = max(0, int(scroll_y // TILE_SIZE))
        end_row = min(len(MAP_LAYOUT), int((scroll_y + SCREEN_H) // TILE_SIZE) + 1)
        
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                if row < len(MAP_LAYOUT) and col < len(MAP_LAYOUT[row]):
                    char = MAP_LAYOUT[row][col]
                    if char == ' ' or char == 'C':
                        continue
                    
                    x = col * TILE_SIZE - int(scroll_x)
                    y = row * TILE_SIZE - int(scroll_y)
                    
                    # Draw tile if exists
                    if char in loaded_tiles:
                        surface.blit(loaded_tiles[char], (x, y))
                    
                    # Draw coins
                    if char == 'C' and (row, col) not in collected_coins:
                        coin_img = loaded_tiles.get('C')
                        if coin_img:
                            surface.blit(coin_img, (x, y))
        
        # Draw decorations (trees, bushes, flowers) on top of ground
        for dx, dy, char in decorations:
            screen_x = dx - int(scroll_x)
            screen_y = dy - int(scroll_y)
            if -100 <= screen_x < SCREEN_W + 100 and -100 <= screen_y < SCREEN_H + 100:
                if char in loaded_tiles:
                    surface.blit(loaded_tiles[char], (screen_x, screen_y))
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(surface, int(scroll_x), int(scroll_y))
        
        # Draw player
        player.draw(surface, int(scroll_x), int(scroll_y))
        
        # Draw HUD
        draw_hud(surface, game_state, len(collected_coins))
        
        pygame.display.flip()
    
    return "quit"


if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    pygame.display.set_caption("Sunny Grassland - Kenney Level")
    result = run_level(screen)
    print(f"Level ended: {result}")
    pygame.quit()
    sys.exit()
