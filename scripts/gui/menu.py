import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import numpy as np
import random
import math

from scripts.gui.player_menu import Player_Menu
from scripts.items.inventory import Inventory
from scripts.config.SETTINGS import SIZE

    ##############################################################################################

#general menu handler for everything
class Menu:
    def __init__(self, player, game):
        self.player = player
        self.game = game

        self.dark = pygame.Surface(SIZE, pygame.SRCALPHA)
        self.dark.fill((0, 0, 0))
        self.dark.set_alpha(180)

        self.open = False
        self.loader = "profile"

        self.inventory = Inventory(self) #actual data store
        self.display = Player_Menu(self) #actual display

    def draw(self):
        self.game.screen.blit(self.dark, (0, 0))
        self.display.update(self.game.screen)