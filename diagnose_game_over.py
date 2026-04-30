#!/usr/bin/env python3
"""Diagnostic script to test game over functionality."""

import pygame
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

print("=" * 70)
print("GAME OVER DIAGNOSTIC TEST")
print("=" * 70)
print()

# Test 1: Check if game_over module can be imported
print("Test 1: Importing game_over module...")
try:
    from core.game_over import show_game_over, GameOverScreen
    print("✅ SUCCESS: game_over module imported")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 2: Check if audio system works
print("Test 2: Checking audio system...")
try:
    from core.audio import audio_sys
    print(f"✅ Audio system loaded with {len(audio_sys.sounds)} sounds")
    print(f"   Available sounds: {list(audio_sys.sounds.keys())}")
    
    # Check if game_over sound exists
    if 'game_over' in audio_sys.sounds:
        print("✅ 'game_over' sound available")
    else:
        print("⚠️  WARNING: 'game_over' sound NOT available")
        
    if 'death' in audio_sys.sounds:
        print("✅ 'death' sound available")
    else:
        print("⚠️  WARNING: 'death' sound NOT available")
        
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Initialize pygame and create screen
print("Test 3: Initializing Pygame...")
try:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Game Over Test")
    print("✅ Pygame initialized successfully")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Try to create GameOverScreen instance
print("Test 4: Creating GameOverScreen instance...")
try:
    test_state = {"score": 100, "health": 0}
    go_screen = GameOverScreen(screen, test_state)
    print("✅ GameOverScreen created successfully")
    print(f"   Screen size: {go_screen.screen_w}x{go_screen.screen_h}")
    print(f"   Buttons created: Restart={go_screen.restart_btn is not None}, Menu={go_screen.menu_btn is not None}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

print()

# Test 5: Run the game over screen
print("Test 5: Running game over screen (5 second test)...")
print("   The screen will show for 5 seconds, then close automatically.")
print("   Press SPACE to restart or ESC for menu before timeout.")
print()

try:
    import time
    start_time = time.time()
    
    # Run for max 5 seconds
    result = None
    running = True
    clock = pygame.time.Clock()
    
    while running and (time.time() - start_time) < 5.0:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    result = "restart"
                    running = False
                    print("   → User pressed SPACE (restart)")
                elif event.key == pygame.K_ESCAPE:
                    result = "menu"
                    running = False
                    print("   → User pressed ESC (menu)")
        
        # Update and draw
        go_screen.run()  # This will handle its own loop
        
    if result:
        print(f"✅ Game over screen returned: '{result}'")
    else:
        print("✅ Test completed (timeout after 5 seconds)")
        
except Exception as e:
    print(f"❌ FAILED during execution: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print()
print("If all tests passed, the game over system should work correctly.")
print("If the game still closes when caught, check:")
print("  1. Console output for error messages")
print("  2. That you're running via core/game.py (not individual maps)")
print("  3. That all dependencies are installed (pygame, numpy)")
print()

pygame.quit()
