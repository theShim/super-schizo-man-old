import pygame
import sys
import math
import numpy as np

# Initialize Pygame
pygame.init()

# Set screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Set colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3D Projection with Point Rotation in Pygame")

# Define the 3D points
points3D = [
    (100, 100, 100),
    (100, -100, 100),
    (-100, -100, 100),
    (-100, 100, 100),
    (100, 100, -100),
    (100, -100, -100),
    (-100, -100, -100),
    (-100, 100, -100)
]

# Define the camera position
camera = (0, 0, -500)

# Define the projection plane distance
projection_plane = 500

# Rotation angle around the y-axis (in radians)
angle_y = math.radians(30)  # Adjust this angle as needed

# Rotation matrix around the y-axis
rotation_matrix_y = lambda angle: np.array([
    [math.cos(angle), 0, math.sin(angle)],
    [0, 1, 0],
    [-math.sin(angle), 0, math.cos(angle)]
])

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(WHITE)
    angle_y += math.radians(0.1)

    # Rotate each point about the y-axis
    rotated_points = []
    for point3D in points3D:
        # Apply rotation matrix
        rotated_point = np.dot(rotation_matrix_y(angle_y), point3D)
        rotated_points.append(rotated_point)

    # Project and draw each rotated point
    for point3D in rotated_points:
        # Perform perspective projection
        x = (point3D[0] - camera[0]) * projection_plane / (point3D[2] - camera[2]) + SCREEN_WIDTH / 2
        y = (point3D[1] - camera[1]) * projection_plane / (point3D[2] - camera[2]) + SCREEN_HEIGHT / 2
        
        # Calculate the radius based on the distance
        distance = math.sqrt((point3D[0] - camera[0]) ** 2 + (point3D[1] - camera[1]) ** 2 + (point3D[2] - camera[2]) ** 2)
        radius = 10 / distance
        
        # Draw the projected point with adjusted radius
        pygame.draw.circle(screen, BLACK, (int(x), int(y)), max(1, int(radius)))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
