import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import numpy as np
import random
import math

    ##############################################################################################

class Menu:
    def __init__(self, player, game):
        self.player = player
        self.game = game