import pygame
from functions import *

pygame.init()

WIDTH = 1920
HEIGHT = 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Simulator - English Version")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

GRAVITY = 0.981

my_ball = create_ball(WIDTH // 2, HEIGHT // 2, 40, BLUE)

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
        
        # Pass the event and our ball to the handler
        handle_mouse(event, my_ball)

    # --- Update Logic ---
    update_inertia(my_ball)
    apply_physics(my_ball, GRAVITY)
    check_boundaries(my_ball, WIDTH, HEIGHT)
    update_shape(my_ball)

    # --- Drawing / Rendering ---
    screen.fill(WHITE)
    draw_ball(screen, my_ball)
    pygame.display.flip()

    # --- Frame Rate Control ---
    clock.tick(FPS)

pygame.quit()