import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import numpy as np
import random
import math

from scripts.config.SETTINGS import SIZE

    ##############################################################################################

class Menu:
    def __init__(self, player, game):
        self.player = player
        self.game = game

        self.open = False

    def draw(self):
        dark = pygame.Surface(SIZE, pygame.SRCALPHA)
        dark.fill((0, 0, 0))
        dark.set_alpha(180)
        self.game.screen.blit(dark, (0, 0))