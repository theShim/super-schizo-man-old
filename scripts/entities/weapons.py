import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    import pygame.gfxdraw

import os
import cv2
import numpy as np
import random
import math

from scripts.config.CORE_FUNCS import vec, lerp
from scripts.config.SETTINGS import Z_LAYERS

from scripts.particles.sword_slash import Slash, Slash_Wave

    ##############################################################################################

class Sword(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player

        self.image = pygame.image.load("assets/weapons/sword/0.png").convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        self.image = pygame.transform.flip(self.image, False, True)
        self.rect = self.image.get_rect()
        self.pos = vec()
        self.angle = 0
        self.held = False

    def rot_to_mouse(self, pos, offset, facing):
        mousePos = pygame.mouse.get_pos()
        self.angle = math.degrees(-math.atan2(mousePos[1] - (pos[1] - offset[1]), mousePos[0] - (pos[0] - offset[0])))

        if facing == 'right':
            self.angle = sorted([-50, 50, self.angle])[1]
        elif facing == 'left':
            if 130 <= self.angle <= 180:
                pass
            elif -130 >= self.angle >= -180:
                pass
            else:
                if self.angle < -129:
                    self.angle = -129
                elif self.angle < 130:
                    self.angle = 130

        self.pos = pos

    def slash(self, pos, offset, game_entities: pygame.sprite.Group):
        mouse = pygame.mouse.get_pressed()
        if mouse[0]:
            if self.held == False:
                mousePos = pygame.mouse.get_pos()
                angle = (math.atan2(mousePos[1] - (pos[1] - offset[1]), mousePos[0] - (pos[0] - offset[0])))

                game_entities.add(Slash_Wave(game_entities, self.pos + self.player.vel * 5, angle))
                self.held = True
        else:
            self.held = False

    def update(self, pos, offset, facing, game_entities):
        self.rot_to_mouse(pos, offset, facing)
        self.slash(pos, offset, game_entities)

    def get_image_rect(self, offset):
        img = pygame.transform.rotate(self.image, self.angle)
        img.set_colorkey((0, 0, 0))

        rect = img.get_rect(center=self.image.get_rect(center=self.pos-offset).center)
        return (img, rect)