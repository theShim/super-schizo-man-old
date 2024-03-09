import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random
import os
import numpy as np

from scripts.config.SETTINGS import TILE_SIZE, Z_LAYERS, ENVIRONMENT_SETTINGS
from scripts.config.CORE_FUNCS import euclidean_distance, vec, normalize

    ##############################################################################################

class Grass_Manager:
    
    @classmethod
    def cache_sprites(cls):
        Grass_Manager.GRASS_IMGS = []
        Grass_Manager.MAX_GRASS_HEIGHT = -1
        for i, img_name in enumerate(os.listdir('assets/natural/grass')):
            img = pygame.image.load('assets/natural/grass/' + img_name).convert_alpha()
            img = pygame.transform.scale(img, vec(img.get_size())*1.25)
            img.set_colorkey((0, 0, 0))
            if img.get_height() > Grass_Manager.MAX_GRASS_HEIGHT:
                Grass_Manager.MAX_GRASS_HEIGHT = img.get_height()
            Grass_Manager.GRASS_IMGS.append(img)
            yield

    def __init__(self, game):
        self.game = game

        self.assets = self.GRASS_IMGS
        self.grass_id = 0
        self.grass_cache = {}

        self.grass_tiles = {}
        self.t = 0

        #config
        self.tilesize = TILE_SIZE
        self.shade_amount = 10

    def add_tile(self, loc, pos, variant):
        loc = loc # str("{x};{y}")
        if loc not in self.grass_tiles.keys():
            self.grass_tiles[loc] = Grass_Tile(self, pos, variant, self.grass_id)
            self.grass_id += 1

    def tiles_to_render(self, offset):
        for x in range(int(offset.x // (self.tilesize)), int((offset.x + self.game.screen.get_width()) // self.tilesize) + 1):
            for y in range(int(offset.y // (self.tilesize)), int((offset.y + self.game.screen.get_height()) // self.tilesize) + 1):
                loc = f"{x};{y}"
                if loc in self.grass_tiles:
                    tile = self.grass_tiles[loc]
                    yield tile

    def player_force(self):
        player_pos = self.game.player.rect.midbottom
        grid_pos = (int(player_pos[0]//TILE_SIZE), int(player_pos[1]//TILE_SIZE))
        for y in range(grid_pos[1]-2, grid_pos[1]+1):
            flag = False
            for x in range(grid_pos[0]-1, grid_pos[0]+1):
                loc = f"{x};{y}"
                if loc in self.grass_tiles:
                    self.grass_tiles[loc].apply_force(player_pos)
                    flag = True
            if flag: break


    def grass_blade_render(self, surf, blade_id, pos, rot):
        rot_img = pygame.transform.rotate(self.assets[blade_id].copy(), rot)

        # shade = pygame.Surface(rot_img.get_size(), pygame.SRCALPHA)
        # shade_amt = self.shade_amount * (abs(rot) / 90)
        # shade.set_alpha(shade_amt)
        # rot_img.blit(shade, (0, 0))

        surf.blit(rot_img, (pos[0] - rot_img.get_width() // 2, pos[1] - rot_img.get_height() // 2))

class Grass_Tile:
    def __init__(self, manager, pos, variant, id, grass_config:list[int] = [0, 1, 2, 3]):
        self.manager: Grass_Manager = manager

        self.type = 'grass'
        self.variant = variant
        self.pos = [pos[0], pos[1] + self.manager.MAX_GRASS_HEIGHT]
        self.z = Z_LAYERS["midground offgrid"]

        self.base_id = id
        self.master_rot = 0
        self.true_rot = 0
        self.precision = 30
        self.inc = 90 / self.precision
        self.padding = 15
        self.padded_size = (TILE_SIZE + self.padding * 2, self.manager.MAX_GRASS_HEIGHT/2 + self.padding)

        self.grass_blades = []
        self.grass_config = grass_config
        self.blade_density = int(random.random() * random.randint(20, 32))
        for i in range(self.blade_density):
            blade_no = random.choice(self.grass_config)
            x = (i/self.blade_density) * (TILE_SIZE) + (random.random())
            self.grass_blades.append({"pos":(x, 0), "blade_id":blade_no, "angle":random.random() * 30 - 15}) #pos, blade_no, {}
        self.pushed_blade_data = None #player collision

        self.render_data = (self.base_id, self.master_rot)

    def tile_render(self):
        surf = pygame.Surface(self.padded_size, pygame.SRCALPHA)
        # surf.set_colorkey((0, 0, 0))

        blades = self.grass_blades
        for blade in blades:
            self.manager.grass_blade_render(surf, blade["blade_id"], list(map(lambda x: x+self.padding, blade["pos"])), max(-90, min(90, blade["angle"] + self.true_rot)))
        
        return surf

    def custom_tile_render(self):
        surf = pygame.Surface(self.padded_size, pygame.SRCALPHA)
        # surf.set_colorkey((0, 0, 0))

        blades = self.pushed_blade_data
        for blade in blades:
            pos = list(map(lambda x: x+self.padding, blade[0]))
            self.manager.grass_blade_render(surf, blade[1], [pos[0], pos[1] + blade[3]], max(-90, min(90, blade[2] + self.true_rot)))
        
        return surf
    
    def render_data_update(self):
        self.render_data = (self.base_id, self.master_rot)
        self.true_rot = self.inc * self.master_rot

    def apply_force(self, force_loc):
        if not self.pushed_blade_data:
            self.pushed_blade_data = [None] * len(self.grass_blades)

        max_dist = TILE_SIZE * 0.75
        for i, blade in enumerate(self.grass_blades):
            dist = math.sqrt((self.pos[0] + blade["pos"][0] - force_loc[0]) ** 2 +
                             (self.pos[1] + blade["pos"][1] - force_loc[1]) ** 2)
            if dist < max_dist:
                force = 2
            else:
                dist = max(0, dist - max_dist)
                force = 1 - min(dist / TILE_SIZE, 1)
            dir = 1 if force_loc[0] > (self.pos[0] + blade["pos"][0]) else -1
            if not self.pushed_blade_data[i] or abs(self.pushed_blade_data[i][2] - self.grass_blades[i]["angle"]) <= abs(force) * 90:
                self.pushed_blade_data[i] = [blade["pos"], blade["blade_id"], blade["angle"] + dir * force * 90, force]


    def update(self, screen, offset):
        self.master_rot = int(math.sin(self.manager.t / 60 + (self.pos[0] / 100)) * ENVIRONMENT_SETTINGS["wind"] * 5)
        self.render_data_update()

        if not self.pushed_blade_data:
            if self.render_data not in self.manager.grass_cache:
                self.manager.grass_cache[self.render_data] = self.tile_render()

            screen.blit(self.manager.grass_cache[self.render_data], (self.pos[0] - offset[0] - self.padding, self.pos[1] - offset[1] - self.padding))
            # pygame.draw.rect(screen, (255, 0, 0), [self.pos[0] - offset[0] - self.padding, self.pos[1] - offset[1] - self.padding, *self.padded_size], 1)
            # pygame.draw.rect(screen, (255, 0, 255), [self.pos[0] - offset[0], self.pos[1] - offset[1] - self.padding, 32, 32], 1)
            # pygame.draw.circle(screen, (255, 0, 0), [self.pos[0] - offset[0] + TILE_SIZE//2, self.pos[1] - offset[1] + TILE_SIZE//2], 10)
        else:
            screen.blit(self.custom_tile_render(), (self.pos[0] - offset[0] - self.padding, self.pos[1] - offset[1] - self.padding))

        # attempt to move blades back to their base position
        if self.pushed_blade_data:
            matching = True
            for i, blade in enumerate(self.pushed_blade_data):
                stiffness = 36
                blade[2] = normalize(blade[2], stiffness, self.grass_blades[i]["angle"])
                if blade[2] != self.grass_blades[i]["angle"]:
                    matching = False
            # mark the data as non-custom once in base position so the cache can be used
            if matching:
                self.pushed_blade_data = None