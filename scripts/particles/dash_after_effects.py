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

class Dash_After_Effect(pygame.sprite.Sprite):
    def __init__(self, parent, pos, spr):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["player_dash"]

        self.spr: pygame.Surface = spr
        pixel_array = pygame.surfarray.array3d(self.spr)
        mask = np.all(pixel_array, axis=-1)
        pixel_array[mask] = (3, 154, 255)
        pygame.surfarray.blit_array(self.spr, pixel_array)
        self.spr.set_colorkey((0, 0, 0))
        
        self.pos = vec(pos)
        self.alpha = 210
        self.alpha_decay = 30

    def update(self, screen, offset):
        self.alpha -= self.alpha_decay
        if self.alpha <= 0:
            return self.parent.remove(self)
        
        spr = self.spr.copy()
        spr.set_alpha(self.alpha)
        screen.blit(spr, self.pos - offset)