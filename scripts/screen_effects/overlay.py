import pygame; pygame.init()

import os
import json
from perlin_numpy import generate_fractal_noise_2d
import numpy as np

from scripts.config.SETTINGS import WIDTH, HEIGHT, SIZE

    ##############################################################################################

class CRT_Overlay:
    
    def __init__(self, game):
        self.screen = pygame.display.get_surface()
        self.game = game
        self.on = False

        self.surf = pygame.Surface(SIZE, pygame.SRCALPHA)
        self.surf.fill((0, 0, 0, 0))
        for y in range(0, HEIGHT, 3):
            pygame.draw.line(self.surf, (0, 0, 0, 20), (0, y), (WIDTH, y), 1)

    def update(self):
        self.game.screen.blit(self.surf, (0, 0))