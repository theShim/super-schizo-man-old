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

        self.grass_tiles = {}

        #config
        self.tilesize = TILE_SIZE

    def add_tile(self, loc, pos, variant):
        loc = loc # str("{x};{y}")
        self.grass_tiles[loc] = Grass_Tile(pos, variant)

class Grass_Tile:
    def __init__(self, pos, variant):
        self.type = 'grass'
        self.variant = variant
        self.pos = pos
        self.z = Z_LAYERS["midground offgrid"]

    def update(self):
        pass