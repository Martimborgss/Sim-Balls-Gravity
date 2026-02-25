import pygame
import math
from collections import defaultdict

def create_ball(x, y, radius, color, bounce=0.8, friction=0.98):
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
        "nearby_balls": [],

        "friction": friction,
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
    """Finds balls that are close using a spatial hash.

    Uses a grid to reduce pair tests from O(n^2) to roughly O(n).
    CELL_SIZE is chosen from the maximum ball diameter to keep neighbors
    within nearby cells.
    """
    for ball in balls:
        ball["nearby_balls"].clear()

    if not balls:
        return

    # choose cell size based on largest ball to keep neighbors local
    max_r = max((b["radius"] for b in balls), default=32)
    CELL_SIZE = max(48, int(max_r * 2))

    grid = defaultdict(list)
    for b in balls:
        cx = int(b["x"]) // CELL_SIZE
        cy = int(b["y"]) // CELL_SIZE
        grid[(cx, cy)].append(b)

    # Check a ball against its cell and adjacent cells
    for b in balls:
        cx = int(b["x"]) // CELL_SIZE
        cy = int(b["y"]) // CELL_SIZE
        bid = id(b)
        for nx in (cx - 1, cx, cx + 1):
            for ny in (cy - 1, cy, cy + 1):
                for other in grid.get((nx, ny), ()):  # neighboring cell
                    if other is b:
                        continue
                    oid = id(other)
                    # compute vector and squared distance
                    dx = other["x"] - b["x"]
                    dy = other["y"] - b["y"]
                    distance_sq = dx * dx + dy * dy
                    sum_radii = b["radius"] + other["radius"]
                    # include a small neighborhood margin to catch near contacts
                    max_distance = sum_radii + max(b["radius"], other["radius"])
                    if distance_sq < max_distance * max_distance:
                        # add pair once (symmetrically) to avoid asymmetry in solver
                        if bid < oid:
                            b["nearby_balls"].append(other)
                            other["nearby_balls"].append(b)

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
            
        # --- NEW: Use the ball's unique ground friction! ---
        ball["vel_x"] *= ball["friction"]

def _collide_with_ball(ball, neighbor):
    """Helper function: Handles math for collision between two balls."""
    # cache lookups in locals to reduce dict overhead
    bx = ball["x"]
    by = ball["y"]
    nx_ = neighbor["x"]
    ny_ = neighbor["y"]
    dx = nx_ - bx
    dy = ny_ - by
    distance = math.sqrt(dx * dx + dy * dy)
    sum_radii = ball["radius"] + neighbor["radius"]

    if distance >= sum_radii:
        return

    if distance == 0:
        distance = 0.01
        dx = 0.01

    # normal vector
    nx_unit = dx / distance
    ny_unit = dy / distance

    # --- 1. Separate the balls (Resolve Overlap) ---
    overlap = sum_radii - distance
    mass_ratio_ball = neighbor["radius"] / sum_radii
    mass_ratio_neighbor = ball["radius"] / sum_radii

    # apply position corrections directly
    ball["x"] = bx - nx_unit * overlap * mass_ratio_ball
    ball["y"] = by - ny_unit * overlap * mass_ratio_ball
    neighbor["x"] = nx_ + nx_unit * overlap * mass_ratio_neighbor
    neighbor["y"] = ny_ + ny_unit * overlap * mass_ratio_neighbor

    # --- 2. Transfer Energy (Bounce) ---
    rvx = neighbor["vel_x"] - ball["vel_x"]
    rvy = neighbor["vel_y"] - ball["vel_y"]
    vel_along_normal = rvx * nx_unit + rvy * ny_unit

    # Only bounce if they are moving towards each other
    if vel_along_normal > 0:
        return

    bounce = min(ball["bounce_factor"], neighbor["bounce_factor"])
    m1 = ball["radius"]
    m2 = neighbor["radius"]

    impulse = -(1 + bounce) * vel_along_normal
    impulse /= (1 / m1) + (1 / m2)

    imp_x = impulse * nx_unit
    imp_y = impulse * ny_unit

    ball["vel_x"] -= imp_x / m1
    ball["vel_y"] -= imp_y / m1
    neighbor["vel_x"] += imp_x / m2
    neighbor["vel_y"] += imp_y / m2

def check_all_collisions(balls, screen_width, screen_height):
    """Narrow Phase: Resolves ALL collisions (walls and neighbors) in one go."""
    for ball in balls:
        # 1. Check walls
        _collide_with_walls(ball, screen_width, screen_height)

    # 2. Resolve pair collisions once per pair. nearby_balls may contain both
    # directions; use id ordering to ensure single resolution per pair.
    for ball in balls:
        bid = id(ball)
        for neighbor in ball["nearby_balls"]:
            if bid < id(neighbor):
                _collide_with_ball(ball, neighbor)