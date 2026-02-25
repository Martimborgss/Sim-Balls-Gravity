import pygame
import random
import math
from functions import *

pygame.init()

WIDTH = 1920
HEIGHT = 1080
FLAGS = pygame.NOFRAME | pygame.DOUBLEBUF
screen = pygame.display.set_mode((WIDTH, HEIGHT), FLAGS, vsync=1)
pygame.display.set_caption("Simulator - Rigid Balls")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)

GRAVITY = 0.81

balls = []
MAX_BALLS = 200
ball_count = 0
selected_ball = None

# --- UI SETUP ---
ui_font = pygame.font.SysFont("Arial", 18, bold=True)
title_font = pygame.font.SysFont("Arial", 22, bold=True)

ui_panel = pygame.Rect(20, 20, 280, 360)
btn_add_10 = pygame.Rect(40, 110, 240, 35)
btn_clear = pygame.Rect(40, 155, 240, 35)
btn_fric_up = pygame.Rect(250, 240, 30, 30)
btn_fric_dn = pygame.Rect(210, 240, 30, 30)
btn_bnc_up = pygame.Rect(250, 290, 30, 30)
btn_bnc_dn = pygame.Rect(210, 290, 30, 30)

def spawn_random_ball():
    """Helper function to spawn a ball safely."""
    global ball_count
    if ball_count < MAX_BALLS:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if ui_panel.collidepoint((mouse_x, mouse_y)):
            mouse_x, mouse_y = WIDTH // 2, HEIGHT // 2
            
        random_radius = random.randint(20, 60)
        random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        random_bounce = random.uniform(0.4, 0.95)
        random_friction = random.uniform(0.85, 0.99) 
        
        new_ball = create_ball(mouse_x, mouse_y, random_radius, random_color, random_bounce)
        new_ball["friction"] = random_friction
        balls.append(new_ball)
        ball_count += 1

def draw_button(surface, rect, text, color, hover_color):
    """Draws an interactive button."""
    mouse_pos = pygame.mouse.get_pos()
    current_color = hover_color if rect.collidepoint(mouse_pos) else color
    pygame.draw.rect(surface, current_color, rect, border_radius=5)
    pygame.draw.rect(surface, BLACK, rect, 2, border_radius=5)
    text_surf = ui_font.render(text, True, BLACK)
    surface.blit(text_surf, text_surf.get_rect(center=rect.center))

def handle_ui_events(event):
    """Processes UI clicks. Returns True if the UI consumed the click."""
    global ball_count, selected_ball
    
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = event.pos
        if ui_panel.collidepoint(mouse_pos):
            if btn_add_10.collidepoint(mouse_pos):
                for _ in range(10): spawn_random_ball()
            elif btn_clear.collidepoint(mouse_pos):
                balls.clear()
                ball_count = 0
                selected_ball = None
            elif selected_ball:
                if btn_fric_up.collidepoint(mouse_pos):
                    selected_ball["friction"] = min(1.0, selected_ball["friction"] + 0.05)
                elif btn_fric_dn.collidepoint(mouse_pos):
                    selected_ball["friction"] = max(0.0, selected_ball["friction"] - 0.05)
                elif btn_bnc_up.collidepoint(mouse_pos):
                    selected_ball["bounce_factor"] = min(1.5, selected_ball["bounce_factor"] + 0.05)
                elif btn_bnc_dn.collidepoint(mouse_pos):
                    selected_ball["bounce_factor"] = max(0.0, selected_ball["bounce_factor"] - 0.05)
            return True # The UI ate the click! Don't pass to physics.
    return False

def draw_debug_ui(screen, current_fps):
    """Draws the entire debug menu."""
    s = pygame.Surface((ui_panel.width, ui_panel.height))
    s.set_alpha(200)
    s.fill(DARK_GRAY)
    screen.blit(s, (ui_panel.x, ui_panel.y))
    pygame.draw.rect(screen, WHITE, ui_panel, 2) 

    screen.blit(title_font.render("DEBUG MENU", True, WHITE), (ui_panel.x + 80, ui_panel.y + 10))
    screen.blit(ui_font.render(f"FPS: {int(current_fps)}", True, YELLOW if current_fps < 50 else WHITE), (40, 50))
    screen.blit(ui_font.render(f"Balls: {ball_count} / {MAX_BALLS}", True, WHITE), (40, 80))

    draw_button(screen, btn_add_10, "Add 10 Balls", GRAY, WHITE)
    draw_button(screen, btn_clear, "Remove All Balls", (255, 100, 100), (255, 150, 150))

    pygame.draw.line(screen, WHITE, (40, 205), (280, 205), 2)
    screen.blit(ui_font.render("SELECTED BALL", True, WHITE), (40, 215))

    if selected_ball:
        screen.blit(ui_font.render(f"Friction: {selected_ball['friction']:.2f}", True, WHITE), (40, 245))
        draw_button(screen, btn_fric_dn, "-", GRAY, WHITE)
        draw_button(screen, btn_fric_up, "+", GRAY, WHITE)

        screen.blit(ui_font.render(f"Bounce: {selected_ball['bounce_factor']:.2f}", True, WHITE), (40, 295))
        draw_button(screen, btn_bnc_dn, "-", GRAY, WHITE)
        draw_button(screen, btn_bnc_up, "+", GRAY, WHITE)
    else:
        screen.blit(ui_font.render("Click a ball to edit.", True, GRAY), (40, 260))

# --- Initial Spawn ---
spawn_random_ball()

# ==========================================
#             MAIN GAME LOOP
# ==========================================
running = True
while running:
    # --- 1. Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            spawn_random_ball()
            
        # to disable the UI, comment out the line below and replace with: ui_clicked = False
        ui_clicked = handle_ui_events(event)
        
        # Only check ball clicks if the UI didn't consume the event
        if not ui_clicked:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if event.button == 1: # Left Click: Select ball
                    clicked_any = False
                    for ball in reversed(balls):
                        if math.sqrt((mouse_pos[0] - ball["x"])**2 + (mouse_pos[1] - ball["y"])**2) <= ball["radius"]:
                            selected_ball = ball
                            clicked_any = True
                            break
                    if not clicked_any: selected_ball = None 
                            
                elif event.button == 3: # Right Click: Delete ball
                    for ball in reversed(balls):
                        if math.sqrt((mouse_pos[0] - ball["x"])**2 + (mouse_pos[1] - ball["y"])**2) <= ball["radius"]:
                            if selected_ball == ball: selected_ball = None
                            balls.remove(ball)
                            ball_count -= 1
                            break 
                            
            for ball in balls:
                handle_mouse(event, ball)

    # --- 2. Update Logic ---
    for ball in balls:
        update_inertia(ball)
        apply_physics(ball, GRAVITY)
        
    calculate_neighbors(balls)
    
    SOLVER_ITERATIONS = 8
    for _ in range(SOLVER_ITERATIONS):
        check_all_collisions(balls, WIDTH, HEIGHT)

    # --- 3. Drawing / Rendering ---
    screen.fill((30, 30, 40)) 
    
    for ball in balls:
        draw_ball(screen, ball)
        if ball == selected_ball:
            pygame.draw.circle(screen, YELLOW, (int(ball["x"]), int(ball["y"])), ball["radius"], 4)
            
    # to disable the UI, comment out the line below!
    #draw_debug_ui(screen, clock.get_fps())
        
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()