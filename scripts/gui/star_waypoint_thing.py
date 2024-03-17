import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    import pygame.gfxdraw
    from pygame.locals import *

import os
import numpy as np
import random
import math
from scipy.spatial import KDTree, delaunay_plot_2d

from scripts.gui.custom_fonts import Custom_Font

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS
from scripts.config.CORE_FUNCS import vec, Timer
from scripts.config.MATRIX_FUNCS import MatrixFunctions as mf

    ##############################################################################################

class Starry_Background:
    def __init__(self):
        self.stars = [Star(z=random.uniform(1, Star.Z_DISTANCE)) for i in range(180)]
        self.planets = [Sphere()]

    @staticmethod
    def find_nearest_neighbors(stars, distance_threshold):
        positions = [star.pos_3d for star in stars]
        kdtree = KDTree(positions)
        pairs = kdtree.query_pairs(distance_threshold)
        return [(stars[i], stars[j]) for i, j in pairs]
    
    @staticmethod
    def draw_polygons_between_neighbors(screen, stars, distance_threshold):
        pairs = Starry_Background.find_nearest_neighbors(stars, distance_threshold)
        for star1, star2 in pairs:
            pos_2d_1 = star1.get_pos_2d()
            pos_2d_2 = star2.get_pos_2d()

            if not pygame.Rect(0, 0, WIDTH, HEIGHT).collidepoint(pos_2d_1): continue
            if not pygame.Rect(0, 0, WIDTH, HEIGHT).collidepoint(pos_2d_2): continue
            
            # Create a polygon between the two stars
            polygon_points = [pos_2d_1, pos_2d_2]
            # Extend the polygon by a certain factor for visual appeal
            extended_points = [pos_2d_1 + (pos_2d_1 - pos_2d_2) * 0.1,
                            pos_2d_2 + (pos_2d_2 - pos_2d_1) * 0.1]
            pygame.draw.polygon(screen, (255, 255, 255), polygon_points + extended_points)

    @staticmethod
    def draw_lines_between_neighbors(screen, stars, distance_threshold):
        pairs = Starry_Background.find_nearest_neighbors(stars, distance_threshold)
        for star1, star2 in pairs:
            pos_2d_1 = star1.get_pos_2d()
            pos_2d_2 = star2.get_pos_2d()
            # pygame.draw.line(screen, (255, 255, 255), pos_2d_1, pos_2d_2)

            num_points = 150
            for i in range(num_points + 1):
                t = i / num_points
                inv_t = 1 - t

                (x1, y1), (x2, y2) = pos_2d_1, pos_2d_2
                control_x = (pos_2d_1[0] + pos_2d_2[0])/2
                control_y = (pos_2d_1[1] + pos_2d_2[1])/2

                x = inv_t ** 2 * x1 + 2 * inv_t * t * control_x + t ** 2 * x2
                y = inv_t ** 2 * y1 + 2 * inv_t * t * control_y + t ** 2 * y2

                # Interpolate thickness
                thickness = int(star1.size * inv_t + star2.size * t)

                # Draw a circle at each point with calculated thickness
                pygame.gfxdraw.filled_circle(screen, int(x), int(y), thickness, star1.color)

    def update(self, screen):
        pos_2ds = []
        for s in sorted(self.stars, key=lambda x:x.pos_3d.z, reverse=True):
            pos_2ds.append(s.get_pos_2d())
            s.update(screen)

        for p in self.planets:
            p.update(screen)
        

        # points = [[p[0]/p[2] + WIDTH/2, p[1]/p[2] + HEIGHT/2] for p in sphere(100) if p[2] != 0]
        # for p in points:
        #     pygame.draw.circle(screen, (255, 0, 0), p, 1)

        # vertices = Delaunay(pos_2ds)
        # for triangle in vertices.simplices:
        #     for i in range(len(triangle)):
        #         start_index = i
        #         end_index = (i + 1) % len(triangle)

        #         start_point = pos_2ds[triangle[start_index]]
        #         end_point = pos_2ds[triangle[end_index]]

        #         # Interpolate thickness based on radii
        #         start_radius = self.stars[triangle[start_index]].size
        #         end_radius = self.stars[triangle[end_index]].size

        #         thickness = (start_radius + end_radius) / 2  # Take average thickness
        #         pygame.draw.line(screen, (255, 255, 255), start_point, end_point, int(thickness))
            
        # self.draw_lines_between_neighbors(screen, self.stars, distance_threshold=500)
        # self.draw_polygons_between_neighbors(screen, self.stars, distance_threshold=2000)

        ##########################################################################################

class Star:
    Z_DISTANCE = 40
    
    def __init__(self, z=None):
        self.pos_3d = self.get_pos_3d()
        self.pos_3d.z = z if z != None else self.pos_3d.z
        c = random.uniform(160, 255)
        self.color = (c, c, c)
        self.size = 10

        self.vel = random.uniform(0.05, 0.25)
        self.rot_speed = random.uniform(0.1, 0.3)

    def get_pos_3d(self, scale=35):
        angle = math.radians(random.uniform(0, 360))
        radius = random.uniform(HEIGHT//scale, HEIGHT) * scale

        x = radius * math.sin(angle)
        y = radius * math.cos(angle)
        return pygame.math.Vector3(x, y, Star.Z_DISTANCE)
    
    def get_pos_2d(self):
        SCREEN_CENTER = vec((WIDTH, HEIGHT)) / 2
        return vec(SCREEN_CENTER) + vec(self.pos_3d.x, self.pos_3d.y) / self.pos_3d.z
    
    def move(self):
        self.pos_3d.z -= self.vel
        self.pos_3d = self.get_pos_3d() if self.pos_3d.z < 1  or not pygame.Rect(0, 0, WIDTH, HEIGHT).collidepoint(self.get_pos_2d()) else self.pos_3d

        self.pos_3d.xy = self.pos_3d.xy.rotate(self.rot_speed)

    
    def update(self, screen):
        self.move()# / (0.1 * self.pos_3d.z)
        self.size = (Star.Z_DISTANCE / self.pos_3d.z)
        if self.size >= 1:
            self.draw(screen)

    def draw(self, screen):
        pos_2d = self.get_pos_2d()
        if pygame.Rect(0, 0, WIDTH, HEIGHT).collidepoint(pos_2d):
            pygame.draw.circle(screen, self.color, pos_2d, self.size)

        ##########################################################################################

class Sphere:
    def __init__(self):
        self.colour = (200, 0, 200)
        self.radius = 128
        self.vel = 0.125
        self.rots = [0, 0, 0]
        self.scale = 100

        self.points = []

    def update(self, screen):
        self.draw(screen)

    def draw(self, screen):
        pass

class Sphere_Point:
    def __init__(self, parent):
        self.parent = parent
        self.pos = self.get_rand_pos()
        self.pos_2d = mf.multiply_matrix(mf.PROJECTION_MATRIX, self.pos)
        self.colour = [200, 0, 200]
        self.radius = 10

    def get_rand_pos(self):
        return None
    
    def move(self):
        pass
    
    def update(self, screen):
        self.move()
        self.draw(screen)

    def draw(self, screen):

        pos = self.pos
        pos = mf.multiply_matrix(mf.rotate_x(self.parent.rots[0]), pos)
        pos = mf.multiply_matrix(mf.rotate_y(self.parent.rots[1]), pos)
        pos = mf.multiply_matrix(mf.rotate_z(self.parent.rots[2]), pos)
        point_2d = mf.multiply_matrix(mf.PROJECTION_MATRIX, pos)

        x = point_2d[0] * self.parent.scale + (WIDTH//2)
        y = point_2d[1] * self.parent.scale + (HEIGHT//2)
        self.pos_2d = (x, y)