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
    def __init__(self, parent):
        self.parent = parent

        self.top_row = pygame.sprite.Group()
        x = 10
        for i, button in enumerate([self.Profile, self.Inventory, self.QuestBook, self.Map, self.Settings]):
            self.top_row.add(e:=button(self, (x, 10), i*2))
            x += e.base.get_width() - 15

        self.profile_buttons = pygame.sprite.Group()
        self.profile_buttons.add(e1:=self.Stats_Select(self, (0, e.base.get_height() + 60), 2))
        self.profile_buttons.add(self.SkillTree_Select(self, (0, e1.base.get_height() + e.base.get_height() + 75), 4))

    def update(self, screen):
        self.top_row.update(screen)

        for b in self.top_row.sprites():
            if b.name == self.parent.loader:
                b.clicked = True
                break

        for b in self.top_row.sprites():
            if b.clicked:
                if b.name == "profile":
                    self.profile_buttons.update(screen)
                elif b.name == "inventory":
                    for i, item in enumerate(self.parent.inventory.data):
                        pygame.draw.rect(screen, (200, 200, 200), [50-10, ((i+2)*50) - 5, item.rect.width+20, item.rect.height+10])
                        screen.blit(item.image, (50, (i+2)*50))
                break
            else:
                if b.name == "profile":
                    for profile_button in self.profile_buttons.sprites():
                        if isinstance(profile_button, self.Long_Button):
                            profile_button.reset()
                            

        ##########################################################################################

    class Top_Button(pygame.sprite.Sprite):
        def __init__(self, parent, name, pos, y_transition_offset):
            super().__init__()
            self.parent = parent
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
                    self.pos = self.pos.lerp(self.end_pos, 0.15)

            mousePos = pygame.mouse.get_pos()
            mousePos_masked = mousePos[0] - self.end_pos[0], mousePos[1] - self.end_pos[1]
            mouse = pygame.mouse.get_pressed()

            if (self.rect.collidepoint(mousePos) and self.mask.get_at(mousePos_masked)) or self.clicked:
                if mouse[0]:
                    self.clicked = True
                    self.parent.parent.loader = self.name
                    [setattr(button, "clicked", False) for button in self.parent.top_row if button != self]
                screen.blit(self.clicked_img, [self.pos.x, self.pos.y - 2])
            else:
                screen.blit(self.base, self.pos)

    class Long_Button(pygame.sprite.Sprite):
        def __init__(self, parent, name, pos, x_transition_offset):
            super().__init__()
            self.parent = parent
            self.name = name

            self.base = pygame.image.load(f"assets/gui/{name}.png")#.convert_alpha()
            self.base = pygame.transform.scale(self.base, vec(self.base.get_size())*2)
            self.base.set_colorkey((0, 0, 0))
            self.clicked_img = pygame.image.load(f"assets/gui/{name+'_clicked'}.png")#.convert_alpha()
            self.clicked_img = pygame.transform.scale(self.clicked_img, vec(self.clicked_img.get_size())*2)
            self.clicked_img.set_colorkey((0, 0, 0))

            self.pos = vec(pos[0]-self.base.get_width()*1.75, pos[1])
            self.end_positions = [pos, [pos[0] - self.base.get_width()*0.75, pos[1]]]
            self.end_pos = self.end_positions[0]
            self.move_timer = Timer(x_transition_offset, 1)

            self.rect = self.base.get_rect(topleft=self.end_pos)
            self.mask = pygame.mask.from_surface(self.base)
            self.clicked = False
            self.held = False

        def reset(self):
            self.pos.x = self.end_pos[0] - self.base.get_width()*1.75
            self.switch_end_pos(0)
            self.move_timer.reset()

        def switch_end_pos(self, index:int = 0):
            self.end_pos = self.end_positions[index]

        def update(self, screen):
            if abs(self.end_pos[0] - self.pos[0]) > 0:
                self.move_timer.update()
                if self.move_timer.finished:
                    self.pos = self.pos.lerp(self.end_pos, 0.15)

            mousePos = pygame.mouse.get_pos()
            mousePos_masked = mousePos[0] - self.end_pos[0], mousePos[1] - self.end_pos[1]
            mouse = pygame.mouse.get_pressed()


            def mask_collide(pos):
                try: return self.mask.get_at(pos)
                except IndexError: False
                
            if (self.rect.collidepoint(mousePos) and mask_collide(mousePos_masked)):
                if mouse[0]:
                    self.clicked = True
                    [setattr(button, "clicked", False) for button in self.parent.profile_buttons if isinstance(button, Player_Menu.Long_Button) and button != self]
                    [button.switch_end_pos(1) for button in self.parent.profile_buttons if isinstance(button, Player_Menu.Long_Button)]
                screen.blit(self.clicked_img, [self.pos.x, self.pos.y - 2])
            else:
                screen.blit(self.base, self.pos)

        ##########################################################################################

    class Profile(Top_Button): #stats and skill tree
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "profile", pos, y_transition_offset)

    class Stats_Select(Long_Button):
        def __init__(self, parent, pos, x_transition_offset=0):
            super().__init__(parent, "stats_select", pos, x_transition_offset)

    class SkillTree_Select(Long_Button):
        def __init__(self, parent, pos, x_transition_offset=0):
            super().__init__(parent, "skilltree_select", pos, x_transition_offset)

        ##########################################################################################

    class Inventory(Top_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "inventory", pos, y_transition_offset)

    class QuestBook(Top_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "questbook", pos, y_transition_offset)

    class Map(Top_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "map", pos, y_transition_offset)

    class Settings(Top_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "settings", pos, y_transition_offset)