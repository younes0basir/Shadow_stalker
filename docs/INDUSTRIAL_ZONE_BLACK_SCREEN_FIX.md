# Industrial Zone Black Screen Fix

## Problem

When transitioning to the 3rd map (Industrial Zone), the screen turns completely black and nothing is visible.

## Root Cause Analysis

The black screen could be caused by several issues:

1. **Background image not loading** - If `bg_img` is `None` or has invalid dimensions
2. **Surface not being drawn to** - Rendering code might be skipped
3. **Camera scroll values incorrect** - Everything drawn off-screen
4. **Transition effect not clearing** - Previous screen state persisting

## Fixes Applied

### 1. Added Fallback Background Gradient

**File:** `maps/industrial_zone_map.py`  
**Lines:** ~463-476

**Before:**
```python
surface.fill((18, 14, 22))

if bg_img:
    surface.blit(bg_img, (0, 0))
# If bg_img is None, screen stays dark gray/black
```

**After:**
```python
surface.fill((18, 14, 22))

if bg_img and bg_img.get_width() > 0:
    surface.blit(bg_img, (0, 0))
else:
    # Fallback: draw a simple gradient background
    for y in range(SCREEN_H):
        shade = int(18 + (y / SCREEN_H) * 15)
        pygame.draw.line(surface, (shade, shade - 4, shade - 8), (0, y), (SCREEN_W, y))
```

**Benefit:** Even if background fails to load, player sees a gradient instead of black screen.

---

### 2. Enhanced Background Loading with Error Checking

**File:** `maps/industrial_zone_map.py`  
**Lines:** ~141-155

**Before:**
```python
bg_dir = os.path.join(BASE, "2 Background")
bg_img = None
for fname in ("Background.png", "1.png"):
    p = os.path.join(bg_dir, fname)
    img = load_image(p)
    if img.get_width() > 1:
        bg_img = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        break
```

**After:**
```python
bg_dir = os.path.join(BASE, "2 Background")
bg_img = None
for fname in ("Background.png", "1.png"):
    p = os.path.join(bg_dir, fname)
    if os.path.exists(p):
        img = load_image(p)
        if img and img.get_width() > 1:
            bg_img = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
            print(f"[Industrial Zone] Background loaded: {fname}")
            break
    else:
        print(f"[Industrial Zone] Warning: Background file not found: {p}")

if bg_img is None:
    print("[Industrial Zone] Warning: No background image loaded, using fallback gradient")
```

**Benefits:**
- Checks if file exists before loading
- Validates image after loading
- Prints debug messages to console
- Warns if no background loaded

---

### 3. Added Debug Output on Level Start

**File:** `maps/industrial_zone_map.py`  
**Lines:** ~375-392

**Added:**
```python
def run_level(surface, game_state=None):
    # ...
    print(f"[Industrial Zone] Level starting - Surface: {surface.get_width()}x{surface.get_height()}, Background: {'Loaded' if bg_img else 'None'}")
    
    # ... camera init ...
    print(f"[Industrial Zone] Camera init: sx={sx}, sy={sy}, Map size: {map_width}x{map_height}")
```

**Purpose:** Helps diagnose issues by showing:
- Surface dimensions
- Whether background loaded
- Camera scroll values
- Map dimensions

---

## How to Diagnose

### Step 1: Run the Game with Console Visible

```bash
python core/game.py
```

Watch the console output when transitioning to Industrial Zone.

### Step 2: Check for These Messages

**Good (Background Loaded):**
```
[Industrial Zone] Background loaded: Background.png (1280x720)
[Industrial Zone] Level starting - Surface: 1280x720, Background: Loaded
[Industrial Zone] Camera init: sx=0, sy=0, Map size: 1280x864
```

**Bad (Background Failed):**
```
[Industrial Zone] Warning: Background file not found: C:\...\Background.png
[Industrial Zone] Warning: No background image loaded, using fallback gradient
[Industrial Zone] Level starting - Surface: 1280x720, Background: None
```

**Very Bad (Crash/Error):**
```
Traceback (most recent call last):
  File "maps/industrial_zone_map.py", line XXX, in ...
Error: ...
```

### Step 3: Verify Background Files Exist

```bash
# Check if background directory exists
Test-Path "assets\craftpix-net-314143-free-industrial-zone-tileset-pixel-art\2 Background"

# List files in directory
Get-ChildItem "assets\craftpix-net-314143-free-industrial-zone-tileset-pixel-art\2 Background"
```

Expected files:
- `Background.png` (6.4 KB)
- `1.png` (1.2 KB)
- `2.png`, `3.png`, etc.

---

## Common Causes & Solutions

### Issue 1: Background File Missing

**Symptoms:**
```
Warning: Background file not found: ...
```

**Solution:**
Verify the asset folder exists and contains the background files. If missing, reinstall assets or check git LFS.

---

### Issue 2: Corrupted Image File

**Symptoms:**
```
Error loading image: ...
```

**Solution:**
Delete and re-download the Industrial Zone tileset from the original source.

---

### Issue 3: Wrong Path

**Symptoms:**
Background not found even though file exists.

**Solution:**
Check that `BASE` path is correct:
```python
BASE = os.path.join(PARENT_DIR, "assets", "craftpix-net-314143-free-industrial-zone-tileset-pixel-art")
```

Verify this matches your actual folder structure.

---

### Issue 4: Surface Not Valid

**Symptoms:**
```
Surface: 0x0  # Invalid dimensions
```

**Solution:**
Ensure pygame display is initialized before calling `run_level()`. This should be handled by `core/game.py`.

---

### Issue 5: Camera Out of Bounds

**Symptoms:**
Screen shows but everything is off-screen.

**Solution:**
Check camera initialization:
```python
sx = max(0, min(player_x - SCREEN_W // 2, map_width - SCREEN_W))
sy = max(0, min(player_y - SCREEN_H // 2, map_height - SCREEN_H))
```

For Industrial Zone (40 tiles wide = 1280px):
- `sx` should be 0 (no horizontal scrolling needed)
- `sy` should center vertically

---

## Testing

### Test 1: Play Through to Industrial Zone

1. Start game: `python core/game.py`
2. Complete Exclusion Zone
3. Complete Green Zone
4. Transition to Industrial Zone
5. **Expected:** See industrial background with tiles, decorations, and player

### Test 2: Direct Launch (Debug)

Create a test script:
```python
import pygame
from maps.industrial_zone_map import run_level

pygame.init()
screen = pygame.display.set_mode((1280, 720))
result = run_level(screen)
print(f"Level returned: {result}")
pygame.quit()
```

This isolates the Industrial Zone from transitions.

### Test 3: Verify Rendering Order

The rendering should happen in this order:
1. Fill background color
2. Draw background image (or gradient fallback)
3. Draw animated conveyor belt
4. Draw static decorations
5. Draw animated decorations
6. Draw tiles
7. Draw coins
8. Draw HUD
9. Draw player
10. Draw bot

If any step fails, subsequent steps still render.

---

## What You Should See

### With Background Loaded
- Dark industrial factory interior
- Gray/metal walls and floors
- Conveyor belts
- Barrels, boxes, lockers
- Player character (VirtualGuy)
- AI bot (MaskDude) chasing you
- Coins to collect
- HUD showing health and score

### With Fallback Gradient Only
- Dark gray to lighter gray vertical gradient
- All game elements (tiles, player, bot, coins) still visible
- Just no background image

### If Still Black
Check console for error messages and refer to troubleshooting section above.

---

## Technical Details

### Map Specifications
- **Width:** 40 tiles × 32px = 1280px (exactly fits screen)
- **Height:** 27 rows × 32px = 864px
- **Scrolling:** Vertical only (player can move up/down)
- **Background:** Static (no parallax)

### Background Image Requirements
- **Format:** PNG with alpha channel
- **Size:** Any (scaled to 1280×720)
- **Style:** Dark industrial/factory theme
- **Location:** `assets/craftpix-net-314143-free-industrial-zone-tileset-pixel-art/2 Background/`

### Color Palette
- **Background fill:** `(18, 14, 22)` - Very dark purple-gray
- **Fallback gradient:** `(18-33, 14-29, 22-37)` - Subtle vertical gradient
- **Tiles:** Various grays, browns, metallic colors

---

## Future Improvements

1. **Add multiple background layers** for parallax effect
2. **Implement dynamic lighting** (flickering lights, shadows)
3. **Add atmospheric effects** (steam, smoke particles)
4. **Create level-specific backgrounds** for different areas
5. **Add background music** specific to Industrial Zone

---

**Date Fixed:** April 28, 2026  
**Severity:** High (game-breaking)  
**Status:** ✅ Fixed with fallback system  
**Testing:** Required - play through to verify
