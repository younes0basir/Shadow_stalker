#!/usr/bin/env python3
"""Test script to verify FreeSFX audio files are loading correctly."""

import pygame
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.audio import audio_sys

def test_audio_loading():
    """Test that all audio files load correctly."""
    print("=" * 60)
    print("AUDIO SYSTEM TEST - FreeSFX Integration")
    print("=" * 60)
    print()
    
    # Check if mixer is initialized
    if not pygame.mixer.get_init():
        print("❌ ERROR: Pygame mixer not initialized!")
        return False
    
    print("✅ Pygame mixer initialized successfully")
    print(f"   Frequency: {pygame.mixer.get_init()[0]} Hz")
    print(f"   Format: {pygame.mixer.get_init()[1]}")
    print(f"   Channels: {pygame.mixer.get_init()[2]}")
    print()
    
    # List all loaded sounds
    print("Loaded Sounds:")
    print("-" * 60)
    
    expected_sounds = [
        'hover', 'click', 'back', 
        'game_over', 'death', 'victory',
        'jump', 'coin', 'powerup', 'explosion'
    ]
    
    all_loaded = True
    for sound_name in expected_sounds:
        if sound_name in audio_sys.sounds:
            sound = audio_sys.sounds[sound_name]
            duration = sound.get_length() if hasattr(sound, 'get_length') else 'N/A'
            print(f"✅ {sound_name:15} - Loaded ({duration:.2f}s)" if isinstance(duration, float) else f"✅ {sound_name:15} - Loaded")
        else:
            print(f"❌ {sound_name:15} - NOT LOADED")
            all_loaded = False
    
    print()
    print("-" * 60)
    
    if all_loaded:
        print("✅ All sounds loaded successfully!")
    else:
        print("⚠️  Some sounds failed to load (using fallbacks)")
    
    print()
    
    # Test playing each sound
    print("Testing Sound Playback:")
    print("-" * 60)
    print("Playing each sound for 0.5 seconds...")
    print()
    
    for sound_name in ['hover', 'click', 'game_over', 'death']:
        if sound_name in audio_sys.sounds:
            print(f"🔊 Playing: {sound_name}")
            try:
                audio_sys.play_sound(sound_name)
                pygame.time.wait(600)  # Wait 600ms between sounds
                print(f"   ✅ Played successfully")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print()
    print("-" * 60)
    print()
    
    # Show file paths
    print("Sound File Locations:")
    print("-" * 60)
    root_dir = audio_sys.root_dir
    sfx_files = {
        'game_over': "assets/FreeSFX/Voices/Game Over.wav",
        'death': "assets/FreeSFX/GameSFX/Impact/Retro Impact Punch Hurt 01.wav",
        'click': "assets/FreeSFX/GameSFX/Events/Retro Event UI StereoUP 01.wav",
        'hover': "assets/FreeSFX/GameSFX/Events/Retro Event UI 01.wav",
    }
    
    for name, path in sfx_files.items():
        full_path = os.path.join(root_dir, path)
        exists = os.path.exists(full_path)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"{status:12} - {path}")
    
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    return all_loaded

if __name__ == "__main__":
    try:
        success = test_audio_loading()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
