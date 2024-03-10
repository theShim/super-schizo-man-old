import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SDL_VIDEO_CENTERED'] = '1'

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import sys
import time
import random
from typing import Literal

from scripts.config.SETTINGS import SIZE, WIDTH, HEIGHT, FPS, TILE_SIZE, Z_LAYERS
from scripts.config.CORE_FUNCS import vec

from scripts.world_loading.tilemap import Tilemap, Tile, Offgrid_Tile
from scripts.world_loading.backgrounds import Editor_Background
from scripts.world_loading.nature import Grass_Manager

    ##############################################################################################

def load_tiles(tilename):
    path = 'assets/tiles/' + tilename
    imgs = []
    for img_name in os.listdir(path):
        img = pygame.transform.scale(
            pygame.image.load(f"{path}/{img_name}").convert_alpha(), 
            (TILE_SIZE, TILE_SIZE)
        )
        img.set_colorkey((0, 0, 0))
        imgs.append(img)
    return imgs

def load_offgrid(tilename):
    path = 'assets/offgrid_tiles/' + tilename
    imgs = []
    for img_name in os.listdir(path):
        img = pygame.image.load(f"{path}/{img_name}").convert_alpha()
        img.set_colorkey((0, 0, 0))
        imgs.append(img)
    return imgs

    ##############################################################################################

class BreakParticle(pygame.sprite.Sprite):
    def __init__(self, pos, col, parent):
        super().__init__()
        self.parent = parent
        self.tilesize = 2
        self.col = col

        self.image = pygame.Surface((self.tilesize, self.tilesize))
        self.image.fill(self.col)
        self.rect = self.image.get_rect(topleft=pos)
        self.alpha = 255
        self.x = random.uniform(-2, 2)

        self.grav = random.uniform(0, 5)

    def update(self, screen):
        self.alpha -= 12
        self.image.set_alpha(self.alpha)

        if self.alpha <= 0:
            self.parent.remove(self)

        self.rect.x += self.x
        self.rect.y -= self.grav
        self.grav -= random.uniform(0, 1)

        self.draw(screen)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class PlaceParticle(pygame.sprite.Sprite):
    def __init__(self, pos, parent):
        super().__init__()
        self.pos = pos
        self.parent: pygame.sprite.Group = parent
        self.timer = 0

    def update(self, screen):
        self.timer += 2
        if self.timer > 32:
            self.parent.remove(self)
        self.draw(screen)

    def draw(self, screen):
        rect = pygame.Rect(0, 0, self.timer, self.timer)
        rect.center = self.pos - editor.offset
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)

    ##############################################################################################

class Editor:
    def __init__(self):
        #intiaising pygame stuff
        self.initialise()

        #assets
        self.assets = {
            "grass" : load_tiles('grass'),
            "stone" : load_tiles('stone'),
            "spawner" : load_tiles('spawner'),
            "water" : load_tiles('water')
        }
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.offgrid_assets = {
            "boxes" : load_offgrid('boxes'),
            "grass" : load_offgrid('grass'),
            "torch" : load_offgrid('torch'),
            "swaying_vine" : load_offgrid("swaying_vine")
        }
        self.offgrid_list = list(self.offgrid_assets)
        self.offgrid_group = 0
        self.offgrid_variant = 0

        #general editor stuff
        self.scroll_speed = 5
        self.on_grid = True
        self.held = False
        self.l_flood_start = None
        self.r_flood_start = None

        #window stuff
        self.running = True
        self.clock = pygame.time.Clock()
        self.dt = 1
        self.offset = vec(0, -8)

        #editor stuff
        self.tilemap = Tilemap(self, editor_flag=True)
        self.bg = Editor_Background()
        self.particles = pygame.sprite.Group()

        ######################################################################################

    def initialise(self):
        pygame.init()  #general pygame
        pygame.display.set_caption("Super Schizo Man - LEVEL EDITOR")

        pygame.font.init() #font stuff
        self.font = pygame.font.SysFont('Verdana', 10)

        #music stuff
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.mixer.init()

        #setting allowed events to reduce lag
        pygame.event.set_blocked(None) 
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL])
        
        #initalising pygame window
        flags = pygame.RESIZABLE | pygame.SCALED
        self.screen = pygame.display.set_mode(SIZE, flags)
        pygame.display.toggle_fullscreen()

        for tile_gen in [Tile.cache_sprites(), Offgrid_Tile.cache_sprites(), Grass_Manager.cache_sprites()]:
            while True:
                try:
                    next(tile_gen)
                except:
                    break

        ######################################################################################

    def calculate_offset(self):
        keys = pygame.key.get_pressed()
        speed = vec()
        if keys[pygame.K_a]:
            speed.x -= self.scroll_speed
        if keys[pygame.K_d]:
            speed.x += self.scroll_speed
        if keys[pygame.K_w]:
            speed.y -= self.scroll_speed
        if keys[pygame.K_s]:
            speed.y += self.scroll_speed
        
        if keys[pygame.K_LSHIFT]:
            speed *= 2
        self.offset += speed

        ######################################################################################

    def left_click(self, tile_loc, tilePos, mousePos):
        delete = False
        if self.on_grid:
            if tile_loc in self.tilemap.tile_map:
                tile: Tile = self.tilemap.tile_map[tile_loc]
                img = Tile.SPRITES[tile.type][tile.variant]
                delete: pygame.Surface = img 
                del self.tilemap.tile_map[tile_loc]

        else:
            for tile in self.tilemap.offgrid_tiles.copy():
                tile_img = self.offgrid_assets[self.offgrid_list[self.offgrid_group]][self.offgrid_variant].copy()
                tile_r = pygame.Rect(tile.pos[0] - self.offset.x, tile.pos[1] - self.offset.y, *tile_img.get_size())
                if tile_r.collidepoint(mousePos):
                    self.tilemap.offgrid_tiles.remove(tile)

        if delete:
            for x in range(0, delete.get_width(), 2):
                for y in range(0, delete.get_height(), 2):
                    if random.randint(0, 1) == 0:
                        self.particles.add(BreakParticle(
                            [tilePos[0] * TILE_SIZE + x - self.offset.x, tilePos[1] * TILE_SIZE + y - self.offset.y], 
                            delete.get_at((x, y)),
                            self.particles
                        ))

    def right_click(self, tile_loc, tilePos, mousePos, current_img: pygame.Surface):
        if self.on_grid:
            self.tilemap.tile_map[tile_loc] = Tile(
                self.tile_list[self.tile_group],
                tilePos,
                self.tile_variant,
            )
            self.particles.add(PlaceParticle(
                [tilePos[0] * TILE_SIZE + TILE_SIZE/2, tilePos[1] * TILE_SIZE + TILE_SIZE/2], 
                self.particles
            ))

        else:
            if self.held == False:
                mousePos = [mousePos[0] - current_img.get_width()//2, mousePos[1] - current_img.get_height()//2]
                pos = vec(mousePos) + self.offset
                if pos not in [t.pos for t in self.tilemap.offgrid_tiles]:
                    tile = Offgrid_Tile(
                        self.offgrid_list[self.offgrid_group],
                        [pos[0], pos[1]],
                        self.offgrid_variant,
                    )
                    tile.z = Z_LAYERS["foreground offgrid"]
                    self.tilemap.offgrid_tiles.append(tile)
                self.held = True


    def flood_left(self, tile_loc, tilePos, mode: Literal["flood", "erase"]):

        if self.l_flood_start == None:
            self.l_flood_start = [c*self.tilemap.tile_size for c in tilePos]
        end_pos = [c*self.tilemap.tile_size for c in tilePos]
        zipped = list(zip(self.l_flood_start - self.offset, end_pos - self.offset))

        top_left = [min(zipped[0]), min(zipped[1])]
        bottom_right = [max(zipped[0]) + self.tilemap.tile_size, max(zipped[1]) + self.tilemap.tile_size]
        width = abs(zipped[0][0] - zipped[0][1]) + self.tilemap.tile_size
        height = abs(zipped[1][0] - zipped[1][1]) + self.tilemap.tile_size

        if mode == 'flood':
            pygame.draw.rect(self.screen, (255, 255, 255), [top_left[0], top_left[1], width, height], 5)
        
        elif mode == 'erase':
            self.l_flood_start = None

            delete = False
            tilePos = [0, 0]
            for x in range(int(top_left[0] + self.offset.x), int(bottom_right[0] + self.offset.x), self.tilemap.tile_size):
                tilePos[0] = x // self.tilemap.tile_size
                for y in range(int(top_left[1] + self.offset.y), int(bottom_right[1] + self.offset.y), self.tilemap.tile_size):
                    tilePos[1] = y // self.tilemap.tile_size
                    tile_loc = str(tilePos[0]) + ";" + str(tilePos[1])

                    if tile_loc in self.tilemap.tile_map:
                        tile: Tile = self.tilemap.tile_map[tile_loc]
                        img = Tile.SPRITES[tile.type][tile.variant]
                        delete: pygame.Surface = img 
                        del self.tilemap.tile_map[tile_loc]

                        for x1 in range(0, delete.get_width(), 2):
                            for y1 in range(0, delete.get_height(), 2):
                                if random.randint(0, 1) == 0:
                                    self.particles.add(BreakParticle(
                                        [tilePos[0] * self.tilemap.tile_size + x1 - self.offset.x, 
                                         tilePos[1] * self.tilemap.tile_size + y1 - self.offset.y], 
                                        delete.get_at((x1, y1)),
                                        self.particles
                                    ))
        

    def flood_right(self, tile_loc, tilePos, mode: Literal["flood", "place"], current_img=None):

        if self.r_flood_start == None:
            self.r_flood_start = [c*self.tilemap.tile_size for c in tilePos]
        end_pos = [c*self.tilemap.tile_size for c in tilePos]
        zipped = list(zip(self.r_flood_start - self.offset, end_pos - self.offset))

        top_left = [min(zipped[0]), min(zipped[1])]
        bottom_right = [max(zipped[0]) + self.tilemap.tile_size, max(zipped[1]) + self.tilemap.tile_size]
        width = abs(zipped[0][0] - zipped[0][1]) + self.tilemap.tile_size
        height = abs(zipped[1][0] - zipped[1][1]) + self.tilemap.tile_size

        if mode == 'flood':
            for x in range(int(top_left[0]), int(bottom_right[0]), self.tilemap.tile_size):
                for y in range(int(top_left[1]), int(bottom_right[1]), self.tilemap.tile_size):
                    self.screen.blit(current_img, (x, y))

            pygame.draw.rect(self.screen, (255, 255, 255), [top_left[0], top_left[1], width, height], 5)
        
        elif mode == 'place':
            self.r_flood_start = None
            tile_Pos = [0, 0]
            for x in range(int(top_left[0] + self.offset.x), int(bottom_right[0] + self.offset.x), self.tilemap.tile_size):
                tile_Pos[0] = x // self.tilemap.tile_size
                for y in range(int(top_left[1] + self.offset.y), int(bottom_right[1] + self.offset.y), self.tilemap.tile_size):
                    tile_Pos[1] = y // self.tilemap.tile_size
                    tileloc = str(tile_Pos[0]) + ";" + str(tile_Pos[1])

                    self.tilemap.tile_map[tileloc] = Tile(
                        self.tile_list[self.tile_group],
                        [t for t in tile_Pos],
                        self.tile_variant,
                    )
                    
                    self.particles.add(PlaceParticle(
                        [tile_Pos[0] * TILE_SIZE + TILE_SIZE/2, tile_Pos[1] * TILE_SIZE + TILE_SIZE/2], 
                        self.particles
                    ))


    def mouse_stuff(self, current_img):
        keys = pygame.key.get_pressed()
        mousePos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()
        tilePos = (
            int((mousePos[0] + self.offset.x) // self.tilemap.tile_size), 
            int((mousePos[1] + self.offset.y) // self.tilemap.tile_size))
        tile_loc = str(tilePos[0]) + ";" + str(tilePos[1])
        
        if self.on_grid:
            self.screen.blit(current_img, (vec(tilePos) * self.tilemap.tile_size) - self.offset)
        else:
            self.screen.blit(current_img, [mousePos[0] - current_img.get_width()//2, mousePos[1] - current_img.get_height()//2])

        #breaking
        if mouse[0] or self.l_flood_start != None:
            if keys[pygame.K_RSHIFT] or keys[pygame.K_LALT]:
                self.flood_left(tile_loc, tilePos, 'flood')
            else:
                if self.l_flood_start != None:
                    self.flood_left(tile_loc, tilePos, 'erase')
                else:
                    self.left_click(tile_loc, tilePos, mousePos)

        #placing
        if mouse[2] or self.r_flood_start != None:
            if keys[pygame.K_RSHIFT] or keys[pygame.K_LALT]:
                self.flood_right(tile_loc, tilePos, 'flood', current_img)
            else:
                if self.r_flood_start != None:
                    self.flood_right(tile_loc, tilePos, 'place')
                else:
                    self.right_click(tile_loc, tilePos, mousePos, current_img)
        else:
            self.held = False

        #pick-block
        if mouse[1]:
            if self.on_grid:
                if tile_loc in self.tilemap.tile_map:
                    tile: Tile = self.tilemap.tile_map[tile_loc]
                    self.tile_group = self.tile_list.index(tile.type)
                    self.tile_variant = tile.variant

        ######################################################################################

    def run(self):

        last_time = time.perf_counter()
        while self.running:  
            #deltatime
            self.dt = time.perf_counter() - last_time
            self.dt *= FPS
            last_time = time.perf_counter()
            
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False

                    if event.key == pygame.K_g:
                        self.on_grid = not self.on_grid

                    if event.key == pygame.K_s and keys[pygame.K_LCTRL]:
                        self.tilemap.save()
                    if event.key == pygame.K_o and keys[pygame.K_LCTRL]:
                        self.tilemap.load()
                    if event.key == pygame.K_t and keys[pygame.K_LCTRL]:
                        self.tilemap.auto_tile()
                        
                elif event.type == pygame.MOUSEWHEEL:
                    #normal tiles
                    if self.on_grid:
                        if keys[pygame.K_LSHIFT]:
                            i = -1 if event.y < 0 else 1
                            self.tile_variant = (self.tile_variant + i) % len(self.assets[self.tile_list[self.tile_group]])
                        else:
                            i = -1 if event.y < 0 else 1
                            self.tile_group = (self.tile_group + i) % len(self.tile_list)
                            if self.tile_group == len(self.tile_list):
                                if i > 0: self.tile_group = 0
                                else: self.tile_group = len(self.tile_list)-1
                            self.tile_variant = 0

                    #offgrid (e.g. grass)
                    else:
                        if keys[pygame.K_LSHIFT]:
                            i = -1 if event.y < 0 else 1
                            self.offgrid_variant = (self.offgrid_variant + i) % len(self.offgrid_assets[self.offgrid_list[self.offgrid_group]])
                        else:
                            i = -1 if event.y < 0 else 1
                            self.offgrid_group = (self.offgrid_group + i) % len(self.offgrid_list)
                            if self.offgrid_group == len(self.offgrid_list)-1:
                                if i > 0: self.offgrid_group = 0
                                else: self.offgrid_group = len(self.offgrid_list)-1
                            self.offgrid_variant = 0

            #refresh
            self.calculate_offset() if not keys[pygame.K_LCTRL] else ...
            self.screen.fill((30, 30, 30))
            self.bg.update()

            #editor stuff
            for spr in sorted(
                    (
                        [t for t in self.tilemap.render_offgrid(self.offset)] +
                        [t for t in self.tilemap.render_tiles(  self.offset)]
                    ), 
                    key=lambda spr:spr.z
                ):
                spr.update(self.screen, self.offset)
            self.particles.update(self.screen)

            #axes
            pygame.draw.line(self.screen, (255, 255, 255), (-self.offset.x, 0), (-self.offset.x, HEIGHT), 1)
            pygame.draw.line(self.screen, (255, 255, 255), (0, HEIGHT - self.offset.y - 8), (WIDTH, HEIGHT - self.offset.y - 8), 1)

            #lil transparent render of current object in top left corner
            if self.on_grid:
                current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            else:
                current_tile_img = self.offgrid_assets[self.offgrid_list[self.offgrid_group]][self.offgrid_variant].copy()
            current_tile_img.set_alpha(100)
            self.screen.blit(current_tile_img, (16, 16))

            #mouse handling
            self.mouse_stuff(current_tile_img)

            #debug stuff
            offset_surf = self.font.render(f"{[int(self.offset.x), int(self.offset.y + 8)]}", False, (255, 255, 255))
            self.screen.blit(offset_surf, (5, HEIGHT-15))

            if keys[pygame.K_h]:
                labels = [
                    "SHIFT + Scroll: Switch Block Variant",
                    "RSHIFT + Click: Flood Fill/Place",
                    "Scroll: Switch Block Type",
                    "CTRL + O: Load File",
                    "CTRL + S: Save File",
                    "CTRL + T: Auto Tile",
                    "G: Toggle Grid",
                    "WASD: Move",
                    "LMB: Break",
                    "RMB: Place",
                    "MMB: Pick",
                ]
                for i, text in enumerate(labels):
                    label = self.font.render(text, False, (255, 255, 255))
                    self.screen.blit(label, label.get_rect(right=WIDTH-5, y = HEIGHT-15-(10*i)))
            else:
                label = self.font.render("Press H for Shortcuts", False, (255, 255, 255))
                self.screen.blit(label, label.get_rect(right=WIDTH-5, y = HEIGHT-15))

            pygame.display.update()
            self.clock.tick(FPS)

    ##############################################################################################

if __name__ == "__main__":
    editor = Editor()
    editor.run()