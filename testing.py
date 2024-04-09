import pygame
import random

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Heatwave Simulation")

# Create a background surface
background = pygame.Surface((WIDTH, HEIGHT))
background.fill((255, 255, 255))  # White background

# Create heatwave effect layers
heatwave_layers = []
for _ in range(3):
    layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # Transparent surface
    heatwave_layers.append(layer)

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update heatwave effect
    for layer in heatwave_layers:
        # Randomly change transparency and color of heatwave layers
        alpha = random.randint(20, 255)  # Random transparency
        color = (random.randint(200, 255), random.randint(150, 200), random.randint(50, 100), alpha)  # Random color with transparency
        layer.fill(color)

    # Clear the screen
    screen.blit(background, (0, 0))

    # Render and blit heatwave effect layers
    for layer in heatwave_layers:
        screen.blit(layer, (0, 0))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
