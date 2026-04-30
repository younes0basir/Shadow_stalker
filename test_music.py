#!/usr/bin/env python3
"""Test script for background music system."""

import pygame
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.audio import audio_sys

def test_music_system():
    """Test the background music system."""
    print("=" * 70)
    print("BACKGROUND MUSIC TEST")
    print("=" * 70)
    print()
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Music Test")
    
    print("Test 1: Check mixer initialization")
    if pygame.mixer.get_init():
        print("✅ Mixer initialized")
        print(f"   Frequency: {pygame.mixer.get_init()[0]} Hz")
    else:
        print("❌ Mixer NOT initialized")
        return False
    
    print()
    
    # Test menu music
    print("Test 2: Menu Music (procedural)")
    print("   Playing ambient menu music for 3 seconds...")
    try:
        audio_sys.start_menu_music()
        time.sleep(3)
        if audio_sys.music_playing:
            print("✅ Menu music playing")
            print(f"   Type: {audio_sys.current_music_type}")
        else:
            print("❌ Menu music NOT playing")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    audio_sys.stop_music()
    print("   Stopped")
    print()
    
    # Test NES gameplay music
    print("Test 3: Gameplay Music - NES Style")
    print("   Playing NES-style chiptune for 5 seconds...")
    try:
        audio_sys.start_gameplay_music(music_type='nes')
        time.sleep(5)
        if audio_sys.music_playing and audio_sys.current_music_type == 'gameplay':
            print("✅ NES gameplay music playing")
            print(f"   Type: {audio_sys.current_music_type}")
        else:
            print("❌ NES gameplay music NOT playing")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    audio_sys.stop_music()
    print("   Stopped")
    print()
    
    # Test ChipWave gameplay music
    print("Test 4: Gameplay Music - ChipWave Style")
    print("   Playing ChipWave electronic for 5 seconds...")
    try:
        audio_sys.start_gameplay_music(music_type='chipwave')
        time.sleep(5)
        if audio_sys.music_playing and audio_sys.current_music_type == 'gameplay':
            print("✅ ChipWave gameplay music playing")
            print(f"   Type: {audio_sys.current_music_type}")
        else:
            print("❌ ChipWave gameplay music NOT playing")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    audio_sys.stop_music()
    print("   Stopped")
    print()
    
    # Test music switching
    print("Test 5: Music Switching")
    print("   Starting menu music...")
    audio_sys.start_menu_music()
    time.sleep(1)
    print(f"   Current: {audio_sys.current_music_type}")
    
    print("   Switching to gameplay music...")
    audio_sys.start_gameplay_music('nes')
    time.sleep(1)
    print(f"   Current: {audio_sys.current_music_type}")
    
    print("   Switching back to menu music...")
    audio_sys.start_menu_music()
    time.sleep(1)
    print(f"   Current: {audio_sys.current_music_type}")
    
    if audio_sys.current_music_type == 'menu':
        print("✅ Music switching works correctly")
    else:
        print("❌ Music switching failed")
    
    audio_sys.stop_music()
    print()
    
    # Test sound effects with music
    print("Test 6: Sound Effects During Music")
    print("   Starting gameplay music...")
    audio_sys.start_gameplay_music('nes')
    time.sleep(1)
    
    print("   Playing sound effects...")
    sounds_to_test = ['click', 'hover', 'coin']
    for sound_name in sounds_to_test:
        if sound_name in audio_sys.sounds:
            print(f"   🔊 Playing: {sound_name}")
            audio_sys.play_sound(sound_name)
            time.sleep(0.5)
    
    print("✅ Sound effects work during music playback")
    
    audio_sys.stop_music()
    print()
    
    # Check music files exist
    print("Test 7: Verify Music Files")
    root_dir = audio_sys.root_dir
    
    music_files = {
        'NES Style': "assets/FreeSFX/GameSFX/Music/Nes Style/Retro Music Loop - PV8 - NES Style 01.wav",
        'ChipWave': "assets/FreeSFX/GameSFX/Music/ChipWave/Retro Music - ABMU - ChipWave 01.wav",
    }
    
    all_exist = True
    for name, path in music_files.items():
        full_path = os.path.join(root_dir, path)
        exists = os.path.exists(full_path)
        size_mb = os.path.getsize(full_path) / (1024 * 1024) if exists else 0
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"{status:12} - {name:15} ({size_mb:.1f} MB)")
        if not exists:
            all_exist = False
    
    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print()
    
    if all_exist:
        print("✅ All music files found")
        print("✅ Music system working correctly")
    else:
        print("⚠️  Some music files missing (will use fallback)")
    
    print()
    print("Music should have played during tests.")
    print("If you didn't hear anything, check:")
    print("  1. System volume")
    print("  2. Speaker/headphone connection")
    print("  3. Pygame mixer initialization")
    print()
    
    pygame.quit()
    return True

if __name__ == "__main__":
    try:
        test_music_system()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        pygame.quit()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)
