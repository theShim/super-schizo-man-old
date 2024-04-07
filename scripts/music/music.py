import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import numpy as np
import random
import math

    ##############################################################################################

#normal pygame sound object just with a name attribute
class Sound(pygame.mixer.Sound):
    def __init__(self, filename):
        super().__init__(filename)
        self.name = filename.split("/")[-1]

SOUNDS = {
    "bg_test0" : Sound("music/test.wav"),
    "memory1" : Sound("music/memory_1.mp3"),
    "typing" : Sound("music/typing.wav"),
    "tutorial_1" : Sound("music/tutorial/tutorial_ambience1.mp3"),
    "tutorial_2" : Sound("music/tutorial/tutorial_ambience2.mp3"),
    "rain_splash" : Sound("music/binbag.ogg")
}
"""
    - "bg_test0"
    - "memory1"
    - "typing"
    - "tutorial_1"
    - "tutorial_2"
    - "rain_splash"
"""