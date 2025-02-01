import pygame
import math
import sys

pygame.init()

# ---------------------------
#  Basic settings
# ---------------------------

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in Spinning Hexagon")
clock = pygame.time.Clock()

# Ball settings
ball_radius = 15
ball_position = [WIDTH // 2, HEIGHT // 4]  # start near top-center
ball_velocity = [100.0, 0.0]  # initial velocity (px/s)
gravity = 500.0  # px/s^2 downward
air_friction = 0.0005  # fraction of velocity lost each frame
bounce_friction = 0.9  # fraction of velocity retained after bounce

# Hexagon settings
hex_radius = 200  # distance from center to each vertex
hex_center = (WIDTH // 2, HEIGHT // 2)
rotation_speed = 30  # degrees per second
current_angle = 0.0


# ---------------------------
#  Helper functions
# ---------------------------

def rotate_point(px, py, cx, cy, angle_degrees):
    """
    Rotate point (px, py) around center (cx, cy) by angle_degrees.
    Returns the new (x, y).
    """
    angle_radians = math.radians(angle_degrees)
    # Translate point to origin relative to center
    tx, ty = px - cx, py - cy

    # Apply rotation
    rx = tx * math.cos(angle_radians) - ty * math.sin(angle_radians)
    ry = tx * math.sin(angle_radians) + ty * math.cos(angle_radians)

    # Translate back
    return rx + cx, ry + cy


def get_hexagon_vertices(cx, cy, radius, angle_degrees):
    """
    Get the 6 vertices of a regular hexagon of given 'radius' (distance from center to vertex)
    centered at (cx, cy). The hexagon is rotated by 'angle_degrees'.
    Returns a list of (x, y) vertex coordinates.
    """
    vertices = []
    for i in range(6):
        # Each vertex is 60 degrees apart for a hexagon
        theta = 60 * i + angle_degrees
        # Convert polar to Cartesian
        vx = cx + radius * math.cos(math.radians(theta))
        vy = cy + radius * math.sin(math.radians(theta))
        vertices.append((vx, vy))
    return vertices


def reflect(velocity, normal):
    """
    Reflect velocity vector across the given normal vector.
    normal should be normalized.
    """
    vx, vy = velocity
    nx, ny = normal
    # Dot product
    dot = vx * nx + vy * ny
    # Reflection: v' = v - 2*(v·n)*n
    rx = vx - 2 * dot * nx
    ry = vy - 2 * dot * ny
    return [rx, ry]


def normalize(vx, vy):
    length = math.sqrt(vx * vx + vy * vy)
    if length == 0:
        return 0, 0
    return vx / length, vy / length


def line_normal(p1, p2):
    """
    Return the outward normal for the line p1->p2 if the polygon vertices go
    in clockwise order. We'll use the "right-hand" normal for the edge direction.
    (This would need to be consistent with how vertices are defined to ensure
    the normal points inside or outside. In this example, we’ll treat it carefully
    to get an inward normal.)
    """
    (x1, y1), (x2, y2) = p1, p2
    # Edge vector
    ex, ey = (x2 - x1, y2 - y1)

    # A 2D vector perpendicular can be (ey, -ex) or (-ey, ex).
    # For a regular hex in CCW order, the inside normal is (ey, -ex).
    nx, ny = (ey, -ex)
    # Normalize
    return normalize(nx, ny)


# ---------------------------
#  Main game loop
# ---------------------------

running = True
while running:
    dt = clock.tick(60) / 1000.0  # dt in seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update hexagon rotation
    current_angle += rotation_speed * dt
    current_angle %= 360

    # Update ball physics
    # Apply gravity
    ball_velocity[1] += gravity * dt

    # Optionally apply in-air friction (simple velocity dampening)
    ball_velocity[0] *= (1.0 - air_friction)
    ball_velocity[1] *= (1.0 - air_friction)

    # Update position
    ball_position[0] += ball_velocity[0] * dt
    ball_position[1] += ball_velocity[1] * dt

    # Get current hexagon vertices
    hex_vertices = get_hexagon_vertices(hex_center[0], hex_center[1],
                                        hex_radius, current_angle)

    # Check collisions with each edge of the hexagon
    # The hexagon edges are formed by consecutive vertex pairs
    for i in range(len(hex_vertices)):
        p1 = hex_vertices[i]
        p2 = hex_vertices[(i + 1) % len(hex_vertices)]

        # We want to see if the ball center is outside this edge.
        # We'll do this by computing the signed distance of the ball center to the line.
        # If the distance is > ball_radius on the "outside" side, we skip.
        # Otherwise, we reflect. We must figure out which side is "inside" vs "outside."

        # Vector from p1 to p2
        edge_vec = (p2[0] - p1[0], p2[1] - p1[1])
        # Normal (we want inward normal, so we define consistently with the vertex order)
        nx, ny = line_normal(p1, p2)

        # We can compute the line normal form:
        # For line p1->p2, param eq: p1 + t*(edge_vec)
        # The normal direction is (nx, ny). The line eq in normal form:
        #   n . (X - p1) = 0  =>  n . X = n . p1
        n_dot_p1 = nx * p1[0] + ny * p1[1]
        # Signed distance of ball center to line
        dist_to_line = (nx * ball_position[0] + ny * ball_position[1]) - n_dot_p1

        # If dist_to_line is negative, that means the center is "outside" if the normal is facing inside,
        # or "inside" if the normal is reversed. We want to handle that carefully.
        # In our line_normal function, we took the "inward" normal for a CCW hex.
        # So, if dist_to_line > 0, the ball is outside. We check for collision if dist_to_line < ball_radius.

        if dist_to_line > 0:
            # Potential outside
            if dist_to_line < ball_radius:
                # There's a collision: ball is penetrating the wall.
                # Move the ball out of the wall
                penetration = ball_radius - dist_to_line
                # Shift the ball back along the normal
                ball_position[0] -= nx * penetration
                ball_position[1] -= ny * penetration
                # Reflect velocity around the inward normal
                ball_velocity = reflect(ball_velocity, (nx, ny))
                # Apply bounce friction
                ball_velocity[0] *= bounce_friction
                ball_velocity[1] *= bounce_friction

    # ---------------------------
    #  Rendering
    # ---------------------------
    screen.fill((30, 30, 30))

    # Draw hexagon
    pygame.draw.polygon(screen, (200, 200, 200), hex_vertices, width=2)

    # Draw ball
    pygame.draw.circle(screen, (255, 100, 100),
                       (int(ball_position[0]), int(ball_position[1])),
                       ball_radius)

    # Flip the display
    pygame.display.flip()

pygame.quit()
sys.exit()
