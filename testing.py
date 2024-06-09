import pygame
import ctypes
import sys

# Initialize Pygame
pygame.init()

# Create a Pygame window
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Pygame Window")

# Get the window handle (HWND)
hwnd = pygame.display.get_wm_info()['window']
print(f"HWND of the current Pygame window: {hwnd}")

# Example: Using ctypes to interact with Windows API to move the window
# MoveWindow(HWND, x, y, width, height, repaint)
MoveWindow = ctypes.windll.user32.MoveWindow
MoveWindow.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool]
MoveWindow.restype = ctypes.c_bool

# Move the window to (100, 100) with size 800x600
MoveWindow(hwnd, 100, 100, 800, 600, True)

# Run a simple Pygame event loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()

pip install winrt