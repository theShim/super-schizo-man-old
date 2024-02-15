import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import numpy as np
import random
import math

from scripts.gui.custom_fonts import Custom_Font
from scripts.config.SETTINGS import SIZE, GRAV, Z_LAYERS, FRIC, FPS
from scripts.config.CORE_FUNCS import vec, Timer

    ##############################################################################################

item_info = {
    # item : {
    #     "name" : str,
    #     "type" : ["weapon", "healing", "collectible"],

    #if weapon
    #     "damage" : int,
    #     "type" : [ranged, melee, magic]

    #if healing
    #     "hp" : int
    # }

    "grains" : {
        "name" : "grains",
        "type" : "collectible"
    }
}

    ##############################################################################################

def clip(surf,x,y,x_size,y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x,y,x_size,y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

    ##############################################################################################

class Item(pygame.sprite.Sprite):

    @classmethod
    def get_item(cls, game, name, pos):
        if (item_data := item_info.get(name, None)) != None:
            if item_data["type"] == "weapon":
                return Weapon(game, item_data, pos)
            elif item_data["type"] == "healing":
                return Healing(game, item_data, pos)
            elif item_data["type"] == "collectible":
                return Collectible(game, item_data, pos)

    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        BASE_TILE_PATH = "assets/items/"
        for img_name in os.listdir(BASE_TILE_PATH):
            img = pygame.image.load(BASE_TILE_PATH + img_name).convert_alpha()
            img.set_colorkey((0, 0, 0))
            cls.SPRITES[img_name.split(".")[0]] = img
            yield

    def __init__(self, game, name, pos):
        super().__init__()
        self.game = game
        self.name = name
        self.z = Z_LAYERS["items"]

        self.image = self.SPRITES[self.name].copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos

        self.vel = vec(random.uniform(0, 10) * 3, 0)
        self.acc = vec(0, GRAV)
        self.landed = False
        self.angle = 0
        self.angleMod = random.uniform(1, 10) * random.choice([-1, 1])

        self.despawn_timer = Timer(FPS*45, 1)
        self.touched = 0

        name_width = Custom_Font.FluffySmall.calc_surf_width(self.name)
        name_height = Custom_Font.FluffySmall.space_height
        self.tag = pygame.Surface((name_width + 30, name_height + 11), pygame.SRCALPHA)
        Custom_Font.FluffySmall.render(self.tag, self.name, (255, 255, 255), (28, 0))
        pygame.draw.line(self.tag, (255, 255, 255), (0, self.tag.get_height()), (10, self.tag.get_height()-10))
        pygame.draw.line(self.tag, (255, 255, 255), (10, self.tag.get_height()-10), (self.tag.get_width(), self.tag.get_height()-10))

        ##########################################################################################

    def move(self):
         # gravity + slight left or right movement
        self.vel += self.acc
        self.vel.x *= FRIC
        self.pos += self.vel
        self.rect.topleft = self.pos

    def tile_collisions(self):
        collision_tolerance = 10
        for rect in self.game.stage_loader.tilemap.physics_rects_around(self.rect.center):
            if self.rect.colliderect(rect):

                if abs(self.rect.bottom - rect.top) < collision_tolerance:
                    print(abs(self.rect.bottom - rect.top))
                    for i in range(abs(self.rect.bottom - rect.top)):
                        self.pos.y -= 1
                        self.rect.y = self.pos.y
                    self.landed = True
                    self.angleMod *= 0.1
                    break
                
                if abs(self.rect.top - rect.bottom) < collision_tolerance and self.vel.y < 0:
                    self.rect.top = rect.bottom 
                    self.vel.y = 0
                
                if abs(self.rect.right - rect.left) < collision_tolerance + 5 and self.vel.x > 0:
                    self.rect.right = rect.left
                    self.vel.x = 0
                if abs(self.rect.left - rect.right) < collision_tolerance + 5 and self.vel.x < 0:
                    self.rect.left =  rect.right
                    self.vel.x = 0

        if self.landed:
            self.vel.y = 0
            self.acc.y = 0

        ##########################################################################################
            
    def player_collisions(self, screen, offset):
        if self.rect.colliderect(self.game.player.hitbox):
            img = clip(self.tag, 0, 0, self.touched, self.tag.get_height()) if self.touched < self.tag.get_width() else self.tag
            screen.blit(img, self.tag.get_rect(midbottom=self.rect.topleft).topleft - offset)
            self.touched = min(self.touched + 5, self.tag.get_width())
        else:
            self.touched = max(self.touched - 10, 0)
            if self.touched:
                img = clip(self.tag, 0, 0, self.touched, self.tag.get_height())
                screen.blit(img, self.tag.get_rect(midbottom=self.rect.topleft).topleft - offset)


        ##########################################################################################

    def get_image_rect(self, offset):
        img = pygame.transform.rotate(self.image, self.angle)
        img.set_colorkey((0, 0, 0))

        rect = img.get_rect(center=self.image.get_rect(bottomleft=self.rect.bottomleft-offset).center)
        return (img, rect)

    def update(self, screen, offset):
        # self.despawn_timer.update()
        # if self.despawn_timer.finished:
        #     return self.game.entities.remove(self)
            
        self.move()
        self.tile_collisions()

        self.angle += self.angleMod
        self.angleMod *= 0.95
        
        img, rect = self.get_image_rect(offset)
        screen.blit(img, rect)

        ##########################################################################################

class Weapon(Item):
    def __init__(self, game, data, pos):
        super().__init__(game, data["name"], pos)
        
class Healing(Item):
    def __init__(self, game, data, pos):
        super().__init__(game, data["name"], pos)
        
class Collectible(Item):
    def __init__(self, game, data, pos):
        super().__init__(game, data["name"], pos)
        