import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import random
import sys
import math
import time
import numpy as np

    ##############################################################################################

#initialising pygame stuff
pygame.init()  #general pygame
pygame.font.init() #font stuff
pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
pygame.mixer.init()
# pygame.event.set_blocked(None) #setting allowed events to reduce lag
# pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.ACTIVEEVENT])
pygame.display.set_caption("")

#initalising pygame window
flags = pygame.DOUBLEBUF #| pygame.FULLSCREEN
SIZE = WIDTH, HEIGHT = (400, 400)
screen = pygame.display.set_mode(SIZE, flags, 16)
clock = pygame.time.Clock()

#renaming common functions
vec = pygame.math.Vector2

#useful functions
def gen_colour():
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

def euclidean_distance(point1, point2):
    return vec(point1).distance_to(vec(point2))

def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    angle = math.radians(angle)

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return vec(qx, qy)

    ##############################################################################################

class Button(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.pos = pos

        self.base = (pygame.transform.scale2x(pygame.image.load("assets/gui/button1.png"))).convert_alpha()
        self.base.set_colorkey((0, 0, 0))
        self.clicked = (pygame.transform.scale2x(pygame.image.load("assets/gui/button2.png"))).convert_alpha()
        self.clicked.set_colorkey((0, 0, 0))

    def update(self, screen):
        mousePos = pygame.mouse.get_pos()
        if self.base.get_rect(topleft=self.pos).collidepoint(mousePos):
            screen.blit(self.clicked, self.pos)
        else:
            screen.blit(self.base, self.pos)

b = Button((200, 200))

    ##############################################################################################

last_time = time.time()

running = True
while running:

    dt = time.time() - last_time
    last_time = time.time()

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    screen.fill((30, 30, 30))
    b.update(screen)

    #fps
    font = pygame.font.SysFont('monospace', 30)
    fps = font.render(f'FPS: {int(clock.get_fps())}', True, (215, 215, 215))
    screen.blit(fps, (0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()