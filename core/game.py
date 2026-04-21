import pygame
import sys
import os
import importlib.util

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from menu import show_menu

def load_module_from_path(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def main():
    pygame.init()
    SCREEN_W, SCREEN_H = 1280, 720
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    pygame.display.set_caption("Dual World Exploration")

    # Show main menu before loading levels
    print("[Game Engine] Showing menu...")
    selected_level = show_menu(screen)
    
    if selected_level == "quit":
        print("[Game Engine] User quit from menu.")
        pygame.quit()
        sys.exit()

    print("[Game Engine] Loading levels...")
    exclusion_demo = load_module_from_path("exclusion_demo", "maps/build_demo_map.py")
    mossy = load_module_from_path("mossy", "maps/map.py")
    kenney = load_module_from_path("kenney", "maps/kenney_level.py")
    exclusion = load_module_from_path("exclusion", "maps/exclusion_level.py")
    adventure = load_module_from_path("adventure", "maps/nature_adventure_map.py")
    green_zone = load_module_from_path("green_zone", "maps/green_zone_map.py")

    # ── Shared game state that persists across levels ──
    game_state = {
        "health": 3,
        "max_health": 3,
        "score": 0,
        "lives": 3,
    }

    current_level = selected_level

    print("[Game Engine] Starting exploration loop...")
    while current_level != "quit":
        # Drain any leftover events so the new level starts clean
        pygame.event.clear()

        if current_level == "kenney":
            print(f"[Game Engine] Entering Sunny Grassland  (HP:{game_state['health']}  Score:{game_state['score']})")
            current_level = kenney.run_level(screen, game_state)

        elif current_level == "exclusion":
            print(f"[Game Engine] Entering Exclusion Zone Industrial  (HP:{game_state['health']}  Score:{game_state['score']})")
            current_level = exclusion.run_level(screen, game_state)

        elif current_level == "exclusion_demo":
            print(f"[Game Engine] Entering Exclusion Zone Classic  (HP:{game_state['health']}  Score:{game_state['score']})")
            current_level = exclusion_demo.run_level(screen, game_state)

        elif current_level == "mossy":
            print(f"[Game Engine] Entering Mossy Forest  (HP:{game_state['health']}  Score:{game_state['score']})")
            current_level = mossy.run_level(screen, game_state)

        elif current_level == "adventure":
            print(f"[Game Engine] Entering Nature Adventure  (HP:{game_state['health']}  Score:{game_state['score']})")
            current_level = adventure.run_level(screen, game_state)

        elif current_level == "green_zone":
            print(f"[Game Engine] Entering Green Zone  (HP:{game_state['health']}  Score:{game_state['score']})")
            current_level = green_zone.run_level(screen, game_state)

        elif current_level == "menu":
            # Return to menu from level
            selected_level = show_menu(screen)
            if selected_level == "quit":
                break
            current_level = selected_level
            continue
        else:
            break

    print("[Game Engine] Shutting down.")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
