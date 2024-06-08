import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.config.CORE_FUNCS import Timer

from scripts.screen_effects.screen_shake import Screen_Shake
from scripts.screen_effects.overlay import CRT_Overlay

    ##############################################################################################

class Effect_Manager:
    def __init__(self, game):
        self.game = game

        self.effects = {
            "screen shake" : Screen_Shake(self),
            "crt overlay" : CRT_Overlay(game),
        }

        # self.effects["crt overlay"].on = True

    def update(self):
        for key in self.effects:
            effect = self.effects[key]
            if effect.on:
                effect.update()
                return


"""
Screen Shake: Rapidly changing the screen's offset to simulate impact, explosions, or intense movement.

Screen Flash: Briefly changing the screen's color or brightness to simulate events like explosions or camera flashes.

Blur: Temporarily blurring the screen to convey a sense of motion, speed, or disorientation.

Vignette: Darkening the edges of the screen to focus attention on the center or to create a cinematic effect.

Lens Distortion: Simulating distortion effects like fish-eye or barrel distortion to create surreal or immersive visuals.

Heat Distortion: Distorting the screen to simulate heat waves or intense heat sources.

Depth of Field: Emulating camera focus effects to blur distant or foreground objects, adding realism or directing focus.

Chromatic Aberration: Simulating the dispersion of light to create a color separation effect at the edges of objects.

Scanlines: Adding horizontal lines to simulate the appearance of old CRT monitors or adding a retro aesthetic.

Pixelation: Reducing the resolution or adding pixelation effects to create a retro or stylized look.

Grayscale/Color Inversion: Temporarily changing the screen to grayscale or inverting colors for dramatic effect or to simulate specific conditions.

Distortion Grid: Overlaying a grid pattern and distorting it to create surreal or psychedelic visuals.

Lighting Effects: Simulating dynamic lighting effects such as flickering, pulsating, or changing color temperatures.

Shadow Effects: Adding dynamic shadows or changing shadow intensity to enhance realism or mood."""