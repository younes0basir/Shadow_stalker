"""
Map Editor - Visual Level Designer for Nature Platformer
Allows drag-and-drop tile placement, decoration positioning, and map export.

Quick Start:
  Left Click      - Place selected tile/object
  Right Click     - Remove tile/object
  Middle Drag     - Pan camera (fastest way!)
  Scroll Wheel    - Change selected tile
  +/-             - Zoom in/out
  T               - Toggle tile/decoration mode
  G               - Toggle grid
  S               - Save map
  L               - Load map
  R               - Reset view
  1-9             - Quick select common tiles
  ESC             - Quit
"""

import os, sys, pygame, json
from pathlib import Path

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_W, SCREEN_H = 1280, 720
TILE_SIZE = 32
GRID_COLOR = (50, 50, 50, 100)
UI_BG = (30, 30, 35)
UI_BORDER = (60, 60, 70)
HIGHLIGHT = (100, 180, 255)

# Asset paths
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
BASE = os.path.join(PARENT_DIR, "assets", "craftpix-net-156752-nature-pixel-art-environment-free-assets-pack")
TILES_DIR = os.path.join(BASE, "PNG", "Tiles")
OBJECTS_DIR = os.path.join(BASE, "PNG", "Objects")

class MapEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
        pygame.display.set_caption("Nature Platformer - Map Editor")
        self.clock = pygame.time.Clock()
        
        # Map dimensions (in tiles)
        self.map_width = 80
        self.map_height = 40
        
        # Camera/viewport
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        
        # Map data
        self.tile_layer = [[' ' for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.decorations = []  # List of (image, tile_x, tile_y)
        
        # Load assets
        self.tiles = {}
        self.objects = {}
        self.load_assets()
        
        # Editor state
        self.selected_tile = 'tile47'  # Default to grass top (more intuitive name)
        self.mode = 'tile'  # 'tile' or 'decoration'
        self.selected_object = None
        self.placing_decoration = False
        self.temp_decoration_pos = None
        
        # Quick access favorites (most used tiles)
        self.favorites = ['tile46', 'tile47', 'tile48', 'tile52', 'tile68', 'tile55', 'tile111', 'tile112', 'tile113']
        
        # Recently used tiles (last 12)
        self.recently_used = []
        self.max_recent = 12
        
        # Search
        self.search_text = ''
        self.search_active = False
        
        # Categorized tiles for easier browsing
        self.tile_categories = {
            'All Tiles': sorted(self.tiles.keys()),
            'Grass Top': ['tile46', 'tile47', 'tile48', 'tile49', 'tile50', 'tile51', 'tile63', 'tile64', 'tile65', 'tile66', 
                         'tile67', 'tile68', 'tile69', 'tile70', 'tile71', 'tile72', 'tile73', 'tile84', 'tile95', 'tile96', 
                         'tile97', 'tile102', 'tile103', 'tile104', 'tile105', 'tile106', 'tile107', 'tile108', 'tile123', 'tile126'],
            'Dirt/Ground': ['tile52', 'tile53', 'tile68', 'tile55', 'tile60', 'tile74', 'tile75', 'tile76', 'tile83', 
                           'tile85', 'tile86', 'tile87', 'tile88', 'tile89', 'tile90', 'tile91', 'tile92', 'tile111', 
                           'tile112', 'tile113', 'tile114', 'tile115', 'tile116', 'tile117', 'tile118', 'tile119', 'tile120', 
                           'tile121', 'tile122', 'tile127', 'tile128'],
            'Dirt Deep': ['tile111', 'tile112', 'tile113', 'tile114', 'tile115', 'tile116', 'tile117', 'tile118', 
                         'tile119', 'tile120', 'tile121', 'tile122'],
            'Water': ['tile33', 'tile34', 'tile35', 'tile36', 'tile38', 'tile54', 'tile56', 'tile57', 'tile58', 
                     'tile59', 'tile77', 'tile78', 'tile79', 'tile80', 'tile82'],
            'Rock/Dark': ['tile73', 'tile74', 'tile75', 'tile76', 'tile11', 'tile25', 'tile26', 'tile39', 'tile40', 
                         'tile41', 'tile42', 'tile61', 'tile83', 'tile94', 'tile115', 'tile117', 'tile118', 'tile121', 'tile122'],
            'Slopes': ['tile2', 'tile3', 'tile4', 'tile5', 'tile16', 'tile17', 'tile18', 'tile19', 'tile20', 'tile21', 
                      'tile124', 'tile125'],
            'Platforms': ['tile99', 'tile100', 'tile101'],
            'Edges/Corners': ['tile1', 'tile43', 'tile44', 'tile45', 'tile81', 'tile93', 'tile94', 'tile111', 
                            'tile112', 'tile113'],
            'Background': ['tile12', 'tile13', 'tile14', 'tile15', 'tile33', 'tile34', 'tile35', 'tile36', 'tile38'],
        }
        
        # Current selected category
        self.selected_category = 'All Tiles'
        self.category_names = list(self.tile_categories.keys())
        
        # Brush size (for painting multiple tiles)
        self.brush_size = 1
        
        # Auto-save
        self.last_save_time = 0
        self.auto_save_interval = 30  # seconds - faster auto-save
        
        # Undo/Redo system
        self.history = []
        self.history_index = -1
        self.max_history = 50
        self.save_state()  # Save initial state
        
        # Copy/Paste
        self.clipboard = None
        self.copy_mode = False
        
        # Minimap
        self.show_minimap = True
        self.minimap_size = 180
        
        # Reference image overlay
        self.reference_image = None
        self.reference_alpha = 120  # Semi-transparent (0-255)
        self.show_reference = False
        
        # View mode
        self.view_mode = 'list'  # 'list' or 'grid'
        
        # Hover tracking
        self.hovered_tile = None
        self.hover_timer = 0
        
        # Tile palette UI
        self.palette_width = 220
        self.palette_scroll = 0
        self.tile_list = sorted(self.tiles.keys())
        self.show_favorites_only = False  # Toggle to show only favorites
        self.palette_scroll_speed = 30  # Pixels per scroll
        
        # Font
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_large = pygame.font.SysFont("consolas", 18)
        self.font_small = pygame.font.SysFont("consolas", 10)
        
        # Grid visibility
        self.show_grid = True
        
    def load_assets(self):
        """Load all available tiles and objects."""
        # Load tiles
        if os.path.exists(TILES_DIR):
            for fname in os.listdir(TILES_DIR):
                if fname.endswith('.png'):
                    try:
                        path = os.path.join(TILES_DIR, fname)
                        img = pygame.image.load(path).convert_alpha()
                        # Use filename without extension as key
                        key = fname.replace('.png', '')
                        self.tiles[key] = img
                    except:
                        pass
        
        # Load objects/decorations
        if os.path.exists(OBJECTS_DIR):
            for fname in os.listdir(OBJECTS_DIR):
                if fname.endswith('.png'):
                    try:
                        path = os.path.join(OBJECTS_DIR, fname)
                        img = pygame.image.load(path).convert_alpha()
                        self.objects[fname] = img
                    except:
                        pass
    
    def screen_to_tile(self, screen_x, screen_y):
        """Convert screen coordinates to tile coordinates."""
        world_x = (screen_x - self.palette_width + self.camera_x) / self.zoom
        world_y = (screen_y + self.camera_y) / self.zoom
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)
        return tile_x, tile_y
    
    def tile_to_screen(self, tile_x, tile_y):
        """Convert tile coordinates to screen coordinates."""
        screen_x = tile_x * TILE_SIZE * self.zoom - self.camera_x + self.palette_width
        screen_y = tile_y * TILE_SIZE * self.zoom - self.camera_y
        return screen_x, screen_y
    
    def handle_events(self):
        """Handle user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # Handle search input
                if self.search_active:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.search_active = False
                        self.search_text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        self.search_text = self.search_text[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        self.search_text += event.unicode
                    # Don't process other keys while searching
                    continue
                
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_s:
                    self.save_map()
                elif event.key == pygame.K_l:
                    self.load_map()
                elif event.key == pygame.K_t:
                    self.mode = 'decoration' if self.mode == 'tile' else 'tile'
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_r:
                    # Reset view
                    self.camera_x = 0
                    self.camera_y = 0
                    self.zoom = 1.0
                elif event.key == pygame.K_f:
                    # Toggle favorites view
                    self.show_favorites_only = not self.show_favorites_only
                    self.palette_scroll = 0
                elif event.key == pygame.K_c:
                    # Cycle through categories
                    cat_idx = self.category_names.index(self.selected_category)
                    cat_idx = (cat_idx + 1) % len(self.category_names)
                    self.selected_category = self.category_names[cat_idx]
                    self.palette_scroll = 0
                    print(f"Category: {self.selected_category}")
                elif event.key == pygame.K_b:
                    # Cycle brush size
                    self.brush_size = (self.brush_size % 3) + 1
                    print(f"Brush size: {self.brush_size}x{self.brush_size}")
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.zoom = min(3.0, self.zoom + 0.1)
                elif event.key == pygame.K_MINUS:
                    self.zoom = max(0.3, self.zoom - 0.1)
                elif event.key == pygame.K_UP:
                    # Scroll palette up
                    self.palette_scroll = max(0, self.palette_scroll - self.palette_scroll_speed)
                elif event.key == pygame.K_DOWN:
                    # Scroll palette down
                    self.palette_scroll += self.palette_scroll_speed
                # Quick select tiles with number keys
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                                  pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    idx = event.key - pygame.K_1
                    if idx < len(self.favorites):
                        self.selected_tile = self.favorites[idx]
                        print(f"Selected: {self.selected_tile}")
                # Undo/Redo
                elif event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.undo()
                elif event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.redo()
                # Copy/Paste
                elif event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.copy_selection()
                elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.paste_selection()
                # Toggle minimap
                elif event.key == pygame.K_m:
                    self.show_minimap = not self.show_minimap
                # Load reference image
                elif event.key == pygame.K_i:
                    self.load_reference_image()
                # Adjust reference transparency
                elif event.key == pygame.K_PERIOD:
                    self.reference_alpha = min(255, self.reference_alpha + 20)
                elif event.key == pygame.K_COMMA:
                    self.reference_alpha = max(20, self.reference_alpha - 20)
                # Quick brush size presets
                elif event.key == pygame.K_0:
                    self.brush_size = 5
                    print(f"Brush size: {self.brush_size}x{self.brush_size}")
                # Search
                elif event.key == pygame.K_F3 or (event.key == pygame.K_f and (pygame.key.get_mods() & pygame.KMOD_CTRL)):
                    self.search_active = not self.search_active
                    if not self.search_active:
                        self.search_text = ''
                # View mode
                elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.view_mode = 'grid' if self.view_mode == 'list' else 'list'
                    print(f"View: {self.view_mode}")
                # Increase/decrease palette width
                elif event.key == pygame.K_LEFTBRACKET:
                    self.palette_width = max(150, self.palette_width - 20)
                elif event.key == pygame.K_RIGHTBRACKET:
                    self.palette_width = min(400, self.palette_width + 20)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Double-click to zoom at cursor
                    if event.pos[0] >= self.palette_width:
                        import time
                        current_time = time.time()
                        if hasattr(self, 'last_click_time') and current_time - self.last_click_time < 0.3:
                            self.zoom_in_at_cursor(event.pos)
                            self.last_click_time = 0  # Reset to prevent triple-click
                        else:
                            self.last_click_time = current_time
                            self.handle_left_click(event.pos)
                    else:
                        self.handle_left_click(event.pos)
                elif event.button == 3:  # Right click
                    self.handle_right_click(event.pos)
                elif event.button == 2:  # Middle click - start panning
                    self.middle_mouse_panning = True
                    self.last_mouse_pos = event.pos
                elif event.button == 4:  # Scroll up
                    # If mouse is in palette area, scroll palette; otherwise change tile
                    if event.pos[0] < self.palette_width:
                        self.palette_scroll = max(0, self.palette_scroll - self.palette_scroll_speed)
                    else:
                        idx = self.tile_list.index(self.selected_tile) if self.selected_tile in self.tile_list else 0
                        idx = (idx - 1) % len(self.tile_list)
                        self.selected_tile = self.tile_list[idx]
                elif event.button == 5:  # Scroll down
                    # If mouse is in palette area, scroll palette; otherwise change tile
                    if event.pos[0] < self.palette_width:
                        self.palette_scroll += self.palette_scroll_speed
                    else:
                        idx = self.tile_list.index(self.selected_tile) if self.selected_tile in self.tile_list else 0
                        idx = (idx + 1) % len(self.tile_list)
                        self.selected_tile = self.tile_list[idx]
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:  # Middle click released
                    self.middle_mouse_panning = False
            
            elif event.type == pygame.MOUSEMOTION:
                # Middle mouse panning (fastest navigation!)
                if hasattr(self, 'middle_mouse_panning') and self.middle_mouse_panning:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.camera_x -= dx
                    self.camera_y -= dy
                    self.last_mouse_pos = event.pos
                elif event.buttons[0]:  # Left mouse held - paint tiles
                    self.handle_drag(event.pos)
                # Track hover for tooltips
                self.track_hover(event.pos)
        
        # Handle continuous key presses for camera movement
        keys = pygame.key.get_pressed()
        pan_speed = 15 / self.zoom  # Faster panning
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera_x -= pan_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x += pan_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera_y -= pan_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y += pan_speed
        
        return True
    
    def track_hover(self, pos):
        """Track which tile is being hovered for tooltips."""
        x, y = pos
        if x >= self.palette_width:
            self.hovered_tile = None
            return
        
        # Check which tile is hovered
        tile_size_ui = 40
        padding = 5
        start_y = 133 - self.palette_scroll
        
        # Get current items
        if self.mode == 'decoration':
            items = list(self.objects.keys())
        elif self.show_favorites_only:
            items = self.favorites
        else:
            items = self.tile_categories.get(self.selected_category, sorted(self.tiles.keys()))
        
        # Search filter
        if self.search_active and self.search_text:
            items = [item for item in items if self.search_text.lower() in item.lower()]
        
        for idx, item_key in enumerate(items):
            y_pos = start_y + idx * (tile_size_ui + padding)
            
            if y_pos <= y <= y_pos + tile_size_ui and 10 <= x <= self.palette_width - 10:
                if self.mode == 'tile':
                    self.hovered_tile = item_key
                else:
                    self.hovered_tile = item_key
                return
        
        self.hovered_tile = None
    
    def add_to_recently_used(self, tile_key):
        """Add tile to recently used list."""
        if tile_key in self.recently_used:
            self.recently_used.remove(tile_key)
        self.recently_used.insert(0, tile_key)
        
        # Keep only max_recent items
        if len(self.recently_used) > self.max_recent:
            self.recently_used = self.recently_used[:self.max_recent]
    
    def handle_left_click(self, pos):
        """Handle left mouse click."""
        x, y = pos
        
        # Save state before modification for undo
        if x >= self.palette_width:
            self.save_state()
        
        # Check if clicking in palette area
        if x < self.palette_width:
            # If clicking on search bar, activate search
            if self.search_active:
                search_y = 112
                if search_y <= y <= search_y + 25:
                    return  # Will handle typing
            self.handle_palette_click(x, y)
            return
        
        # Convert to tile coordinates
        tile_x, tile_y = self.screen_to_tile(x, y)
        
        # Check bounds
        if not (0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height):
            return
        
        if self.mode == 'tile':
            # Place tile with brush
            half_brush = self.brush_size // 2
            for dy in range(-half_brush, half_brush + 1):
                for dx in range(-half_brush, half_brush + 1):
                    px, py = tile_x + dx, tile_y + dy
                    if 0 <= px < self.map_width and 0 <= py < self.map_height:
                        self.tile_layer[py][px] = self.selected_tile
                        # Add to recently used
                        self.add_to_recently_used(self.selected_tile)
        elif self.mode == 'decoration':
            # Start placing decoration
            self.placing_decoration = True
            self.temp_decoration_pos = (tile_x, tile_y)
    
    def handle_right_click(self, pos):
        """Handle right mouse click (remove with brush)."""
        x, y = pos
        
        # Save state before modification
        self.save_state()
        
        # Ignore palette area
        if x < self.palette_width:
            return
        
        tile_x, tile_y = self.screen_to_tile(x, y)
        
        if not (0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height):
            return
        
        if self.mode == 'tile':
            # Remove tiles with brush
            half_brush = self.brush_size // 2
            for dy in range(-half_brush, half_brush + 1):
                for dx in range(-half_brush, half_brush + 1):
                    px, py = tile_x + dx, tile_y + dy
                    if 0 <= px < self.map_width and 0 <= py < self.map_height:
                        self.tile_layer[py][px] = ' '
        elif self.mode == 'decoration':
            # Remove decorations at this position
            self.decorations = [(img, tx, ty) for img, tx, ty in self.decorations 
                               if not (tx == tile_x and ty == tile_y)]
    
    def handle_drag(self, pos):
        """Handle mouse drag (painting tiles with brush)."""
        if self.mode != 'tile':
            return
        
        x, y = pos
        if x < self.palette_width:
            return
        
        tile_x, tile_y = self.screen_to_tile(x, y)
        
        # Paint with brush size
        half_brush = self.brush_size // 2
        for dy in range(-half_brush, half_brush + 1):
            for dx in range(-half_brush, half_brush + 1):
                px, py = tile_x + dx, tile_y + dy
                if 0 <= px < self.map_width and 0 <= py < self.map_height:
                    self.tile_layer[py][px] = self.selected_tile
    
    def handle_palette_click(self, x, y):
        """Handle clicks in the tile palette."""
        # Calculate which tile was clicked
        tile_size_ui = 40
        padding = 5
        start_y = 60 - self.palette_scroll
        
        idx = (y - start_y) // (tile_size_ui + padding)
        
        if 0 <= idx < len(self.tile_list):
            self.selected_tile = self.tile_list[idx]
    
    def save_map(self):
        """Save current map to JSON file."""
        filename = "custom_map.json"
        try:
            data = {
                'width': self.map_width,
                'height': self.map_height,
                'tiles': self.tile_layer,
                'decorations': [(obj_name, tx, ty) for obj_img, tx, ty in self.decorations 
                               for obj_name, obj_img2 in self.objects.items() if obj_img2 is obj_img]
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            import time
            self.last_save_time = time.time()
            print(f"✓ Map saved to {filename}")
        except Exception as e:
            print(f"Error saving map: {e}")
    
    def load_map(self):
        """Load map from JSON file."""
        filename = "custom_map.json"
        if not os.path.exists(filename):
            print(f"File {filename} not found")
            return
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.map_width = data['width']
            self.map_height = data['height']
            self.tile_layer = data['tiles']
            
            # Reload decorations
            self.decorations = []
            for obj_name, tx, ty in data.get('decorations', []):
                if obj_name in self.objects:
                    self.decorations.append((self.objects[obj_name], tx, ty))
            
            print(f"✓ Map loaded from {filename}")
        except Exception as e:
            print(f"Error loading map: {e}")
    
    def draw_palette(self):
        """Draw the tile/object palette on the left side."""
        # Background
        pygame.draw.rect(self.screen, UI_BG, (0, 0, self.palette_width, SCREEN_H))
        pygame.draw.line(self.screen, UI_BORDER, (self.palette_width, 0), 
                        (self.palette_width, SCREEN_H), 2)
        
        # Title with mode
        title = self.font_large.render("Tile Palette", True, (200, 200, 200))
        self.screen.blit(title, (10, 10))
        
        # Mode indicator (more prominent)
        mode_color = HIGHLIGHT if self.mode == 'tile' else (255, 180, 100)
        mode_text = f"Mode: {self.mode.upper()}"
        mode_surf = self.font_large.render(mode_text, True, mode_color)
        self.screen.blit(mode_surf, (10, 35))
        
        # Brush size indicator
        brush_text = f"Brush: {self.brush_size}x{self.brush_size}"
        brush_surf = self.font.render(brush_text, True, (180, 180, 180))
        self.screen.blit(brush_surf, (10, 58))
        
        # Favorites toggle indicator
        fav_text = "[F] Favorites ON" if self.show_favorites_only else "[F] Show All"
        fav_surf = self.font.render(fav_text, True, (150, 200, 150))
        self.screen.blit(fav_surf, (10, 76))
        
        # Search bar
        if self.search_active:
            search_bg = pygame.Surface((self.palette_width - 20, 25), pygame.SRCALPHA)
            search_bg.fill((50, 50, 60, 220))
            pygame.draw.rect(search_bg, (100, 180, 255, 150), (0, 0, self.palette_width - 20, 25), 2, border_radius=4)
            self.screen.blit(search_bg, (10, 94))
            
            search_text = f"🔍 {self.search_text}▌" if self.search_text else "🔍 Type to search..."
            search_surf = self.font.render(search_text, True, (200, 200, 200))
            self.screen.blit(search_surf, (15, 97))
        else:
            # Category selector (only show in tile mode)
            if self.mode == 'tile':
                cat_text = f"[C] Category: {self.selected_category}"
                cat_surf = self.font.render(cat_text, True, (150, 200, 255))
                self.screen.blit(cat_surf, (10, 94))
            else:
                # Show object count in decoration mode
                obj_text = f"Objects: {len(self.objects)} available"
                obj_surf = self.font.render(obj_text, True, (255, 180, 100))
                self.screen.blit(obj_surf, (10, 94))
        
        # Scroll hint
        scroll_hint = "↑↓ or Scroll to browse | F3: Search | Ctrl+V: Grid"
        scroll_surf = self.font.render(scroll_hint, True, (100, 100, 100))
        self.screen.blit(scroll_surf, (10, 112))
        
        # Recently used section (if has items)
        if self.recently_used and not self.show_favorites_only:
            recent_y = 130
            recent_label = "Recent:"
            recent_surf = self.font.render(recent_label, True, (200, 180, 100))
            self.screen.blit(recent_surf, (10, recent_y))
            
            # Draw recently used tiles in a row
            recent_tile_size = 28
            recent_x = 10
            recent_start_y = recent_y + 18
            
            for idx, recent_key in enumerate(self.recently_used[:6]):  # Show max 6 recent
                if recent_key in self.tiles:
                    x_pos = recent_x + idx * (recent_tile_size + 4)
                    
                    # Highlight if selected
                    if recent_key == self.selected_tile:
                        pygame.draw.rect(self.screen, HIGHLIGHT, 
                                       (x_pos - 2, recent_start_y - 2, recent_tile_size + 4, recent_tile_size + 4), 2)
                    
                    # Draw tile
                    img = self.tiles[recent_key]
                    scaled = pygame.transform.scale(img, (recent_tile_size, recent_tile_size))
                    self.screen.blit(scaled, (x_pos, recent_start_y))
                    
                    # Show number key hint for first 9
                    if idx < 9:
                        num_bg = pygame.Surface((12, 12), pygame.SRCALPHA)
                        num_bg.fill((0, 0, 0, 150))
                        self.screen.blit(num_bg, (x_pos, recent_start_y))
                        num_text = self.font_small.render(str(idx + 1), True, (255, 255, 150))
                        self.screen.blit(num_text, (x_pos + 2, recent_start_y + 1))
        
        # Draw scrollbar if there are more items than can fit
        tile_size_ui = 40
        padding = 5
        item_height = tile_size_ui + padding
        
        # Determine which items to show for scrollbar calculation
        if self.mode == 'decoration':
            items_for_scroll = list(self.objects.keys())
        elif self.show_favorites_only:
            items_for_scroll = self.favorites
        else:
            items_for_scroll = self.tile_categories.get(self.selected_category, sorted(self.tiles.keys()))
        
        # Apply search filter
        if self.search_active and self.search_text:
            items_for_scroll = [item for item in items_for_scroll if self.search_text.lower() in item.lower()]
        
        total_height = len(items_for_scroll) * item_height
        visible_height = SCREEN_H - 130  # Available space for tiles
        
        if total_height > visible_height:
            # Draw scrollbar track
            scrollbar_x = self.palette_width - 12
            scrollbar_y = 115
            scrollbar_h = visible_height
            pygame.draw.rect(self.screen, (50, 50, 50), (scrollbar_x, scrollbar_y, 8, scrollbar_h))
            
            # Calculate scrollbar thumb
            thumb_height = max(30, (visible_height / total_height) * visible_height)
            max_scroll = total_height - visible_height
            scroll_ratio = self.palette_scroll / max_scroll if max_scroll > 0 else 0
            thumb_y = scrollbar_y + scroll_ratio * (scrollbar_h - thumb_height)
            
            # Draw scrollbar thumb
            pygame.draw.rect(self.screen, (120, 120, 120), (scrollbar_x, thumb_y, 8, thumb_height))
        
        # Draw tiles/objects
        tile_size_ui = 40
        padding = 5
        
        # Adjust start_y based on recently used section
        start_y = 170 if (self.recently_used and not self.show_favorites_only) else 133
        start_y = start_y - self.palette_scroll
        
        # Determine which items to show
        if self.mode == 'decoration':
            # In decoration mode, show all objects (no categories)
            items = list(self.objects.keys())
        elif self.show_favorites_only:
            items = self.favorites
        else:
            # Use selected category in tile mode
            items = self.tile_categories.get(self.selected_category, sorted(self.tiles.keys()))
        
        # Apply search filter
        if self.search_active and self.search_text:
            items = [item for item in items if self.search_text.lower() in item.lower()]
        
        if self.view_mode == 'grid':
            # Grid view - 3 columns
            self.draw_palette_grid(items, start_y, tile_size_ui)
        else:
            # List view - traditional single column
            self.draw_palette_list(items, start_y, tile_size_ui, padding)
        
        # Instructions (compact & organized) - positioned at bottom
        instructions = [
            "Middle Drag: Pan | WASD: Move",
            "+/−: Zoom | Double-Click: Zoom In",
            "",
            "Left: Place | Right: Remove | Drag: Paint",
            "B: Brush | 0: 5×5 | 1-9: Quick Select",
            "",
            "Ctrl+Z: Undo | Ctrl+Y: Redo",
            "Ctrl+C: Copy | Ctrl+V: Paste",
            "T: Mode | F: Favorites | C: Category",
            "F3: Search | Ctrl+V: View Mode | M: Minimap",
        ]
        
        # Draw instructions in a compact block at the bottom
        # Start from a fixed position near bottom
        instr_start_y = SCREEN_H - 150
        
        for idx, instr in enumerate(instructions):
            if instr == '':
                continue
            
            y_pos = instr_start_y + (idx * 16)
            
            # Skip if off-screen
            if y_pos < 0 or y_pos > SCREEN_H - 20:
                continue
            
            if instr.startswith('──'):
                text = self.font.render(instr, True, (180, 180, 100))
            else:
                text = self.font.render(instr, True, (130, 130, 130))
            
            self.screen.blit(text, (8, y_pos))
    
    def draw_grid(self):
        """Draw the grid lines."""
        if not self.show_grid:
            return
        
        grid_surface = pygame.Surface((self.map_width * TILE_SIZE, self.map_height * TILE_SIZE), 
                                     pygame.SRCALPHA)
        
        # Vertical lines
        for x in range(0, self.map_width * TILE_SIZE + 1, TILE_SIZE):
            pygame.draw.line(grid_surface, GRID_COLOR, (x, 0), (x, self.map_height * TILE_SIZE))
        
        # Horizontal lines
        for y in range(0, self.map_height * TILE_SIZE + 1, TILE_SIZE):
            pygame.draw.line(grid_surface, GRID_COLOR, (0, y), (self.map_width * TILE_SIZE, y))
        
        # Apply zoom and camera
        scaled_grid = pygame.transform.scale(grid_surface, 
                                            (int(self.map_width * TILE_SIZE * self.zoom),
                                             int(self.map_height * TILE_SIZE * self.zoom)))
        
        self.screen.blit(scaled_grid, (self.palette_width - self.camera_x, -self.camera_y))
    
    def draw_tiles(self):
        """Draw all placed tiles."""
        for row_idx, row in enumerate(self.tile_layer):
            for col_idx, tile_key in enumerate(row):
                if tile_key != ' ' and tile_key in self.tiles:
                    screen_x, screen_y = self.tile_to_screen(col_idx, row_idx)
                    
                    # Skip if off-screen
                    if (screen_x < self.palette_width - TILE_SIZE * self.zoom or 
                        screen_x > SCREEN_W or
                        screen_y < -TILE_SIZE * self.zoom or 
                        screen_y > SCREEN_H):
                        continue
                    
                    img = self.tiles[tile_key]
                    scaled = pygame.transform.scale(img, 
                                                   (int(TILE_SIZE * self.zoom), 
                                                    int(TILE_SIZE * self.zoom)))
                    self.screen.blit(scaled, (screen_x, screen_y))
    
    def draw_decorations(self):
        """Draw all placed decorations."""
        for img, tile_x, tile_y in self.decorations:
            screen_x, screen_y = self.tile_to_screen(tile_x, tile_y)
            
            # Skip if off-screen
            if (screen_x < self.palette_width - 200 or 
                screen_x > SCREEN_W or
                screen_y < -200 or 
                screen_y > SCREEN_H):
                continue
            
            # Scale decoration
            scaled_w = int(img.get_width() * self.zoom)
            scaled_h = int(img.get_height() * self.zoom)
            scaled = pygame.transform.scale(img, (scaled_w, scaled_h))
            
            # Position decoration (anchor at bottom)
            draw_x = screen_x
            draw_y = screen_y + TILE_SIZE * self.zoom - scaled_h
            
            self.screen.blit(scaled, (draw_x, draw_y))
    
    def draw_cursor_preview(self):
        """Draw preview of tile/decoration under cursor with brush size."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Draw tooltip if hovering over palette tile
        if mouse_x < self.palette_width and self.hovered_tile:
            tooltip_text = self.hovered_tile
            tooltip_surf = self.font.render(tooltip_text, True, (255, 255, 255))
            
            # Draw tooltip background
            tooltip_width = tooltip_surf.get_width() + 12
            tooltip_height = 22
            tooltip_x = mouse_x + 15
            tooltip_y = mouse_y - 30
            
            # Keep tooltip on screen
            if tooltip_x + tooltip_width > self.palette_width:
                tooltip_x = mouse_x - tooltip_width - 5
            if tooltip_y < 0:
                tooltip_y = mouse_y + 15
            
            tooltip_bg = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
            tooltip_bg.fill((0, 0, 0, 200))
            pygame.draw.rect(tooltip_bg, (100, 180, 255, 150), (0, 0, tooltip_width, tooltip_height), 1, border_radius=3)
            self.screen.blit(tooltip_bg, (tooltip_x, tooltip_y))
            self.screen.blit(tooltip_surf, (tooltip_x + 6, tooltip_y + 4))
        
        # Don't show preview in palette area
        if mouse_x < self.palette_width:
            return
        
        tile_x, tile_y = self.screen_to_tile(mouse_x, mouse_y)
        
        if not (0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height):
            return
        
        # Draw brush area based on brush size
        half_brush = self.brush_size // 2
        for dy in range(-half_brush, half_brush + 1):
            for dx in range(-half_brush, half_brush + 1):
                px, py = tile_x + dx, tile_y + dy
                if 0 <= px < self.map_width and 0 <= py < self.map_height:
                    screen_x, screen_y = self.tile_to_screen(px, py)
                    
                    # Draw highlight box
                    highlight_rect = pygame.Rect(screen_x, screen_y, 
                                                int(TILE_SIZE * self.zoom), 
                                                int(TILE_SIZE * self.zoom))
                    
                    # Center tile gets brighter highlight
                    if dx == 0 and dy == 0:
                        pygame.draw.rect(self.screen, HIGHLIGHT, highlight_rect, 3)
                    else:
                        pygame.draw.rect(self.screen, (*HIGHLIGHT[:3], 150), highlight_rect, 2)
                    
                    # Draw semi-transparent preview for center tile only
                    if dx == 0 and dy == 0 and self.mode == 'tile' and self.selected_tile in self.tiles:
                        img = self.tiles[self.selected_tile]
                        scaled = pygame.transform.scale(img, 
                                                       (int(TILE_SIZE * self.zoom), 
                                                        int(TILE_SIZE * self.zoom)))
                        scaled.set_alpha(128)
                        self.screen.blit(scaled, (screen_x, screen_y))
                        scaled.set_alpha(255)
    
    def zoom_in_at_cursor(self, pos):
        """Zoom in at cursor position."""
        x, y = pos
        old_zoom = self.zoom
        self.zoom = min(3.0, self.zoom + 0.5)
        
        # Adjust camera to zoom at cursor
        scale_factor = self.zoom / old_zoom
        self.camera_x = (self.camera_x - x + self.palette_width) * scale_factor + x - self.palette_width
        self.camera_y = (self.camera_y - y) * scale_factor + y
        print(f"Zoom: {self.zoom:.1f}x")
    
    def save_state(self):
        """Save current state for undo."""
        state = {
            'tiles': [row[:] for row in self.tile_layer],
            'decorations': self.decorations[:]
        }
        
        # Remove future states if we've undone some actions
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(state)
        
        # Keep history within limit
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        self.history_index = len(self.history) - 1
    
    def undo(self):
        """Undo last action."""
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.tile_layer = [row[:] for row in state['tiles']]
            self.decorations = state['decorations'][:]
            print("↶ Undo")
    
    def redo(self):
        """Redo last undone action."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.tile_layer = [row[:] for row in state['tiles']]
            self.decorations = state['decorations'][:]
            print("↷ Redo")
    
    def copy_selection(self):
        """Copy selected area (simplified - copies entire visible area)."""
        # Get current view area
        start_tile_x = max(0, int((-self.camera_x / self.zoom) // TILE_SIZE))
        start_tile_y = max(0, int((-self.camera_y / self.zoom) // TILE_SIZE))
        end_tile_x = min(self.map_width, start_tile_x + int((SCREEN_W - self.palette_width) / (TILE_SIZE * self.zoom)) + 1)
        end_tile_y = min(self.map_height, start_tile_y + int(SCREEN_H / (TILE_SIZE * self.zoom)) + 1)
        
        self.clipboard = {
            'tiles': [row[start_tile_x:end_tile_x] for row in self.tile_layer[start_tile_y:end_tile_y]],
            'offset_x': start_tile_x,
            'offset_y': start_tile_y
        }
        print(f"✓ Copied {end_tile_x - start_tile_x}x{end_tile_y - start_tile_y} area")
    
    def paste_selection(self):
        """Paste clipboard at current cursor position."""
        if not self.clipboard:
            print("Nothing to paste")
            return
        
        self.save_state()
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile_x, tile_y = self.screen_to_tile(mouse_x, mouse_y)
        
        # Paste tiles
        for row_idx, row in enumerate(self.clipboard['tiles']):
            for col_idx, tile_key in enumerate(row):
                px = tile_x + col_idx - self.clipboard['offset_x']
                py = tile_y + row_idx - self.clipboard['offset_y']
                if 0 <= px < self.map_width and 0 <= py < self.map_height:
                    self.tile_layer[py][px] = tile_key
        
        print("✓ Pasted")
    
    def draw_minimap(self):
        """Draw minimap showing entire map and viewport."""
        if not self.show_minimap:
            return
        
        # Minimap position (top-right corner)
        map_x = SCREEN_W - self.minimap_size - 10
        map_y = 50
        
        # Calculate minimap scale
        scale_x = self.minimap_size / self.map_width
        scale_y = self.minimap_size / self.map_height
        scale = min(scale_x, scale_y)
        
        minimap_w = int(self.map_width * scale)
        minimap_h = int(self.map_height * scale)
        
        # Background
        bg = pygame.Surface((minimap_w + 20, minimap_h + 20), pygame.SRCALPHA)
        pygame.draw.rect(bg, (0, 0, 0, 180), (0, 0, minimap_w + 20, minimap_h + 20), border_radius=8)
        pygame.draw.rect(bg, (60, 60, 70, 200), (0, 0, minimap_w + 20, minimap_h + 20), 2, border_radius=8)
        self.screen.blit(bg, (map_x - 10, map_y - 10))
        
        # Draw tiles on minimap
        minimap_surf = pygame.Surface((minimap_w, minimap_h))
        minimap_surf.fill((20, 20, 25))
        
        # Sample tiles (draw every nth tile for performance)
        sample_rate = max(1, self.map_width // minimap_w)
        
        for row_idx in range(0, self.map_height, sample_rate):
            for col_idx in range(0, self.map_width, sample_rate):
                tile_key = self.tile_layer[row_idx][col_idx]
                if tile_key != ' ':
                    x = int(col_idx * scale)
                    y = int(row_idx * scale)
                    # Color based on tile type
                    if 'tile4' in tile_key or 'tile5' in tile_key or 'tile6' in tile_key:
                        color = (50, 150, 50)  # Grass
                    elif 'tile7' in tile_key or 'tile8' in tile_key or 'tile9' in tile_key:
                        color = (150, 100, 50)  # Dirt
                    elif 'tile3' in tile_key or 'tile54' in tile_key or 'tile77' in tile_key:
                        color = (50, 100, 200)  # Water
                    else:
                        color = (100, 100, 100)  # Other
                    pygame.draw.rect(minimap_surf, color, (x, y, max(1, int(scale * 2)), max(1, int(scale * 2))))
        
        self.screen.blit(minimap_surf, (map_x, map_y))
        
        # Draw viewport rectangle
        view_start_x = int((-self.camera_x / self.zoom) / TILE_SIZE * scale)
        view_start_y = int((-self.camera_y / self.zoom) / TILE_SIZE * scale)
        view_w = int((SCREEN_W - self.palette_width) / self.zoom / TILE_SIZE * scale)
        view_h = int(SCREEN_H / self.zoom / TILE_SIZE * scale)
        
        pygame.draw.rect(self.screen, (255, 255, 0, 100), 
                        (map_x + view_start_x, map_y + view_start_y, view_w, view_h), 2)
    
    def draw_info_bar(self):
        """Draw information bar at the top."""
        info_bg = pygame.Surface((SCREEN_W - self.palette_width, 35), pygame.SRCALPHA)
        info_bg.fill((0, 0, 0, 180))
        self.screen.blit(info_bg, (self.palette_width, 0))
        
        # Main info
        info_text = f"Zoom: {self.zoom:.1f}x | Pos: ({int(-self.camera_x)}, {int(-self.camera_y)}) | Selected: {self.selected_tile}"
        text_surf = self.font.render(info_text, True, (220, 220, 220))
        self.screen.blit(text_surf, (self.palette_width + 10, 10))
        
        # Quick tips that fade out
        import time
        current_time = time.time()
        if current_time - self.last_save_time < 3:
            tip_text = "✓ Auto-saved!"
            tip_surf = self.font.render(tip_text, True, (100, 255, 100))
            self.screen.blit(tip_surf, (self.palette_width + 10, 28))
    
    def load_reference_image(self):
        """Load a reference image for tracing."""
        # Try to load the attached image
        reference_paths = [
            "reference_image.png",  # Converted PNG first
            "reference_image.jpg",
            "C:/Users/basir/AppData/Roaming/Lingma/SharedClientCache/cache/images/7d3c6126/wmremove-transformed-0727f663.webp",
        ]
        
        for path in reference_paths:
            try:
                self.reference_image = pygame.image.load(path).convert_alpha()
                self.show_reference = True
                print(f"✓ Reference image loaded: {path}")
                print(f"  Press I to toggle | ,/. to adjust transparency: {self.reference_alpha}")
                return
            except:
                continue
        
        print("✗ Could not load reference image")
        print("  Tip: Place image as 'reference_image.png' in project folder")
    
    def draw_reference_overlay(self):
        """Draw semi-transparent reference image overlay."""
        if not self.show_reference or not self.reference_image:
            return
        
        # Create a copy with alpha
        overlay = self.reference_image.copy()
        overlay.set_alpha(self.reference_alpha)
        
        # Draw on canvas area only (after palette)
        self.screen.blit(overlay, (self.palette_width, 0))
        
        # Show indicator
        indicator_text = f"Reference: {self.reference_alpha} | I:Toggle | ,/-:Less | ./+ :More"
        indicator_surf = self.font.render(indicator_text, True, (255, 200, 100))
        self.screen.blit(indicator_surf, (self.palette_width + 10, SCREEN_H - 58))
    
    def draw_palette_list(self, items, start_y, tile_size_ui, padding):
        """Draw palette in traditional list view."""
        for idx, item_key in enumerate(items):
            y_pos = start_y + idx * (tile_size_ui + padding)
            
            # Only draw if visible
            if y_pos < 130 or y_pos > SCREEN_H:
                continue
            
            x_pos = 10
            
            # Highlight selected tile
            if item_key == self.selected_tile:
                pygame.draw.rect(self.screen, HIGHLIGHT, 
                               (x_pos - 2, y_pos - 2, tile_size_ui + 4, tile_size_ui + 4), 2)
            
            # Draw tile preview
            if self.mode == 'tile' and item_key in self.tiles:
                img = self.tiles[item_key]
                scaled = pygame.transform.scale(img, (tile_size_ui, tile_size_ui))
                self.screen.blit(scaled, (x_pos, y_pos))
            elif self.mode == 'decoration' and item_key in self.objects:
                img = self.objects[item_key]
                # Scale to fit
                scale_factor = min(tile_size_ui / img.get_width(), tile_size_ui / img.get_height())
                new_w = int(img.get_width() * scale_factor)
                new_h = int(img.get_height() * scale_factor)
                scaled = pygame.transform.scale(img, (new_w, new_h))
                # Center in slot
                offset_x = (tile_size_ui - new_w) // 2
                offset_y = (tile_size_ui - new_h) // 2
                self.screen.blit(scaled, (x_pos + offset_x, y_pos + offset_y))
            
            # Show number key hint for favorites (first 9)
            if self.show_favorites_only and idx < 9:
                num_bg = pygame.Surface((16, 16), pygame.SRCALPHA)
                num_bg.fill((0, 0, 0, 150))
                self.screen.blit(num_bg, (x_pos, y_pos))
                num_text = self.font_small.render(str(idx + 1), True, (255, 255, 150))
                self.screen.blit(num_text, (x_pos + 4, y_pos + 2))
    
    def draw_palette_grid(self, items, start_y, tile_size_ui):
        """Draw palette in grid view (3 columns)."""
        cols = 3
        col_width = tile_size_ui + 8
        row_height = tile_size_ui + 8
        
        for idx, item_key in enumerate(items):
            col = idx % cols
            row = idx // cols
            
            x_pos = 10 + col * col_width
            y_pos = start_y + row * row_height
            
            # Only draw if visible
            if y_pos < 130 or y_pos > SCREEN_H:
                continue
            
            # Highlight selected tile
            if item_key == self.selected_tile:
                pygame.draw.rect(self.screen, HIGHLIGHT, 
                               (x_pos - 2, y_pos - 2, tile_size_ui + 4, tile_size_ui + 4), 2)
            
            # Draw tile preview
            if self.mode == 'tile' and item_key in self.tiles:
                img = self.tiles[item_key]
                scaled = pygame.transform.scale(img, (tile_size_ui, tile_size_ui))
                self.screen.blit(scaled, (x_pos, y_pos))
            elif self.mode == 'decoration' and item_key in self.objects:
                img = self.objects[item_key]
                # Scale to fit
                scale_factor = min(tile_size_ui / img.get_width(), tile_size_ui / img.get_height())
                new_w = int(img.get_width() * scale_factor)
                new_h = int(img.get_height() * scale_factor)
                scaled = pygame.transform.scale(img, (new_w, new_h))
                # Center in slot
                offset_x = (tile_size_ui - new_w) // 2
                offset_y = (tile_size_ui - new_h) // 2
                self.screen.blit(scaled, (x_pos + offset_x, y_pos + offset_y))
    
    def run(self):
        """Main editor loop."""
        running = True
        
        while running:
            running = self.handle_events()
            
            # Auto-save
            import time
            current_time = time.time()
            if current_time - self.last_save_time > self.auto_save_interval:
                self.save_map()
                print("Auto-saved")
            
            # Clear screen
            self.screen.fill((20, 20, 25))
            
            # Draw components
            self.draw_grid()
            self.draw_tiles()
            self.draw_decorations()
            self.draw_reference_overlay()
            self.draw_cursor_preview()
            self.draw_palette()
            self.draw_minimap()
            self.draw_info_bar()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        # Final save on exit
        self.save_map()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    editor = MapEditor()
    editor.run()
