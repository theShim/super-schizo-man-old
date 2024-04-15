import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random
import os
import numpy as np

from scripts.config.SETTINGS import TILE_SIZE, Z_LAYERS, ENVIRONMENT_SETTINGS, FRIC
from scripts.config.CORE_FUNCS import vec, euclidean_distance

    ##############################################################################################

class Swaying_Vine(pygame.sprite.Sprite):
    def __init__(self, pos, variant, scale=2):
        super().__init__()
        self.pos = pos
        self.variant = variant
        self.z = Z_LAYERS["midground offgrid"]

        self.points = np.array([                    #verlet points
            (-1, 0), (2, 0), (4, 0), (7, 0),
            (3, 2),
            (0.5, 2.5), (5.5, 2.5),
            (3, 4.75),
            (1, 7.75), (5, 7.75),
            (1.2, 10), (4.8, 10),
            (3, 11),
            (1.5, 13), (4.5, 13),
            (2.7, 14), (3.3, 14),
            (3, 18)
        ])
        self.points = self.points * scale + pos
        self.old_points = self.points.copy()
        self.pinned = [0, 1, 2, 3,]             #points on the vine that don't move at all
        
        self.joints = [                 #connections between points
            (0, 1), (1, 2), (2, 3),
            (0, 4), (1, 4), (2, 4), (3, 4),
            (0, 5), (3, 6), (4, 7),
            (5, 7), (6, 7), (5, 8), (6, 9),
            (7, 8), (7, 9),
            (8, 10), (9, 11), (8, 11), (9, 10),
            (7, 12), (10, 12), (11, 12),
            (12, 15), (12, 16), (12, 17),
            (15, 17), (16, 17),
            (10, 13), (11, 14),
            (13, 15), (14, 16)
        ]
        #the maximum joint lengths
        self.lengths = [euclidean_distance(self.points[self.joints[i][0]], self.points[self.joints[i][1]]) 
                        for i in range(len(self.joints))]

        #the polygon indices to draw
        self.polys = [(0, 1, 4), (1, 2, 4), (2, 3, 4), 
                      (0, 4, 7, 5), (3, 4, 7, 6),
                      (5, 7, 8), (6, 7, 9), (7, 8, 11, 9), (7, 9, 10, 8), (9, 10, 12, 11),
                      (12, 10, 13, 15), (12, 11, 14, 16),
                      (12, 15, 17), (12, 16, 17)]

        self.wind_offset = math.radians(self.pos[0] // 4) #wind sim
        self.wind_clock = 0

    #verlet integration
    def move(self):
        temp = self.points.copy()

        delta = (self.points - self.old_points)
        delta[:, 0] *= FRIC
        delta[:, 1] += 9.81/2
        delta[:, 0] += (math.sin(self.wind_clock + self.wind_offset + random.random() / 6))
        immovable_mask = np.zeros_like(self.points, dtype=bool)
        immovable_mask[self.pinned] = True
        delta[immovable_mask] = 0

        self.points += delta
        self.old_points = temp

    #after moving, constrain the joints to the initialised self.lengths
    def constrain(self):
        for joint, length in zip(self.joints, self.lengths):
            p1, p2 = self.points[joint[0]], self.points[joint[1]]
            diff = p1 - p2
            dist = euclidean_distance(p1, p2)

            try:
                update = 0.5 * diff * (length - dist) / dist
                update[np.isnan(update)] = 0  
            except ZeroDivisionError:
                update = np.zeros_like(diff)

            if not (joint[0] in self.pinned or joint[1] in self.pinned):
                self.points[joint[0]] += update
                self.points[joint[1]] -= update
            elif joint[0] not in self.pinned and joint[1] in self.pinned:
                self.points[joint[0]] += 2 * np.int_(update)
            elif joint[0] in self.pinned and joint[1] not in self.pinned:
                self.points[joint[1]] -= 2 * update
        
    def update(self, screen, offset):
        self.wind_clock += math.radians(ENVIRONMENT_SETTINGS["wind"])
        self.move()
        self.constrain()
        self.draw(screen, offset)

    def draw(self, screen, offset):
        for poly in self.polys:
            points = (self.points[np.array(poly)] - list(offset)).tolist()
            pygame.draw.polygon(screen, (20, 180, 67), points, 0)
            pygame.draw.polygon(screen, (40-25, 180-25, 97-25), points, 1)