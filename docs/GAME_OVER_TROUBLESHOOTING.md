# Game Over Troubleshooting Guide

## Problem: Game Closes When Bot Catches You

If the game window closes immediately when the bot catches you instead of showing the game over screen with retry/menu options, follow these steps:

---

## Quick Fixes

### 1. Run the Diagnostic Script

First, run the diagnostic to identify the issue:

```bash
python diagnose_game_over.py
```

This will test:
- ✅ Module imports
- ✅ Audio system
- ✅ Pygame initialization
- ✅ Game over screen creation
- ✅ Screen execution

**Check the output for any ❌ FAILED messages.**

---

### 2. Verify You're Running the Correct File

**❌ WRONG - Don't run individual maps:**
```bash
python maps/green_zone_map.py     # This won't show game over UI
python maps/exclusion_zone_map.py # This won't show game over UI
```

**✅ CORRECT - Run the main game engine:**
```bash
python core/game.py               # This has game over UI support
```

The game over screen is integrated into `core/game.py`, not the individual map files.

---

## Common Issues & Solutions

### Issue 1: Missing Dependencies

**Symptoms:** Import errors in console

**Solution:** Install required packages
```bash
pip install pygame numpy
```

---

### Issue 2: Audio Files Missing

**Symptoms:** Warnings about missing sound files

**Solution:** The system has fallback sounds, but to get full audio:
1. Verify `assets/FreeSFX/` folder exists
2. Check that WAV files are present
3. Run `python test_audio.py` to verify

**Note:** Missing audio won't prevent game over from working - it will use fallback beeps.

---

### Issue 3: Import Errors

**Symptoms:** 
```
ModuleNotFoundError: No module named 'game_over'
ImportError: cannot import name 'show_game_over'
```

**Solution:**
1. Verify `core/game_over.py` exists
2. Check file permissions (readable)
3. Ensure you're running from project root directory

---

### Issue 4: Pygame Not Initialized

**Symptoms:**
```
pygame.error: display not initialized
pygame.error: mixer not initialized
```

**Solution:**
The game engine initializes pygame automatically. Make sure you're running:
```bash
python core/game.py
```

---

### Issue 5: Python Version Issues

**Symptoms:** Syntax errors or import failures

**Solution:**
- Requires Python 3.8 or higher
- Check version: `python --version`
- If using Windows, try `py -3 core/game.py`

---

## Step-by-Step Debugging

### Step 1: Check Console Output

When the bot catches you, look at the terminal/console for messages:

**Good signs:**
```
[Game Engine] GAME OVER - Restarting from Exclusion Zone
```

**Bad signs:**
```
Traceback (most recent call last):
  File "core/game.py", line XXX, in ...
Error: ...
```

If you see errors, copy them and check the solutions below.

---

### Step 2: Test Game Over Screen Directly

Run the standalone test:
```bash
python test_game_over.py
```

This should show the game over screen immediately. If this works but the game doesn't show it when caught, the issue is in the integration.

---

### Step 3: Check Error Handling

The updated code now has error handling. If the game over screen fails, it should:
1. Print an error message to console
2. Fall back to simple restart (no UI)

Look for messages like:
```
Warning: Game over screen not available: ...
Error showing game over screen: ...
```

---

### Step 4: Verify File Structure

Make sure these files exist:
```
Shadow_stalker/
├── core/
│   ├── game.py              ← Main game engine
│   ├── game_over.py         ← Game over screen
│   ├── audio.py             ← Sound system
│   └── menu.py              ← Menu buttons
├── assets/
│   └── FreeSFX/             ← Sound files
└── maps/
    ├── green_zone_map.py    ← Returns "game_over"
    ├── exclusion_zone_map.py
    └── ...
```

---

## Emergency Fallback

If the game over screen still doesn't work, the game will fall back to automatic restart. To force this:

1. Open `core/game.py`
2. Find the game over handlers
3. They should automatically use fallback if `GAME_OVER_AVAILABLE = False`

The game will still restart, just without the fancy UI.

---

## What Should Happen

### Correct Behavior:

1. **Bot catches player**
   ↓
2. **Level returns `"game_over"` signal**
   ↓
3. **Game engine receives signal**
   ↓
4. **Game over screen appears with:**
   - Dark overlay
   - "GAME OVER" title
   - Death message
   - Score display
   - Particles and effects
   - Two buttons: [RESTART] [MAIN MENU]
   ↓
5. **Player chooses:**
   - Click RESTART or press SPACE → Game restarts
   - Click MAIN MENU or press ESC → Returns to menu

---

## Still Not Working?

### Collect Information:

1. **Run diagnostic:**
   ```bash
   python diagnose_game_over.py > diagnostic_output.txt
   ```

2. **Run game and catch error:**
   ```bash
   python core/game.py 2>&1 | tee game_output.txt
   ```

3. **Check both files for errors**

### Common Error Messages:

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing file | Verify file exists |
| `pygame.error` | Not initialized | Run via core/game.py |
| `FileNotFoundError` | Missing assets | Check assets folder |
| `ImportError` | Wrong Python path | Run from project root |
| `AttributeError` | Version mismatch | Update pygame |

---

## Manual Test

To manually verify the game over flow works:

1. Start the game: `python core/game.py`
2. Play until bot catches you OR intentionally walk into bot
3. Watch console for: `[Game Engine] GAME OVER`
4. Game over screen should appear
5. Try both buttons (Restart and Menu)

---

## Code Verification

Check that `core/game.py` has this import at the top:

```python
# Import game over screen with error handling
try:
    from game_over import show_game_over
    GAME_OVER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Game over screen not available: {e}")
    GAME_OVER_AVAILABLE = False
```

And the handler looks like:

```python
elif next_level_signal == "game_over":
    if GAME_OVER_AVAILABLE:
        try:
            result = show_game_over(screen, game_state)
            if result == "restart":
                # Reset game
                ...
            else:
                current_level = "menu"
        except Exception as e:
            print(f"Error: {e}")
            current_level = "menu"
    else:
        # Fallback restart
        ...
```

---

## Quick Checklist

- [ ] Running `python core/game.py` (not individual maps)
- [ ] Python 3.8+ installed
- [ ] Pygame and numpy installed
- [ ] `core/game_over.py` file exists
- [ ] `diagnose_game_over.py` passes all tests
- [ ] Console shows no import errors
- [ ] Game window stays open when caught

---

## Need More Help?

If none of this works:

1. Run `python diagnose_game_over.py` and save output
2. Run the game, get caught, save console output
3. Check what Python version: `python --version`
4. List installed packages: `pip list`
5. Share the error messages for further assistance

---

**Last Updated:** April 28, 2026  
**Status:** Error handling added, fallback system in place
