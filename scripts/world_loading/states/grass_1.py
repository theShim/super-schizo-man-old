import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.world_loading.backgrounds import Sky_Background
from scripts.world_loading.state_machine import State

    ##############################################################################################

class Grass_1_1(State):
    def __init__(self, game, prev):
        super().__init__(game, prev, "grass_1-1")
        self.name = "grass_1-1"
        self.tilemap.load("data/stage_data/1-Grass/area_1.json")
        self.bg = Sky_Background(self.game)