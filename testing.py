import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Delta Time Example")

# Set up colors
black = (0, 0, 0)
white = (255, 255, 255)

# Set up a simple moving object
x, y = width // 2, height // 2
speed = 200  # pixels per second

# Initialize the clock
clock = pygame.time.Clock()

# Get the initial time
last_time = pygame.time.get_ticks()
FPS = 60

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                FPS += 10
            if event.key == pygame.K_DOWN:
                FPS -= 10
                

    # Get the current time and calculate delta time
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0  # Convert milliseconds to seconds
    last_time = current_time

    # Update the position of the object
    x += speed * delta_time

    # Keep the object within the screen bounds
    if x > width:
        x = 0
    elif x < 0:
        x = width

    # Clear the screen
    screen.fill(black)

    # Draw the object
    pygame.draw.circle(screen, white, (int(x), y), 20)
    pygame.display.set_caption(str(FPS  ))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 10 FPS
    clock.tick(FPS)  # You can adjust the frame rate here to test different frame rates

# Quit Pygame
pygame.quit()
sys.exit()
