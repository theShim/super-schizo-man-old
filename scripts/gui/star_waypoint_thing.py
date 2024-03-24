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
from scripts.config.CORE_FUNCS import vec, vec3, Timer
from scripts.config.MATRIX_FUNCS import MatrixFunctions as mf

    ##############################################################################################

class Starry_Background:
    def __init__(self):
        self.stars = [Star(z=random.uniform(1, Star.Z_DISTANCE)) for i in range(180)]
        self.planets = [Constellation()]

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
        for s in sorted(self.stars, key=lambda x:x.pos_3d.z, reverse=True):
            s.update(screen)

        for p in self.planets:
            p.update(screen)

        ##########################################################################################

class Star:
    Z_DISTANCE = 40
    
    def __init__(self, z=None):
        self.pos_3d = self.get_pos_3d()
        self.pos_3d.z = z if z != None else self.pos_3d.z

        c = random.uniform(160, 255) - 40
        self.color = (c, c, c)
        self.size = 10
        self.radius = 1.5

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
        self.move()
        self.size = max(1, (Star.Z_DISTANCE / (self.pos_3d.z * self.radius)))
        if self.size >= 1:
            self.draw(screen)
        else:
            self.draw(screen, True)

    def draw(self, screen, pixel=False):
        pos_2d = self.get_pos_2d()
        if pygame.Rect(0, 0, WIDTH, HEIGHT).collidepoint(pos_2d):
            if pixel:
                screen.set_at(pos_2d, self.color)
            else:
                pygame.draw.circle(screen, self.color, pos_2d, self.size)

        ##########################################################################################

class Constellation:
    def __init__(self):
        self.colour = (200, 0, 200)
        self.radius = 64
        self.vel = 0.125
        self.rots = [0, 0, 0]
        self.scale = 100

        self.camera = vec3(0, 0, -312.5)
        self.projection_plane = 500
        self.points = [Constellation_Point(self) for i in range(12)]
        self.joints = {(i-1, i) : Orbiting_Constellation_Point(
            self, 
            (point_set:=[self.points[i-1], self.points[i]]),
            sorted([random.random(), 0.1, 0.9])[1]
        )for i in range(len(self.points))}
        for joint in self.joints: self.joints[joint] = self.joints[joint] if random.randint(1, 4) == 1 else None
        self.remnants = []
        self.centre = (WIDTH/2, HEIGHT/2 + 12)
    
    def camera_move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.camera.z -= 0.5
        if keys[pygame.K_s]:
            self.camera.z += 0.5

    def update(self, screen):
        # self.rots[0] -= math.radians(0.6)
        self.rots[1] += math.radians(0.5)

        self.camera_move()
        self.draw(screen)

    def draw(self, screen):
        for remnant in self.remnants:
            remnant.update(screen)

        draw_joint = lambda start, end: pygame.draw.line(screen, (200, 0, 255), start.get_pos_2d(), end.get_pos_2d(), 1)
        for joint in sorted(self.joints.keys(), key=lambda j: vec3(self.points[j[0]].pos).lerp(vec3(self.points[j[1]].pos), 0.5).z, reverse=True):
            start = self.points[joint[0]]
            end = self.points[joint[1]]

            if (orbiting_point := self.joints.get(joint, None)) != None:
                midpoint = vec3(start.pos).lerp(vec3(end.pos), orbiting_point.t)
                rotated_point = np.dot(mf.rotate_x(self.rots[0]), midpoint)
                rotated_point = np.dot(mf.rotate_y(self.rots[1]), rotated_point)
                rotated_point = np.dot(mf.rotate_z(self.rots[2]), rotated_point)

                if orbiting_point.current_vector().z < rotated_point[2]:
                    orbiting_point.update(screen)
                    draw_joint(start, end)
                else:
                    draw_joint(start, end)
                    orbiting_point.update(screen)
            else:
                draw_joint(start, end)

            start.update(screen)
            end.update(screen)

        end.draw(screen)

class Constellation_Point:
    def __init__(self, parent):
        self.parent = parent
        self.pos = self.get_rand_pos()
        self.pos_2d = mf.multiply_matrix(mf.PROJECTION_MATRIX, self.pos)
        self.colour = [200, 0, 200]
        self.radius = 10

        self.angle_offset = math.radians(random.uniform(0, 1))
        self.angle_mod = math.radians(random.uniform(0, 1)) / 10

    def get_rand_pos(self):
        r = self.parent.radius
        point = [random.uniform(-r, r), random.uniform(-r, r), random.uniform(-r, r)]
        return point
    
    def rotate_3d(self, angle_offset=0):
        point3D = self.pos.copy()
        rotated_point = np.dot(mf.rotate_x(self.parent.rots[0] + angle_offset), point3D)
        rotated_point = np.dot(mf.rotate_y(self.parent.rots[1] + angle_offset), rotated_point)
        rotated_point = np.dot(mf.rotate_z(self.parent.rots[2] + angle_offset), rotated_point)
        return rotated_point
    
    def get_pos_2d(self, rot=True):
        point3D = self.pos.copy()
        camera = self.parent.camera
        projection_plane = self.parent.projection_plane

        point3D = self.rotate_3d(self.angle_offset) if rot else point3D

        x = (point3D[0] - camera[0]) * projection_plane / (point3D[2] - camera[2]) + self.parent.centre[0]
        y = (point3D[1] - camera[1]) * projection_plane / (point3D[2] - camera[2]) + self.parent.centre[1]
        return (x, y)
    
    def get_z_distance(self, pos=None):
        point3D = self.pos.copy() if pos == None else pos
        camera = self.parent.camera

        z_distance = math.sqrt((point3D[0] - camera[0]) ** 2 + (point3D[1] - camera[1]) ** 2 + (point3D[2] - camera[2]) ** 2)
        return z_distance
    
    def update(self, screen):
        self.angle_offset += self.angle_mod
        self.draw(screen)

    def draw(self, screen):
        x, y = self.get_pos_2d()
        z_distance = self.get_z_distance()
        radius = max(1, int(200*self.radius / z_distance))

        pygame.draw.circle(screen, (255, 0, 255), (int(x), int(y)), radius)
        pygame.draw.circle(screen, self.colour, (int(x), int(y)), radius, 2)

class Orbiting_Constellation_Point(Constellation_Point):
    def __init__(self, parent, points, start_t=0):
        super().__init__(parent)
        for var in list(vars(self).keys()):
            delattr(self, var)

        self.parent = parent
        self.start = points[0]
        self.end = points[1]
        self.t = start_t
        self.t_mod = random.random()/500 * random.choice([-1, 1])
        self.radius = random.uniform(5, 8)
        self.orbit_radius = 6
        self.a = 0

    def current_pos(self):
        start_3D = self.start.rotate_3d(self.start.angle_offset)
        end_3D =   self.end.rotate_3d(self.end.angle_offset)
        return vec3(start_3D.tolist()).lerp(vec3(end_3D.tolist()), self.t)

    def current_vector(self):
        pos = self.current_pos()

        v = self.end.rotate_3d(self.end.angle_offset) - self.start.rotate_3d(self.start.angle_offset)
        normal_vectors = [
            (0, v[2], -v[1]),  # (0, z, -y)
            (v[2], 0, -v[0]),  # (z, 0, -x)
            (v[1], -v[0], 0)   # (y, -x, 0)
        ]
        for v_norm in normal_vectors:
            if any(v_norm):
                break
        
        angle = np.radians(self.a%360)
        axis = v / np.linalg.norm(v)
        cos_theta = np.cos(angle)
        sin_theta = np.sin(angle)
        cross = np.cross(axis, v_norm)
        dot = np.dot(axis, v_norm)
        v_rotted = np.array(v_norm) * cos_theta + cross * sin_theta + axis * dot * (1 - cos_theta)
        pos += vec3(v_rotted.tolist()).normalize() * self.orbit_radius

        return pos
    
    def get_pos_2d(self, pos):
        point3D = pos
        camera = self.parent.camera
        projection_plane = self.parent.projection_plane

        x = (point3D[0] - camera[0]) * projection_plane / (point3D[2] - camera[2]) + self.parent.centre[0]
        y = (point3D[1] - camera[1]) * projection_plane / (point3D[2] - camera[2]) + self.parent.centre[1]
        return (x, y)

    def update(self, screen):
        self.t += self.t_mod
        if self.t > .9 or self.t < 0.1:
            self.t_mod *= -1
        self.a += 5

        pos = self.current_vector()
        self.parent.remnants.append(Orbiting_Remnant(self.parent, pos, self.radius*0.75))

        self.draw(screen, self.current_vector())

    def draw(self, screen, pos):
        x, y, = self.get_pos_2d(pos)
        z_distance = self.get_z_distance(pos)
        radius = max(1, int(200*self.radius / z_distance))

        pygame.draw.circle(screen, (255, 0, 155), (int(x), int(y)), radius)

class Orbiting_Remnant(Constellation_Point):
    def __init__(self, parent, pos, radius):
        super().__init__(parent)
        self.pos = pos.copy()
        self.colour = [200-20, 0, 200-20-100]
        self.alpha = 255
        self.radius = radius
        self.t = FPS
        
    def update(self, screen):
        self.t -= 1
        if self.t <= 0:
            self.parent.remnants.remove(self)
            return
        
        self.alpha = 255 * (self.t / FPS)
        self.draw(screen)

    def draw(self, screen):
        x, y = self.get_pos_2d(rot=False)
        z_distance = self.get_z_distance()
        radius = max(1, int(200*self.radius / z_distance)) * (self.t / FPS)
        
        surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.colour, (radius, radius), radius)
        surf.set_alpha(self.alpha)

        screen.blit(surf, surf.get_rect(center=(x, y)))