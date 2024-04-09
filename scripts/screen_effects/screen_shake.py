import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.config.CORE_FUNCS import Timer, vec

    ##############################################################################################

class Screen_Shake:
    def __init__(self, manager):
        self.game = manager.game
        self.manager = manager

        self.timer = 0
        self.intensity = 1

    @property
    def on(self):
        return bool(self.timer)

    def start(self, duration: int, intensity=1):
        self.timer = duration
        self.intensity = intensity

    def update(self):
        if self.timer <= 0: return

        self.timer -= 1
        self.game.offset += vec(random.uniform(-5*self.intensity, 5*self.intensity), random.uniform(-5*self.intensity, 5*self.intensity))