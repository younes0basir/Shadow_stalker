import pygame
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from menu import COLORS, MenuButton
from audio import audio_sys

class Particle:
    """Simple particle effect for visual flair."""
    def __init__(self, x, y, color, velocity, lifetime=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.age = 0.0
        self.size = 3
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        return self.age < self.lifetime
        
    def draw(self, surface):
        if self.age >= self.lifetime:
            return
        alpha = int(255 * (1 - self.age / self.lifetime))
        size = max(1, int(self.size * (1 - self.age / self.lifetime)))
        
        # Create a surface with alpha for the particle
        particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*self.color, alpha), (size, size), size)
        surface.blit(particle_surf, (int(self.x - size), int(self.y - size)))


class GameOverScreen:
    """Game over screen with animations and effects."""
    def __init__(self, screen, game_state=None):
        self.screen = screen
        self.game_state = game_state or {"score": 0, "health": 0}
        self.clock = pygame.time.Clock()
        
        # Screen dimensions
        self.screen_w = screen.get_width()
        self.screen_h = screen.get_height()
        
        # Fonts
        self.font_title = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        # Animation state
        self.fade_alpha = 0
        self.shake_offset = [0, 0]
        self.shake_duration = 0.5
        self.shake_timer = 0.0
        
        # Particles
        self.particles = []
        self.particle_timer = 0.0
        
        # Buttons
        center_x = self.screen_w // 2
        button_y_start = self.screen_h // 2 + 80
        button_width = 280
        button_height = 55
        
        self.restart_btn = MenuButton(
            center_x - button_width - 10, 
            button_y_start, 
            button_width, 
            button_height, 
            "RESTART", 
            font_size=36
        )
        self.menu_btn = MenuButton(
            center_x + 10, 
            button_y_start, 
            button_width, 
            button_height, 
            "MAIN MENU", 
            font_size=36
        )
        
        # Timing
        self.display_time = 0.0
        self.can_skip = False
        
    def spawn_particles(self, count=20):
        """Spawn explosion particles at center of screen."""
        center_x = self.screen_w // 2
        center_y = self.screen_h // 2 - 50
        
        for _ in range(count):
            angle = pygame.math.Vector2(1, 0).rotate(pygame.random.uniform(0, 360))
            speed = pygame.random.uniform(50, 200)
            velocity = (angle.x * speed, angle.y * speed)
            
            color_choice = pygame.random.choice([
                (255, 50, 50),    # Red
                (255, 100, 50),   # Orange
                (255, 150, 100),  # Light orange
                (200, 50, 50),    # Dark red
            ])
            
            lifetime = pygame.random.uniform(0.5, 1.5)
            particle = Particle(center_x, center_y, color_choice, velocity, lifetime)
            self.particles.append(particle)
            
    def update_shake(self, dt):
        """Update screen shake effect."""
        if self.shake_timer > 0:
            self.shake_timer -= dt
            intensity = 10 * (self.shake_timer / self.shake_duration)
            self.shake_offset[0] = pygame.random.uniform(-intensity, intensity)
            self.shake_offset[1] = pygame.random.uniform(-intensity, intensity)
        else:
            self.shake_offset = [0, 0]
            
    def run(self):
        """Run the game over screen. Returns 'restart' or 'menu'."""
        audio_sys.play_sound('game_over')
        audio_sys.stop_music()
        
        # Initial effects
        self.spawn_particles(50)
        self.shake_timer = self.shake_duration
        
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            self.display_time += dt
            
            # Allow skipping after 1 second
            if self.display_time > 1.0:
                self.can_skip = True
                
            # Fade in
            if self.fade_alpha < 255 and self.display_time < 0.5:
                self.fade_alpha = min(255, int(self.display_time * 510))
                
            # Update effects
            self.update_shake(dt)
            
            # Update particles
            self.particle_timer += dt
            if self.particle_timer > 0.1:  # Spawn particles periodically
                self.spawn_particles(5)
                self.particle_timer = 0.0
                
            self.particles = [p for p in self.particles if p.update(dt)]
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                    
                if event.type == pygame.KEYDOWN:
                    if self.can_skip:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            return "restart"
                        elif event.key == pygame.K_ESCAPE:
                            return "menu"
                            
                # Button clicks
                if self.can_skip:
                    if self.restart_btn.is_clicked(event):
                        audio_sys.play_sound('click')
                        return "restart"
                    if self.menu_btn.is_clicked(event):
                        audio_sys.play_sound('back')
                        return "menu"
                        
            # Update buttons
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            
            if self.can_skip:
                self.restart_btn.update(mouse_pos, mouse_pressed)
                self.menu_btn.update(mouse_pos, mouse_pressed)
                
            # Draw everything
            self.draw()
            pygame.display.flip()
            
        return "menu"
        
    def draw(self):
        """Draw the game over screen."""
        # Apply shake offset
        shake_x, shake_y = self.shake_offset
        
        # Dark overlay with fade
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.fade_alpha))
        self.screen.blit(overlay, (shake_x, shake_y))
        
        # Only show full UI after fade-in
        if self.fade_alpha > 200:
            # Title with glow effect
            title_text = "GAME OVER"
            
            # Multiple layers for glow
            for i in range(3, 0, -1):
                glow_surf = self.font_title.render(title_text, True, (255, 0, 0))
                glow_surf.set_alpha(50 // i)
                glow_rect = glow_surf.get_rect(
                    center=(self.screen_w // 2 + shake_x, self.screen_h // 2 - 100 + shake_y)
                )
                glow_rect.inflate_ip(i * 10, i * 10)
                self.screen.blit(glow_surf, glow_rect)
            
            # Main title
            title_surf = self.font_title.render(title_text, True, (255, 50, 50))
            title_rect = title_surf.get_rect(
                center=(self.screen_w // 2 + shake_x, self.screen_h // 2 - 100 + shake_y)
            )
            self.screen.blit(title_surf, title_rect)
            
            # Death message
            death_msg = "You were caught by the Shadow Stalker!"
            death_surf = self.font_medium.render(death_msg, True, COLORS['text'])
            death_rect = death_surf.get_rect(
                center=(self.screen_w // 2 + shake_x, self.screen_h // 2 - 30 + shake_y)
            )
            self.screen.blit(death_surf, death_rect)
            
            # Score display
            score_text = f"Final Score: {self.game_state.get('score', 0)}"
            score_surf = self.font_large.render(score_text, True, COLORS['secondary'])
            score_rect = score_surf.get_rect(
                center=(self.screen_w // 2 + shake_x, self.screen_h // 2 + 20 + shake_y)
            )
            self.screen.blit(score_surf, score_rect)
            
            # Draw particles
            for particle in self.particles:
                particle.draw(self.screen)
            
            # Draw buttons (only when can skip)
            if self.can_skip:
                # Add semi-transparent panel behind buttons
                btn_panel = pygame.Surface((600, 100), pygame.SRCALPHA)
                btn_panel.fill((0, 0, 0, 100))
                panel_rect = btn_panel.get_rect(
                    center=(self.screen_w // 2, self.screen_h // 2 + 110)
                )
                self.screen.blit(btn_panel, panel_rect)
                
                self.restart_btn.draw(self.screen)
                self.menu_btn.draw(self.screen)
                
                # Instructions
                if not self.can_skip or self.display_time < 2.0:
                    instr_text = "Press SPACE to restart or ESC for menu"
                    instr_surf = self.font_small.render(instr_text, True, COLORS['text_dim'])
                    instr_rect = instr_surf.get_rect(
                        center=(self.screen_w // 2 + shake_x, self.screen_h - 50 + shake_y)
                    )
                    self.screen.blit(instr_surf, instr_rect)


def show_game_over(screen, game_state=None):
    """Entry point to show game over screen."""
    game_over = GameOverScreen(screen, game_state)
    return game_over.run()


if __name__ == "__main__":
    # Test the game over screen standalone
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Game Over Screen Test")
    
    test_state = {"score": 1250, "health": 0}
    result = show_game_over(screen, test_state)
    print(f"Game Over returned: {result}")
    pygame.quit()
