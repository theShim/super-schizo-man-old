import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import math
import random
import os
import numpy as np

from scripts.config.SETTINGS import TILE_SIZE, Z_LAYERS, GRAV, FRIC
from scripts.config.CORE_FUNCS import vec, euclidean_distance

    ##############################################################################################

class Torch(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        Torch.SPRITES = []
        for img_name in sorted(os.listdir('assets/offgrid_tiles/torch')):
            img = pygame.image.load('assets/offgrid_tiles/torch/' + img_name).convert_alpha()
            img.set_colorkey((0, 0, 0))
            Torch.SPRITES.append(img)
            yield

    def __init__(self, pos, variant):
        super().__init__()
        self.type = 'torch'
        self.variant = variant
        self.pos = pos
        self.z = Z_LAYERS["foreground offgrid"]

        self.facing = ['forward', 'left', 'right'][self.variant]
        self.flame_intensity = 2
        self.start = True

    @property
    def dict(self):
        return {'type':self.type, "pos":self.pos, "variant":self.variant}
    
    def update(self, screen, offset, particle_manager):
        img = Torch.SPRITES[self.variant]
        screen.blit(img, self.pos - offset)

        if self.start:
            for i in range(self.flame_intensity * 10):
                particle_manager.add_particle("foreground", "fire", pos=(self.pos + vec(random.uniform(-5, 5) + 12, random.uniform(-5, 5) - 2)), radius=random.uniform(1, 3))
            self.start = False

class Bridge(pygame.sprite.Sprite):
    def __init__(self, pos, variant, end_pos):
        super().__init__()
        self.type = "bridge"
        self.variant = variant
        self.z = Z_LAYERS["foreground offgrid"]

        self.pos = [pos[0] + 5, pos[1] + 5]
        self.end_pos = [end_pos[0] + 5, end_pos[1] + 5]

        self.points = np.linspace(self.pos, self.end_pos, 12)
        self.old_points = self.points.copy()
        self.pinned = [0, len(self.points)-1]
        self.joints = [(i, i+1) for i in range(len(self.points)-1)]
        self.lengths = []
        for j in self.joints:
            p1 = self.points[j[0]].tolist()
            p2 = self.points[j[1]].tolist()
            length = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2) - 5
            self.lengths.append(length)

    @property
    def dict(self):
        return {'type':self.type, "pos":self.pos, "end_pos":self.end_pos, "variant":self.variant}
    
    def move(self):
        temp = self.points.copy()

        delta = (self.points - self.old_points)
        delta[:, 1] += GRAV / 4 + random.random() / 25
        immovable_mask = np.zeros_like(self.points, dtype=bool)
        immovable_mask[self.pinned] = True
        delta[immovable_mask] = 0

        self.points += delta
        self.old_points = temp

    def constrain(self):
        for joint, length in zip(self.joints, self.lengths):
            p1, p2 = self.points[joint[0]], self.points[joint[1]]
            diff = p1 - p2
            dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

            try:
                update = 0.5 * diff * (length - dist) / dist
                update[np.isnan(update)] = 0  
            except ZeroDivisionError:
                update = np.zeros_like(diff)

            if not (joint[0] in self.pinned or joint[1] in self.pinned):
                self.points[joint[0]] += update
                self.points[joint[1]] -= update
            elif joint[0] not in self.pinned and joint[1] in self.pinned:
                self.points[joint[0]] += 2 * update
            elif joint[0] in self.pinned and joint[1] not in self.pinned:
                self.points[joint[1]] -= 2 * update

    def draw_segment(self, screen, offset, joint):
        a = vec(self.points[joint[0]].tolist())
        b = vec(self.points[joint[1]].tolist())
        p1 = a.lerp(b, 0.1)
        p2 = b.lerp(a, 0.1)

        delta_y = p2[1] - p1[1]
        delta_x = p2[0] - p1[0]
        angle = math.atan2(delta_y, delta_x)

        cos = math.cos
        sin = math.sin
        points = [
            p1 + vec(cos(angle-90), sin(angle-90)) * 5 - offset,
            p1 + vec(cos(angle+90), sin(angle+90)) * 5 - offset,
            p2 + vec(cos(angle+90), sin(angle+90)) * 5 - offset,
            p2 + vec(cos(angle-90), sin(angle-90)) * 5 - offset,
        ]

        pygame.draw.polygon(screen, (154, 57, 28), points)
        pygame.draw.polygon(screen, (125, 38, 12), points, 1)

    def update(self, screen, offset):
        self.move()
        self.constrain()

        for j in self.joints:
            p1 = self.points[j[0]].tolist()
            p2 = self.points[j[1]].tolist()
            pygame.draw.line(screen, (154, 57, 28), vec(p1) - offset, vec(p2) - offset, 1)

            self.draw_segment(screen, offset, j)

        #temporarily showing joints
        # for p in self.points:
        #     pygame.draw.circle(screen, (255, 255, 255), vec(p.tolist()) - offset, 5)