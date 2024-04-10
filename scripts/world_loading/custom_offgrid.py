import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random
import os
import numpy as np

from scripts.config.SETTINGS import TILE_SIZE, Z_LAYERS
from scripts.config.CORE_FUNCS import vec

    ##############################################################################################

class Torch(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        Torch.SPRITES = []
        for img_name in sorted(os.listdir('assets/offgrid_tiles/torch')):
            img = pygame.image.load('assets/offgrid_tiles/torch/' + img_name).convert_alpha()
            img.set_colorkey((0, 0, 0))
            Torch.SPRITES.append(img)
            yield

    def __init__(self, pos, variant):
        super().__init__()
        self.type = 'torch'
        self.variant = variant
        self.pos = pos
        self.z = Z_LAYERS["foreground offgrid"]

        self.facing = ['forward', 'left', 'right'][self.variant]
        self.flame_intensity = 2
        self.start = True

    @property
    def dict(self):
        return {'type':self.type, "pos":self.pos, "variant":self.variant}
    
    def update(self, screen, offset, particle_manager):
        img = Torch.SPRITES[self.variant]
        screen.blit(img, self.pos - offset)

        if self.start:
            for i in range(self.flame_intensity * 10):
                particle_manager.add_particle("foreground", "fire", pos=(self.pos + vec(random.uniform(-5, 5) + 12, random.uniform(-5, 5) - 2)), radius=random.uniform(1, 3))
            self.start = False

class Bridge(pygame.sprite.Sprite):
    def __init__(self, pos, variant):
        super().__init__()
        self.type = "bridge"
        self.variant = variant
        self.z = Z_LAYERS["foreground offgrid"]

        self.pos = pos
        self.end_pos = None

    @property
    def dict(self):
        return {'type':self.type, "pos":self.pos, "end_pos":self.end_pos, "variant":self.variant}

    def update(self, screen, offset):
        #temporary showing joints
        pygame.draw.line(screen, (201, 201, 201), vec(self.pos) - offset + vec(5, 5), vec(self.end_pos) - offset + vec(5, 5), 1)