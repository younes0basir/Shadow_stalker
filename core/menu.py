import pygame
import sys
import os

# Menu Constants
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60

# Colors - Pixel art palette
COLORS = {
    'bg_dark': (25, 28, 38),
    'bg_light': (45, 50, 65),
    'primary': (99, 199, 77),      # Green
    'primary_dark': (67, 138, 54),
    'secondary': (255, 198, 93),   # Yellow/Gold
    'secondary_dark': (207, 152, 56),
    'accent': (255, 107, 107),     # Red/Coral
    'text': (240, 240, 240),
    'text_dim': (160, 160, 170),
    'border': (80, 85, 100),
    'shadow': (15, 18, 25),
}

class MenuButton:
    """Pixel-art styled menu button with hover and click effects."""
    def __init__(self, x, y, width, height, text, icon=None, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.hovered = False
        self.clicked = False
        self.font = pygame.font.Font(None, font_size)
        self.anim_offset = 0
        
    def draw(self, surface):
        # Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(surface, COLORS['shadow'], shadow_rect, border_radius=0)
        
        # Main button body - pixel style
        color = COLORS['secondary'] if self.hovered else COLORS['primary']
        dark_color = COLORS['secondary_dark'] if self.hovered else COLORS['primary_dark']
        
        # Button face
        face_rect = self.rect.copy()
        if self.clicked:
            face_rect.move_ip(2, 2)
        pygame.draw.rect(surface, color, face_rect, border_radius=0)
        
        # Button border (pixel style - 3px)
        border_rect = face_rect.inflate(-6, -6)
        pygame.draw.rect(surface, dark_color, border_rect, width=3, border_radius=0)
        
        # Inner highlight
        highlight_rect = border_rect.inflate(-4, -4)
        pygame.draw.rect(surface, color, highlight_rect, border_radius=0)
        
        # Text
        text_surf = self.font.render(self.text, True, COLORS['text'])
        text_rect = text_surf.get_rect(center=face_rect.center)
        if self.clicked:
            text_rect.move_ip(2, 2)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos, mouse_pressed):
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.clicked = self.hovered and mouse_pressed[0]
        return self.clicked
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

class LevelCard:
    """Level selection card with preview and info."""
    def __init__(self, x, y, level_id, name, description, color_key):
        self.rect = pygame.Rect(x, y, 280, 200)
        self.level_id = level_id
        self.name = name
        self.description = description
        self.color_key = color_key
        self.hovered = False
        self.selected = False
        
        # Load background preview
        self.preview = None
        bg_path = f"assets/Background/{color_key}.png"
        if os.path.exists(bg_path):
            self.preview = pygame.image.load(bg_path).convert()
            self.preview = pygame.transform.scale(self.preview, (260, 120))
            
    def draw(self, surface, font_title, font_desc):
        # Card shadow
        shadow_rect = self.rect.copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(surface, COLORS['shadow'], shadow_rect, border_radius=0)
        
        # Card body
        color = COLORS['secondary'] if self.hovered or self.selected else COLORS['bg_light']
        pygame.draw.rect(surface, color, self.rect, border_radius=0)
        
        # Inner area
        inner_rect = self.rect.inflate(-8, -8)
        pygame.draw.rect(surface, COLORS['bg_dark'], inner_rect, border_radius=0)
        
        # Preview image
        preview_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, 260, 120)
        if self.preview:
            surface.blit(self.preview, preview_rect.topleft)
        else:
            pygame.draw.rect(surface, COLORS['border'], preview_rect, border_radius=0)
            
        # Selection indicator
        if self.selected:
            pygame.draw.rect(surface, COLORS['secondary'], self.rect, width=4, border_radius=0)
            # Corner brackets for selection
            bracket_len = 15
            bracket_color = COLORS['secondary']
            corners = [
                (self.rect.left, self.rect.top),
                (self.rect.right, self.rect.top),
                (self.rect.left, self.rect.bottom),
                (self.rect.right, self.rect.bottom),
            ]
            for i, (cx, cy) in enumerate(corners):
                offsets = [
                    (bracket_len if i % 2 == 0 else -bracket_len, 0),
                    (0, bracket_len if i < 2 else -bracket_len),
                ]
                for dx, dy in offsets:
                    pygame.draw.line(surface, bracket_color, (cx, cy), (cx + dx, cy + dy), 3)
        
        # Title
        title_surf = font_title.render(self.name, True, COLORS['text'])
        surface.blit(title_surf, (self.rect.x + 10, self.rect.y + 135))
        
        # Description (truncated)
        desc_surf = font_desc.render(self.description[:35] + "..." if len(self.description) > 35 else self.description, 
                                      True, COLORS['text_dim'])
        surface.blit(desc_surf, (self.rect.x + 10, self.rect.y + 165))
        
    def update(self, mouse_pos, mouse_pressed):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered and mouse_pressed[0]
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

class GameMenu:
    """Main menu system with multiple screens."""
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = "main"  # main, levels, controls, credits
        self.selected_level = None
        
        # Fonts
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 48)
        self.font_button = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        
        # Load background
        self.bg_pattern = self._create_bg_pattern()
        
        # Initialize screens
        self._init_main_screen()
        self._init_level_screen()
        self._init_controls_screen()
        
    def _create_bg_pattern(self):
        """Create a pixelated background pattern."""
        pattern = pygame.Surface((SCREEN_W, SCREEN_H))
        pattern.fill(COLORS['bg_dark'])
        
        # Add pixel noise pattern
        for y in range(0, SCREEN_H, 40):
            for x in range(0, SCREEN_W, 40):
                if (x // 40 + y // 40) % 3 == 0:
                    pygame.draw.rect(pattern, COLORS['bg_light'], (x, y, 40, 40))
                    
        # Add gradient overlay
        for y in range(SCREEN_H):
            alpha = int(50 * (y / SCREEN_H))
            pygame.draw.line(pattern, (0, 0, 0, alpha), (0, y), (SCREEN_W, y))
            
        return pattern
        
    def _init_main_screen(self):
        """Initialize main menu buttons."""
        center_x = SCREEN_W // 2 - 150
        start_y = 280
        button_width = 300
        button_height = 60
        spacing = 20
        
        self.main_buttons = [
            MenuButton(center_x, start_y, button_width, button_height, "PLAY", font_size=40),
            MenuButton(center_x, start_y + button_height + spacing, button_width, button_height, "LEVELS", font_size=40),
            MenuButton(center_x, start_y + (button_height + spacing) * 2, button_width, button_height, "CONTROLS", font_size=40),
            MenuButton(center_x, start_y + (button_height + spacing) * 3, button_width, button_height, "QUIT", font_size=40),
        ]
        
    def _init_level_screen(self):
        """Initialize level selection cards."""
        self.level_cards = [
            LevelCard(60, 180, "kenney", "Sunny Grassland", "A bright, cheerful world with green hills", "Green"),
            LevelCard(350, 180, "exclusion", "Exclusion Zone", "Industrial wasteland with hazards", "Gray"),
            LevelCard(640, 180, "mossy", "Mossy Forest", "Ancient forest with mysterious ruins", "Green"),
            LevelCard(930, 180, "exclusion_demo", "Classic Zone", "Original exclusion zone demo", "Brown"),
            LevelCard(495, 400, "adventure", "Dungeon Adventure", "8-stage dungeon with treasures & boss", "Pink"),
        ]
        self.back_button = MenuButton(50, 50, 120, 45, "BACK", font_size=32)
        self.play_selected_button = MenuButton(SCREEN_W // 2 - 150, 660, 300, 50, "START LEVEL", font_size=36)
        
    def _init_controls_screen(self):
        """Initialize controls screen."""
        self.controls_back = MenuButton(50, 50, 120, 45, "BACK", font_size=32)
        
    def run(self):
        """Main menu loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_screen == "main":
                            return "quit"
                        else:
                            self.current_screen = "main"
                            
                self._handle_event(event)
                
            # Update
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            self._update(mouse_pos, mouse_pressed)
            
            # Draw
            self._draw()
            pygame.display.flip()
            
        return self.selected_level if self.selected_level else "quit"
        
    def _handle_event(self, event):
        """Handle input events based on current screen."""
        if self.current_screen == "main":
            for i, btn in enumerate(self.main_buttons):
                if btn.is_clicked(event):
                    if i == 0:  # PLAY - go to level select with default
                        self.selected_level = "kenney"
                        self.running = False
                    elif i == 1:  # LEVELS
                        self.current_screen = "levels"
                    elif i == 2:  # CONTROLS
                        self.current_screen = "controls"
                    elif i == 3:  # QUIT
                        self.selected_level = "quit"
                        self.running = False
                        
        elif self.current_screen == "levels":
            if self.back_button.is_clicked(event):
                self.current_screen = "main"
                
            for card in self.level_cards:
                if card.is_clicked(event):
                    for c in self.level_cards:
                        c.selected = False
                    card.selected = True
                    self.selected_level = card.level_id
                    
            if self.play_selected_button.is_clicked(event) and self.selected_level:
                self.running = False
                
        elif self.current_screen == "controls":
            if self.controls_back.is_clicked(event):
                self.current_screen = "main"
                
    def _update(self, mouse_pos, mouse_pressed):
        """Update UI elements."""
        if self.current_screen == "main":
            for btn in self.main_buttons:
                btn.update(mouse_pos, mouse_pressed)
                
        elif self.current_screen == "levels":
            self.back_button.update(mouse_pos, mouse_pressed)
            for card in self.level_cards:
                card.update(mouse_pos, mouse_pressed)
            if self.selected_level:
                self.play_selected_button.update(mouse_pos, mouse_pressed)
                
        elif self.current_screen == "controls":
            self.controls_back.update(mouse_pos, mouse_pressed)
            
    def _draw(self):
        """Render current screen."""
        # Background
        self.screen.blit(self.bg_pattern, (0, 0))
        
        if self.current_screen == "main":
            self._draw_main()
        elif self.current_screen == "levels":
            self._draw_levels()
        elif self.current_screen == "controls":
            self._draw_controls()
            
    def _draw_main(self):
        """Draw main menu."""
        # Title with shadow effect
        title_text = "PIXEL ADVENTURE"
        shadow_surf = self.font_title.render(title_text, True, COLORS['shadow'])
        title_surf = self.font_title.render(title_text, True, COLORS['secondary'])
        
        title_rect = title_surf.get_rect(center=(SCREEN_W // 2, 120))
        self.screen.blit(shadow_surf, title_rect.move(4, 4))
        self.screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_surf = self.font_subtitle.render("Dual World Exploration", True, COLORS['text_dim'])
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_W // 2, 180))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
        # Decorative pixel line
        pygame.draw.rect(self.screen, COLORS['primary'], (SCREEN_W // 2 - 200, 210, 400, 4))
        pygame.draw.rect(self.screen, COLORS['secondary'], (SCREEN_W // 2 - 100, 218, 200, 4))
        
        # Buttons
        for btn in self.main_buttons:
            btn.draw(self.screen)
            
        # Version info
        version_surf = self.font_small.render("v1.0 - Kenney Assets Edition", True, COLORS['text_dim'])
        self.screen.blit(version_surf, (20, SCREEN_H - 40))
        
    def _draw_levels(self):
        """Draw level selection screen."""
        # Title
        title_surf = self.font_title.render("SELECT LEVEL", True, COLORS['secondary'])
        title_rect = title_surf.get_rect(center=(SCREEN_W // 2, 80))
        self.screen.blit(title_surf, title_rect)
        
        # Back button
        self.back_button.draw(self.screen)
        
        # Level cards
        for card in self.level_cards:
            card.draw(self.screen, self.font_subtitle, self.font_small)
            
        # Start button (only if level selected)
        if self.selected_level:
            self.play_selected_button.draw(self.screen)
            
        # Instructions
        inst_surf = self.font_small.render("Click a level to select, then click START LEVEL", True, COLORS['text_dim'])
        inst_rect = inst_surf.get_rect(center=(SCREEN_W // 2, 620))
        self.screen.blit(inst_surf, inst_rect)
        
    def _draw_controls(self):
        """Draw controls/instructions screen."""
        # Title
        title_surf = self.font_title.render("CONTROLS", True, COLORS['secondary'])
        title_rect = title_surf.get_rect(center=(SCREEN_W // 2, 80))
        self.screen.blit(title_surf, title_rect)
        
        # Back button
        self.controls_back.draw(self.screen)
        
        # Controls list
        controls = [
            ("MOVE", "Arrow Keys or WASD"),
            ("JUMP", "Space or Up Arrow"),
            ("DOUBLE JUMP", "Press Jump again in air"),
            ("WALL JUMP", "Jump while touching wall"),
            ("PAUSE", "ESC key"),
            ("GOAL", "Collect coins, reach the flag!"),
        ]
        
        start_y = 200
        spacing = 70
        box_width = 500
        box_height = 50
        start_x = (SCREEN_W - box_width) // 2
        
        for i, (action, key) in enumerate(controls):
            y = start_y + i * spacing
            
            # Control box background
            box_rect = pygame.Rect(start_x, y, box_width, box_height)
            pygame.draw.rect(self.screen, COLORS['bg_light'], box_rect, border_radius=0)
            pygame.draw.rect(self.screen, COLORS['border'], box_rect, width=2, border_radius=0)
            
            # Action name
            action_surf = self.font_button.render(action, True, COLORS['secondary'])
            self.screen.blit(action_surf, (start_x + 20, y + 12))
            
            # Key binding
            key_surf = self.font_small.render(key, True, COLORS['text'])
            key_rect = key_surf.get_rect(right=start_x + box_width - 20, centery=y + 25)
            self.screen.blit(key_surf, key_rect)
            
        # Tip box
        tip_y = start_y + len(controls) * spacing + 30
        tip_rect = pygame.Rect(start_x, tip_y, box_width, 60)
        pygame.draw.rect(self.screen, COLORS['primary_dark'], tip_rect, border_radius=0)
        pygame.draw.rect(self.screen, COLORS['primary'], tip_rect, width=3, border_radius=0)
        
        tip_surf = self.font_small.render("TIP: Explore both paths in each level!", True, COLORS['text'])
        tip_rect2 = tip_surf.get_rect(center=(SCREEN_W // 2, tip_y + 30))
        self.screen.blit(tip_surf, tip_rect2)


def show_menu(screen):
    """Entry point to show the menu and get selected level."""
    menu = GameMenu(screen)
    return menu.run()


if __name__ == "__main__":
    # Test the menu standalone
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    pygame.display.set_caption("Pixel Adventure - Menu Test")
    
    result = show_menu(screen)
    print(f"Menu returned: {result}")
    pygame.quit()
