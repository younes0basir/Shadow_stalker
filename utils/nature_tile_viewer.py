import os
import sys
import pygame

# Paths
ROOT = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(ROOT)
BASE = os.path.join(PARENT_DIR, "assets", "craftpix-net-156752-nature-pixel-art-environment-free-assets-pack", "PNG")
TILES_DIR = os.path.join(BASE, "Tiles")
OBJECTS_DIR = os.path.join(BASE, "Objects")

def create_asset_surface(screen_width, screen_height):
    font = pygame.font.SysFont("consolas", 12)
    title_font = pygame.font.SysFont("consolas", 20, bold=True)
    
    PAD = 15
    sections = [
        ("Tiles", TILES_DIR),
        ("Objects", OBJECTS_DIR)
    ]
    
    loaded_sections = []
    
    for section_name, folder in sections:
        if not os.path.exists(folder): continue
        files = sorted([f for f in os.listdir(folder) if f.endswith('.png')])
        
        if section_name == "Tiles":
            def sort_key(f):
                name = f.replace('tile', '').replace('.png', '').replace('Layer-', '0')
                try: return int(name)
                except ValueError: return float('inf')
            try:
                files.sort(key=sort_key)
            except:
                pass
                
        images = []
        for f in files:
            try:
                img = pygame.image.load(os.path.join(folder, f)).convert_alpha()
                # Upscale small tiles for better visibility
                if section_name == "Tiles" and img.get_width() <= 32:
                    img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
                images.append((f, img))
            except Exception as e:
                print(f"Failed to load {f}: {e}")
                
        loaded_sections.append((section_name, images))
        
    layout_data = [] 
    y = PAD
    for section_name, images in loaded_sections:
        y += 30 
        section_layout = []
        x = PAD
        row_max_h = 0
        
        for fname, img in images:
            w, h = img.get_size()
            lbl = font.render(fname.replace('.png', ''), True, (200, 200, 200))
            item_w = max(w, lbl.get_width())
            item_h = h + lbl.get_height() + 5
            
            if x + item_w + PAD > screen_width:
                x = PAD
                y += row_max_h + PAD
                row_max_h = 0
                
            section_layout.append((x, y, fname, img, lbl))
            x += item_w + PAD
            row_max_h = max(row_max_h, item_h)
            
        y += row_max_h + PAD * 2
        layout_data.append((section_name, section_layout))
        
    total_height = max(screen_height, y + PAD)
    
    surf = pygame.Surface((screen_width, total_height))
    surf.fill((30, 30, 40))
    
    for section_name, section_layout in layout_data:
        if section_layout:
            first_y = section_layout[0][1] - 30
            title_lbl = title_font.render(f"--- {section_name} ---", True, (255, 230, 100))
            surf.blit(title_lbl, (PAD, first_y))
            
        for x, y_pos, fname, img, lbl in section_layout:
            w, h = img.get_size()
            item_w = max(w, lbl.get_width())
            
            img_x = x + (item_w - w) // 2
            lbl_x = x + (item_w - lbl.get_width()) // 2
            
            surf.blit(img, (img_x, y_pos))
            surf.blit(lbl, (lbl_x, y_pos + h + 5))
            
    return surf

def main():
    pygame.init()
    
    # We set the display mode before loading images so `convert_alpha()` works properly!
    screen_width, screen_height = 1000, 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Nature Asset Viewer - Use Mouse Wheel or Up/Down to Scroll")
    
    print("Generating asset layout...")
    content_surf = create_asset_surface(screen_width, screen_height)
    
    # Save the reference image
    ref_image_path = "nature_assets_reference.png"
    pygame.image.save(content_surf, ref_image_path)
    print(f"Saved reference image to '{ref_image_path}'")
    print("Opening interactive viewer...")
    
    clock = pygame.time.Clock()
    scroll_y = 0
    max_scroll = max(0, content_surf.get_height() - screen_height)
    scroll_speed = 40
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_DOWN:
                    scroll_y = min(max_scroll, scroll_y + scroll_speed * 2)
                elif event.key == pygame.K_UP:
                    scroll_y = max(0, scroll_y - scroll_speed * 2)
            elif event.type == pygame.MOUSEWHEEL:
                scroll_y -= event.y * scroll_speed
                scroll_y = max(0, min(max_scroll, scroll_y))
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            scroll_y = min(max_scroll, scroll_y + 15)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            scroll_y = max(0, scroll_y - 15)
            
        screen.fill((0, 0, 0))
        screen.blit(content_surf, (0, -scroll_y))
        
        if max_scroll > 0:
            bar_h = max(30, screen_height * (screen_height / content_surf.get_height()))
            bar_y = (scroll_y / max_scroll) * (screen_height - bar_h)
            pygame.draw.rect(screen, (100, 100, 120), (screen_width - 15, bar_y, 10, bar_h), border_radius=5)
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
