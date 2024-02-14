import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import numpy as np
import random
import math

from scripts.config.SETTINGS import SIZE, GRAV
from scripts.config.CORE_FUNCS import vec

    ##############################################################################################

item_info = {
    # item : {
    #     "name" : str,
    #     "type" : ["weapon", "healing", "collectible"],

    #if weapon
    #     "damage" : int,
    #     "type" : [ranged, melee, magic]

    #if healing
    #     "hp" : int
    # }
}

    ##############################################################################################

class Item(pygame.sprite.Sprite):

    @classmethod
    def get_item(cls, game, name, pos):
        if (item_data := item_info.get(name, None)) != None:
            if item_data["type"] == "weapon":
                return Weapon(item_data, pos)
            elif item_data["type"] == "healing":
                return Healing(item_data, pos)
            elif item_data["type"] == "collectible":
                return Collectible(item_data, pos)

    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        yield

    def __init__(self, game, name, pos):
        super().__init__()
        self.game = game
        self.name = name

        self.image = self.SPRITES[self.name].copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos

        self.vel = vec(random.uniform(-2.5, 2.5), GRAV)

    def move(self):
         # gravity + slight left or right movement
        self.vel = self.vel.lerp(vec(0, 0), 0.1)
        self.pos += self.vel
        self.rect.topleft = self.pos

    def update(self):
        self.game.screen.blit(self.image, self.rect)


class Weapon(Item):
    def __init__(self, game, data, pos):
        super().__init__(game, data["name"], pos)
        
class Healing(Item):
    def __init__(self, game, data, pos):
        super().__init__(game, data["name"], pos)
        
class Collectible(Item):
    def __init__(self, game, data, pos):
        super().__init__(game, data["name"], pos)
        