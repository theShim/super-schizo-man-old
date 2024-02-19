import pygame; pygame.init()

import numpy as np
import random
from scipy.spatial import Delaunay
import math

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.config.CORE_FUNCS import vec

    ##############################################################################################

screen = pygame.display.set_mode((WIDTH, HEIGHT))#pygame.display.get_surface()

x = pygame.Surface((20, 20))
x.fill((255, 0, 0))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    screen.fill((0, 0 ,0))
            
    for i in range(100):
        screen.blit(x, (random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))
    pygame.display.update()
    clock.tick(60)