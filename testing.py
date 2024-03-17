import pygame
import sys
import math
import pygame.gfxdraw

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smooth Transition Line")

# Colors
WHITE = (255, 255, 255)

# Circle center points
x1, y1 = 200, 300  # Center of circle with radius 10
x2, y2 = 600, 300  # Center of circle with radius 2
y2o = y2
x2o = x2
# Calculate distance between centers and angle
dx = x2 - x1
dy = y2 - y1
distance = math.sqrt(dx ** 2 + dy ** 2)
angle = math.atan2(dy, dx)

# Control point distance
control_point_distance = distance / 2

# Control point
control_x = (x1 + x2) / 2
control_y = (y1 + y2) / 2

# Thickness variables
start_thickness = 10
end_thickness = 2

# Calculate intermediate points along the Bézier curve
num_points = 100
a = 0

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill((0, 0, 0))
    a += math.radians(.1)

    for i in range(num_points + 1):
        t = i / num_points
        inv_t = 1 - t

        x = inv_t ** 2 * x1 + 2 * inv_t * t * control_x + t ** 2 * x2
        y = inv_t ** 2 * y1 + 2 * inv_t * t * control_y + t ** 2 * y2

        # Interpolate thickness
        thickness = int(start_thickness * inv_t + end_thickness * t)

        # Draw a circle at each point with calculated thickness
        pygame.gfxdraw.filled_circle(screen, int(x), int(y), thickness, WHITE)
    pygame.display.flip()
