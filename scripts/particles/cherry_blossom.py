import contextlib
from typing import Any
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math
import numpy as np

from scripts.config.CORE_FUNCS import vec, warp
from scripts.config.SETTINGS import Z_LAYERS, HEIGHT, WIDTH

    ##############################################################################################

class Cherry_Blossom(pygame.sprite.Sprite):

    blossoms = []
    for colour in [(255, 61, 239), (255, 151, 246), (255, 63, 181)]:
        for size in range(2, 5):
            surf = pygame.Surface((size*3, size*2), pygame.SRCALPHA)
            pygame.draw.rect(surf, colour, [size, 0, size*2, size])
            pygame.draw.rect(surf, colour, [0, size, size*2, size])
            blossoms.append(surf)
            blossoms.append(pygame.transform.flip(surf, True, False))
            # surf.set_alpha(150)

    def __init__(self, parent, pos):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["foreground particle"]

        self.pos = vec(pos)
        self.angle = random.uniform(0, 360)
        self.speed = [random.uniform(0.1, 0.5), random.uniform(0.2, 0.6)]

        self.surf = random.choice(self.blossoms)
        self.rect = self.surf.get_frect(topleft=self.pos)

        x = random.randint(0, 2)
        self.point_info = {i:{
            "target" : (i + 2) % 4,
            "t" : random.uniform(0, 1) if i % 2 == x else 0,
            "dt" : random.uniform(0.01, 0.2) / 20 if i % 2 == x else 0,
        } for i in range(4)}

    @property
    def corners(self):
        c = [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft]
        to_use = []
        for i in range(4):
            p1 = c[i]
            p2 = c[self.point_info[i]["target"]]
            t  = self.point_info[i]["t"]
            to_use.append(vec(p1).lerp(p2, t))

            self.point_info[i]["t"] += self.point_info[i]["dt"]
            if self.point_info[i]["t"] > 1:
                self.point_info[i]["t"] = 1
                self.point_info[i]["dt"] *= -1
            elif self.point_info[i]["t"] < 0:
                self.point_info[i]["t"] = 0
                self.point_info[i]["dt"] *= -1
        return to_use

    def update(self, screen, offset):
        self.rect.x += self.speed[0] * random.randint(-1, 1)
        self.rect.y += self.speed[1]
        x = self.rect.x + math.sin(self.angle) * 10
        self.angle += 0.05
        
        if self.rect.x + self.surf.get_width() < -self.surf.get_width():
            self.rect.x = WIDTH-1
        elif self.rect.x > WIDTH + self.surf.get_width():
            self.rect.x = -self.surf.get_width()+1

        corners = [(int((c[0] - self.rect.x) + x), int(c[1])) for c in self.corners]
        warped_img, warped_rect = warp(
            self.surf,
            corners,
            smooth=not True
        )
        warped_img.set_alpha(120)
        screen.blit(warped_img, warped_rect)