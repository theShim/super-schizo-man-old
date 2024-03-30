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
from scripts.nature_tiles.water import Water, segment_water

from scripts.config.SETTINGS import TILE_SIZE, Z_LAYERS, SIZE
from scripts.config.CORE_FUNCS import euclidean_distance

    ##############################################################################################

class Nature_Manager:
    def __init__(self, game):
        self.game = game
        
        self.grass_manager = Grass_Manager(game)
        self.water_tiles = {}
        self.others = []

    def add_tile(self, type, pos, variant):
        if type == "grass":
            loc = f"{int(pos[0]//TILE_SIZE)};{int(pos[1]//TILE_SIZE)}"
            self.grass_manager.add_tile(loc, pos, variant)

        elif type == "water":
            self.water_tiles[tuple(pos)] = variant

        else:
            match type:
                case "swaying_vine":
                    tile = Swaying_Vine(pos, variant)
            self.others.append(tile)

    def clump_water(self):
        groups = segment_water(self.water_tiles)
        self.water_tiles = []
        for g in groups:
            positions = list(map(lambda t:t[0], g))
            xs, ys = list(zip(*positions))

            x = min(xs)
            y = min(ys)
            width = max(xs) - min(xs) + 1
            height = max(ys) - min(ys) + 1
            variant = g[0][1]
            self.water_tiles.append(Water(self.game, [x, y], [width, height], variant))

    def render_tiles(self, offset):
        self.grass_manager.t += 5
        self.grass_manager.player_force()
        grass_tiles = [t for t in self.grass_manager.tiles_to_render(offset)]
        for tile in grass_tiles: yield tile
        
        for tile in self.water_tiles:
            if pygame.FRect(tile.pos.x - offset.x, tile.pos.y - offset.y, tile.size.x, tile.size.y).colliderect([0, 0, *SIZE]):
                tile.player_collision(self.game.player)
                yield tile

        for tile in self.others: yield tile