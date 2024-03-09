import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import random
import sys
import math
import time
import numpy as np
import json

    ##############################################################################################

#initialising pygame stuff
pygame.init()  #general pygame
pygame.font.init() #font stuff
pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
pygame.mixer.init()
pygame.event.set_blocked(None) #setting allowed events to reduce lag
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL])
pygame.display.set_caption("")

#initalising pygame window
flags = pygame.DOUBLEBUF #| pygame.FULLSCREEN
SIZE = WIDTH, HEIGHT = (720, 720)
screen = pygame.display.set_mode(SIZE, flags, 16)
clock = pygame.time.Clock()

#renaming common functions
vec = pygame.math.Vector2

#useful functions
def gen_colour():
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

def euclidean_distance(point1, point2):
    try:
        return vec(point1).distance_to(vec(point2))
    except:
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    ##############################################################################################

WIND = 0

class Vine:
    def __init__(self, pos, variant, scale=4):
        self.pos = pos
        self.variant = variant

        self.wind_offset = math.radians(self.pos[0] // 4)

        self.points = np.array([(0, 0), (2, 0), (4, 0), (6, 0),
                       (3, 2),
                       (0.5, 2.5), (5.5, 2.5),
                       (3, 4.75),
                       (1, 7.75), (5, 7.75),
                       (1.2, 10), (4.8, 10),
                       (3, 11),
                       (1.5, 13), (4.5, 13),
                       (2.7, 14), (3.3, 14),
                       (3, 18)])
        self.points = self.points * scale + pos
        self.old_points = self.points.copy()
        self.pinned = [0, 1, 2, 3]
        
        self.joints = [(0, 1), (1, 2), (2, 3),
                       (0, 4), (1, 4), (2, 4), (3, 4),
                       (0, 5), (3, 6), (4, 7),
                       (5, 7), (6, 7), (5, 8), (6, 9),
                       (7, 8), (7, 9),
                       (8, 10), (9, 11), (8, 11), (9, 10),
                       (7, 12), (10, 12), (11, 12),
                       (12, 15), (12, 16), (12, 17),
                       (15, 17), (16, 17),
                       (10, 13), (11, 14),
                       (13, 15), (14, 16)]
        self.lengths = [euclidean_distance(self.points[self.joints[i][0]], self.points[self.joints[i][1]]) for i in range(len(self.joints))]

        self.fill = True
        self.polys = [(0, 1, 4), (1, 2, 4), (2, 3, 4), 
                      (0, 4, 7, 5), (3, 4, 7, 6),
                      (5, 7, 8), (6, 7, 9), (7, 8, 11, 9), (7, 9, 10, 8), (9, 10, 12, 11),
                      (12, 10, 13, 15), (12, 11, 14, 16),
                      (12, 15, 17), (12, 16, 17)]

    def move(self):
        temp = self.points.copy()

        delta = (self.points - self.old_points)
        delta *= (FRIC:=0.9)
        delta[:, 1] += (GRAV:=9.81/4)
        # delta[:, 0] += math.sin(WIND + self.wind_offset) #+ random.random() / 2
        immovable_mask = np.zeros_like(self.points, dtype=bool)
        immovable_mask[self.pinned] = True
        delta[immovable_mask] = 0

        self.points += delta
        self.old_points = temp

    def constrain(self):
        for i, joint in enumerate(self.joints):
            l = self.lengths[i]

            point1, point2 = self.points[joint[0]], self.points[joint[1]]
            p1, p2 = point1, point2
            dist = euclidean_distance(p1, p2)

            diffx, diffy = p1[0] - p2[0], p1[1] - p2[1]
            diff = l - dist

            try: updatex = 0.5 * diffx * diff/dist
            except ZeroDivisionError: updatex = 0
            try: updatey = 0.5 * diffy * diff/dist
            except ZeroDivisionError: updatey = 0


            if not (joint[0] in self.pinned or joint[1] in self.pinned):
                point1[0] += updatex
                point1[1] += updatey
                point2[0] -= updatex
                point2[1] -= updatey

            if not joint[0] in self.pinned and joint[1] in self.pinned:
                point1[0] += int(updatex) * 2
                point1[1] += int(updatey) * 2
            if joint[0] in self.pinned and not joint[1] in self.pinned:
                point2[0] -= updatex * 2
                point2[1] -= updatey * 2
        
    def update(self, screen):
        self.move()
        self.constrain()
        self.draw(screen)

    def draw(self, screen):
        # if self.fill:
        for joint in self.joints:
            p1 = self.points[joint[0]]
            p2 = self.points[joint[1]]
            pygame.draw.line(screen, (255, 255, 255), p1, p2, 1)

        for poly in self.polys:
            points = self.points[np.array(poly)].tolist()
            pygame.draw.polygon(screen, (40-30, 180-30, 97-30), points, 0)

        for poly in self.polys:
            points = self.points[np.array(poly)].tolist()
            pygame.draw.polygon(screen, (20, 180, 67), points, 3)

        # else:
        #     for point in self.points:
        #         pygame.draw.circle(screen, (255, 255, 255), point, 2)

        #     for joint in self.joints:
        #         p1 = self.points[joint[0]]
        #         p2 = self.points[joint[1]]
        #         pygame.draw.line(screen, (255, 255, 255), p1, p2, 1)

vs = [Vine(((i+1)*100, 100), 0) for i in range(3)]

    ##############################################################################################
        


last_time = time.time()

running = True
while running:
    WIND  += math.radians(1)

    dt = time.time() - last_time
    last_time = time.time()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_SPACE:
                for v in vs:
                    v.fill = not v.fill

        # elif event.type == pygame.MOUSEWHEEL:
        #     WIND += event.y / 10

    screen.fill((30, 30, 30))
    #points.update(screen, dt, True)
    for v in vs:
        v.update(screen)

    #fps
    font = pygame.font.SysFont('monospace', 30)
    fps = font.render(f'FPS: {int(clock.get_fps())}', True, (215, 215, 215))
    screen.blit(fps, (0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()