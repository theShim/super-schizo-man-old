import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import cv2
import numpy as np
import random
import math

from scripts.config.CORE_FUNCS import vec, lerp, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, Z_LAYERS, FRIC, GRAV, CONTROLS, DEBUG, FPS

from scripts.entities.sprite_animator import SpriteAnimator
from scripts.entities.weapons import Sword

    ##############################################################################################

class Butterfly(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        path = 'assets/entities/butterfly'
        Butterfly.SPRITES = {}
        for anim in os.listdir(path):
            imgs = []
            for move_name in os.listdir(f"{path}/{anim}"):
                img = pygame.image.load(f"{path}/{anim}/{move_name}").convert_alpha()
                img = pygame.transform.scale(img, pygame.math.Vector2(img.get_size())*2)
                img.set_colorkey((0, 0, 0))
                imgs.append(img)
            animator = SpriteAnimator(imgs, animation_speed=0.4)
            Butterfly.SPRITES[anim.lower()] = animator
            yield

    def __init__(self, game, entities, start_pos=(WIDTH/2, HEIGHT/2)):
        super().__init__()

        self.game = game
        self.game_entities = entities
        self.type = "partner"
        
        self.sprites = self.SPRITES.copy()
        self.status = "idle"
        self.z = Z_LAYERS['partner']
        self.start_pos = start_pos

        self.image = self.sprites[self.status].get_sprite()
        self.rect = self.image.get_rect(center=start_pos)
        self.size = self.image.get_size()
        self.direction = 'left'
        self.hitbox_size = vec(self.image.get_size())

        self.t = 0
        self.particle_spawner = Timer(FPS/4, 1)
        
        ###################################################################################### 

    def move(self, particle_manager):
        if self.game.stage_loader.current_stage.area_index == 2 and self.game.stage_loader.current_stage_index == 0:
            self.t += math.degrees(.0002)
            # self.rect.x = self.start_pos[0] + math.sin(self.t) * 90
            self.rect.y = self.start_pos[1] + math.sin(3*self.t + math.degrees(45)) * 20

            # if math.cos(self.t) < 0:
            #     self.direction = 'left'
            # else:
            #     self.direction = 'right'
        
        ###################################################################################### 

    def change_status(self, status):
        if status != self.status:
            self.sprites[self.status].reset_frame()
            self.status = status

    def animate(self):
        self.sprites[self.status].next(self.game.dt)
        
        ###################################################################################### 

    def handle_particles(self, particle_manager):
        self.particle_spawner.update()
        if self.particle_spawner.finished:
            self.particle_spawner.reset()
            particle_manager.add_particle("foreground", "rainbow", pos=[self.rect.centerx, self.rect.bottom + 2])
            
        ###################################################################################### 
        
    def update(self, screen: pygame.Surface, offset: vec, particle_manager):
        self.move(particle_manager)

        self.animate() #current animation based off status
        self.handle_particles(particle_manager)
        self.draw(screen, offset)

    def draw(self, screen, offset):
        spr = self.sprites[self.status].get_sprite()
        if self.direction == 'left':
            spr = pygame.transform.flip(spr, True, False)
            spr.set_colorkey((0, 0, 0))

        rect = spr.get_rect(center=self.rect.center - offset)
        screen.blit(spr, rect)

        if DEBUG:
            pygame.draw.rect(screen, (200, 0, 0), [self.rect.x - offset.x, self.rect.y - offset.y, *self.rect.size], 1)