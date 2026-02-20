import pygame
import math

def create_ball(x, y, radius, color, bounce=0.8):
    """Creates a dictionary with all the ball's properties."""
    return {
        "x": x, 
        "y": y, 
        "radius": radius, 
        "color": color,
        "dragging": False, 
        "offset_x": 0, 
        "offset_y": 0,
        "vel_x": 0, 
        "vel_y": 0, 
        "prev_x": x, 
        "prev_y": y,
        "bounce_factor": bounce,           
        "nearby_balls": []
    }

def handle_mouse(event, ball):
    """Handles mouse clicks and movement for dragging the ball."""
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_x, mouse_y = event.pos
        distance = math.sqrt((mouse_x - ball["x"])**2 + (mouse_y - ball["y"])**2)
        if distance <= ball["radius"]:
            ball["dragging"] = True
            ball["offset_x"] = ball["x"] - mouse_x
            ball["offset_y"] = ball["y"] - mouse_y
            
            # Stop the ball when grabbed
            ball["vel_x"] = 0
            ball["vel_y"] = 0

    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        ball["dragging"] = False

    elif event.type == pygame.MOUSEMOTION:
        if ball["dragging"]:
            mouse_x, mouse_y = event.pos
            ball["x"] = mouse_x + ball["offset_x"]
            ball["y"] = mouse_y + ball["offset_y"]

def update_inertia(ball):
    """Calculates throwing velocity based on mouse movement."""
    if ball["dragging"]:
        ball["vel_x"] = ball["x"] - ball["prev_x"]
        ball["vel_y"] = ball["y"] - ball["prev_y"]
        
        ball["prev_x"] = ball["x"]
        ball["prev_y"] = ball["y"]

def apply_physics(ball, gravity):
    """Applies gravity and updates position."""
    if not ball["dragging"]:
        ball["vel_y"] += gravity
        ball["x"] += ball["vel_x"]
        ball["y"] += ball["vel_y"]

def calculate_neighbors(balls):
    """Finds balls that are close (within 1 extra radius of distance)."""
    for ball in balls:
        ball["nearby_balls"].clear()

    for i in range(len(balls)):
        b1 = balls[i]
        for j in range(i + 1, len(balls)):
            b2 = balls[j]

            dx = b2["x"] - b1["x"]
            dy = b2["y"] - b1["y"]
            
            distance_sq = dx**2 + dy**2
            
            sum_radii = b1["radius"] + b2["radius"]
            max_distance = sum_radii + max(b1["radius"], b2["radius"])

            if distance_sq < max_distance**2:
                b1["nearby_balls"].append(b2)
                b2["nearby_balls"].append(b1)

def draw_ball(screen, ball):
    """Draws the ball as a perfect circle."""
    center_x = int(ball["x"])
    center_y = int(ball["y"])
    pygame.draw.circle(screen, ball["color"], (center_x, center_y), ball["radius"])

# --- collisions --- 

def _collide_with_walls(ball, screen_width, screen_height):
    """Helper function: Handles collisions with screen edges."""
    # Horizontal boundaries
    if ball["x"] - ball["radius"] < 0:
        ball["x"] = ball["radius"]
        ball["vel_x"] = -ball["vel_x"] * ball["bounce_factor"]
    elif ball["x"] + ball["radius"] > screen_width:
        ball["x"] = screen_width - ball["radius"]
        ball["vel_x"] = -ball["vel_x"] * ball["bounce_factor"]

    # Vertical boundaries (Floor and Ceiling)
    if ball["y"] - ball["radius"] < 0:
        ball["y"] = ball["radius"]
        ball["vel_y"] = -ball["vel_y"] * ball["bounce_factor"]
        
    elif ball["y"] + ball["radius"] > screen_height:
        ball["y"] = screen_height - ball["radius"]
        ball["vel_y"] = -ball["vel_y"] * ball["bounce_factor"]
        
        # System to stop micro-bouncing
        if abs(ball["vel_y"]) < 1:
            ball["vel_y"] = 0
            
        # Ground friction
        ball["vel_x"] *= 0.95

def _collide_with_ball(ball, neighbor):
    """Helper function: Handles math for collision between two balls."""
    dx = neighbor["x"] - ball["x"]
    dy = neighbor["y"] - ball["y"]
    distance = math.sqrt(dx**2 + dy**2)
    sum_radii = ball["radius"] + neighbor["radius"]

    if distance < sum_radii:
        if distance == 0:
            distance = 0.01
            dx = 0.01

        nx = dx / distance
        ny = dy / distance

        # --- 1. Separate the balls (Resolve Overlap) ---
        overlap = sum_radii - distance
        
        mass_ratio_ball = neighbor["radius"] / sum_radii
        mass_ratio_neighbor = ball["radius"] / sum_radii

        ball["x"] -= nx * overlap * mass_ratio_ball
        ball["y"] -= ny * overlap * mass_ratio_ball
        neighbor["x"] += nx * overlap * mass_ratio_neighbor
        neighbor["y"] += ny * overlap * mass_ratio_neighbor

        # --- 2. Transfer Energy (Bounce) ---
        rv_x = neighbor["vel_x"] - ball["vel_x"]
        rv_y = neighbor["vel_y"] - ball["vel_y"]

        vel_along_normal = rv_x * nx + rv_y * ny

        # Only bounce if they are moving towards each other
        if vel_along_normal > 0:
            return

        bounce = min(ball["bounce_factor"], neighbor["bounce_factor"])
        m1 = ball["radius"]
        m2 = neighbor["radius"]

        impulse = -(1 + bounce) * vel_along_normal
        impulse /= (1 / m1) + (1 / m2)

        impulse_x = impulse * nx
        impulse_y = impulse * ny

        ball["vel_x"] -= impulse_x / m1
        ball["vel_y"] -= impulse_y / m1
        neighbor["vel_x"] += impulse_x / m2
        neighbor["vel_y"] += impulse_y / m2

def check_all_collisions(balls, screen_width, screen_height):
    """Narrow Phase: Resolves ALL collisions (walls and neighbors) in one go."""
    for ball in balls:
        # 1. Check walls
        _collide_with_walls(ball, screen_width, screen_height)
        
        # 2. Check neighbors
        for neighbor in ball["nearby_balls"]:
            if id(ball) < id(neighbor):
                _collide_with_ball(ball, neighbor)