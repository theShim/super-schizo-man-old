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

class Floating_Light(pygame.sprite.Sprite):
    def __init__(self, parent, pos):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["foreground particle"]

        self.pos = vec(pos)
        self.angle = random.uniform(0, 360)
        self.speed = random.uniform(0.1, 0.5)
        self.size = random.randint(3, 5)

        self.surf = pygame.Surface((self.size*3, self.size*3), pygame.SRCALPHA)
        pygame.draw.rect(self.surf, (100, 100, 100), [self.size, self.size, self.size, self.size])
        square = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        square.fill((50, 50, 50))
        square.set_alpha(100)
        self.surf.blit(square, (self.size, 0))
        self.surf.blit(square, (0, self.size))
        self.surf.blit(square, (self.size*2, self.size))
        self.surf.blit(square, (self.size, self.size*2))

    def update(self, screen, offset):
        self.pos.x += self.speed * random.randint(-1, 1)
        self.pos.y += self.speed
        x = self.pos.x + math.sin(self.angle) * 10
        self.angle += 0.05
        # pygame.draw.rect(screen, (200, 200, 200), [x - offset.x, self.pos.y - offset.y, self.size, self.size])
        # self.surf = pygame.transform.scale(self.surf, vec(self.surf.get_size()) - vec(0.000000000000001, 0.000000000000001))
        screen.blit(self.surf, (x - offset.x, self.pos.y - offset.y), special_flags=pygame.BLEND_RGBA_ADD)