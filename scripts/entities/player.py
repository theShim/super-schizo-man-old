import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
# import cv2
import numpy as np
import random
import math

from scripts.config.CORE_FUNCS import vec, lerp, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, Z_LAYERS, FRIC, GRAV, CONTROLS, DEBUG, FPS
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
                'eye_colour' : eye_colours.get(char_num, [0, 0, 0]), 
                'face_colour' : face_colours.get(char_num, [0, 0, 0])
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
        self.sprites: dict = Player.SPRITES[char_num]
        self.status = "idle"
        self.z = Z_LAYERS['player']

        image = self.sprites[self.status].get_sprite() #current sprite
        self.spawn_pos = spawn_pos #depends on where the spawning tile is
        self.rect = image.get_rect(topleft=spawn_pos) #rect for movement and stuff
        self.size = image.get_size()
        self.direction = 'left' #which way the player is facing
        self.hitbox_size = vec(image.get_size()) #actual hitbox

        self.vel = vec() #x and y velocity
        self.run_speed = 40 #scalar
        self.jump_vel = 10
        self.jumps = 2 #total number of jumps left
        self.jumpHeld = False #ensures player only jumps once
        self.landed = False #checks if the player is currently on the floor

        #blink stuff, don't remember how it works but it does
        self.blinking = 0
        self.blinker = 0
        self.blink_timer = 1
        self.blink_cooldown = 200

        self.move_manager = Move_Manager(self, game)

        self.weapon = Sword(self) #implement a weapon handler at some point

        self.menu = Menu(self, game) #menu manager
    
    #actual colliding rect
    @property
    def hitbox(self):
        return pygame.Rect(self.rect.centerx - self.hitbox_size.x / 2, self.rect.y + 4, self.hitbox_size.x, self.hitbox_size.y - 4)
    
    @property
    def image(self):
        spr = self.current_sprite.get_sprite()
        if self.direction == 'left':
            spr = pygame.transform.flip(spr, True, False)
            spr.set_colorkey((0, 0, 0))
        return spr

    @property
    def current_sprite(self) -> SpriteAnimator:
        return self.sprites.get(self.status, self.sprites["idle"])
        
        ###################################################################################### 

    #handles x-directional movements, changing their acceleration
    def horizontal_move(self, keys, particle_manager):
        old = self.direction
        if keys[CONTROLS["left"]]:
            self.acc.x = -1
            self.direction = 'left'
        if keys[CONTROLS["right"]]:
            self.acc.x = 1
            self.direction = 'right'

        #if the player is on the floor and changes directions, add some run particles
        # if self.landed:
        #     if self.direction != old:
        #         for i in range(random.randint(1, 3)):
        #             particle_manager.add_particle("background", "run", pos=self.hitbox.midbottom, facing=self.direction)

        #change the current animation depending on if the player is moving/holding the buttons
        if not (keys[CONTROLS['left']] or keys[CONTROLS['right']]):
            self.change_status('idle')
        else:
            self.change_status('run')

    #handles jump inputs
    def jump(self, keys):
        if keys[CONTROLS["jump"]] or keys[CONTROLS['up']]:
            if self.jumps > 0 and self.jumpHeld == False:
                self.vel.y = -self.jump_vel
                self.jumps -= 1
                self.jumpHeld = True
        else:
            if self.vel.y < 0:
                self.vel.y = lerp(0, self.vel.y , 0.1) #allows for short hops and high jumps by interpolation
            self.jumpHeld = False

        #change the current animation depending on if the player is moving up or down
        if self.vel.y > 0:
            self.change_status('fall')
        elif self.vel.y < 0:
            self.change_status('jump')

    #accelerating and moving the player
    def apply_forces(self):
        self.vel.x += self.acc.x * self.run_speed * self.game.dt #horizontal acceleration
        self.vel.y += self.acc.y * self.game.dt #vertical acceleration (gravity and jumping)

        self.vel.x *= FRIC #applying friction
        if -0.5 < self.vel.x < 0.5: #bounds to prevent sliding bug
            self.vel.x = 0

        self.rect.topleft += self.vel# * self.game.dt #actually applying the velocity

        if self.rect.bottom > HEIGHT*3: #failsafe if they fall into the void, prolly tie this into the stage later
            self.rect.topleft = self.spawn_pos
            self.vel.y = 0

    def move(self, keys, particle_manager):
        self.acc = vec(0, GRAV)

        self.horizontal_move(keys, particle_manager)
        self.jump(keys)
        self.special_moves(keys, particle_manager)
        self.apply_forces()

        ######################################################################################

    def special_moves(self, keys, particle_manager):
        self.move_manager.update(keys, particle_manager)

        ######################################################################################

    #checks collisions from all 4 sides of the player with tiles
    def tile_collisions(self, particle_manager):
        collision_tolerance = 10
        for rect in self.game.state_loader.tilemap.physics_rects_around(self.hitbox.center):
            if self.hitbox.colliderect(rect):
                
                #if the player lands
                if abs(self.hitbox.bottom - rect.top) < collision_tolerance + 10 and self.vel.y > 0:
                    # if self.landed == False:
                    #     # for i in range(max(2, int(self.vel.y/3))): #add landing particles
                    #     #     c = random.uniform(150, 200)
                    #     #     particle_manager.add_particle(
                    #     #         "background", 
                    #     #         "land", 
                    #     #         pos=self.hitbox.midbottom, 
                    #     #         scale=min(7, int(self.vel.y/2)), 
                    #     #         colour=(c, c, c)
                    #     #     )

                    self.rect.bottom = rect.top + 1
                    self.vel.y = 0 #reset y velocity
                    self.jumps = 2 #reset jumps
                    self.landed = True
                    break
                
                #ceiling
                if abs(self.hitbox.top - rect.bottom) < collision_tolerance and self.vel.y < 0:
                    self.rect.top = rect.bottom 
                    self.vel.y = 0
                
                #walls
                if abs(self.hitbox.right - rect.left) < collision_tolerance + 20 and self.vel.x > 0:
                    self.rect.right = rect.left
                    self.vel.x = 0
                if abs(self.hitbox.left - rect.right) < collision_tolerance + 20 and self.vel.x < 0:
                    self.rect.left =  rect.right
                    self.vel.x = 0
        else:
            #if the player hasn't collided with the floor then they're midair
            self.landed = False

        #if they're on the floor, reset y velocity
        # if self.landed:
        #     self.vel.y = 0

    def offgrid_collisions(self): #mostly handled on tile end
        for tile in self.game.state_loader.tilemap.render_offgrid(self.game.offset):
            if tile.type == "bridge":
                # if tile.touched:
                #     if self.status in ['fall', "jump"]:
                #         self.change_status('idle')

                for j in tile.joints:
                    if tile.player_collisions(j, self): 
                        return
        
        ###################################################################################### 
                
    def handle_menu(self, keys):
        if self.menu.open:
            return True

        for event in self.game.events:
            if event.type == pygame.KEYDOWN:
                if event.key == CONTROLS["menu_open"]:
                    self.menu.loader = "profile"
                    self.menu.open = True
                    self.menu.open_cooldown.reset()
                    break
        
                if keys[CONTROLS['inv_open']]:
                    self.menu.loader = "inventory"
                    self.menu.open = True
                    self.menu.open_cooldown.reset()
                    break

        return False
        
        ###################################################################################### 

    def change_status(self, status):
        if status != self.status:
            self.current_sprite.reset_frame()
            self.status = status

    def animate(self):
        self.current_sprite.next(self.game.dt)

    def blink(self, spr):
        spr = spr.copy()
        # if self.status == 'idle':
        #     return spr     
            
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

            #weapon position handling
            x = self.hitbox.right if self.direction == 'right' else self.hitbox.left
            pos = [x, self.hitbox.centery + 4]
            self.weapon.update(pos, offset, facing=self.direction, game_entities=self.game_entities)
        
        self.animate() #current animation based off status
        self.handle_particles(particle_manager)
        self.draw(screen, offset)

    def draw(self, screen, offset):
        spr = self.image #get sprite and flip if needed

        # spr = self.blink(spr) #get the blinking sprite
        rect = spr.get_rect(center=self.hitbox.center - offset)
        screen.blit(spr, rect)

        weapon_img, weapon_rect = self.weapon.get_image_rect(offset)
        screen.blit(weapon_img, weapon_rect)

        if DEBUG: #hitbox
            pygame.draw.rect(screen, (200, 0, 0), [self.hitbox.x - offset.x, self.hitbox.y - offset.y, *self.hitbox.size], 1)





class Move:
    def __init__(self, parent, name: str, sequence: list, duration: float, delay: float, simultaneous=False, between_delay=FPS/4):
        self.parent = parent
        self.game = self.parent.game
        self.player = self.parent.player

        self.name = name
        self._simultaneous = simultaneous
        self.delay = delay

        if not self._simultaneous:
            self.between_delay = int(between_delay)
            self.leeway = Timer(between_delay, 1)

        self.sequence = sequence 
        self.key_map = {key : False for key in self.sequence}
        self.stack = []

        self.move_timer = Timer(duration, 1)
        self.move_timer.switch(False)
            
        ###################################################################################### 

    def check_sequence(self, keys: pygame.key.ScancodeWrapper) -> bool:
        if self._simultaneous == False:
            current_key_map = {to_press : keys[to_press] for to_press in self.sequence}
            if current_key_map != self.key_map:
                #new changes of key states this frame compared to the last, specifically pressing not releasing keys
                new = [key for key in self.sequence if current_key_map[key] and current_key_map[key] != self.key_map[key]]
                self.key_map = current_key_map.copy()

                if new:
                    #if its the right move add it to the stack
                    to_add = new[0]
                    if self.sequence[len(self.stack)] == to_add:
                        self.stack.append(to_add)
                    else:
                        self.stack = []
                        return False

                    #if the stack is complete, and should now be ordered, then the move itself can be run.
                    if self.stack == self.sequence:
                        self.move_timer.run = True
                        self.move_timer.reset()
                        self.stack = []
                        return True
        else:
            #for keys that need to be pressed at the same time
            current_key_pressed = set([key for key in self.sequence if keys[key]])
            if current_key_pressed == set(self.sequence) and not self.parent.held:
                self.move_timer.run = True
                self.move_timer.reset()
                self.parent.held = self.delay
                return True
        
        #if no key is entered or the incorrect sequeunce is entered, nothing should happen
        return False
    
    def execute(self, keys, particle_manager):
        #if the move has already been entered then keep updating it for its duration
        if self.move_timer.run and not self.move_timer.finished:
            self.move_timer.update()
        elif self.move_timer.finished:
            self.parent.triggered_move = None
        
        if self.name.endswith("_dash"):
            self.dash(keys, particle_manager, self.name)

        else:
            print(self.name)
            
        ###################################################################################### 

    def dash(self, keys, particle_manager, dash_dir):
        self.player.acc.x = self.player.vel.x = 0
        self.player.acc.y = self.player.vel.y = 0
        diag = math.sqrt((16/40)**2 + (10/40)**2) / 2

        #dashing in the 8 cardinal directions
        if dash_dir == "l_dash":
            self.player.vel.x = self.player.run_speed * -(16/40)
            self.player.change_status("run")
        elif dash_dir == "r_dash":
            self.player.vel.x = self.player.run_speed * (16/40)
            self.player.change_status("run")

        elif dash_dir == "u_dash":
            self.player.vel.y = self.player.run_speed * -(10/40)
            self.player.change_status("jump")
        elif dash_dir == "d_dash":
            self.player.vel.y = self.player.run_speed * (10/40)
            self.player.change_status("fall")

        elif dash_dir == "ul_dash":
            self.player.vel.x = self.player.run_speed * -diag
            self.player.vel.y = self.player.run_speed * -diag
            self.player.change_status("jump")
        elif dash_dir == "ur_dash":
            self.player.vel.x = self.player.run_speed * diag
            self.player.vel.y = self.player.run_speed * -diag
            self.player.change_status("jump")

        elif dash_dir == "dl_dash":
            self.player.vel.x = self.player.run_speed * -diag
            self.player.vel.y = self.player.run_speed * diag
            self.player.change_status("fall")
        elif dash_dir == "dr_dash":
            self.player.vel.x = self.player.run_speed * diag
            self.player.vel.y = self.player.run_speed * diag
            self.player.change_status("fall")

        #lil bug fix
        if "l" in dash_dir:
            pos = self.player.rect.topleft + self.player.vel
        else:
            pos = self.player.rect.topleft
        
        #adding the after effects of the dash as particles that fade out
        particle_manager.add_particle("background", "dash_effect", pos=pos, spr=self.player.image.copy())

        self.game.effect_manager.effects["screen shake"].start(int(FPS*0.25))


class Move_Manager:
    def __init__(self, player, game):
        self.game = game
        self.player = player

        self.moves: dict[str:Move] = {}
        for move in [
            Move(self,  "ul_dash",  [CONTROLS["up"],   CONTROLS["left"],  CONTROLS["dash"]],  delay=FPS, duration=20,  simultaneous=True),
            Move(self,  "ur_dash",  [CONTROLS["up"],   CONTROLS["right"], CONTROLS["dash"]],  delay=FPS, duration=20,  simultaneous=True),
            Move(self,  "dl_dash",  [CONTROLS["down"], CONTROLS["left"],  CONTROLS["dash"]],  delay=FPS, duration=20,  simultaneous=True),
            Move(self,  "dr_dash",  [CONTROLS["down"], CONTROLS["right"], CONTROLS["dash"]],  delay=FPS, duration=20,  simultaneous=True),

            Move(self,   "l_dash",   [CONTROLS["left"],   CONTROLS["dash"]],   delay=FPS,   duration=20,   simultaneous=True),
            Move(self,   "r_dash",   [CONTROLS["right"],  CONTROLS["dash"]],   delay=FPS,   duration=20,   simultaneous=True),
            Move(self,   "u_dash",   [CONTROLS["up"],     CONTROLS["dash"]],   delay=FPS,   duration=20,   simultaneous=True),
            Move(self,   "d_dash",   [CONTROLS["down"],   CONTROLS["dash"]],   delay=FPS,   duration=20,   simultaneous=True),

            Move(self, "combo test",   [pygame.K_i, pygame.K_o, pygame.K_i],   delay=FPS,   duration=FPS)
        ]:
            self.add_move(move)
        self.triggered_move = None
        self.held = 0
            
        ###################################################################################### 

    def add_move(self, move: Move):
        self.moves[move.name] = move

    def execute_move(self, keys, particle_manager):
        if self.triggered_move:
            self.triggered_move.execute(keys, particle_manager)
            return 
        
        if self.held:
            self.held -= 1
            return
        
        for move_name, move in self.moves.items():
            if move.check_sequence(keys):
                self.triggered_move = move
                break
            
        ###################################################################################### 

    def update(self, keys, particle_manager):
        self.execute_move(keys, particle_manager)