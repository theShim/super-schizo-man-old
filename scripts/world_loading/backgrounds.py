import pygame; pygame.init()

from perlin_numpy import generate_fractal_noise_2d
import numpy as np
import random
from scipy.spatial import Delaunay
import math

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.config.CORE_FUNCS import vec

    ##############################################################################################

class Editor_Background:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.line_width = 40
        self.line_speed = 1
        self.lines = [
            [[0, HEIGHT - (i*self.line_width)], [WIDTH, HEIGHT - self.line_width * 4 - (i*self.line_width)]]
            for i in range(-6, 9, 2)
        ]

    def update(self):
        #diagonal lines scrolling up
        for l in self.lines:
            p1 = l[0]
            p2 = l[1]
            pygame.draw.line(self.screen, (20, 20, 20), p1, p2, self.line_width)

            p1[1] -= self.line_speed
            p2[1] -= self.line_speed
            if p1[1] < -self.line_width:
                p1[1] = HEIGHT - (-5*self.line_width)
                p2[1] = HEIGHT - self.line_width * 4 - (-5*self.line_width)


class Forest_Background:

    @classmethod
    def cache_sprites(cls):
        Forest_Background.CACHED_BACKGROUNDS = {}
        Forest_Background.SPRITES = [pygame.image.load(f'assets/worlds/Forest/bg-{i}.png').convert_alpha() for i in range(4)]
        Forest_Background.SPRITES = [pygame.transform.scale(s, vec(s.get_size()) * 1.75) for s in Forest_Background.SPRITES]

        #parallax scrolled tree backgrounds
        for offsetx in range(-WIDTH//2, int(WIDTH*1.5), 8):
            cls.cache(offsetx)
            yield

    @classmethod
    def cache(cls, offsetx):
        bg = pygame.Surface((WIDTH*2, HEIGHT*2))
        bg.fill((144, 202, 183))
        speed = 0
        x = 0

        for spr in Forest_Background.SPRITES:
            bg.blit(spr, (int(offsetx - WIDTH) * (x*speed) - 100, -spr.get_height()/2.5))
            speed -= 0.005
            x += 1
            
        Forest_Background.CACHED_BACKGROUNDS[offsetx] = bg


    def __init__(self, game):
        self.screen = pygame.display.get_surface()
        self.sprites = [pygame.image.load(f'assets/worlds/Forest/bg-{i}.png').convert_alpha() for i in range(4)]
        self.sprites = [pygame.transform.scale(s, vec(s.get_size()) * 1.75) for s in self.sprites]
        [s.set_colorkey((0, 0, 0)) for s in self.sprites]
        self.game = game

    def update(self):
        #try find it in cache otherwise just make a new parallaxed sprite
        #maybe add it to cache asw but i cba
        try:
            spr = self.CACHED_BACKGROUNDS[8 * round(self.game.offset.x/8)]
            self.screen.blit(spr, (0, 0))   
        except:
            self.cache(self.game.offset.x)

class Perlin_Background:
    NOISE = generate_fractal_noise_2d(
        (160, 160),
        (8, 8),
        3,
    )
    NOISE = NOISE[:, :100]

    CACHE = {}

    @classmethod
    def add_colour(cls, noise: np.ndarray):
        color_world = np.zeros(noise.shape+(3,))
        
        noise = noise.copy() * 2

        condition = (noise % 4 < 4.1)
        color_world[condition] = [9, 10, 27]
        condition = (noise % 4 < 3.5)
        color_world[condition] = [4, 3, 6]
        condition = (noise % 4 < 2.6)
        color_world[condition] = [14, 19, 32]
        condition = (noise % 4 < 1.9)
        color_world[condition] = [17, 25, 37]

        return color_world
    
    def __init__(self, game):
        self.screen = pygame.display.get_surface()
        self.game = game
        self.og_offset = int((self.game.offset.x + self.game.offset.y)/1000)
    
    def update(self):
        target_offset = ((self.game.offset.x + self.game.offset.y)/1000) % 4.1
        self.NOISE -= min(max(-0.01, self.og_offset - target_offset), 0.01)
        self.og_offset += (target_offset - self.og_offset) * .1

        try:
            surf = self.CACHE[round(self.og_offset, 2)]
        except:
            surf = pygame.surfarray.make_surface(self.add_colour(self.NOISE))
            surf = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size())*4)
            self.CACHE[self.og_offset] = surf
        self.screen.blit(surf, (0, 0))


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
        self.screen = pygame.display.get_surface()
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

class Black_Screen_Background:
    def __init__(self, game):
        self.screen = pygame.display.get_surface()
        self.game = game

    def update(self):
        self.screen.fill((0, 0, 0))