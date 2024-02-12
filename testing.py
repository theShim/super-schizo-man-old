import pygame; pygame.init()

import numpy as np
import random
from scipy.spatial import Delaunay
import math

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.config.CORE_FUNCS import vec

    ##############################################################################################

class Delaunay_Background:
    
    @classmethod
    def point_on_triangle(cls, pt1, pt2, pt3):
        """
        Random point on the triangle with vertices pt1, pt2 and pt3.
        """
        x, y = sorted([random.random(), random.random()])
        s, t, u = x, y - x, 1 - y
        return (s * pt1[0] + t * pt2[0] + u * pt3[0],
                s * pt1[1] + t * pt2[1] + u * pt3[1])
    
    @classmethod
    def get_colour(cls, height):
        prop = max(0, min(1, -0.1+(height / HEIGHT)))
        cols = [[196, 187, 148], [191, 186, 140], [187, 185, 133], [187, 185, 133], [180, 173, 123], [183, 172, 123], [183, 172, 123], [179, 167, 119], [175, 162, 115]]

        index_lower = int(prop * (len(cols) - 1))
        index_upper = min(index_lower + 1, len(cols) - 1)

        color_lower = cols[index_lower]
        color_upper = cols[index_upper]

        interpolated_color = tuple(
            int(color_lower[i] + prop * (color_upper[i] - color_lower[i]))
            for i in range(3)
        )

        return interpolated_color
    
    def __init__(self, game, point_num=100):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))#pygame.display.get_surface()
        self.game = game

        self.super_triangle = [
            vec(WIDTH/2, 50),
            vec(50, HEIGHT-50),
            vec(WIDTH-50, HEIGHT-50)
        ]

        self.points = np.array([
            vec(random.uniform(-50, WIDTH+50), random.uniform(-50, HEIGHT+50)) for i in range(point_num)
        ] + [
            vec(-50, -50),
            vec(-50, HEIGHT+50),
            vec(WIDTH+50, -50),
            vec(WIDTH+50, HEIGHT+50)
        ])
        self.vectors = np.array([
            vec([random.uniform(-1, 1)*0.5, random.uniform(-1, 1)*0.2]) for i in range(point_num)
        ] + [
            vec(0, 0),
            vec(0, 0),
            vec(0, 0),
            vec(0, 0),
        ])

    def update(self):
        self.points += self.vectors

        condition1 = self.points[:, 0] < -50
        condition2 = self.points[:, 1] < -50
        condition3 = self.points[:, 0] > WIDTH + 50
        condition4 = self.points[:, 1] > HEIGHT + 50

        self.vectors[condition1, 0] *= -1
        self.vectors[condition2, 1] *= -1
        self.vectors[condition3, 0] *= -1
        self.vectors[condition4, 1] *= -1

        self.triangles = Delaunay(self.points)
        self.draw()

    def draw(self):
        for polygon in self.triangles.simplices:
            polygon = self.points[polygon]

            height = polygon[polygon[:, 1].argsort()][-1][1]
            col = self.get_colour(height)
            pygame.draw.polygon(self.screen, col, polygon, 0)

bg = Delaunay_Background(None, 100)
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
    bg.update()
    pygame.display.update()
    clock.tick(60)