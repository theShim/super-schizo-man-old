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

class Grass_Manager:
    def __init__(self, game):
        self.game = game

        self.assets = {}
        self.grass_id = 0
        self.grass_cache = {}

        self.grass_tiles = {}

        #config
        self.tilesize = TILE_SIZE

    def add_tile(self, loc, pos, variant):
        loc = loc # str("{x};{y}")
        self.grass_tiles[loc] = Grass_Tile(pos, variant, self.grass_id)
        self.grass_id += 1

    def tiles_to_render(self, offset):
        for x in range(int(offset.x // (self.tile_size)), int((offset.x + self.game.screen.get_width()) // self.tile_size) + 1):
            for y in range(int(offset.y // (self.tile_size)), int((offset.y + self.game.screen.get_height()) // self.tile_size) + 1):
                loc = f"{x};{y}"
                if loc in self.grass_tiles:
                    tile = self.grass_tiles[loc]
                    yield tile

class Grass_Tile:
    def __init__(self, pos, variant, id):
        self.type = 'grass'
        self.variant = variant
        self.pos = pos
        self.z = Z_LAYERS["midground offgrid"]

    def update(self):
        if ()