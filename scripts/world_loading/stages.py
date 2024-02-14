import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.entities.player import Player
from scripts.entities.butterfly import Butterfly

from scripts.world_loading.tilemap import Tilemap
from scripts.world_loading.backgrounds import *
from scripts.world_loading.nature_tiles import Grass
from scripts.world_loading.light_tiles import Torch

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
        self.particle_manager = Particle_Manager("")

        self.areas = []
        self.area_index = 0

    def current_bg_music(self):
        return self.areas[self.area_index].bg_music

    def update(self, player):
        if not self.game.music_player.is_playing("bg"):
            self.game.music_player.play(self.current_bg_music(), "bg", loop=True)

        self.game.calculate_offset()
        self.areas[self.area_index].bg.update()
        self.particle_manager.update(self.game.offset)
        self.render(player)

    def render(self, player):
        for spr in sorted(
                (
                    [player] + 
                    [t for t in self.tilemap.render_offgrid(self.game.offset)] +
                    [t for t in self.tilemap.render_tiles(  self.game.offset)] +
                    self.particle_manager.sprites() +
                    self.game.entities.sprites()
                ), 
                key=lambda spr:spr.z
            ):

            if isinstance(spr, Grass):
                spr.update(self.screen, self.game.offset, player)
            elif isinstance(spr, Torch):
                spr.update(self.screen, self.game.offset, self.particle_manager)
            elif isinstance(spr, Player):
                spr.update(self.screen, self.game.offset, self.particle_manager)
            elif isinstance(spr, Butterfly):
                spr.update(self.screen, self.game.offset, self.particle_manager)
            elif isinstance(spr, Rain_Particle):
                spr.update(self.screen, self.game.offset, self.tilemap.render_tiles(self.game.offset))
            else:
                spr.update(self.screen, self.game.offset)

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
        self.particle_manager = Particle_Manager("opening")

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
        self.stage_index = 1 #just general utility thing might be useful later on
        self.areas = [Forest_Area1(game)] #list of Areas
        self.tilemap.load("data/stage_data/test2.json") #custom for each stage
        self.particle_manager = Particle_Manager("forest")

class Forest_Area1:
    def __init__(self, game):
        # self.bg = Forest_Background(game)
        self.bg = Perlin_Background(game)
        self.bg_music = "tutorial_1"