import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random
import os
import numpy as np

from scripts.config.SETTINGS import TILE_SIZE, Z_LAYERS
from scripts.config.CORE_FUNCS import euclidean_distance

    ##############################################################################################

class Grass:
    def __init__(self, pos, variant):
        self.type = 'grass'
        self.variant = variant
        self.pos = pos
        self.z = Z_LAYERS["midground offgrid"]

        self.grass_blades = pygame.sprite.Group()
        [self.grass_blades.add(Grass_Blade(pos)) for i in range(24)]

    @property
    def dict(self):
        return {'type':self.type, "pos":self.pos, "variant":self.variant}

    def hitbox(self, offset):
        rect = pygame.Rect(*(self.pos - offset), TILE_SIZE, TILE_SIZE/1.5)
        rect.y += TILE_SIZE/2 + 4
        return rect
    
    # def player_collision(self, player_pos):
    #     i = 0
    #     for g in self.grass_blades:
    #         g.flattened = i*2
    #         g.collided = 20
    #         if player_pos[0] - g.pos[0] < 0:
    #             g.collided *= -1
    #             g.flattened = abs(g.flattened - 6)
    #         i += 0.5

    def update(self, screen, offset, player):
        self.grass_blades.update(screen, offset, player)
        # pygame.draw.rect(screen, (255, 0, 0), self.hitbox(offset), 1)

class Grass_Blade(pygame.sprite.Sprite):

    WIND = 0
    ROTATED_CACHE = {}
    
    @classmethod
    def cache_sprites(cls):
        Grass_Blade.GRASS_IMGS = []
        for i, img_name in enumerate(os.listdir('assets/natural/grass')):
            img = pygame.image.load('assets/natural/grass/' + img_name).convert_alpha()
            img.set_colorkey((0, 0, 0))
            Grass_Blade.GRASS_IMGS.append(img)
            Grass_Blade.ROTATED_CACHE[i] = {}
            yield

    def __init__(self, pos):
        super().__init__()
        x_offset = random.uniform(0, TILE_SIZE)
        self.image = random.choices(self.GRASS_IMGS, [1.5, 1, 1.5, 1], k=1)[0]
        self.grass_index = self.GRASS_IMGS.index(self.image)
        self.pos = (pos[0] + x_offset, pos[1] + 34)
        self.angle = int(2 * random.random() + pos[0] // TILE_SIZE) / 2

    def update(self, screen, offset, player):
        self.angle += .05

        collided = 0
        player_rect: pygame.Rect = pygame.Rect(0, 0, player.hitbox.size[0] * 2, player.hitbox.size[1])
        player_rect.midbottom = player.hitbox.midbottom - offset
        if player_rect.colliderect(self.image.get_rect(midbottom=self.pos-offset)):
            collided = sorted([-60, 60, (player.rect.centerx - (self.pos[0] + 2))])[1]

        if collided:
            angle = collided
        else:
            angle = 12 + int(math.sin(self.angle) * 24)

        if angle in self.ROTATED_CACHE[self.grass_index]:
            rotated_img = self.ROTATED_CACHE[self.grass_index][angle]
        else:
            rotated_img = pygame.transform.rotate(self.image, angle)
            rotated_img.set_colorkey((0, 0, 0))
            self.ROTATED_CACHE[self.grass_index][angle] = rotated_img

        rotated_rect = rotated_img.get_rect(center=self.image.get_rect(midbottom=self.pos-offset).center)
        rotated_rect.y += 6 if collided else 0

        # if collided:
        #     rotated_img.fill((255, 0, 0))
        # if not self.collided:
        screen.blit(rotated_img, rotated_rect)
        # pygame.draw.rect(screen, (255, 0, 0), rotated_rect, 1)
        # pygame.draw.rect(screen, (255, 0, 0), self.image.get_rect(midbottom=self.pos-offset), 1)

    ##############################################################################################