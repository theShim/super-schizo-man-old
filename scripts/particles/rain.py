import contextlib
from typing import Any
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math
import numpy as np

from scripts.config.CORE_FUNCS import vec
from scripts.config.SETTINGS import Z_LAYERS, GRAV, ENVIRONMENT_SETTINGS, TILE_SIZE

    ################################################################################################

class Rain_Particle(pygame.sprite.Sprite):
    def __init__(self, parent, pos, music_player):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["foreground particle"]
        self.music_player = music_player

        self.length = random.randint(4, 8)
        self.fall_speed = random.uniform(5, 10) * 4
        
        self.top_x = random.uniform(0.2, 2)
        self.bottom_x = self.top_x + random.uniform(0.4, 2) / 100
        self.top_x *= ENVIRONMENT_SETTINGS["wind"]
        self.bottom_x *= ENVIRONMENT_SETTINGS["wind"]
        
        self.pos = vec(pos)
        self.end_pos = vec(self.pos.x, self.pos.y + self.length + self.bottom_x)

        self.collision = random.randint(1, 100) == 1

    def move(self):
        self.pos.y += GRAV * self.fall_speed
        self.end_pos.y += GRAV * self.fall_speed

        self.pos.x += self.top_x
        self.end_pos.x += self.bottom_x

    def tile_collisions(self, tiles):
        if len(tiles):
            probability = int(2000 / len(tiles)) + 1
            if random.randint(1, probability) == 1:
                t = random.choice(list(tiles))
                pos = [random.uniform((t.pos[0] * TILE_SIZE), (t.pos[0] * TILE_SIZE) + TILE_SIZE), (t.pos[1] * TILE_SIZE) + random.uniform(0, TILE_SIZE/2)]
                for i in range(1, 3):
                    self.parent.add(Rain_Splash(self.parent, pos, random.uniform(1.5, 2.5)))
                    self.music_player.play("rain_splash", "rain")
        
    def update(self, screen, offset, tiles):
        self.move()
        if self.collision and ENVIRONMENT_SETTINGS["rain"]:
            self.tile_collisions(list(tiles))
        self.draw(screen, offset)

    def draw(self, screen, offset):
        pygame.draw.line(screen, (173, 206, 240), self.pos - offset, self.end_pos - offset)


class Rain_Splash(pygame.sprite.Sprite):
    def __init__(self, parent, pos, scale):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["foreground particle"]

        self.pos = vec(pos)
        self.scale = scale
        self.angle = math.radians(random.uniform(-120, -60))
        self.rotation = math.radians(random.uniform(0, 90))
        self.speed = random.uniform(4, 8)
        self.colour = (173, 206, 240)
        self.grav = 0

    def move(self):
        self.pos += vec(math.cos(self.angle), math.sin(self.angle)) * self.speed
        self.pos.y += self.grav
        self.grav += GRAV * 2

    def update(self, screen, offset):
        self.scale -= 0.2
        if self.scale <= 0:
            self.parent.remove(self)

        self.rotation += math.radians(self.speed)
        self.move()

        self.draw(screen, offset)

    def draw(self, screen, offset):
        points = [
            vec(math.cos(self.rotation), math.sin(self.rotation)) * self.scale,
            vec(math.cos(self.rotation + math.pi/2), math.sin(self.rotation + math.pi/2)) * self.scale,
            vec(math.cos(self.rotation + math.pi), math.sin(self.rotation + math.pi)) * self.scale,
            vec(math.cos(self.rotation + 3*math.pi/2), math.sin(self.rotation + 3*math.pi/2)) * self.scale,
        ]
        points = [p + self.pos - offset for p in points]
        pygame.draw.polygon(screen, self.colour, points)
        pygame.draw.polygon(screen, list(map(lambda x: x-100, self.colour)), points, math.ceil(self.scale/4))