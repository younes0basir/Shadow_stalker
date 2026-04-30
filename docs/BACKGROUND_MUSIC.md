# Background Music System

## Overview

Shadow Stalker now features dynamic background music that changes based on game state:
- **Menu Music**: Ambient atmospheric loop in the main menu
- **Gameplay Music**: Retro NES-style chiptune during gameplay
- **Game Over**: Music stops, replaced by voice announcements

## Music Files Used

### Gameplay Music
Located in `assets/FreeSFX/GameSFX/Music/`

| Type | File | Style | Duration |
|------|------|-------|----------|
| **NES Style** (Default) | `Nes Style/Retro Music Loop - PV8 - NES Style 01.wav` | Classic 8-bit Nintendo style | ~30 seconds (loops) |
| **ChipWave** (Alternative) | `ChipWave/Retro Music - ABMU - ChipWave 01.wav` | Modern chiptune/electronic | ~5 minutes (loops) |

### Menu Music
- **Procedurally generated** ambient pad
- 4-second seamless loop
- Low-frequency atmospheric sound
- Created using numpy sine waves

## How It Works

### Music Transitions

```
Main Menu
  ↓ [Start Game]
Stop Menu Music → Start Gameplay Music
  ↓ [Game Over / Return to Menu]
Stop Gameplay Music → Start Menu Music
  ↓ [Restart Game]
Stop Menu Music → Start Gameplay Music
```

### Automatic Music Management

The audio system automatically handles:
1. **Stopping current music** before starting new music
2. **Volume control** (gameplay at 30% for background)
3. **Seamless looping** (music plays continuously)
4. **State tracking** (knows if playing menu or gameplay music)

## Implementation Details

### AudioSystem Updates

**File:** `core/audio.py`

#### New Attribute
```python
self.current_music_type = None  # 'menu' or 'gameplay'
```

#### New Method: `start_gameplay_music()`
```python
def start_gameplay_music(self, music_type='nes'):
    """Start background music during gameplay.
    
    Args:
        music_type: 'nes' for NES-style, 'chipwave' for chipwave
    """
    # Stops current music
    # Loads selected music file
    # Sets volume to 30%
    # Plays in infinite loop
```

#### Updated Method: `stop_music()`
```python
def stop_music(self):
    if self.music_playing:
        self.music.stop()
        self.music_playing = False
        self.current_music_type = None  # Reset type
```

### Game Engine Integration

**File:** `core/game.py`

#### When Starting Game
```python
# After menu selection
audio_sys.stop_music()              # Stop menu music
audio_sys.start_gameplay_music('nes')  # Start gameplay music
```

#### When Returning to Menu
```python
audio_sys.stop_music()      # Stop gameplay music
show_menu(screen)           # Show menu (starts menu music)
audio_sys.start_menu_music() # Ensure menu music playing
```

#### When Game Over
```python
# In game_over.py
audio_sys.play_sound('game_over')  # Play voice
audio_sys.stop_music()             # Stop all music
```

## Usage

### For Players

Music plays automatically:
- **In menu**: Ambient background music
- **During gameplay**: Upbeat NES-style chiptune
- **On game over**: Silence + voice announcement

No action required - it's fully automatic!

### For Developers

#### Start Gameplay Music
```python
from core.audio import audio_sys

# Default (NES style)
audio_sys.start_gameplay_music()

# Or specify style
audio_sys.start_gameplay_music(music_type='nes')
audio_sys.start_gameplay_music(music_type='chipwave')
```

#### Stop All Music
```python
audio_sys.stop_music()
```

#### Check Music State
```python
if audio_sys.music_playing:
    print(f"Music is playing: {audio_sys.current_music_type}")
```

## Customization

### Change Default Music Style

In `core/game.py`, find:
```python
audio_sys.start_gameplay_music(music_type='nes')
```

Change to:
```python
audio_sys.start_gameplay_music(music_type='chipwave')
```

### Adjust Music Volume

In `core/audio.py`, in `start_gameplay_music()`:
```python
self.music.set_volume(0.3)  # Change 0.3 (30%) to desired level
```

Recommended volumes:
- **Background music**: 0.2 - 0.4 (20-40%)
- **Sound effects**: 0.5 - 0.8 (50-80%)
- **Voice announcements**: 0.7 - 1.0 (70-100%)

### Add More Music Options

1. **Add WAV file** to `assets/FreeSFX/GameSFX/Music/YourStyle/`

2. **Update `start_gameplay_music()`** in `core/audio.py`:
```python
elif music_type == 'yourstyle':
    music_path = "assets/FreeSFX/GameSFX/Music/YourStyle/YourMusic.wav"
```

3. **Use it**:
```python
audio_sys.start_gameplay_music(music_type='yourstyle')
```

## Technical Notes

### Music Format Requirements
- **Format**: WAV files
- **Sample Rate**: 44100 Hz (standard)
- **Channels**: Stereo or Mono (both work)
- **Bit Depth**: 16-bit recommended

### Performance
- **Memory**: ~1-5 MB per music track (loaded into RAM)
- **CPU**: Negligible (pygame handles playback efficiently)
- **FPS Impact**: None (hardware-accelerated audio)

### Looping
- Music uses `loops=-1` parameter for infinite looping
- No gap between loops (seamless)
- No fade-out/fade-in needed (handled by pygame)

### Volume Control
- Global volume: Set via `pygame.mixer.music.set_volume()`
- Per-track volume: Set via `sound.set_volume()`
- Range: 0.0 (silent) to 1.0 (full volume)

## Troubleshooting

### Music Not Playing

**Check 1:** Verify file exists
```bash
ls assets/FreeSFX/GameSFX/Music/Nes\ Style/
```

**Check 2:** Check console for errors
```
Warning: Music file not found: ...
Warning: Could not load gameplay music: ...
```

**Check 3:** Verify pygame mixer initialized
```python
print(pygame.mixer.get_init())  # Should not be None
```

### Music Too Loud/Quiet

Adjust volume in `start_gameplay_music()`:
```python
self.music.set_volume(0.5)  # Increase to 50%
```

### Music Doesn't Loop

Ensure `loops=-1` parameter is used:
```python
self.music.play(loops=-1)  # Infinite loop
```

### Wrong Music Playing

Check `current_music_type`:
```python
print(audio_sys.current_music_type)  # 'menu' or 'gameplay'
```

## Future Enhancements

Potential improvements:
1. **Level-specific music** (different tracks per zone)
2. **Dynamic music** (changes based on intensity)
3. **Music settings menu** (volume sliders, toggle on/off)
4. **Crossfade transitions** (smooth music changes)
5. **More music styles** (orchestral, electronic, etc.)
6. **Boss battle music** (intense tracks for challenges)
7. **Victory fanfare** (special music on completion)

## Credits

**Music Sources:**
- FreeSFX Library (`assets/FreeSFX/GameSFX/Music/`)
- NES Style: "Retro Music Loop - PV8 - NES Style 01.wav"
- ChipWave: "Retro Music - ABMU - ChipWave 01.wav"

**Implementation:**
- Pygame mixer for playback
- NumPy for procedural menu music
- Custom AudioSystem class for management

**Integration Date:** April 28, 2026

---

*Background music enhances immersion and makes the game feel more polished and professional.*
