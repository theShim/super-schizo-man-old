import numpy as np
import pygame

# Initialize pygame
pygame.init()

# Define the size of the image
width, height = 100, 100  # Size of the circle image

# Create a numpy array for the image
image = np.zeros((height, width), dtype=np.uint8)

# Get the center coordinates
center_x, center_y = width // 2, height // 2

# Define the maximum radius
max_radius = min(center_x, center_y)

# Fill the image with a radial gradient
for y in range(height):
    for x in range(width):
        # Calculate the distance from the center
        distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
        # Calculate the intensity based on the distance
        intensity = max(0, 255 - int((distance / max_radius) * 255))
        intensity = min(255, int((distance / max_radius) * 255))
        # Assign the intensity to the pixel
        image[y, x] = intensity

# Create a Pygame surface from the numpy array
light_surface = pygame.surfarray.make_surface(np.repeat(image[:, :, np.newaxis], 3, axis=2))

# Save the surface as an image file
pygame.image.save(light_surface, 'circle.png')