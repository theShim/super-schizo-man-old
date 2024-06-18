import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.entities.player import Player
from scripts.entities.butterfly import Butterfly
from scripts.items.item import Item

from scripts.particles.rain import Rain_Particle
from scripts.particles.particle_manager import Particle_Manager

from scripts.world_loading.tilemap import Tilemap
from scripts.world_loading.backgrounds import Black_Screen_Background
from scripts.world_loading.custom_offgrid import Torch

    ##############################################################################################

class State_Loader:
    def __init__(self, game, start=None):
        self.game = game
        self.stack: list[State] = []

        self.start = start
        self.states = {}
        self.populate_states()

        self.last_state = None

    def populate_states(self):
        from scripts.world_loading.states.grass_1 import Grass_1_1

        self.states = {
            "grass_1-1" : Grass_1_1(self.game, None)
        }

        if self.start:
            self.add_state(self.states[self.start])

        #############################################################################
    
    @property
    def current_state(self):
        return self.stack[-1]

    @property
    def tilemap(self) -> Tilemap:
        if (t := self.current_state.tilemap): return t
        else:
            for i in range(len(self.states)-2, -1, -1):
                if (t := self.stack[i].tilemap): 
                    break
            else:
                t = "No Tilemap".lower()
            return t

    @property
    def player_spawn_pos(self):
        return self.tilemap.get_player_spawn_pos()

        #############################################################################

    def add_state(self, state):
        self.stack.append(state)

    def pop_state(self):
        self.last_state = self.stack.pop(-1)

    def get_state(self, name):
        return self.states.get(name, default=None)

        #############################################################################

    def update(self):
        self.stack[-1].update()


class State:
    def __init__(self, game, prev=None, name=None):
        self.game = game
        self.prev_state = prev
        self.name = name

        self.tilemap = Tilemap(game)
        self.particle_manager = Particle_Manager(self.game, self.name)
        self.screen = pygame.display.get_surface()
        self.bg = Black_Screen_Background(self.game)

    def update(self): #custom for each state
        self.game.calculate_offset()
        self.bg.update()
        self.render(self.game.player)

    def render(self, player):
        items = pygame.sprite.Group()
        for spr in sorted(
                (
                    [player] + 
                    [t for t in self.tilemap.render_offgrid(self.game.offset)] +
                    [t for t in self.tilemap.render_tiles(  self.game.offset)] +
                    [t for t in self.tilemap.nature_manager.render_tiles(self.game.offset)] +
                    self.particle_manager.sprites() +
                    self.game.entities.sprites()# +
                    # [self.minimap]
                ), 
                key=lambda spr:spr.z
            ):

            if isinstance(spr, (Player, Butterfly, Torch)): #emit particles
                spr.update(self.screen, self.game.offset, self.particle_manager)
            elif isinstance(spr, Rain_Particle): #collide with tiles
                spr.update(self.screen, self.game.offset, self.tilemap.render_tiles(self.game.offset))
            elif isinstance(spr, Item): #items
                spr.update(self.screen, self.game.offset)
                items.add(spr)
            else: #everything else
                spr.update(self.screen, self.game.offset)

        [item.player_collisions(self.screen, self.game.offset) for item in items]
        items.empty()


