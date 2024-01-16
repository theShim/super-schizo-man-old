import contextlib
from typing import Any
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.config.CORE_FUNCS import vec
from scripts.config.SETTINGS import Z_LAYERS

    ##############################################################################################

class Rainbow_Particle(pygame.sprite.Sprite):
    @staticmethod
    def get_colour():
        colours = [
            (245, 70, 80),
            (239, 172, 116),
            (24, 240, 138),
            (36, 173, 129),
            (50, 151, 121),
            (110, 156, 152),
            (135, 117, 152),
            (180, 159, 145),
            (189, 160, 144),
        ]
        i = 0
        while True:
            yield colours[i]
            i += 1
            if i == len(colours): i = 0
    COLOUR_GEN = get_colour()

    def __init__(self, parent, pos):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["foreground particle"]
        
        self.pos = vec(pos[0] + random.uniform(-4, 4), pos[1])
        self.speed = random.uniform(0.1, 0.5) * 2
        self.size = random.randint(4, 6)
        self.col = next(self.COLOUR_GEN)
        self.rotation = 0
        self.rotMod = (math.degrees(random.uniform(-5, 5)) / 1000) ** 2

    def update(self, screen, offset):
        self.rotation += self.rotMod
        self.pos.y += self.speed
        self.size -= 0.1
        if self.size <= 0:
            self.parent.remove(self)

        p1 = (vec(math.cos(self.rotation), math.sin(self.rotation)) * self.size) + self.pos - offset
        p2 = (vec(math.cos(self.rotation + math.pi), math.sin(self.rotation + math.pi)) * self.size) + self.pos - offset
        pygame.draw.line(screen, self.col, p1, p2, 1)

        p1 = (vec(math.cos(self.rotation + math.pi/2), math.sin(self.rotation + math.pi/2)) * self.size) + self.pos - offset
        p2 = (vec(math.cos(self.rotation + 3*math.pi/2), math.sin(self.rotation + 3*math.pi/2)) * self.size) + self.pos - offset
        pygame.draw.line(screen, self.col, p1, p2, 1)