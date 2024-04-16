import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import numpy as np
import random
import math

from scripts.config.CORE_FUNCS import vec
from scripts.config.SETTINGS import WIDTH, HEIGHT, Z_LAYERS, TILE_SIZE

    ##############################################################################################

class Minimap(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        cls.BORDER = pygame.transform.scale((img:=pygame.image.load("assets/gui/minimap.png")), vec(img.get_size())*3).convert_alpha()
        cls.BORDER.set_colorkey((0, 0, 0))
        yield
    
    def __init__(self, game, tiles):
        super().__init__()
        self.game = game
        self.z = Z_LAYERS["in-game gui"]

        self.tiles = tiles
        self.buffer = [16*1.25, 10*1.25] # the buffersize for the surrounding area beyond the current screen (in no. of tiles) (ratio=8:5)
        self.map_size = vec(self.BORDER.get_size()) - vec(15, 15)

        self.border = self.BORDER.copy()
        self.border_rect = self.border.get_rect(topright=(WIDTH-3, 3))

    def update(self, screen, offset):
        map_ = pygame.Surface((WIDTH/TILE_SIZE + self.buffer[0], HEIGHT/TILE_SIZE + self.buffer[1]), pygame.SRCALPHA)
        map_.fill((0, 0, 0))
        for tile in self.game.stage_loader.tilemap.render_tiles(offset, self.buffer):
            if tuple(tile.pos) in self.tiles:
                map_pos = (vec(tile.pos) - vec(offset) / TILE_SIZE)
                map_.set_at((math.floor(map_pos.x + self.buffer[0]/2), math.floor(map_pos.y + self.buffer[1]/2)), (92, 95, 112))

        player_pos = (vec(self.game.player.hitbox.midtop) - vec(offset)) / TILE_SIZE
        player_pos = (math.floor(player_pos.x), math.floor(player_pos.y))
        map_.set_at((player_pos[0] + int(self.buffer[0]/2), player_pos[1]+int(self.buffer[1]/2)),   (189, 17, 17))
        map_.set_at((player_pos[0] + int(self.buffer[0]/2), player_pos[1]+int(self.buffer[1]/2)+1), (189, 17, 17))
        map_ = pygame.transform.scale(map_, self.map_size)

        screen.blit(map_, map_.get_rect(topright=self.border_rect.topright))
        screen.blit(self.border, self.border_rect)