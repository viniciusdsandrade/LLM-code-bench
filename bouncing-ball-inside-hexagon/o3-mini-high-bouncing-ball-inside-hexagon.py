import pygame
import math
import sys

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Gravity (pixels per second²)
GRAVITY = 500.0

# Coefficient of restitution (<1 loses energy on bounce)
RESTITUTION = 0.9

# Friction coefficient on tangential component during collision (0 = no friction)
FRICTION_COEFF = 0.1

# Hexagon properties
HEXAGON_RADIUS = 250
# Angular speed in radians per second (e.g. 30°/sec)
HEXAGON_ANGULAR_VELOCITY = math.radians(30)
HEXAGON_CENTER = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)

# Ball properties
BALL_RADIUS = 15
ball = {
    'pos': pygame.math.Vector2(WIDTH / 2, HEIGHT / 2 - 100),
    'vel': pygame.math.Vector2(200, 0),
    'radius': BALL_RADIUS,
}


def compute_hexagon_vertices(center, radius, angle_offset):
    """
    Compute the six vertices of a regular hexagon centered at 'center' with the given radius.
    The hexagon is rotated by angle_offset (in radians).
    """
    vertices = []
    for i in range(6):
        angle = angle_offset + i * (2 * math.pi / 6)
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        vertices.append(pygame.math.Vector2(x, y))
    return vertices


def collide_ball_with_segment(ball, A, B, hex_center, angular_velocity):
    """
    Check and resolve a collision between the ball (a circle) and the line segment AB.
    Because the hexagon rotates, we compute the wall’s velocity at the collision point.

    If a collision is detected (i.e. the distance from the ball’s center to the line is
    less than the ball’s radius), we push the ball out and adjust its velocity. The velocity
    correction is done in the wall’s instantaneous reference frame.
    """
    P = ball['pos']
    # Compute projection of P onto the segment AB
    AB = B - A
    AB_length_sq = AB.length_squared()
    if AB_length_sq == 0:
        return False  # Avoid division by zero for degenerate segment

    t = (P - A).dot(AB) / AB_length_sq
    # Clamp t so the closest point lies on the segment
    t = max(0, min(1, t))
    closest_point = A + t * AB

    # Compute the distance from the ball’s center to the closest point on the segment
    distance = (P - closest_point).length()
    if distance < ball['radius']:
        # The ball overlaps the wall – determine how far it penetrated.
        penetration = ball['radius'] - distance

        # Determine the collision normal (from wall to ball)
        if distance != 0:
            normal = (P - closest_point).normalize()
        else:
            normal = pygame.math.Vector2(0, -1)  # Arbitrary if exactly overlapping

        # Push the ball out so it sits exactly at the surface
        ball['pos'] += normal * penetration

        # --- Collision response: account for the wall’s motion ---
        # A rotating hexagon means each point on its perimeter has a tangential velocity.
        # For a point with position r (relative to the center), its velocity is given by:
        #     v = angular_velocity * (-r_y, r_x)
        rel_point = closest_point - hex_center
        wall_vel = angular_velocity * pygame.math.Vector2(-rel_point.y, rel_point.x)

        # Compute the ball's velocity relative to the wall.
        v_rel = ball['vel'] - wall_vel

        # Only respond if the ball is moving toward the wall (dot product negative)
        if v_rel.dot(normal) < 0:
            # Decompose the relative velocity into normal and tangential components.
            v_normal = normal * v_rel.dot(normal)
            v_tangent = v_rel - v_normal

            # Reflect the normal component and scale by restitution.
            v_normal = -RESTITUTION * v_normal
            # Apply friction to the tangential component.
            v_tangent = (1 - FRICTION_COEFF) * v_tangent

            new_v_rel = v_normal + v_tangent
            # Transform back to world coordinates.
            ball['vel'] = new_v_rel + wall_vel
        return True
    return False


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Bouncing in a Spinning Hexagon")
    clock = pygame.time.Clock()

    hex_angle = 0.0  # initial rotation angle of the hexagon (radians)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # dt in seconds

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Update Physics ---
        # Gravity affects the vertical velocity.
        ball['vel'].y += GRAVITY * dt
        # Update ball position based on its velocity.
        ball['pos'] += ball['vel'] * dt

        # Update the hexagon’s rotation.
        hex_angle += HEXAGON_ANGULAR_VELOCITY * dt
        vertices = compute_hexagon_vertices(HEXAGON_CENTER, HEXAGON_RADIUS, hex_angle)

        # Check for collisions with each of the six edges.
        for i in range(len(vertices)):
            A = vertices[i]
            B = vertices[(i + 1) % len(vertices)]
            collide_ball_with_segment(ball, A, B, HEXAGON_CENTER, HEXAGON_ANGULAR_VELOCITY)

        # --- Drawing ---
        screen.fill((30, 30, 30))  # dark background

        # Draw the hexagon (using a polygon outline)
        hex_points = [(v.x, v.y) for v in vertices]
        pygame.draw.polygon(screen, (200, 200, 200), hex_points, 3)

        # Draw the ball.
        pygame.draw.circle(
            screen, (255, 100, 100), (int(ball['pos'].x), int(ball['pos'].y)), ball['radius']
        )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
