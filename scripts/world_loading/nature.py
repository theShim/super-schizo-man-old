import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random
import os
import numpy as np

from scripts.nature_tiles.grass import Grass_Manager
from scripts.nature_tiles.vines import Swaying_Vine

from scripts.config.SETTINGS import TILE_SIZE, Z_LAYERS
from scripts.config.CORE_FUNCS import euclidean_distance

    ##############################################################################################

class Nature_Manager:
    def __init__(self, game):
        self.game = game
        
        self.grass_manager = Grass_Manager(game)
        self.others = []

    def add_tile(self, type, pos, variant):
        if type == "grass":
            loc = f"{int(pos[0]//TILE_SIZE)};{int(pos[1]//TILE_SIZE)}"
            self.grass_manager.add_tile(loc, pos, variant)
        else:
            match type:
                case "swaying_vine":
                    tile = Swaying_Vine(pos, variant)
                case "water":
                    tile = Swaying_Vine([pos[0]*TILE_SIZE, pos[1]*TILE_SIZE], variant)
            self.others.append(tile)

    def render_tiles(self, offset):
        self.grass_manager.t += 5
        self.grass_manager.player_force()
        grass_tiles = [t for t in self.grass_manager.tiles_to_render(offset)]
        for tile in grass_tiles: yield tile

        for tile in self.others: yield tile