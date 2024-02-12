import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import cv2
import numpy as np
import random
import math

    ##############################################################################################

class Music_Player:
    def __init__(self, channel_num = 20):
        pygame.mixer.set_num_channels(channel_num)

        #every sound file loaded
        self.sounds = {
            "bg_test0" : Sound("music/test.wav"),
            "memory1" : Sound("music/memory_1.mp3"),
            "typing" : Sound("music/typing.wav"),
            "tutorial_1" : Sound("music/tutorial/tutorial_ambience.mp3")
        }

        #every sound channel to be used, gonna be more later on
        self.background = pygame.mixer.Channel(0)
        self.typing = pygame.mixer.Channel(1)
        self.channels = [
            self.background,
            self.typing,
        ]

    def get_channel(self, channel_name):
        match channel_name:
            case "background" | "bg":
                return self.background
            case "typing" | "type":
                return self.typing
            case _:
                return None
            
    def is_playing(self, channel):
        channel = self.get_channel(channel)
        return channel.get_busy()
            

    #play a specified sound in a specified channel, with the option to constantly loop it
    #sound should be a key straight from the self.sounds dict
    def play(self, sound, channel, loop=False):  
        if sound == "":
            return
        sound = self.sounds[sound]
        channel = self.get_channel(channel)
        channel.play(sound, loops=-1 if loop else 0)

    #queue a song to play after the current one in a specified channel
    def queue_sound(self, sound, channel):  
        sound = self.sounds[sound]
        channel = self.get_channel(channel)
        channel.queue(sound)

    #stop the playback of a specified channel or all, with an optional fade out timer
    def stop(self, channel="all", fadeout_ms=1000):
        if channel == "all":
            for c in self.channels:
                c.fadeout(fadeout_ms)
            return
        
        self.get_channel(channel).fadeout(fadeout_ms)
    
    #change vol with float between 0 and 1 for specified channels
    def set_vol(self, vol: float, channel="all"):
        if channel == "all":
            for c in self.channels:
                c.set_volume(vol)
            return
        self.get_channel(channel).set_volume(vol)

#normal pygame sound object just with a name attribute
class Sound(pygame.mixer.Sound):
    def __init__(self, filename):
        super().__init__(filename)
        self.name = filename.split("/")[-1]