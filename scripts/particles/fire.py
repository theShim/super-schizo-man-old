import contextlib
from typing import Any
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.config.CORE_FUNCS import vec
from scripts.config.SETTINGS import Z_LAYERS

    ################################################################################################

class Fire_Particle(pygame.sprite.Sprite):

    alpha_layer_qty = 2
    alpha_glow_constant = 2

    def __init__(self, parent, pos, radius, master_pos=None):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["foreground particle"]

        self.pos = vec(pos)
        self.oPos = self.pos.copy()
        self.master_pos = master_pos if master_pos != None else self.pos.copy()
        self.radius = radius
        self.yellow = 0

        self.alpha_layers = Fire_Particle.alpha_layer_qty
        self.alpha_glow = Fire_Particle.alpha_glow_constant
        self.burn_rate = 0.01 * random.uniform(1, 4)

        self.max_size = 2 * self.radius * self.alpha_glow * self.alpha_layers ** 2

    def burn(self):
        self.radius -= self.burn_rate
        if self.radius < 0:
            self.parent.remove(self)
            self.parent.add(Fire_Particle(self.parent, (self.master_pos + vec(random.uniform(-1, 1), random.uniform(-1, 1))), random.uniform(1, 3)))
            return True
        
        self.pos.x += random.uniform(-self.radius, self.radius) / 2
        self.pos.y -= (random.uniform(5, 8) - self.radius) / 16

        self.yellow += 2
        if self.yellow > 255:
            self.yellow = 255


    def update(self, screen, offset):
        dead = self.burn()
        if dead: return
         
        self.draw(screen, offset)

    def draw(self, screen, offset):
        surf = pygame.Surface((self.max_size, self.max_size), pygame.SRCALPHA)

        for i in range(self.alpha_layers, -1, -1):
            alpha = 255 - i * (255 // self.alpha_layers - 5)
            if alpha < 0: alpha = 0

            radius = self.radius * self.alpha_glow * i**2
            pygame.draw.circle(surf, (255, self.yellow, 0, alpha), list(map(lambda x: x/2, surf.get_size())), radius)
        screen.blit(surf, surf.get_rect(center=self.pos-offset))