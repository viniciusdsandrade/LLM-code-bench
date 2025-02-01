import pygame
import math


def closest_point_on_segment(A, B, P):
    ax, ay = A
    bx, by = B
    px, py = P
    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay

    t = (apx * abx + apy * aby) / (abx ** 2 + aby ** 2 + 1e-8)
    t = max(0, min(1, t))
    return ax + t * abx, ay + t * aby


pygame.init()
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Parâmetros do hexágono
cx, cy = width // 2, height // 2
hex_radius = 300
angle = 0
angle_velocity = 0.5  # Rotação mais lenta (radianos/segundo)

# Parâmetros da bola
ball_radius = 20
ball_x, ball_y = cx, cy - 200
ball_vx, ball_vy = 0, 0

# Parâmetros físicos realistas
gravity = 980  # Aproximadamente 9.8 m/s² (1 pixel = 1 cm)
air_friction = 0.02
cor = 0.8
wall_friction = 0.2

running = True
while running:
    dt = clock.tick(60) / 1000  # Delta time em segundos

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Atualização da rotação do hexágono
    angle += angle_velocity * dt
    angle %= 2 * math.pi

    # Atualização da física da bola
    ball_vy += gravity * dt
    ball_vx *= (1 - air_friction * dt)
    ball_vy *= (1 - air_friction * dt)
    ball_x += ball_vx * dt
    ball_y += ball_vy * dt

    # Geração dos vértices do hexágono
    vertices = []
    for i in range(6):
        theta = angle + math.radians(i * 60)
        x = cx + hex_radius * math.cos(theta)
        y = cy + hex_radius * math.sin(theta)
        vertices.append((x, y))

    # Detecção e resposta de colisão
    collision_occurred = False
    for i in range(6):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % 6]

        # Cálculo da normal interna da face
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        normal = (-dy, dx)
        length = math.hypot(normal[0], normal[1])
        if length == 0:
            continue
        normal = (normal[0] / length, normal[1] / length)

        # Distância da bola até a face
        distance = (ball_x - p1[0]) * normal[0] + (ball_y - p1[1]) * normal[1]

        if distance <= ball_radius and not collision_occurred:
            # Aqui tratamos a colisão como se a parede estivesse fixa,
            # usando diretamente a velocidade da bola.
            dot_product = ball_vx * normal[0] + ball_vy * normal[1]

            if dot_product < 0:
                new_normal = -cor * dot_product
                tangent = (ball_vx - dot_product * normal[0],
                           ball_vy - dot_product * normal[1])

                tangent_magnitude = math.hypot(tangent[0], tangent[1])
                if tangent_magnitude > 0:
                    tangent_normalized = (tangent[0] / tangent_magnitude,
                                          tangent[1] / tangent_magnitude)
                    tangent_scale = max(0, tangent_magnitude * (1 - wall_friction))
                    tangent = (tangent_normalized[0] * tangent_scale,
                               tangent_normalized[1] * tangent_scale)
                else:
                    tangent = (0, 0)

                ball_vx = new_normal * normal[0] + tangent[0]
                ball_vy = new_normal * normal[1] + tangent[1]

                # Correção de posição para evitar penetração
                penetration = ball_radius - distance
                ball_x += normal[0] * penetration
                ball_y += normal[1] * penetration

                collision_occurred = True
                break

    # Renderização
    screen.fill((0, 0, 0))
    pygame.draw.polygon(screen, (255, 255, 255), vertices, 2)
    pygame.draw.circle(screen, (255, 0, 0), (int(ball_x), int(ball_y)), ball_radius)
    pygame.display.flip()

pygame.quit()
