import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in Spinning Hexagon")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Clock
clock = pygame.time.Clock()

# Hexagon properties
hexagon_radius = 200
hexagon_center = (WIDTH // 2, HEIGHT // 2)
hexagon_angle = 0  # Rotation angle
hexagon_angular_speed = 0.01  # Rotation speed

# Ball properties
ball_radius = 20
ball_pos = [WIDTH // 2, HEIGHT // 2 - hexagon_radius + ball_radius]
ball_vel = [0, 0]  # Velocity in x and y directions
gravity = 0.5
friction = 0.99


# Function to draw a rotated hexagon
def draw_hexagon(center, radius, angle):
    points = []
    for i in range(6):
        x = center[0] + radius * math.cos(math.radians(60 * i + angle))
        y = center[1] + radius * math.sin(math.radians(60 * i + angle))
        points.append((x, y))
    pygame.draw.polygon(screen, BLACK, points, 2)


# Function to check collision with hexagon walls
def check_collision(ball_pos, ball_radius, hexagon_center, hexagon_radius, angle):
    for i in range(6):
        x1 = hexagon_center[0] + hexagon_radius * math.cos(math.radians(60 * i + angle))
        y1 = hexagon_center[1] + hexagon_radius * math.sin(math.radians(60 * i + angle))
        x2 = hexagon_center[0] + hexagon_radius * math.cos(math.radians(60 * (i + 1) + angle))
        y2 = hexagon_center[1] + hexagon_radius * math.sin(math.radians(60 * (i + 1) + angle))

        # Line segment from (x1, y1) to (x2, y2)
        dx = x2 - x1
        dy = y2 - y1
        segment_length = math.hypot(dx, dy)

        # Vector from ball to line segment start
        ball_to_segment_x = ball_pos[0] - x1
        ball_to_segment_y = ball_pos[1] - y1

        # Projection of ball position onto the line segment
        projection = (ball_to_segment_x * dx + ball_to_segment_y * dy) / (segment_length ** 2)
        projection = max(0, min(1, projection))  # Clamp to segment

        # Closest point on the segment to the ball
        closest_x = x1 + projection * dx
        closest_y = y1 + projection * dy

        # Distance from ball to the closest point
        distance = math.hypot(ball_pos[0] - closest_x, ball_pos[1] - closest_y)

        if distance < ball_radius:
            # Calculate normal vector
            normal_x = (closest_x - ball_pos[0]) / distance
            normal_y = (closest_y - ball_pos[1]) / distance

            # Reflect velocity vector
            dot_product = ball_vel[0] * normal_x + ball_vel[1] * normal_y
            ball_vel[0] -= 2 * dot_product * normal_x
            ball_vel[1] -= 2 * dot_product * normal_y

            # Move ball outside the collision
            overlap = ball_radius - distance
            ball_pos[0] += overlap * normal_x
            ball_pos[1] += overlap * normal_y


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update hexagon rotation
    hexagon_angle += hexagon_angular_speed

    # Apply gravity
    ball_vel[1] += gravity

    # Apply friction
    ball_vel[0] *= friction
    ball_vel[1] *= friction

    # Update ball position
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Check for collisions with hexagon walls
    check_collision(ball_pos, ball_radius, hexagon_center, hexagon_radius, hexagon_angle)

    # Clear screen
    screen.fill(WHITE)

    # Draw hexagon
    draw_hexagon(hexagon_center, hexagon_radius, hexagon_angle)

    # Draw ball
    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
