import contextlib
from typing import Any
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math
import numpy as np

from scripts.config.CORE_FUNCS import vec
from scripts.config.SETTINGS import Z_LAYERS, HEIGHT, WIDTH

    ##############################################################################################

class Floating_Light(pygame.sprite.Sprite):

    lights = {}
    for size in range(3, 6):
        surf = pygame.Surface((size*5, size*5), pygame.SRCALPHA)
        
        horizontal = pygame.Surface((size, 1), pygame.SRCALPHA)
        horizontal.fill((100, 100, 100))
        vertical = pygame.Surface((1, size), pygame.SRCALPHA)
        vertical.fill((100, 100, 100))
        
        for i in range(int(size*2.5), 0, -1):
            light_surface = pygame.Surface((size*5, size*5), pygame.SRCALPHA)
            pygame.draw.circle(light_surface, (16, 16, 16), (size*2.5, size*2.5), i/2)
            light_surface.set_alpha(200)
            surf.blit(light_surface, light_surface.get_rect(center=(size*2.5, size*2.5)), special_flags=pygame.BLEND_RGB_ADD)
        surf.set_alpha(150)

        lights[size] = surf

    def __init__(self, parent, pos):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["foreground particle"]

        self.pos = vec(pos)
        self.angle = random.uniform(0, 360)
        self.speed = [random.uniform(0.1, 0.5), random.uniform(0.1, 0.5)]
        self.size = random.randint(3, 5)

        self.surf = self.lights[self.size]
        self.og_offset = None

    def update(self, screen, offset):

        self.pos.x += self.speed[0] * random.randint(-1, 1)
        self.pos.y += self.speed[1]
        x = self.pos.x + math.sin(self.angle) * 10
        self.angle += 0.05

        if self.pos.y - self.surf.get_height()/2 > HEIGHT:
            self.pos.y = -self.surf.get_height()
        if self.pos.x + self.surf.get_width() < -self.surf.get_width():
            self.pos.x = WIDTH-1
        elif self.pos.x > WIDTH + self.surf.get_width():
            self.pos.x = -self.surf.get_width()+1

        current_offset = offset.copy() // 1
        offset_dist = vec()
        if self.og_offset == None: 
            self.og_offset = current_offset
        if current_offset.distance_to(self.og_offset) > 0:
            offset_dist = self.og_offset - current_offset
            self.og_offset = current_offset

        if (dist:=offset_dist.magnitude()):
            for i in range(0, int(dist), 2):
                s = self.surf.copy()
                s.set_alpha((i/dist)*60)
                screen.blit(s, (x+offset_dist.x/(0.5*(i+1)), self.pos.y+offset_dist.y/(0.5*(i+1))))

        screen.blit(self.surf, (x, self.pos.y), special_flags=pygame.BLEND_RGBA_ADD)