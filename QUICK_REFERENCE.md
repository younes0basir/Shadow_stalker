# Quick Reference Guide

## 🚀 Quick Commands

### Play the Game
```bash
python core/game.py
```

### Run Specific Map
```bash
python maps/green_zone_map.py
python maps/map.py
python maps/kenney_level.py
```

### Open Map Editor
```bash
python editor/map_editor.py
```

### View Assets
```bash
python utils/tile_viewer.py
python utils/nature_tile_viewer.py
```

---

## 📂 Where to Find Things

### Want to play? → `core/`
- `game.py` - Main game with menu
- `menu.py` - Menu system

### Want to edit levels? → `editor/`
- `map_editor.py` - Visual map editor

### Want to add enemies? → `ai/`
- `mask_dude_bot.py` - Bot AI system

### Want developer tools? → `utils/`
- Tile viewers, renderers, analyzers

### Want to see all levels? → `maps/`
- 9 different playable maps

### Want game art? → `assets/`
- All images and sprites

---

## 🎯 Common Tasks

### Add a New Level
1. Create file in `maps/your_level.py`
2. Add to `core/game.py` loader
3. (Optional) Add to `core/menu.py`

### Add Enemy AI
1. Use existing `ai/mask_dude_bot.py`
2. Import in your map:
   ```python
   from mask_dude_bot import BotManager
   ```

### Create Custom Map
1. Run `python editor/map_editor.py`
2. Design your level
3. Save as JSON
4. Load in your game

### View Available Tiles
1. Run `python utils/tile_viewer.py`
2. See all tiles with IDs
3. Use IDs when building maps

---

## 📖 Documentation

- **Full Structure**: `PROJECT_STRUCTURE.md`
- **Reorganization**: `REORGANIZATION_COMPLETE.md`
- **Path Fixes**: `PATH_FIX_SUMMARY.md`
- **Folder Details**: Check README in each folder

---

## ⚡ Tips

✅ All paths are relative - move folder anywhere  
✅ Each folder has its own README  
✅ Maps can run standalone or through menu  
✅ Utilities are independent tools  
✅ Editor saves maps as JSON  

---

## 🆘 Troubleshooting

**Import errors?** 
- Make sure you're running from project root
- Check that sys.path is set correctly

**Assets not loading?**
- Verify assets/ folder exists
- Check path uses os.path.join()

**Map won't start?**
- Try running it directly: `python maps/your_map.py`
- Check for syntax errors

---

**Need more help? Check the README in each folder!**
