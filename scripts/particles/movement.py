import contextlib
from typing import Any
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.config.CORE_FUNCS import vec
from scripts.config.SETTINGS import Z_LAYERS, GRAV

    ##############################################################################################

class Run_Particle(pygame.sprite.Sprite):
    def __init__(self, parent, pos, facing):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["background particle"]

        self.pos = vec(pos)
        self.direction = 1 if facing == 'left' else -1
        self.acc = vec(-self.direction/50, GRAV)
        self.vel = vec(random.uniform(self.direction*0.25, self.direction*4), -random.uniform(4, 9))
        self.radius = random.uniform(2, 5)
        self.colour = random.uniform(90, 180)
        self.decay_factor = random.uniform(0.5, 1) / 10

    def update(self, screen, offset):
        self.radius -= self.decay_factor
        if self.radius <= 0:
            self.parent.remove(self)

        self.vel += self.acc
        self.pos += self.vel 

        self.draw(screen, offset)

    def draw(self, screen, offset):
        pygame.draw.circle(screen, (self.colour, self.colour, self.colour), self.pos - offset, self.radius, 1 if self.radius <= 2.5 else 2)





class Land_Particle(pygame.sprite.Sprite):
    def __init__(self, parent, pos, scale, speed=None, colour=(255, 255, 255)):
        super().__init__()
        self.parent = parent 
        self.z = Z_LAYERS["background particle"]

        self.pos = vec(pos)
        self.scale = scale
        self.angle = math.radians(random.choice([-120, -60]))
        self.rotation = math.radians(random.uniform(0, 180))
        self.speed = random.uniform(3, 6) * 2.5 if speed == None else speed
        self.colour = colour


    def move(self):
        self.pos += vec(math.cos(self.angle), math.sin(self.angle)) * self.speed

    def apply_gravity(self, friction, force, terminal_velocity):
        movement = vec(math.cos(self.angle), math.sin(self.angle)) * self.speed
        movement[1] = min(terminal_velocity, movement[1] + force)
        movement[0] *= friction
        self.angle = math.atan2(movement[1], movement[0])


    def update(self, screen, offset):
        self.speed -= 0.2
        if self.speed < 0:
            return self.parent.remove(self)
        self.rotation += math.radians(self.speed)
        
        self.apply_gravity(0.99, 2, 24)
        self.move()
        
        self.draw(screen, offset)

    def draw(self, screen, offset):
        points = [
            vec(math.cos(self.rotation), math.sin(self.rotation)) * self.scale * (self.speed) / 5,
            vec(math.cos(self.rotation + math.pi/2), math.sin(self.rotation + math.pi/2)) * self.scale * (self.speed) / 5,
            vec(math.cos(self.rotation + math.pi), math.sin(self.rotation + math.pi)) * self.scale * (self.speed) / 5,
            vec(math.cos(self.rotation + 3*math.pi/2), math.sin(self.rotation + 3*math.pi/2)) * self.scale * (self.speed) / 5,
        ]
        points = [p + self.pos - offset for p in points]
        pygame.draw.polygon(screen, self.colour, points)
        pygame.draw.polygon(screen, (0, 0, 0), points, math.ceil(self.scale/4))



class Land_Particle(pygame.sprite.Sprite):
    def __init__(self, parent, pos, scale, colour=(255, 255, 255)):
        super().__init__()
        self.parent = parent
        self.z = Z_LAYERS["background particle"]

        self.pos = vec(pos)
        self.scale = scale
        self.angle = math.radians(random.uniform(-120, -60))
        self.rotation = math.radians(random.uniform(0, 90))
        self.speed = random.uniform(4, 8)
        self.colour = colour
        self.grav = 0

    def move(self):
        self.pos += vec(math.cos(self.angle), math.sin(self.angle)) * self.speed
        self.pos.y += self.grav
        self.grav += GRAV * 2

    def update(self, screen, offset):
        self.scale -= 0.2
        if self.scale <= 0:
            self.parent.remove(self)

        self.rotation += math.radians(self.speed)
        self.move()

        self.draw(screen, offset)

    def draw(self, screen, offset):
        points = [
            vec(math.cos(self.rotation), math.sin(self.rotation)) * self.scale,
            vec(math.cos(self.rotation + math.pi/2), math.sin(self.rotation + math.pi/2)) * self.scale,
            vec(math.cos(self.rotation + math.pi), math.sin(self.rotation + math.pi)) * self.scale,
            vec(math.cos(self.rotation + 3*math.pi/2), math.sin(self.rotation + 3*math.pi/2)) * self.scale,
        ]
        points = [p + self.pos - offset for p in points]
        pygame.draw.polygon(screen, self.colour, points)
        pygame.draw.polygon(screen, list(map(lambda x: x-100, self.colour)), points, math.ceil(self.scale/4))