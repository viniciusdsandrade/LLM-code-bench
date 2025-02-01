import pygame
import math
from pygame.math import Vector2

pygame.init()

# Screen settings
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Hexagon parameters
center = Vector2(width // 2, height // 2)
hex_radius = 200
rotation_speed = 1.5  # radians per second

# Ball parameters
ball_radius = 10
ball_pos = Vector2(center.x, center.y - hex_radius + ball_radius + 20)
ball_vel = Vector2(2, 0)  # Initial slight horizontal velocity
gravity = Vector2(0, 500)
friction_coeff = 0.85  # Energy retention after bounce
air_friction = 0.999  # Air resistance factor


def get_hexagon_vertices(center, radius, rotation):
    """Generate hexagon vertices with current rotation"""
    vertices = []
    for i in range(6):
        angle_rad = math.radians(60 * i) + rotation
        x = center.x + radius * math.cos(angle_rad)
        y = center.y + radius * math.sin(angle_rad)
        vertices.append(Vector2(x, y))
    return vertices


def closest_point_on_segment(p, a, b):
    """Find closest point on line segment a-b to point p"""
    ap = p - a
    ab = b - a
    t = ap.dot(ab) / ab.dot(ab)
    t = max(0, min(1, t))
    return a + t * ab


running = True
while running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update hexagon rotation
    current_rotation = pygame.time.get_ticks() * 0.001 * rotation_speed

    # Apply physics to ball
    ball_vel += gravity * dt
    ball_vel *= air_friction ** (dt * 60)  # Adjust air friction for frame rate
    ball_pos += ball_vel * dt

    # Get current hexagon vertices
    vertices = get_hexagon_vertices(center, hex_radius, current_rotation)

    # Collision detection and response
    collision_occurred = False
    for i in range(6):
        if collision_occurred:
            break

        a = vertices[i]
        b = vertices[(i + 1) % 6]

        # Find closest point on the edge
        closest = closest_point_on_segment(ball_pos, a, b)
        to_ball = ball_pos - closest
        distance = to_ball.length()

        if distance < ball_radius:
            # Calculate edge normal
            edge = b - a
            normal = Vector2(edge.y, -edge.x).normalize()

            # Ensure normal points inward
            midpoint = (a + b) * 0.5
            center_to_mid = center - midpoint
            if normal.dot(center_to_mid) < 0:
                normal = -normal

            # Calculate wall velocity at collision point
            rel_pos = closest - center
            wall_vel = Vector2(-rotation_speed * rel_pos.y, rotation_speed * rel_pos.x)

            # Calculate relative velocity
            relative_vel = ball_vel - wall_vel

            # Reflect velocity with energy loss
            normal_vel = relative_vel.dot(normal)
            if normal_vel < 0:  # Only collide when moving towards the wall
                tangent_vel = relative_vel - normal * normal_vel
                relative_vel = tangent_vel - normal_vel * friction_coeff * normal
                ball_vel = relative_vel + wall_vel

                # Position correction
                penetration = ball_radius - distance
                ball_pos += normal * penetration * 1.1

                collision_occurred = True

    # Drawing
    screen.fill(BLACK)

    # Draw hexagon
    pygame.draw.polygon(screen, WHITE, [(v.x, v.y) for v in vertices], 2)

    # Draw ball
    pygame.draw.circle(screen, RED, (int(ball_pos.x), int(ball_pos.y)), ball_radius)

    pygame.display.flip()

pygame.quit()
