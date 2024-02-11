import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import cv2
import numpy as np
import random
import math

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS
from scripts.config.CORE_FUNCS import vec, Timer

    ##############################################################################################

class Player_Menu:
    def __init__(self):
        self.top_row = pygame.sprite.Group()
        self.top_row.add(x1:=self.Dropdown( self.top_row, (10, 10)))
        self.top_row.add(x2:=self.Profile(  self.top_row, (x1.base.get_width() - 5, 10), 5))
        self.top_row.add(x3:=self.Inventory(self.top_row, (x1.base.get_width() + x2.base.get_width() - 18, 10), 10))

    def update(self, screen):
        self.top_row.update(screen)

    class Button(pygame.sprite.Sprite):
        def __init__(self, parent, name, pos, y_transition_offset):
            super().__init__()
            self.parent: pygame.sprite.Group = parent
            self.name = name

            self.base = pygame.image.load(f"assets/gui/{name}.png")#.convert_alpha()
            self.base = pygame.transform.scale(self.base, vec(self.base.get_size())*2)
            self.base.set_colorkey((0, 0, 0))
            self.clicked_img = pygame.image.load(f"assets/gui/{name+'_clicked'}.png")#.convert_alpha()
            self.clicked_img = pygame.transform.scale(self.clicked_img, vec(self.clicked_img.get_size())*2)
            self.clicked_img.set_colorkey((0, 0, 0))

            self.pos = vec(pos[0], pos[1]-self.base.get_height()*1.5)
            self.end_pos = pos
            self.move_timer = Timer(y_transition_offset, 1)

            self.rect = self.base.get_rect(topleft=self.end_pos)
            self.mask = pygame.mask.from_surface(self.base)
            self.clicked = False
            self.held = False

        def update(self, screen):
            if abs(self.end_pos[1] - self.pos[1]) > 0:
                self.move_timer.update()
                if self.move_timer.finished:
                    self.pos = self.pos.lerp(self.end_pos, 0.25)

            mousePos = pygame.mouse.get_pos()
            mousePos_masked = mousePos[0] - self.end_pos[0], mousePos[1] - self.end_pos[1]
            mouse = pygame.mouse.get_pressed()
            if (self.rect.collidepoint(mousePos) and self.mask.get_at(mousePos_masked)) or self.clicked:
                if mouse[0]:
                    self.clicked = True
                    [setattr(button, "clicked", False) for button in self.parent if button != self]
                screen.blit(self.clicked_img, self.pos)
            else:
                screen.blit(self.base, self.pos)

    class Dropdown(Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "dropdown", pos, y_transition_offset)

    class Profile(Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "profile", pos, y_transition_offset)

    class Inventory(Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "inventory", pos, y_transition_offset)