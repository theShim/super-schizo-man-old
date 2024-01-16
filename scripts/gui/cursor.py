import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import cv2
import numpy as np
import random
import math

    ##############################################################################################

class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.mouse.get_pos()

    def update(self, screen):
        self.pos = pygame.mouse.get_pos()
        pygame.draw.circle(screen, (230, 230, 230), self.pos, 8, 1)
        pygame.draw.circle(screen, (230, 230, 230), self.pos, 1, 0)