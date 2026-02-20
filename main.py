import pygame
import random
import math
from functions import *

pygame.init()

WIDTH = 1920
HEIGHT = 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Simulator - Rigid Balls")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

GRAVITY = 0.981

balls = []
balls.append(create_ball(WIDTH // 2, HEIGHT // 2, 40, BLUE))

# --- Main Game Loop ---
running = True
while running:
    
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH = event.w
            HEIGHT = event.h
            
        # Press SPACE to spawn a new ball
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            random_radius = random.randint(20, 60)
            random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            
            # Generate a random bounce factor but NO squash
            random_bounce = random.uniform(0.4, 0.95)
            
            new_ball = create_ball(mouse_x, mouse_y, random_radius, random_color, random_bounce)
            balls.append(new_ball)
            
        # Right Click to remove ONE ball
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: 
            mouse_x, mouse_y = event.pos
            for ball in reversed(balls):
                distance = math.sqrt((mouse_x - ball["x"])**2 + (mouse_y - ball["y"])**2)
                if distance <= ball["radius"]:
                    balls.remove(ball)
                    break 
        
        for ball in balls:
            handle_mouse(event, ball)

    # --- Update Logic ---
    for ball in balls:
        update_inertia(ball)
        apply_physics(ball, GRAVITY)
        
    calculate_neighbors(balls)
    SOLVER_ITERATIONS = 8
    for _ in range(SOLVER_ITERATIONS):
        check_all_collisions(balls, WIDTH, HEIGHT)

    # --- Drawing / Rendering ---
    screen.fill(WHITE)
    
    for ball in balls:
        draw_ball(screen, ball)
        
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()