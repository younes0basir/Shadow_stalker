# 🚀 Map Editor - Speed & Efficiency Guide

## ⚡ Fastest Workflow Tips

### 1. **Middle Mouse Drag to Pan** (GAME CHANGER!)
   - Hold middle mouse button and drag to pan around
   - MUCH faster than WASD keys
   - Works while zoomed in or out

### 2. **Quick Tile Selection with Number Keys**
   - Press **1-9** to instantly select favorite tiles
   - No need to scroll through the palette!
   - Favorites shown at top of palette when you press **F**

### 3. **Brush Sizes for Fast Painting**
   - Press **B** to cycle brush sizes: 1x1 → 2x2 → 3x3
   - Paint large areas quickly by dragging
   - Visual preview shows brush area under cursor
   - Right-click with brush to erase large areas

### 4. **Favorites Mode**
   - Press **F** to toggle favorites view
   - Shows only the 9 most commonly used tiles
   - Each has a number (1-9) for quick selection
   - Press **F** again to see all tiles

### 5. **Smart Navigation**
   - **R** - Reset view to default (zoom 1.0x, center)
   - **+/-** - Zoom in/out smoothly
   - **Scroll Wheel** - Cycle through tiles quickly
   - **G** - Toggle grid on/off (cleaner view)

## 🎯 Common Tasks - Fastest Way

### Creating Ground Platforms
1. Press **2** (selects grass tile)
2. Set brush to 3x3 (press **B** twice)
3. Click and drag to paint ground quickly
4. Switch to 1x1 brush for edges

### Building Walls/Pillars
1. Press **F** for favorites
2. Select rock tile (usually **7**, **8**, or **9**)
3. Use 2x2 brush for thick walls
4. Drag vertically to build up

### Adding Decorations
1. Press **T** to switch to decoration mode
2. Scroll wheel to browse trees/rocks
3. Click to place
4. Right-click to remove mistakes

### Quick Corrections
- **Right-click + drag** to erase multiple tiles
- Brush size affects eraser too!
- No need to switch tools

## 🎨 Pro Tips

### Layer Your Work
1. **Base layer**: Paint all ground first (large brush)
2. **Detail layer**: Add edges and variations (small brush)
3. **Platform layer**: Add floating platforms
4. **Decoration layer**: Trees, rocks, grass

### Use Zoom Strategically
- **Zoomed out (0.5x)**: Plan overall layout
- **Normal (1.0x)**: Place most tiles
- **Zoomed in (2.0x+)**: Fine details and precision work

### Keyboard Shortcuts Memory Aid
```
Navigation:
  Middle Drag = Move around (like Google Maps!)
  R = Reset (when you're lost)
  
Editing:
  B = Brush (bigger = faster)
  T = Toggle mode (tile ↔ decoration)
  
View:
  F = Favorites (speed up selection)
  G = Grid (toggle visibility)
  
File:
  S = Save (do this often!)
  L = Load
```

### Efficient Palette Usage
- **Favorites ON**: Only 9 tiles visible → less scrolling
- **Favorites OFF**: All tiles available
- Use favorites for 90% of your work
- Switch to full list only when needed

## 💡 Time-Saving Techniques

### Technique 1: The Sweep
- Set brush to 3x3
- Start at one edge
- Drag across to fill entire row/column
- 10x faster than clicking individual tiles!

### Technique 2: Stamp and Repeat
- Place one perfect section
- Use small brush to copy pattern
- Great for repeating platforms

### Technique 3: Quick Switch Workflow
```
1. Paint ground (mode: tile, brush: 3x3)
2. Press T → add decorations
3. Press T → back to tiles
4. Press F → use favorites
5. Press 1-9 → instant tile select
```

### Technique 4: The Eraser Sweep
- Made a mistake over large area?
- Right-click + drag with 3x3 brush
- Clears 9 tiles at once!

## 📊 Speed Comparison

| Task | Old Way | New Way | Time Saved |
|------|---------|---------|------------|
| Pan camera | WASD keys | Middle drag | 70% faster |
| Select tile | Scroll palette | Press 1-9 | 90% faster |
| Paint ground | Click each tile | 3x3 brush drag | 80% faster |
| Find common tiles | Search palette | Favorites mode | 85% faster |
| Reset view | Manual zoom/pan | Press R | 95% faster |

## 🎮 Recommended Workflow

### Starting a New Map
1. **Plan**: Zoom out (press -), sketch rough layout
2. **Ground**: Brush 3x3, paint base terrain
3. **Platforms**: Brush 1x1, add floating platforms
4. **Details**: Switch decorations (T), add trees/rocks
5. **Polish**: Zoom in (+), fix edges and gaps
6. **Save**: Press S frequently!

### Editing Existing Map
1. Load map (L)
2. Jump to area (middle-drag pan)
3. Make changes (use appropriate brush)
4. Save (S)

## 🔧 Customization

Want different favorites? Edit this line in `map_editor.py`:
```python
self.favorites = ['tile46', 'tile47', 'tile48', ...]
```

Change brush size range? Modify:
```python
self.brush_size = (self.brush_size % 3) + 1  # Change 3 to max size
```

## ⚠️ Common Mistakes to Avoid

❌ **Don't** click individual tiles for large areas  
✅ **Do** use brush + drag

❌ **Don't** use WASD to pan long distances  
✅ **Do** middle-drag instead

❌ **Don't** scroll through all tiles every time  
✅ **Do** use favorites (F) and number keys (1-9)

❌ **Don't** forget to save  
✅ **Do** press S every few minutes

## 🏆 Master Level Tips

1. **Keep both hands ready**: Left on keyboard (shortcuts), right on mouse
2. **Memorize your 9 favorites**: Muscle memory for 1-9 keys
3. **Use brush size contextually**: Large for filling, small for detail
4. **Pan with middle mouse ALWAYS**: Never go back to WASD for panning
5. **Toggle favorites based on task**: F on for building, F off for variety

---

**Remember**: The goal is to spend more time designing and less time fighting the interface. These shortcuts make the editor invisible so you can focus on creativity! 🎨✨
