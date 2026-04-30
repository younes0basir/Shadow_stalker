import pygame
import sys
import os
import importlib.util

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from menu import show_menu, COLORS, MenuButton
from database import get_or_create_user, update_high_score, get_high_scores, update_total_score
from quiz import show_quiz

# Import game over screen with error handling
try:
    from game_over import show_game_over
    GAME_OVER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Game over screen not available: {e}")
    GAME_OVER_AVAILABLE = False

def load_module_from_path(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def show_pause_menu(screen):
    """Show a pause overlay with options."""
    overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    font_pause = pygame.font.Font(None, 80)
    title_surf = font_pause.render("PAUSED", True, COLORS['secondary'])
    title_rect = title_surf.get_rect(center=(1280 // 2, 250))
    screen.blit(title_surf, title_rect)
    
    btn_w, btn_h = 240, 50
    center_x = 1280 // 2 - btn_w // 2
    resume_btn = MenuButton(center_x, 350, btn_w, btn_h, "RESUME", font_size=36)
    quit_btn = MenuButton(center_x, 420, btn_w, btn_h, "QUIT RUN", font_size=36)
    
    paused = True
    while paused:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
            
            if resume_btn.is_clicked(event):
                return "resume"
            if quit_btn.is_clicked(event):
                return "quit"
                
        resume_btn.update(mouse_pos, mouse_pressed)
        quit_btn.update(mouse_pos, mouse_pressed)
        
        resume_btn.draw(screen)
        quit_btn.draw(screen)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def show_game_over(screen):
    """Show a dramatic game over screen with effects."""
    overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
    font_large = pygame.font.Font(None, 120)
    font_small = pygame.font.Font(None, 48)
    
    # Flash red effect
    for flash in range(5):
        screen.fill((255, 0, 0) if flash % 2 == 0 else (0, 0, 0))
        pygame.display.flip()
        pygame.time.delay(100)
    
    # Dark red overlay
    screen.fill((40, 0, 0))
    
    # Draw "GAME OVER" text with blood red color
    go_surf = font_large.render("GAME OVER", True, (200, 30, 30))
    go_rect = go_surf.get_rect(center=(1280 // 2, 720 // 2 - 50))
    screen.blit(go_surf, go_rect)
    
    # Subtitle
    sub_surf = font_small.render("The stalker caught you...", True, (150, 50, 50))
    sub_rect = sub_surf.get_rect(center=(1280 // 2, 720 // 2 + 50))
    screen.blit(sub_surf, sub_rect)
    
    pygame.display.flip()
    pygame.time.delay(2000)

def show_transition(screen, text):
    """Show a smooth fade-in/out transition with text."""
    overlay = pygame.Surface((1280, 720))
    font = pygame.font.Font(None, 64)
    
    # Fade In
    for alpha in range(0, 255, 15):
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        
        # Render text
        text_surf = font.render(text, True, COLORS['secondary'])
        text_rect = text_surf.get_rect(center=(1280 // 2, 720 // 2))
        
        # Draw current screen state (already on screen) then overlay
        temp_surf = screen.copy()
        temp_surf.blit(overlay, (0, 0))
        temp_surf.blit(text_surf, text_rect)
        
        screen.blit(temp_surf, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)

    # Stay black for a moment
    pygame.time.delay(500)
    
    # Fade Out
    for alpha in range(255, -1, -15):
        # We need the game engine to render the NEW level here, 
        # but since this is a simple wrapper, we'll just clear to black
        screen.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)

def main():
    pygame.init()
    SCREEN_W, SCREEN_H = 1280, 720
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    pygame.display.set_caption("Dual World Exploration")

    # Show main menu before loading levels
    print("[Game Engine] Showing menu...")
    selected_level, username, game_mode, age_group = show_menu(screen)
    
    # Stop menu music when entering levels
    from audio import audio_sys
    audio_sys.stop_music()
    
    # Start gameplay background music
    audio_sys.start_gameplay_music(music_type='nes')
    
    if selected_level == "quit":
        print("[Game Engine] User quit from menu.")
        pygame.quit()
        sys.exit()

    user_id = get_or_create_user(username)
    print(f"[Game Engine] User logged in: {username} (ID: {user_id})")

    print("[Game Engine] Loading levels...")
    exclusion = load_module_from_path("exclusion", "maps/exclusion_zone_map.py")
    green_zone = load_module_from_path("green_zone", "maps/green_zone_map.py")
    industrial = load_module_from_path("industrial", "maps/industrial_zone_map.py")
    adventure = load_module_from_path("adventure", "maps/nature_adventure_map.py")

    # ── Shared game state that persists across levels ──
    game_state = {
        "health": 3,
        "max_health": 3,
        "score": 0,
        "lives": 3,
    }

    # Define level sequence
    LEVEL_SEQUENCE = ["exclusion", "green_zone", "industrial", "adventure"]
    
    if selected_level not in LEVEL_SEQUENCE and selected_level != "menu":
        # Default to first level if something goes wrong
        current_level = LEVEL_SEQUENCE[0]
    else:
        current_level = selected_level

    # Add global keyboard hook for pause if levels are running
    # This requires levels to cooperate, but since we can't touch maps,
    # we'll handle it in the game engine loop by intercepting the return signals
    # or by wrapping the run_level calls.
    while current_level != "quit":
        # Drain any leftover events so the new level starts clean
        pygame.event.clear()

        # Wrap level execution to handle UI overlays without touching map code
        def run_wrapped_level(level_module, level_id):
            while True:
                signal = level_module.run_level(screen, game_state)
                if signal == "quit":
                    pause_signal = show_pause_menu(screen)
                    if pause_signal == "quit":
                        update_high_score(user_id, level_id, game_state["score"])
                        return "quit"
                    else:
                        # Resume - just loop again
                        continue
                
                # Show quiz in kids mode between levels
                if game_mode == "kids" and signal == "next":
                    show_quiz(screen, age_group)
                    
                return signal

        if current_level == "exclusion":
            show_transition(screen, "Entering Exclusion Zone")
            print(f"[Game Engine] Entering Exclusion Zone  (HP:{game_state['health']}  Score:{game_state['score']})")
            next_level_signal = run_wrapped_level(exclusion, "exclusion")
            if next_level_signal == "quit":
                current_level = "quit"
            elif next_level_signal == "game_over":
                show_game_over(screen)
                # Reset and restart from beginning
                game_state["health"] = game_state["max_health"]
                game_state["score"] = 0
                game_state.pop("bot_x", None)
                game_state.pop("bot_y", None)
                print("[Game Engine] GAME OVER - Restarting from Exclusion Zone")
                current_level = "exclusion"
            else:
                current_level = "green_zone"

        elif current_level == "green_zone":
            show_transition(screen, "Entering Green Zone")
            print(f"[Game Engine] Entering Green Zone  (HP:{game_state['health']}  Score:{game_state['score']})")
            next_level_signal = run_wrapped_level(green_zone, "green_zone")
            if next_level_signal == "quit":
                current_level = "quit"
            elif next_level_signal == "game_over":
                show_game_over(screen)
                # Reset and restart from beginning
                game_state["health"] = game_state["max_health"]
                game_state["score"] = 0
                game_state.pop("bot_x", None)
                game_state.pop("bot_y", None)
                print("[Game Engine] GAME OVER - Restarting from Exclusion Zone")
                current_level = "exclusion"
            else:
                current_level = "industrial"

        elif current_level == "industrial":
            show_transition(screen, "Entering Industrial Zone")
            print(f"[Game Engine] Entering Industrial Zone  (HP:{game_state['health']}  Score:{game_state['score']})")
            next_level_signal = run_wrapped_level(industrial, "industrial")
            if next_level_signal == "quit":
                current_level = "quit"
            elif next_level_signal == "game_over":
                show_game_over(screen)
                # Reset and restart from beginning
                game_state["health"] = game_state["max_health"]
                game_state["score"] = 0
                game_state.pop("bot_x", None)
                game_state.pop("bot_y", None)
                print("[Game Engine] GAME OVER - Restarting from Exclusion Zone")
                current_level = "exclusion"
            else:
                current_level = "adventure"

        elif current_level == "adventure":
            show_transition(screen, "Entering Nature Adventure")
            print(f"[Game Engine] Entering Nature Adventure  (HP:{game_state['health']}  Score:{game_state['score']})")
            
            # Pass game_mode to level state
            game_state["game_mode"] = game_mode
            
            next_level_signal = run_wrapped_level(adventure, "adventure")
            if next_level_signal == "quit":
                current_level = "quit"
            elif next_level_signal == "game_over":
                show_game_over(screen)
                # Reset and restart from beginning
                game_state["health"] = game_state["max_health"]
                game_state["score"] = 0
                game_state.pop("bot_x", None)
                game_state.pop("bot_y", None)
                print("[Game Engine] GAME OVER - Restarting from Exclusion Zone")
                current_level = "exclusion"
            else:
                # Trigger victory screen
                print("[Game Engine] Game Completed! Showing victory screen.")
                # Save final score to database for adventure level
                update_high_score(user_id, "adventure", game_state["score"])
                # Save overall total score for leaderboard
                update_total_score(user_id, game_state["score"])
                
                selected_level, username, game_mode, age_group = show_menu(screen, victory_data=game_state)
                if selected_level == "quit":
                    current_level = "quit"
                else:
                    # Reset game state for replay
                    game_state["health"] = game_state["max_health"]
                    game_state["score"] = 0
                    current_level = selected_level

        elif current_level == "menu":
            # Stop gameplay music when returning to menu
            audio_sys.stop_music()
            
            # Return to menu from level
            selected_level, username, game_mode, age_group = show_menu(screen)
            if selected_level == "quit":
                break
            
            # Restart menu music
            audio_sys.start_menu_music()
            
            current_level = selected_level
            continue
        else:
            break

    print("[Game Engine] Shutting down.")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
