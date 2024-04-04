import contextlib
from typing import Any
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    import pygame.gfxdraw

import random
import math
import numpy as np

from scripts.config.CORE_FUNCS import vec, lerp, bezierfy
from scripts.config.SETTINGS import Z_LAYERS

    ##############################################################################################

class Slash_Wave(pygame.sprite.Sprite):
    def __init__(self, game_entities, pos, angle):
        super().__init__()
        self.game_entities = game_entities
        self.z = Z_LAYERS["attacks"]

        self.angle = angle + math.radians(random.uniform(-10, 10))
        self.colour = (255, 255, 255)
        self.alpha = 255
        self.speed = 1
        self.fill = 2
        self.fill_speed = 1
        self.gapfill_speed = random.uniform(1, 2)
        
        start_pos = pos + vec(math.cos(self.angle), math.sin(self.angle)) * 30
        self.points = np.array([
            start_pos + vec(math.cos(self.angle - 30), math.sin(self.angle - 30)) * 30 - vec(math.cos(self.angle), math.sin(self.angle)) * 20 + vec(math.cos(self.angle), math.sin(self.angle)) * random.uniform(-10, 10),
            start_pos + vec(math.cos(self.angle + 30), math.sin(self.angle + 30)) * 30 - vec(math.cos(self.angle), math.sin(self.angle)) * 20 + vec(math.cos(self.angle), math.sin(self.angle)) * random.uniform(-10, 10),
            start_pos + vec(math.cos(self.angle), math.sin(self.angle)) * random.uniform(20, 40),
            start_pos - vec(math.cos(self.angle), math.sin(self.angle)) * 4
        ])
        # for p in self.points:
        self.points += vec(math.cos(self.angle), math.sin(self.angle)) * random.uniform(-5, 5)


    def move(self):
        # for p in self.points:
        self.points += vec(math.cos(self.angle), math.sin(self.angle)) * self.speed
        self.points[3] += vec(math.cos(self.angle), math.sin(self.angle)) * self.gapfill_speed
        self.points[random.randint(0, len(self.points)-1)] += vec(math.cos(self.angle), math.sin(self.angle)) * self.gapfill_speed / 2

    def update(self, screen, offset):
        self.alpha -= 12
        if self.alpha <= 10:
            return self.game_entities.remove(self)
        
        self.fill += self.fill_speed
        
        self.move()
        self.draw(screen, offset)

    def draw(self, screen, offset):
        # for p in self.points:
        #     pygame.draw.circle(screen, (255, 255, 0), p-offset, 2)

        back_curve = [self.points[1], self.points[2], self.points[0]]
        back_points = [p-offset for p in bezierfy(back_curve, self.fill_speed*10)]
        # pygame.draw.lines(screen, (0, 255, 255), False, back_points, 2)

        front_curve = [self.points[1], self.points[3], self.points[0]]
        front_points = [p-offset for p in bezierfy(front_curve, self.fill_speed*10)]
        # pygame.draw.lines(screen, (0, 255, 255), False, front_points, 2)

        points = back_points[:int(self.fill)+5]
        points += front_points[:int(self.fill)][::-1]
        pygame.gfxdraw.filled_polygon(screen, points, (*self.colour, self.alpha))

        # pygame.draw.circle(screen, (255, 0, 255), self.pos-offset, 2)


class Slash(pygame.sprite.Sprite):
    def __init__(self, game_entities, pos, angle):
        super().__init__()
        self.game_entities = game_entities
        self.z = Z_LAYERS["attacks"]

        self.angle = angle
        self.pos = pos + vec(math.cos(self.angle), math.sin(self.angle)) * 40
        self.rot = math.radians(random.uniform(0, 360))
        self.alpha = 255

        self.slash_length = random.randint(8, 12)

    def move(self):
        pass

    def update(self, screen, offset):
        self.alpha -= 12
        if self.alpha <= 10:
            return self.game_entities.remove(self)
        
        self.move()
        self.draw(screen, offset)

    def draw(self, screen, offset):

        spark_points = [
            -offset + self.pos + vec(math.cos(self.rot), math.sin(self.rot)) * self.slash_length * 2,
            -offset + self.pos + vec(math.cos(self.rot + 90), math.sin(self.rot + 90)) * 5,
            -offset + self.pos + vec(math.cos(self.rot), math.sin(self.rot)) * -self.slash_length * 2.5,
            -offset + self.pos + vec(math.cos(self.rot - 90), math.sin(self.rot - 90)) * 5,
        ]
        pygame.draw.polygon(screen, (self.alpha, self.alpha, self.alpha), spark_points)