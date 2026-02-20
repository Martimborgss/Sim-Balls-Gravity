import pygame
import math

def create_ball(x, y, radius, color):
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
        "scale_x": 1.0, 
        "scale_y": 1.0 
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

def check_boundaries(ball, screen_width, screen_height):
    """Prevents the ball from leaving the screen and handles bouncing."""
    bounce_factor = 0.8 

    # Horizontal boundaries
    if ball["x"] - ball["radius"] < 0:
        ball["x"] = ball["radius"]
        ball["vel_x"] = -ball["vel_x"] * bounce_factor
    elif ball["x"] + ball["radius"] > screen_width:
        ball["x"] = screen_width - ball["radius"]
        ball["vel_x"] = -ball["vel_x"] * bounce_factor

    # Vertical boundaries
    if ball["y"] - ball["radius"] < 0:
        ball["y"] = ball["radius"]
        ball["vel_y"] = -ball["vel_y"] * bounce_factor
        
    elif ball["y"] + ball["radius"] > screen_height:
        impact = abs(ball["vel_y"])
        
        # Deformation (Squash)
        if impact > 2:
            deformation = min(impact * 0.03, 0.6)
            ball["scale_y"] = 1.0 - deformation
            ball["scale_x"] = 1.0 + deformation

        ball["y"] = screen_height - ball["radius"]
        ball["vel_y"] = -ball["vel_y"] * bounce_factor
        
        if abs(ball["vel_y"]) < 1:
            ball["vel_y"] = 0
            
        # Ground friction
        ball["vel_x"] *= 0.95

def update_shape(ball):
    """Gradually restores the ball to its original circular shape."""
    ball["scale_x"] += (1.0 - ball["scale_x"]) * 0.1
    ball["scale_y"] += (1.0 - ball["scale_y"]) * 0.1

def draw_ball(screen, ball):
    """Draws the ball as an ellipse to allow for deformation."""
    rx = ball["radius"] * ball["scale_x"]
    ry = ball["radius"] * ball["scale_y"]

    visual_center_y = ball["y"] + (ball["radius"] - ry)

    rect_x = int(ball["x"] - rx)
    rect_y = int(visual_center_y - ry)
    width = int(rx * 2)
    height = int(ry * 2)

    pygame.draw.ellipse(screen, ball["color"], (rect_x, rect_y, width, height))