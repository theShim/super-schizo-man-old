import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random
import os
import numpy as np
from scipy.interpolate import interp1d

from scripts.config.SETTINGS import TILE_SIZE, Z_LAYERS, SIZE
from scripts.config.CORE_FUNCS import vec, euclidean_distance

    ##############################################################################################

def get_curve(points, interval=1):
    x_new = np.arange(points[0].x, points[-1].x, interval)
    x = np.array([i.x for i in points])
    y = np.array([i.y for i in points])
    f = interp1d(x, y, kind='cubic', fill_value='extrapolate')
    y_new = f(x_new)
    x1 = list(x_new)
    y1 = list(y_new)
    points = [vec(x1[i], y1[i]) for i in range(len(x1))]
    return points

    ##############################################################################################

class Water_Spring(pygame.sprite.Sprite):
    def __init__(self, pos, target_height=None):
        super().__init__()
        self.pos = pos
        self.radius = 2
        self.target_height = target_height if target_height else self.pos + vec(0, TILE_SIZE//8)

        self.dampening = 0.05 * 2
        self.tension = 0.01
        self.vel = 0
        self.held = False
        self.pinned = False

    def mouse_collide(self, offset):
        mouse = pygame.mouse.get_pressed()
        mousePos = vec(pygame.mouse.get_pos())

        if mouse[0]:
            if vec(mousePos).distance_to(self.pos - offset) < self.radius:
                self.held = True
        else:
            self.held = False

        if self.held:
            self.pos.y = vec(mousePos).y + offset.y

    def move(self):
        if self.pinned:
            return 
        
        dh = self.target_height - self.pos.y
        if abs(dh) < 0.01:
            self.pos.y = self.target_height
        
        self.vel += self.tension * dh - self.vel * self.dampening
        self.pos.y += self.vel

    def update(self, screen, offset):
        self.mouse_collide(offset)
        self.move()
        # self.draw(screen, offset)

    def draw(self, screen, offset):
            
            start, end = int(min(self.pos.y, self.target_height)), int(max(self.pos.y, self.target_height))
            for y in range(start, end, 20):
                pygame.draw.circle(screen, (255, 255, 255), vec(self.pos.x, y) - offset, self.radius/8)

            pygame.draw.circle(screen, (255, 255, 255), self.pos - offset, self.radius)

class Water:
    def __init__(self, pos, size, variant):
        self.pos = vec(pos) * TILE_SIZE
        self.variant = variant
        self.size = vec(size) * TILE_SIZE
        self.z = Z_LAYERS["midground offgrid"]
        
        self.col = [(0, 134, 191, 64), ][variant]
        # self.image.set_alpha((65))

        self.springs = pygame.sprite.Group()
        self.spacing = TILE_SIZE/2
        for i in range(int(self.pos.x), int(self.pos.x + self.size.x)+int(self.spacing), int(self.spacing)):
            self.springs.add(Water_Spring(vec(i, self.pos.y + TILE_SIZE//8), self.pos.y + TILE_SIZE//8))
        self.springs.sprites()[0].pinned = True
        self.springs.sprites()[-1].pinned = True

    def spread_wave(self):
        spread = 0.02
        for i in range(len(self.springs)):
            springs = self.springs.sprites().copy()
            if i > 0:
                springs[i - 1].vel += spread * (springs[i].pos.y - springs[i - 1].pos.y)
            try:
                springs[i + 1].vel += spread * (springs[i].pos.y - springs[i + 1].pos.y)
            except IndexError:
                pass

    def player_collision(self, player):
        if player.vel.y <= 0:
            return
        
        for spring in self.springs.sprites():
            if spring.pinned: continue
            if player.hitbox.collidepoint(spring.pos):
                spring.pos.y += 1.1 ** player.vel.y

    def update(self, screen, offset):
        self.springs.update(screen, offset)
        self.spread_wave()

        self.draw(screen, offset)

    def draw(self, screen, offset):
        springs = self.springs.sprites().copy()
        points = get_curve(list(map(lambda s: s.pos, springs)))
        # pygame.draw.circle(screen, (255, 0, 255), points[-1] - offset, 4)

        # surf = pygame.Surface(self.size, pygame.SRCALPHA)
        # surf.fill(self.col)
        # screen.blit(surf, self.pos - offset + vec(0, TILE_SIZE//8))

        surf = pygame.Surface(SIZE, pygame.SRCALPHA)
        pygame.draw.polygon(
            surf,
            self.col,
            [vec(self.pos[0], self.pos[1]+self.size[1]) - offset, 
             *list(map(lambda p:p-offset, points)), 
             vec(self.pos[0]+self.size[0], self.pos[1]+self.size[1]) - offset]
        )
        surf.set_alpha(192)
        screen.blit(surf, (0, 0))

        for i in range(2, len(points)):
            pygame.draw.line(screen, (255, 255, 255), points[i-1] - offset, points[i] - offset)

    ##############################################################################################

def segment_water(water_tiles):
    groups = []
    visited = set()
    for pos in water_tiles:
        if pos not in visited:
            group = []
            dfs(pos, water_tiles, visited, group)
            groups.append(group)
    return groups

def get_adjacent_tiles(pos, tiles):
    x, y = pos
    adjacent_tiles = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if (dx != dy) and (x + dx, y + dy) in tiles:
                adjacent_tiles.append((x + dx, y + dy))
    return adjacent_tiles

def dfs(start_pos, tiles, visited, group):
    visited.add(start_pos)
    group.append([start_pos, tiles[start_pos]])
    adjacent_tiles = get_adjacent_tiles(start_pos, tiles)
    for tile in adjacent_tiles:
        if tile not in visited:
            dfs(tile, tiles, visited, group)