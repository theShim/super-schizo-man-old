import contextlib
with contextlib.redirect_stdout(None):
    import pygame; pygame.init()
    from pygame.locals import *
    
import os
import json
import random
from tkinter.filedialog import asksaveasfile, askopenfilename

from scripts.config.SETTINGS import TILE_SIZE, WIDTH, HEIGHT, Z_LAYERS, LOADED_SPRITE_NUMBER
from scripts.config.CORE_FUNCS import euclidean_distance, vec
from scripts.world_loading.nature import Nature_Manager
from scripts.world_loading.custom_offgrid import Torch, Bridge

    ##############################################################################################

#collision detection stuff
NEIGHBOUR_OFFSETS = [
    (-1, -1),
    (-1, 0),
    (0, -1),
    (1, -1),
    (1, 0),
    (0, 0),
    (-1, 1),
    (0, 1),
    (1, 1)
]

#tile groups
PHYSICS_TILES = {'grass', 'stone'}
INVISIBLE_TILES = {'spawner'}
NATURE_TILES = {'grass', 'swaying_vine'}
COLLIDEABLE_OFFGRID = {'grass'}

#auto tiling group and settings associating every neighbour tile
AUTO_TILE_TYPES = {'grass', 'stone'}
AUTO_TILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,                   #top-left
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,          #top
    tuple(sorted([(-1, 0), (0, 1)])): 2,                  #top-right
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,         #right
    tuple(sorted([(-1, 0), (0, -1)])): 4,                 #bottom-right
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,         #bottom
    tuple(sorted([(1, 0), (0, -1)])): 6,                  #bottom-left
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,          #left
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8, #middle
    # tuple(sorted([(0, -1)])): 9,                          #lonesome top
}

    ##############################################################################################

class Tilemap:
    def __init__(self, game, tile_size = TILE_SIZE, editor_flag = False):
        self.game = game

        self.tile_size = tile_size
        self.tile_map = {} #all actual block tiles
        self.offgrid_tiles = [] #all decor tiles

        self.nature_manager = Nature_Manager(game)

        self.editor_flag = editor_flag

        ######################################################################################

    #auto tiles (idk how it works either just does)
    def auto_tile(self):
        for loc in self.tile_map:
            tile = self.tile_map[loc]
            neighbours = set()
            for shift in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                check_loc = str(tile.pos[0] + shift[0]) + ';' + str(tile.pos[1] + shift[1])
                if check_loc in self.tile_map:
                    if self.tile_map[check_loc].type == tile.type:
                        neighbours.add(shift)

            neighbours = tuple(sorted(neighbours))
            if tile.type in AUTO_TILE_TYPES and neighbours in AUTO_TILE_MAP:
                tile.variant = AUTO_TILE_MAP[neighbours]

    #save the tilemap as a json file
    def save(self):
        f = asksaveasfile(
            filetypes=[('JSON File', ".json")], 
            defaultextension=".json",
            initialdir="level_data"
        )
        if f:
            json.dump({
                    'tilemap' : {key:item.dict for key, item in self.tile_map.items()}, 
                    'tile_size' : self.tile_size, 
                    'offgrid' : [item.dict for item in self.offgrid_tiles]
                }, 
                f,
                indent=4)
            print("Saved to", f.name)

    #open and load a previously saved tilemap.json
    def load(self, path: str=None):
        if path == None:
            f = askopenfilename(
                title="Open existing level data...",
                initialdir="level_data",
                filetypes=[('JSON File', ".json")]
            )
        else:
            f = path

        try:
            with open(f, 'r') as file:
                data = json.load(file)
        except FileNotFoundError as err:
            raise FileNotFoundError(err)
        except:
            return

        self.tile_map = {}
        for dic in data['tilemap']:
            if data['tilemap'][dic]['type'] == "water" and self.editor_flag == False:
                self.nature_manager.add_tile("water", data['tilemap'][dic]['pos'], data['tilemap'][dic]['variant'])
            else:
                self.tile_map[dic] = Tile(
                    data['tilemap'][dic]['type'],
                    data['tilemap'][dic]['pos'],
                    data['tilemap'][dic]['variant'],
                )
        self.nature_manager.clump_water()

        self.offgrid_tiles = []
        for tile in data['offgrid']:
            if tile["type"] in NATURE_TILES and self.editor_flag == False:
                self.nature_manager.add_tile(tile["type"], tile["pos"], tile["variant"])
            elif tile["type"] == "bridge":
                to_add = Offgrid_Tile.get_offgrid_tile(tile['type'], tile['pos'], tile['variant'], self.editor_flag, end_pos=tile["end_pos"])
                self.offgrid_tiles.append(to_add)
            else:
                to_add = Offgrid_Tile.get_offgrid_tile(tile['type'], tile['pos'], tile['variant'], self.editor_flag)
                self.offgrid_tiles.append(to_add)
        self.tile_size = data['tile_size']

        ######################################################################################

    #try to get a random player spawning location from the level data otherwise just put it at the centre
    def get_player_spawn_pos(self):
        locs = []
        for loc in self.tile_map:
            tile = self.tile_map[loc]
            if tile.type == "spawner" and tile.variant == 0:
                locs.append([tile.pos[0] * TILE_SIZE + TILE_SIZE/2, tile.pos[1] * TILE_SIZE + TILE_SIZE/2])
        return random.choice(locs) if locs else (WIDTH/2, 0)

        ######################################################################################
        
    #list of tiles currently around the (player) pos
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOUR_OFFSETS:
            check_loc = f"{str(tile_loc[0] + offset[0])};{str(tile_loc[1] + offset[1])}"
            if check_loc in self.tile_map:
                tiles.append(self.tile_map[check_loc])
        return tiles
    
    #list of tiles currently around the (player) pos that are collide-able
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile.type in PHYSICS_TILES:
                rects.append(pygame.Rect(tile.pos[0] * self.tile_size, tile.pos[1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def collideable_offgrid_around(self, hitbox: pygame.Rect):
        tiles = []
        for tile in self.offgrid_tiles:
            if tile.type in COLLIDEABLE_OFFGRID:
                # if tile.type == 'grass':
                #     pass
                if pygame.Rect(
                        hitbox.x - self.game.offset.x, hitbox.y - self.game.offset.y, *hitbox.size
                    ).colliderect(tile.hitbox(self.game.offset)):
                    tiles.append(tile)
        return tiles

        ######################################################################################

    def render_tiles(self, offset, buffer=[0, 0]):
        start_x = int(offset.x // (self.tile_size) - buffer[0])
        end_x = int((offset.x + self.game.screen.get_width()) // self.tile_size  + buffer[0]) + 1
        start_y = int(offset.y // (self.tile_size) - buffer[1])
        end_y = int((offset.y + self.game.screen.get_height()) // self.tile_size + buffer[1]) + 1

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                loc = f"{x};{y}"
                if loc in self.tile_map:
                    tile: Tile = self.tile_map[loc]

                    if tile.type not in INVISIBLE_TILES or self.editor_flag == True:
                        yield tile

    def render_offgrid(self, offset):
        for tile in self.offgrid_tiles:
            if (offset.x - TILE_SIZE < tile.pos[0] < offset.x + WIDTH and
                offset.y - TILE_SIZE < tile.pos[1] < offset.y + HEIGHT):
                yield tile

            elif tile.type == "bridge" and (offset.x - TILE_SIZE < tile.end_pos[0] < offset.x + WIDTH and
                                            offset.y - TILE_SIZE < tile.end_pos[1] < offset.y + HEIGHT):
                yield tile

    ##############################################################################################

class Tile(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        Tile.SPRITES = {}
        BASE_TILE_PATH = 'assets/tiles/'

        for img_name in os.listdir(BASE_TILE_PATH):
            images = []
            for name in sorted(os.listdir(BASE_TILE_PATH + img_name)):
                img = pygame.transform.scale(
                    pygame.image.load(BASE_TILE_PATH + img_name + '/' + name).convert_alpha(),
                    (TILE_SIZE, TILE_SIZE)
                )
                img.set_colorkey((0, 0, 0))
                images.append(img)

            Tile.SPRITES[img_name] = images
            yield

        ######################################################################################

    def __init__(self, type, pos, variant=1):
        super().__init__()
        self.type = type #tile type e.g. grass, the folder
        self.variant = variant #tile variant e.g. grass_8, the asset itself
        self.pos = pos
        self.z = Z_LAYERS["tiles"]

    #dictionary object used for json saving
    @property
    def dict(self) -> dict:
        return {"type":self.type, "variant":self.variant, "pos":self.pos}
    
    #actually draw it onto the screen
    def update(self, screen, offset):
        return
        # print(self.pos, "*")
        img = Tile.SPRITES[self.type][self.variant]
        screen.blit(img, [
            (self.pos[0] * TILE_SIZE) - offset.x, 
            (self.pos[1] * TILE_SIZE) - offset.y
        ])


class Offgrid_Tile(pygame.sprite.Sprite):

    MIDGROUND_OFFGRID = {'grass'}
    FOREGROUND_OFFGRID = {'torch'}

    #same caching system as Tile
    @classmethod
    def cache_sprites(cls):
        Offgrid_Tile.SPRITES = {}
        BASE_TILE_PATH = 'assets/offgrid_tiles/'
        
        for img_name in os.listdir(BASE_TILE_PATH):
            imgs = []
            for name in sorted(os.listdir(BASE_TILE_PATH + img_name)):
                img = pygame.image.load(BASE_TILE_PATH + img_name + '/' + name).convert_alpha()
                img.set_colorkey((0, 0, 0))
                imgs.append(img)

            Offgrid_Tile.SPRITES[img_name] = imgs
            yield 

    #just wanted a fancy match statement rather than if
    @staticmethod
    def get_offgrid_tile(type, pos, variant, editor_flag = False, **kwargs):
        if editor_flag:
            tile = Offgrid_Tile(type, pos, variant)
            tile.z = Z_LAYERS["foreground offgrid"]
            return tile
        
        match type:
            case "torch":
                return Torch(pos, variant)
            case "bridge":
                return Bridge(pos, variant, *kwargs.values())
            case _:
                return Offgrid_Tile(type, pos, variant)

        ######################################################################################
    
    def __init__(self, type, pos, variant):
        super().__init__()
        self.type = type
        self.variant = variant
        self.pos = pos

        if self.type in self.MIDGROUND_OFFGRID:
            self.z = Z_LAYERS["midground offgrid"] 
        elif self.type in self.FOREGROUND_OFFGRID:
            self.z = Z_LAYERS["foreground offgrid"] 
        else:
            self.z = Z_LAYERS["background offgrid"] 

    @property
    def dict(self):
        # if self.type == "bridge":
        #     return {'type':self.type, "pos":self.pos, "end_pos":self.end_pos, "variant":self.variant}
        # else:
        return {'type':self.type, "pos":self.pos, "variant":self.variant}
    
    def update(self, screen, offset):
        img = Offgrid_Tile.SPRITES[self.type][self.variant]
        screen.blit(img, self.pos - offset)


    ##############################################################################################