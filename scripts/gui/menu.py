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
from scripts.config.SETTINGS import SIZE, CONTROLS, FPS
from scripts.config.CORE_FUNCS import Timer

    ##############################################################################################

#general menu handler for everything
class Menu:
    def __init__(self, player, game):
        self.player = player
        self.game = game

        self.window = pygame.Surface(SIZE, pygame.SRCALPHA)

        self.dark = pygame.Surface(SIZE, pygame.SRCALPHA)
        self.dark.fill((0, 0, 0))
        self.dark.set_alpha(180)
        self.dark_timer = Timer(FPS//2, 1)

        self.open = False
        self.loader = "profile"
        self.open_cooldown = Timer(FPS//2, 1)

        self.inventory = Inventory(self) #actual data store
        self.display = Player_Menu(self) #actual display

    def draw(self):
        self.window.fill((0, 0, 0, 0))

        if not self.dark_timer.finished:
            self.dark_timer.update()
            dark = self.dark.copy()
            dark.set_alpha((self.dark_timer.t / self.dark_timer.end) * 180)
            self.window.blit(dark, (0, 0))
        else:
            self.window.blit(self.dark, (0, 0))

        self.display.update(self.window)
        self.game.screen.blit(self.window, (0, 0))

        if self.open_cooldown.finished:
            for event in self.game.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == CONTROLS["menu_open"]:
                        self.open = False
                        break
        else:
            if self.open_cooldown.t == 0:
                self.dark_timer.reset()

            self.open_cooldown.update()