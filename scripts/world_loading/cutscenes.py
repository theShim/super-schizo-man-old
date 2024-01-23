import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS
from scripts.config.CORE_FUNCS import gaussian_blur, vec, Timer

from scripts.world_loading.stages import Area
from scripts.world_loading.backgrounds import Delaunay_Background, Black_Screen_Background  

from scripts.entities.butterfly import Butterfly

from scripts.gui.custom_fonts import Custom_Font
from scripts.gui.text_writer import Text_Box, Rainbow_Text_Box
from scripts.texts.cutscene_dialogues import DIALOGUES

    ##############################################################################################

class Cutscene_Area(Area):
    def __init__(self):
        super().__init__()

    ##############################################################################################
        
class Opening_Cutscene1(Cutscene_Area): #monster speech
    def __init__(self, game, parent_stage):
        self.game = game
        self.parent_stage = parent_stage
        self.bg = Black_Screen_Background(game)

        self.dialogue_timer = Timer(FPS*2, 1)
        self.exit_timer = Timer(FPS*8, 1)

        self.text_boxes = [
            Text_Box(
                DIALOGUES['opening_cutscene'][1], 
                (50, 80), 
                Custom_Font.Fluffy),
            Text_Box(
                DIALOGUES['opening_cutscene'][2], 
                (50, 80), 
                Custom_Font.Fluffy),
            Text_Box(
                DIALOGUES['opening_cutscene'][3],
                (50, 80), 
                Custom_Font.Fluffy),
        ]
        self.text_box = self.text_boxes.pop(0)
        self.bg_music = "memory1"

    def render(self):
        self.game.music_player.set_vol(0.1, "type")
        if len(self.text_boxes) > 0 or not self.text_box.finished:
            self.text_box.update()
            self.text_box.render(self.game.screen, (200, 200, 200))
            if self.text_box.finished:
                self.dialogue_timer.update()

            if self.dialogue_timer.finished:
                self.dialogue_timer.reset()
                self.text_box = self.text_boxes.pop(0)

            if self.text_box.text[min(len(self.text_box.text)-1, int(self.text_box.t))].isalpha() and self.text_box.click:
                self.game.music_player.play("typing", "type")

        else:
            self.text_box.render(self.game.screen, (200, 200, 200))
            self.exit_timer.update()
            if self.exit_timer.finished:
                self.parent_stage.area_index = 1
                self.game.music_player.stop(fadeout_ms=500)
        
class Opening_Cutscene2(Cutscene_Area): #blinking
    def __init__(self, game, parent_stage):
        super().__init__()
        self.game = game
        self.parent_stage = parent_stage
        self.bg = Delaunay_Background(game, 100)

        self.y = math.pi/2.1
        self.deltay = .0002

        self.e = True
        self.expand = False
        self.alpha = 255
        self.fade = 1

        self.pause = Timer(FPS*3, 1)

    def render(self):
        self.pause.update()
        if not self.pause.finished:
            self.game.screen.fill((0, 0, 0))
            return

        if self.expand == False:
            self.y += math.degrees(self.deltay)
            self.deltay += 0.00005

        if self.y > (6 * math.pi / 2):
            if self.e:
                self.game.entities.add(Butterfly(self.game, self.game.entities))
                self.game.offset = vec(0, 0)
                self.parent_stage.particle_manager.reset()
                self.e = False
                
        if self.y > (7 * math.pi / 2):
            self.expand = True

        n = 3.3
        x = 100
        blink = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        y = ((HEIGHT/n) * math.sin(self.y)) + ((HEIGHT/2) - (HEIGHT/n))
        pygame.draw.ellipse(
            blink, 
            (0, 0, 0), 
            [
                -x,
                y,
                WIDTH+x*2,
                HEIGHT-y*2
            ]
        )
        mask = pygame.mask.from_surface(blink)
        blink = mask.to_surface().convert_alpha()
        blink.set_colorkey((255, 255, 255))
        blink = gaussian_blur(blink)

        if self.expand:
            self.fade += 0.05
            blink = pygame.transform.scale(blink, vec(blink.get_size())*self.fade)
        self.game.screen.blit(blink, blink.get_rect(center=(WIDTH/2, HEIGHT/2)))

        if self.fade >= 1.3:
            self.parent_stage.area_index = 2


class Opening_Cutscene3(Cutscene_Area): #butterfly
    def __init__(self, game, parent_stage):
        super().__init__()
        self.game = game
        self.parent_stage = parent_stage
        self.bg = Delaunay_Background(game, 100)

        self.text_boxes = [
            Rainbow_Text_Box(
                "obamaaaaaaaaaaaaaaaaaaaaaa",
                (50, 50),
                Custom_Font.Fluffy,
                (WIDTH-100, 100)
            )
        ]
        self.text_box = self.text_boxes.pop(0)

    def render(self):
        self.text_box.update()
        self.text_box.render(self.game.screen, (0, 0, 0))