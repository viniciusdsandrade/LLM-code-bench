import math
import pygame
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in a Spinning Hexagon")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HEX_COLOR = (50, 200, 50)
BALL_COLOR = (200, 50, 50)

# Physics parameters
gravity = 500.0  # pixels per second^2
ball_radius = 15
ball_pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
ball_vel = pygame.math.Vector2(200, -150)  # initial velocity in pixels/sec

# Friction / damping (applied each frame)
velocity_damping = 0.999  # a bit of air friction

# Collision restitution (bounciness)
restitution = 0.9

# Hexagon parameters
hex_center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
hex_radius = 250  # distance from center to vertex
num_sides = 6
hex_rotation = 0  # current rotation angle (radians)
hex_angular_speed = 1.0  # radians per second (constant)


def get_hexagon_vertices(center, radius, rotation, sides):
    """Return list of vertices for a regular polygon."""
    vertices = []
    for i in range(sides):
        angle = 2 * math.pi * i / sides + rotation
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        vertices.append(pygame.math.Vector2(x, y))
    return vertices


def nearest_point_on_segment(p, a, b):
    """Return the nearest point on the line segment ab to point p."""
    ab = b - a
    if ab.length_squared() == 0:
        return a
    t = (p - a).dot(ab) / ab.length_squared()
    t = max(0, min(1, t))
    return a + t * ab


def wall_velocity_at_point(point, center, angular_speed):
    """
    For a point on the rotating hexagon, compute its velocity vector due to rotation.
    The velocity is perpendicular to the radius vector from the center.
    """
    r = point - center
    # In 2D, the tangential velocity from a rotation is:
    # v = angular_speed * r rotated by 90 degrees.
    # Rotating (rx, ry) by 90° gives (-ry, rx)
    return angular_speed * pygame.math.Vector2(-r.y, r.x)


def reflect_velocity(ball_velocity, normal, wall_vel):
    """
    Reflect the ball's velocity relative to the wall.
    That is, compute the relative velocity, reflect it and add back the wall velocity.
    """
    rel_vel = ball_velocity - wall_vel
    vn = rel_vel.dot(normal)
    if vn >= 0:
        # The ball is moving away from the wall already.
        return ball_velocity
    # Reflect the relative velocity along the normal.
    rel_vel = rel_vel - (1 + restitution) * vn * normal
    return wall_vel + rel_vel


def handle_collisions(ball_pos, ball_vel, vertices):
    """
    Check for collision of the ball (a circle) with each edge of the hexagon.
    If a collision is detected, adjust ball_pos and ball_vel accordingly.
    """
    collided = False
    for i in range(len(vertices)):
        a = vertices[i]
        b = vertices[(i + 1) % len(vertices)]
        # Find the nearest point on this edge to the ball's center.
        nearest = nearest_point_on_segment(ball_pos, a, b)
        diff = ball_pos - nearest
        dist = diff.length()

        if dist < ball_radius:
            collided = True
            # Avoid division by zero.
            if dist == 0:
                normal = pygame.math.Vector2(0, -1)
            else:
                normal = diff.normalize()
            # Compute the velocity of the wall at the collision point.
            wall_vel = wall_velocity_at_point(nearest, hex_center, hex_angular_speed)
            # Reflect the ball velocity (in the frame moving with the wall).
            ball_vel = reflect_velocity(ball_vel, normal, wall_vel)
            # Correct the ball position so it is just outside the wall.
            penetration = ball_radius - dist
            ball_pos += normal * penetration

    return ball_pos, ball_vel


def main():
    global ball_pos, ball_vel, hex_rotation

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds.

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update hexagon rotation.
        hex_rotation += hex_angular_speed * dt

        # Update ball physics
        # Apply gravity (only vertical acceleration)
        ball_vel.y += gravity * dt

        # Update ball position.
        ball_pos += ball_vel * dt

        # Apply damping (simulate friction/air resistance).
        ball_vel *= velocity_damping

        # Get current hexagon vertices.
        vertices = get_hexagon_vertices(hex_center, hex_radius, hex_rotation, num_sides)

        # Handle collisions with the hexagon walls.
        ball_pos, ball_vel = handle_collisions(ball_pos, ball_vel, vertices)

        # Clear the screen.
        screen.fill(BLACK)

        # Draw the hexagon.
        pygame.draw.polygon(screen, HEX_COLOR, [(v.x, v.y) for v in vertices], 3)

        # Draw the ball.
        pygame.draw.circle(screen, BALL_COLOR, (int(ball_pos.x), int(ball_pos.y)), ball_radius)

        # Update display.
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
