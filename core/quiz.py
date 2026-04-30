import pygame
import random
from menu import COLORS, MenuButton

QUIZ_DATA = {
    "younger": [ # Under 5
        {"q": "What color is the sky?", "a": ["Blue", "Green", "Red"], "correct": 0},
        {"q": "Which animal says 'Meow'?", "a": ["Dog", "Cat", "Cow"], "correct": 1},
        {"q": "How many fingers on one hand?", "a": ["3", "5", "10"], "correct": 1},
        {"q": "What color is a banana?", "a": ["Purple", "Yellow", "Blue"], "correct": 1},
        {"q": "Which one is BIG?", "a": ["Ant", "Elephant", "Bee"], "correct": 1},
    ],
    "older": [ # 5 and older
        {"q": "Solve the Square: [ 2 | ? | 6 | 8 ]", "a": ["4", "5", "7"], "correct": 0},
        {"q": "Completing the pattern: 2, 4, 6, ?", "a": ["7", "8", "10"], "correct": 1},
        {"q": "What is 5 + 5?", "a": ["8", "10", "15"], "correct": 1},
        {"q": "Which shape has 4 equal sides?", "a": ["Circle", "Square", "Triangle"], "correct": 1},
        {"q": "Pattern: [Square | Circle | Square | ?]", "a": ["Triangle", "Circle", "Square"], "correct": 1},
    ]
}

def show_quiz(screen, age_group):
    """Show a quiz screen and return True if answered correctly."""
    questions = QUIZ_DATA.get(age_group, QUIZ_DATA["older"])
    quiz = random.choice(questions)
    
    font_q = pygame.font.Font(None, 64)
    font_a = pygame.font.Font(None, 48)
    
    btn_w, btn_h = 400, 60
    buttons = []
    for i, choice in enumerate(quiz["a"]):
        btn = MenuButton(1280 // 2 - btn_w // 2, 300 + i * 80, btn_w, btn_h, choice, font_size=36)
        buttons.append(btn)
        
    running = True
    result = False
    
    # Draw Question Box
    q_box_w, q_box_h = 1000, 150
    q_box_rect = pygame.Rect(1280 // 2 - q_box_w // 2, 120, q_box_w, q_box_h)
    pygame.draw.rect(screen, COLORS['bg_light'], q_box_rect, border_radius=15)
    pygame.draw.rect(screen, COLORS['primary'], q_box_rect, width=3, border_radius=15)

    while running:
        screen.fill(COLORS['bg_dark'])
        # Background blur effect (optional)
        
        # Draw Question Box
        pygame.draw.rect(screen, COLORS['bg_light'], q_box_rect, border_radius=15)
        pygame.draw.rect(screen, COLORS['primary'], q_box_rect, width=3, border_radius=15)
        
        # Draw Question
        q_surf = font_q.render(quiz["q"], True, COLORS['secondary'])
        q_rect = q_surf.get_rect(center=q_box_rect.center)
        screen.blit(q_surf, q_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            for i, btn in enumerate(buttons):
                if btn.is_clicked(event):
                    if i == quiz["correct"]:
                        result = True
                    running = False
                    
        for btn in buttons:
            btn.update(mouse_pos, mouse_pressed)
            btn.draw(screen)
            
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        
    # Feedback screen
    screen.fill(COLORS['bg_dark'])
    msg = "CORRECT!" if result else "Oopsy! Try again next time!"
    color = COLORS['primary'] if result else COLORS['accent']
    f_surf = font_q.render(msg, True, color)
    f_rect = f_surf.get_rect(center=(1280 // 2, 360))
    screen.blit(f_surf, f_rect)
    pygame.display.flip()
    pygame.time.delay(1500)
    
    return result
