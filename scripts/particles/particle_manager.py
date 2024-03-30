import contextlib
from typing import Any
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.config.CORE_FUNCS import vec
from scripts.config.SETTINGS import Z_LAYERS, WIDTH, HEIGHT, ENVIRONMENT_SETTINGS

from scripts.particles.floating_lights import Floating_Light
from scripts.particles.movement import Run_Particle, Land_Particle
from scripts.particles.fire import Fire_Particle
from scripts.particles.rain import Rain_Particle, Rain_Splash
from scripts.particles.rainbow import Rainbow_Particle
from scripts.particles.snow import Snow_Particle

    ##############################################################################################

class Particle_Manager:
    def __init__(self, stage):
        self.stage = stage

        self.foreground_particles = pygame.sprite.Group()
        self.background_particles = pygame.sprite.Group()
        # for i in range(20):
        #     self.add_particle('foreground', 'float_light', pos=[random.uniform(0, WIDTH*2), random.uniform(-HEIGHT, HEIGHT)])

        self.start = True
        self.to_cull = {'rain', 'float_light'}

    def reset(self):
        self.foreground_particles.empty()
        self.background_particles.empty()

    def sprites(self):
        return self.foreground_particles.sprites() + self.background_particles.sprites()
    
    def add_particle(self, group: str, particle_type: str, **kwargs):
        particle_type = {
            'float_light' : Floating_Light,
            'run'         : Run_Particle,
            'land'        : Land_Particle,
            'fire'        : Fire_Particle,
            'rain'        : Rain_Particle,
            'rainbow'     : Rainbow_Particle,
            'snow'        : Snow_Particle,
        }[particle_type]

        if group == 'foreground':
            particle = particle_type(self.foreground_particles, *kwargs.values())
            self.foreground_particles.add(particle)
        elif group == 'background':
            particle = particle_type(self.background_particles, *kwargs.values())
            self.background_particles.add(particle)
    
    def update(self, offset):
        if self.start:
            #float lights
            if self.stage == "forest":
                for i in range((n:=random.randint(10, 15))):
                    self.add_particle('foreground', 'float_light', pos=[((i+1)/n)*WIDTH + random.uniform(-50, 50), random.uniform(0, HEIGHT)])

            self.start = False

        if ENVIRONMENT_SETTINGS["rain"]:
            # if random.randint(1, 2) == 1: 
            for i in range(random.randint(1, 6)):
                self.add_particle('foreground', 'rain', pos=[random.uniform(offset.x - WIDTH * 0.1, WIDTH * 1.1 + offset.x), offset.y - 20])
            for rain in set(filter(lambda spr: isinstance(spr, Rain_Particle), self.foreground_particles)):
                screen_pos = rain.pos - offset
                if screen_pos.y > HEIGHT:
                    self.foreground_particles.remove(rain)
                
        elif ENVIRONMENT_SETTINGS["snow"]:
            if random.randint(1, 3) == 1: 
                self.add_particle('foreground', 'snow', pos=[random.uniform(0, WIDTH*1.2), -5])
                for snow in set(filter(lambda spr: isinstance(spr, Snow_Particle), self.foreground_particles)):
                    screen_pos = snow.pos
                    if screen_pos.y > HEIGHT:
                        self.foreground_particles.remove(snow)