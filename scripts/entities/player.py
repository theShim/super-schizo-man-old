import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import cv2
import numpy as np
import random
import math

from scripts.config.CORE_FUNCS import vec, lerp
from scripts.config.SETTINGS import WIDTH, HEIGHT, Z_LAYERS, FRIC, GRAV, CONTROLS, DEBUG
from scripts.entities.sprite_animator import SpriteAnimator
from scripts.entities.weapons import Sword
from scripts.gui.menu import Menu

    ##############################################################################################

class Player(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        Player.SPRITES = {}
        for char_num in os.listdir('assets/players'):
            path = 'assets/players/' + str(char_num)
            eye_colours = {'1' : [23, 24, 23], '2' : [23, 24, 23]}
            face_colours = {'1' : [233, 237, 233], '2' : [233, 237, 233]}
            Player.SPRITES[int(char_num)] = {
                'eye_colour' : eye_colours[char_num], 
                'face_colour' : face_colours[char_num]
            }

            for anim in os.listdir(path):
                imgs = []
                for move_name in os.listdir(f"{path}/{anim}"):
                    img = pygame.image.load(f"{path}/{anim}/{move_name}").convert_alpha()
                    img = pygame.transform.scale(img, pygame.math.Vector2(img.get_size())*2)
                    img.set_colorkey((0, 0, 0))
                    imgs.append(img)
                animator = SpriteAnimator(imgs, animation_speed=0.2)
                Player.SPRITES[int(char_num)][anim.lower()] = animator
                yield

    def __init__(self, game, entities, char_num=1, spawn_pos=(WIDTH/2, 0)):
        super().__init__()
        
        self.game = game
        self.game_entities = entities

        self.char_num = char_num
        self.sprites = Player.SPRITES[char_num]
        self.status = "idle"
        self.z = Z_LAYERS['player']

        self.image = self.sprites[self.status].get_sprite()
        self.rect = self.image.get_rect(topleft=spawn_pos)
        self.size = self.image.get_size()
        self.direction = 'left'
        self.hitbox_size = vec(self.image.get_size())

        self.vel = vec()
        self.run_speed = 1
        self.jumps = 2
        self.jumpHeld = False
        self.landed = False

        self.blinking = 0
        self.blinker = 0
        self.blink_timer = 1
        self.blink_cooldown = 200

        self.weapon = Sword(self)

        self.menu = Menu(self, game)
    
    @property
    def hitbox(self):
        return pygame.Rect(self.rect.centerx - self.hitbox_size.x / 2, self.rect.y + 4, self.hitbox_size.x, self.hitbox_size.y - 4)
        
        ###################################################################################### 

    def horizontal_move(self, keys, particle_manager):
        old = self.direction
        if keys[CONTROLS["left"]]:
            self.acc.x = -1
            self.direction = 'left'
        if keys[CONTROLS["right"]]:
            self.acc.x = 1
            self.direction = 'right'

        if self.landed:
            if self.direction != old:
                for i in range(random.randint(1, 3)):
                    particle_manager.add_particle("background", "run", pos=self.hitbox.midbottom, facing=self.direction)

        if not (keys[CONTROLS['left']] or keys[CONTROLS['right']]):
            self.change_status('idle')
        else:
            self.change_status('run')

    def jump(self, keys):
        if keys[CONTROLS["jump"]] or keys[CONTROLS['up']]:
            if self.jumps > 0 and self.jumpHeld == False:
                self.vel.y = -10
                self.jumps -= 1
                self.jumpHeld = True
        else:
            if self.vel.y < 0:
                self.vel.y = lerp(0, self.vel.y, 0.1)
            self.jumpHeld = False

        if self.vel.y > 0:
            self.change_status('fall')
        if self.vel.y < 0:
            self.change_status('jump')

    def apply_forces(self):
        self.vel.x += self.acc.x * self.run_speed * self.game.dt
        self.vel.y += self.acc.y * self.game.dt

        self.vel.x *= FRIC
        if -0.5 < self.vel.x < 0.5:
            self.vel.x = 0

        self.rect.topleft += self.vel * self.game.dt

    def move(self, keys, particle_manager):
        self.acc = vec(0, GRAV)

        self.horizontal_move(keys, particle_manager)
        self.jump(keys)
        self.apply_forces()

        ######################################################################################

    def tile_collisions(self, particle_manager):
        collision_tolerance = 10
        for rect in self.game.stage_loader.tilemap.physics_rects_around(self.hitbox.center):
            if self.hitbox.colliderect(rect):
                
                if abs(self.hitbox.bottom - rect.top) < collision_tolerance + 5 and self.vel.y > 0:
                    if self.landed == False:
                        for i in range(max(2, int(self.vel.y/3))):
                            c = random.uniform(150, 200)
                            particle_manager.add_particle(
                                "background", 
                                "land", 
                                pos=self.hitbox.midbottom, 
                                scale=min(7, int(self.vel.y/2)), 
                                colour=(c, c, c)
                            )

                    self.rect.bottom = rect.top + 1
                    self.vel.y = 0
                    self.jumps = 2
                    self.landed = True
                    break
                
                if abs(self.hitbox.top - rect.bottom) < collision_tolerance and self.vel.y < 0:
                    self.rect.top = rect.bottom 
                    self.vel.y = 0
                
                if abs(self.hitbox.right - rect.left) < collision_tolerance and self.vel.x > 0:
                    self.rect.right = rect.left
                    self.vel.x = 0
                if abs(self.hitbox.left - rect.right) < collision_tolerance + 20 and self.vel.x < 0:
                    self.rect.left =  rect.right
                    self.vel.x = 0
        else:
            self.landed = False

        if self.landed:
            self.vel.y = 0

    def offgrid_collisions(self):
        return
        for tile in self.game.stage_loader.tilemap.collideable_offgrid_around(self.hitbox):
            if tile.type == 'grass':
                tile.player_collision(self.hitbox.midbottom)
                # tile.grass_blades.empty()
        
        ###################################################################################### 
                
    def handle_menu(self, keys):
        if self.menu.open:
            return True
        
        if keys[CONTROLS['menu_open']]:
            self.menu.loader = "profile"
            self.menu.open = True
        if keys[CONTROLS['inv_open']]:
            self.menu.loader = "inventory"
            self.menu.open = True

        return False
        
        ###################################################################################### 

    def change_status(self, status):
        if status != self.status:
            self.sprites[self.status].reset_frame()
            self.status = status

    def animate(self):
        self.sprites[self.status].next(self.game.dt)

    def blink(self, spr):
        spr = spr.copy()
        # if self.status == 'idle':
        #     return spr     
            
        # if self.blinking != 16:
        self.blink_timer += 1

        if self.blink_timer % self.blink_cooldown == 0 and self.blinking == 16:
            self.blink_cooldown += random.randint(-2, 2)
            self.blink_cooldown = sorted([self.blink_cooldown, 240, 260])[1]
            self.blinking = 0
            self.blinker = 0

        if self.blinking < 16:
            view = pygame.surfarray.array3d(spr)
            view = view.transpose([1, 0, 2])
            img = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)
            colour = Player.SPRITES[self.char_num]['eye_colour']
            Y, X = np.where(np.all(img==colour,axis=2))
            zipped = np.column_stack((X,Y))
            
            # print(zipped, self.blinker, zipped[:2 * round(int(self.blinker % 8)/2)])
            for coord in zipped[:2 * round(int(self.blinker % 8)/2)]:
                spr.set_at(coord, Player.SPRITES[self.char_num]['face_colour'])

            self.blinking += 1
            self.blinker += 1 if self.blinking < 8 else -1
            
            if math.floor(self.blinking) == 16:
                self.blinking = 16
        
        return spr
        
        ###################################################################################### 

    def handle_particles(self, particle_manager):
        if self.status == "run":
            if self.landed:
                if random.randint(1, 80) == 1:
                    for i in range(random.randint(1, 3)):
                        particle_manager.add_particle("background", "run", pos=self.hitbox.midbottom, facing=self.direction)
            
        ###################################################################################### 

    def update(self, screen: pygame.Surface, offset: vec, particle_manager):
        keys = pygame.key.get_pressed()

        inv_open = self.handle_menu(keys) # if this returns True, then make everything under not happen except draw a darker filter over

        if not inv_open:
            self.move(keys, particle_manager)
            self.tile_collisions(particle_manager)
            self.offgrid_collisions()

            #weapom position handling
            x = self.hitbox.right if self.direction == 'right' else self.hitbox.left
            pos = [x, self.hitbox.centery + 4]
            self.weapon.update(pos, offset, facing=self.direction, game_entities=self.game_entities)
        
        self.animate() #current animation based off status
        self.handle_particles(particle_manager) #
        self.draw(screen, offset)

    def draw(self, screen, offset):
        spr = self.sprites[self.status].get_sprite()
        if self.direction == 'left':
            spr = pygame.transform.flip(spr, True, False)
            spr.set_colorkey((0, 0, 0))

        spr = self.blink(spr)
        rect = spr.get_rect(center=self.hitbox.center - offset)
        screen.blit(spr, rect)

        weapon_img, weapon_rect = self.weapon.get_image_rect(offset)
        screen.blit(weapon_img, weapon_rect)

        if DEBUG:
            pygame.draw.rect(screen, (200, 0, 0), [self.hitbox.x - offset.x, self.hitbox.y - offset.y, *self.hitbox.size], 1)