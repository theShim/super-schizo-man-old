import contextlib
from typing import Any
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math
import numpy as np

from scripts.config.CORE_FUNCS import vec
from scripts.config.SETTINGS import Z_LAYERS, GRAV, ENVIRONMENT_SETTINGS, TILE_SIZE, WIDTH, HEIGHT

    ################################################################################################

class Snow_Particle(pygame.sprite.Sprite):
    ROTTED_IMGS = {}

    def __init__(self, parent, pos):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["foreground particle"]

        self.size = random.randint(1, 3)
        self.colour = (c:= random.randint(150, 255), c, c)
        self.image = pygame.Surface((self.size*3, self.size*3), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.colour, [self.size, 0, self.size, self.size])
        pygame.draw.rect(self.image, self.colour, [self.size, self.size, self.size, self.size])
        pygame.draw.rect(self.image, self.colour, [self.size, self.size*2, self.size, self.size])
        pygame.draw.rect(self.image, self.colour, [0, self.size, self.size, self.size])
        pygame.draw.rect(self.image, self.colour, [self.size*2, self.size, self.size, self.size])
        self.image.set_alpha(random.randint(100, 180))

        self.pos = vec(pos)
        self.delta_x = random.uniform(0.01, 1.8) * ENVIRONMENT_SETTINGS["wind"]
        self.fall_speed = random.uniform(5, 10) * 0.5

        self.angle = 0
        self.angle_rot = random.uniform(0.2, 0.75) * random.choice([-1, 1])

    def move(self):
        self.pos.x += self.delta_x
        self.pos.y += 0.9 * self.fall_speed
        
    def update(self, screen, offset):
        self.angle += self.angle_rot
        self.move()

        self.draw(screen)

    def draw(self, screen):
        if (rotted_img := Snow_Particle.ROTTED_IMGS.get((self.size, round(self.angle, 2)), None)) == None:
            rotted_img = pygame.transform.rotate(self.image, self.angle)
            Snow_Particle.ROTTED_IMGS[(self.size, round(self.angle, 2))] = rotted_img
        screen.blit(rotted_img, rotted_img.get_rect(center=self.pos))

        

class Snow_Particle2(pygame.sprite.Sprite):
    def __init__(self, parent, pos):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["foreground particle"]

        self.pos = vec(pos)
        self.radius = random.randint(1, 3)
        self.colour = (c:=random.randint(150, 255), c, c)
        self.speed = random.uniform(1, 2)

    def calculate(self):
        self.pos.x += self.speed if random.randint(0,1) == 0 else -self.speed
        self.pos.y += self.speed
        
        if self.pos.x - self.radius < -self.radius:
            self.pos.x = WIDTH + self.radius - self.speed
        elif self.pos.x + self.radius > WIDTH + self.radius:
            self.pos.x = -self.radius + self.speed
            
        self.radius = random.randint(1, 3)
        self.speed = random.randint(1, 2)

    def update(self, screen, offset):
        self.calculate()
        pygame.draw.circle(screen, self.colour, self.pos, self.radius)

        light = pygame.Surface((self.radius*2*2, self.radius*2*2), pygame.SRCALPHA)
        pygame.draw.circle(light, (255, 255, 255), (self.radius*2, self.radius*2), self.radius*2)
        light.set_alpha(random.randint(10, 40))
        screen.blit(light, self.pos-vec(self.radius*2, self.radius*2))