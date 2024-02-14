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

class Inventory:
    def __init__(self, game):
        self.game = game

        self.data = []