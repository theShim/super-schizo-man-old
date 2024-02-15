import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import cv2
import numpy as np
import random
import math

from scripts.config.CORE_FUNCS import vec

    ##############################################################################################

def clip(surf,x,y,x_size,y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x,y,x_size,y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

class Font():
    def __init__(self, path, scale=1):
        self.spacing = 1
        self.spacing *= scale if scale >= 1 else (1/scale)
        self.character_order = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','.','-',',',':','+','\'','!','?','0','1','2','3','4','5','6','7','8','9','(',')','/','_','=','\\','[',']','*','"','<','>',';']
        font_img = pygame.image.load(path).convert_alpha()
        current_char_width = 0
        self.characters = {}
        character_count = 0
        for x in range(font_img.get_width()):
            c = font_img.get_at((x, 0))
            if c[0] == 127:
                char_img = clip(font_img, x - current_char_width, 0, current_char_width, font_img.get_height())
                char_img = pygame.transform.scale(char_img, vec(char_img.get_size())*scale) if scale != 1 else char_img
                self.characters[self.character_order[character_count]] = char_img.copy()
                character_count += 1
                current_char_width = 0
            else:
                current_char_width += 1
        self.space_width = self.characters['A'].get_width()
        self.space_height = self.characters['A'].get_height()

    def calc_surf_width(self, text):
        letters = list(text)
        return sum(list(map(lambda letter: self.characters[letter].get_width() + self.spacing if letter != " " else self.space_width + self.spacing, letters))) - self.spacing

    def render(self, screen, text, col, loc):
        x_offset = 0
        y_offset = 0
        for char in text:
            if char == ' ':
                x_offset += self.space_width + self.spacing
            elif char == "\t":
                pass
            elif char == '\n':
                y_offset += self.space_height
                x_offset = 0
            else:
                letter = self.characters.get(char, self.characters['?'])

                pixel_array = pygame.surfarray.array3d(letter)
                mask = np.all(pixel_array == (255, 0, 0), axis=-1)
                pixel_array[mask] = col
                pygame.surfarray.blit_array(letter, pixel_array)
                letter.set_colorkey((0, 0, 0))

                screen.blit(letter, (loc[0] + x_offset, loc[1] + y_offset))
                x_offset += letter.get_width() + self.spacing

    ##############################################################################################
                
class Custom_Font:
    @classmethod
    def init(cls):
        cls.Fluffy = Font('assets/fonts/fluffy.png')
        cls.FluffySmall = Font('assets/fonts/fluffy.png', scale=0.75)