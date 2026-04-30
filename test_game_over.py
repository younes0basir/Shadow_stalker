#!/usr/bin/env python3
"""Test script for the game over screen."""

import pygame
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.game_over import show_game_over

def test_game_over():
    """Test the game over screen."""
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Game Over Screen Test")
    
    # Test with sample game state
    test_state = {
        "score": 1250,
        "health": 0,
        "max_health": 3,
        "lives": 2
    }
    
    print("Testing game over screen...")
    print("Press SPACE to restart, ESC for menu")
    
    result = show_game_over(screen, test_state)
    print(f"Game Over returned: {result}")
    
    pygame.quit()
    return result

if __name__ == "__main__":
    test_game_over()
