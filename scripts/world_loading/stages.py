import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.entities.player import Player
from scripts.entities.butterfly import Butterfly

from scripts.gui.minimap import Minimap

from scripts.items.item import Item

from scripts.world_loading.tilemap import Tilemap, INVISIBLE_TILES
from scripts.world_loading.backgrounds import *
from scripts.world_loading.custom_offgrid import Torch

from scripts.particles.floating_lights import Floating_Light
from scripts.particles.particle_manager import Particle_Manager
from scripts.particles.rain import Rain_Particle

    ##############################################################################################

class Stage_Loader:
    def __init__(self, game, default_index=0):
        self.screen = pygame.display.get_surface()
        self.game = game

        self.stages = [
            stage(game) for stage in 
            [
                Opening_Stage,
                Forest_Stage,
            ]
        ]
        self.current_stage_index = default_index
        self.current_stage_index = 1

    @property
    def tilemap(self):
        return self.current_stage.tilemap
    
    @property
    def current_stage(self):
        return self.stages[self.current_stage_index]
    
    @property
    def player_spawn_pos(self):
        return self.tilemap.get_player_spawn_pos()

    def render(self, player):
        self.current_stage.update(player)

    ##############################################################################################

"""
>> Stage
- Denotes an entire thematic world. 
- e.g. Forest, Hell, Underworld, Cloud Land ...

>> Area
- Denotes a screen within that stage, that changes when you move off-screen to a new section.
- e.g. Forest_Area1, Forest_Area2 ...

>> Cutscene_Area (in cutscenes.py)
- Inherits from 'Area' but is mostly auto-played
- e.g. Opening_Cutscene

>> Room
- Denotes a room opened when you go through a door or something in an Area.
- e.g. A house in the Forest_Area1.
"""

    ##############################################################################################

class Stage:
    def __init__(self, game):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.game = game

        self.tilemap = Tilemap(game)
        self.particle_manager = Particle_Manager(game, "")

        self.areas = []
        self.area_index = 0

    def current_bg_music(self):
        return self.areas[self.area_index].bg_music
    
    
    def find_tiles_outline(self):
        outlines = []
        visited = set()

        for key in self.tilemap.tile_map:
            tile = self.tilemap.tile_map[key]
            x, y = tile.pos
            if (x, y) not in visited:
                outline = self.find_outline(visited, x, y)
                outlines.append(outline)

        return set().union(*outlines)
    
    def find_outline(self, visited: set, start_x, start_y):
        outline_tiles = set()
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack.pop()
            if (x, y) not in visited:
                visited.add((x, y))
                
                if (tile:=self.tilemap.tile_map.get(f"{x};{y}")) and tile.type not in INVISIBLE_TILES:
                    neighbours = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

                    valid_neighbours = [(nx, ny) for nx, ny in neighbours if (tile:=self.tilemap.tile_map.get(f"{nx};{ny}")) and tile.type not in INVISIBLE_TILES]
                    if len(valid_neighbours) != 4:
                        outline_tiles.add((x, y))

                    unvisited_neighbours = [(nx, ny) for nx, ny in valid_neighbours if (nx, ny) not in visited]
                    stack.extend(unvisited_neighbours)

        return outline_tiles
    

    def update(self, player):
        # if not self.game.music_player.is_playing("bg"):
        #     self.game.music_player.play(self.current_bg_music(), "bg", loop=True)

        self.game.calculate_offset()
        self.areas[self.area_index].bg.update()
        self.particle_manager.update(self.game.offset)
        self.render(player)

        if pygame.key.get_just_pressed()[pygame.K_m]:
            self.areas[self.area_index].cycle_bg()

    def render(self, player):
        items = pygame.sprite.Group()
        for spr in sorted(
                (
                    [player] + 
                    [t for t in self.tilemap.render_offgrid(self.game.offset)] +
                    [t for t in self.tilemap.render_tiles(  self.game.offset)] +
                    [t for t in self.tilemap.nature_manager.render_tiles(self.game.offset)] +
                    self.particle_manager.sprites() +
                    self.game.entities.sprites() +
                    [self.minimap]
                ), 
                key=lambda spr:spr.z
            ):

            if isinstance(spr, Torch):
                spr.update(self.screen, self.game.offset, self.particle_manager)
            elif isinstance(spr, Player):
                spr.update(self.screen, self.game.offset, self.particle_manager)
            elif isinstance(spr, Butterfly):
                spr.update(self.screen, self.game.offset, self.particle_manager)
            elif isinstance(spr, Rain_Particle):
                spr.update(self.screen, self.game.offset, self.tilemap.render_tiles(self.game.offset))
            elif isinstance(spr, Item):
                spr.update(self.screen, self.game.offset)
                items.add(spr)
            else:
                spr.update(self.screen, self.game.offset)

        [item.player_collisions(self.screen, self.game.offset) for item in items]
        items.empty()

        # s = pygame.Surface(SIZE)
        # s.fill((0, 0, 0))
        # s.set_alpha(200)
        # self.screen.blit(s, (0, 0))

class Area:
    def __init__(self):
        self.bg = None
        self.rooms: list[Room] = []
        self.bg_music: str = ""
from scripts.world_loading.cutscenes import *

class Room:
    def __init__(self):
        pass

    ##############################################################################################

class Opening_Stage(Stage):
    def __init__(self, game):
        super().__init__(game)
        self.stage_index = 0
        self.areas = [
            Opening_Cutscene1(game, self), 
            Opening_Cutscene2(game, self),
            Opening_Cutscene3(game, self)
        ]
        self.areas[2].bg = self.areas[1].bg
        self.area_index = 0
        self.particle_manager = Particle_Manager(game, "opening")

    def update(self, *args):
        if not self.game.music_player.is_playing("bg"):
            self.game.music_player.play(self.current_bg_music(), "bg", loop=True)

        self.areas[self.area_index].bg.update()
        self.render()

    def render(self):
        self.areas[self.area_index].render()
        for spr in sorted(
                (
                    [t for t in self.tilemap.render_offgrid(self.game.offset)] +
                    [t for t in self.tilemap.render_tiles(  self.game.offset)] +
                    self.particle_manager.sprites() +
                    self.game.entities.sprites() 
                ), 
                key=lambda spr:spr.z
            ):

            if isinstance(spr, Player):
                spr.update(self.screen, self.game.offset, self.particle_manager)
            elif isinstance(spr, Butterfly):
                spr.update(self.screen, self.game.offset, self.particle_manager)
            else:
                spr.update(self.screen, self.game.offset)

    ##############################################################################################

class Forest_Stage(Stage):
    def __init__(self, game):
        super().__init__(game)
        self.name = "forest"
        self.stage_index = 1 #just general utility thing might be useful later on
        self.areas = [Forest_Area1(game)] #list of Areas
        self.tilemap.load("data/stage_data/1-Grass/area_1.json") #custom for each stage
        self.minimap = Minimap(game, self.find_tiles_outline())
        self.particle_manager = Particle_Manager(game, self)

class Forest_Area1:
    def __init__(self, game):
        # self.bg = Forest_Background(game)
        # self.bg = Perlin_Background(game)
        self.bg = Sky_Background(game)
        # self.bg = Black_Screen_Background(game)
        self.bg_music = "tutorial_1"

        self.bgs = [Perlin_Background(game), Sky_Background(game), ]

        self.i = 0

    def cycle_bg(self):
        self.bg = self.bgs[self.i]
        
        self.i += 1
        if self.i == len(self.bgs):
            self.i = 0

    ##############################################################################################

# class Intro_Area