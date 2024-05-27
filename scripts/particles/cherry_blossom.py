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

class Cherry_Blossom(pygame.sprite.Sprite):

    blossoms = []
    for colour in [(255, 61, 239), (255, 151, 246), (255, 63, 181)]:
        for size in range(3, 6):
            surf = pygame.Surface((size*3, size*2), pygame.SRCALPHA)
            pygame.draw.rect(surf, colour, [size, 0, size*2, size])
            pygame.draw.rect(surf, colour, [0, size, size*2, size])
            blossoms.append(surf)
            surf.set_alpha(150)

    def __init__(self, parent, pos):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["foreground particle"]

        self.pos = vec(pos)
        self.angle = random.uniform(0, 360)
        self.speed = [random.uniform(0.1, 0.5), random.uniform(0.1, 0.5)*2]

        self.surf = random.choice(self.blossoms)

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

        screen.blit(self.surf, (x, self.pos.y))