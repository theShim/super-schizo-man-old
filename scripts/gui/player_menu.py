import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import cv2
import numpy as np
import random
import math

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS
from scripts.config.CORE_FUNCS import vec, Timer, lerp

from scripts.gui.text_writer import Text_Box
from scripts.gui.custom_fonts import Custom_Font
from scripts.gui.star_waypoint_thing import Starry_Background

from scripts.particles.lightning import Lightning

    ##############################################################################################

ITEM_DESCRIPTIONS = {
    "grains" : {
        "text" : "A key ingredient in yeast infections.",
        "buffs": [], 
    }
}

    ##############################################################################################

class Player_Menu:
    def __init__(self, parent):
        self.parent = parent

        self.top_row = pygame.sprite.Group()
        x = 10
        for i, button in enumerate([self.Profile, self.Inventory, self.QuestBook, self.Map, self.Settings]):
            self.top_row.add(e:=button(self, (x, 10), i*2))
            x += e.base.get_width() - 15

        self.profile_buttons = pygame.sprite.Group()
        self.profile_buttons.add(e1:=self.Stats_Select(self, (0, e.base.get_height() + 60), 2))
        self.profile_buttons.add(self.SkillTree_Select(self, (0, e1.base.get_height() + e.base.get_height() + 75), 4))

        self.item_buttons = pygame.sprite.Group()
        x = 10 + e.base.get_width()*0.5
        for i, button in enumerate([self.Weapons, self.Armour, self.Consumables, self.Key_Items]):
            self.item_buttons.add(e:=button(self, (x, HEIGHT-86+28), i*2))
            if i == 0:e.clicked = True; e.switch_end_pos(1)
            x += e.base.get_width() + 10
        self.item_card_display = self.Item_Card_Display(self, (20, 80))

        self.waypoint_map = self.Waypoint_Map()

        self.settings_case = self.Settings_Case(self, (36, e.base.get_height() - 12))

    def reset(self):
        pass

    def update(self, screen):

        for b in self.top_row.sprites():
            if b.clicked:
                if b.name == "profile":
                    self.profile_buttons.update(screen)

                elif b.name == "inventory":
                    to_check = "weapons"
                    for item_button in self.item_buttons.sprites():
                        if isinstance(item_button, self.Item_Bottom_Button):
                            if item_button.clicked:
                                to_check = item_button.name
                                break

                    self.item_card_display.update(screen, to_check)
                    self.item_buttons.update(screen)

                elif b.name == "map":
                    self.waypoint_map.update(screen)
                    
                elif b.name == "settings":
                    self.settings_case.update(screen)

                break
            
            else:
                if b.name == "profile":
                    for profile_button in self.profile_buttons.sprites():
                        if isinstance(profile_button, self.Long_Button):
                            profile_button.reset()
                elif b.name == "inventory":
                    for item_button in self.item_buttons.sprites():
                        if isinstance(item_button, self.Item_Bottom_Button):
                            item_button.reset()
                            if item_button.name == "weapons":
                                item_button.clicked = True
                                item_button.switch_end_pos(1)

        self.top_row.update(screen)
        for b in self.top_row.sprites():
            if b.name == self.parent.loader:
                b.clicked = True
                break

        ##########################################################################################

    class Top_Button(pygame.sprite.Sprite):
        def __init__(self, parent, name, pos, y_transition_offset):
            super().__init__()
            self.parent = parent
            self.name = name

            self.base = pygame.image.load(f"assets/gui/{name}.png")#.convert_alpha()
            self.base = pygame.transform.scale(self.base, vec(self.base.get_size())*2)
            self.base.set_colorkey((0, 0, 0))
            self.clicked_img = pygame.image.load(f"assets/gui/{name+'_clicked'}.png")#.convert_alpha()
            self.clicked_img = pygame.transform.scale(self.clicked_img, vec(self.clicked_img.get_size())*2)
            self.clicked_img.set_colorkey((0, 0, 0))

            self.pos = vec(pos[0], pos[1]-self.base.get_height()*1.5)
            self.end_pos = pos
            self.move_timer = Timer(y_transition_offset, 1)

            self.rect = self.base.get_rect(topleft=self.end_pos)
            self.mask = pygame.mask.from_surface(self.base)
            self.clicked = False
            self.held = False

        def update(self, screen):
            if abs(self.end_pos[1] - self.pos[1]) > 0:
                self.move_timer.update()
                if self.move_timer.finished:
                    self.pos = self.pos.lerp(self.end_pos, 0.15)

            mousePos = pygame.mouse.get_pos()
            mousePos_masked = mousePos[0] - self.end_pos[0], mousePos[1] - self.end_pos[1]
            mouse = pygame.mouse.get_pressed()

            if (self.rect.collidepoint(mousePos) and self.mask.get_at(mousePos_masked)) or self.clicked:
                if mouse[0]:
                    self.clicked = True
                    self.parent.parent.loader = self.name
                    [setattr(button, "clicked", False) for button in self.parent.top_row if button != self]
                screen.blit(self.clicked_img, [self.pos.x, self.pos.y - 2])
            else:
                screen.blit(self.base, self.pos)

    class Long_Button(pygame.sprite.Sprite):
        def __init__(self, parent, name, pos, x_transition_offset):
            super().__init__()
            self.parent = parent
            self.name = name

            self.base = pygame.image.load(f"assets/gui/{name}.png")#.convert_alpha()
            self.base = pygame.transform.scale(self.base, vec(self.base.get_size())*2)
            self.base.set_colorkey((0, 0, 0))
            self.clicked_img = pygame.image.load(f"assets/gui/{name+'_clicked'}.png")#.convert_alpha()
            self.clicked_img = pygame.transform.scale(self.clicked_img, vec(self.clicked_img.get_size())*2)
            self.clicked_img.set_colorkey((0, 0, 0))

            self.pos = vec(pos[0]-self.base.get_width()*1.75, pos[1])
            self.end_positions = [pos, [pos[0] - self.base.get_width()*0.75, pos[1]]]
            self.end_pos = self.end_positions[0]
            self.move_timer = Timer(x_transition_offset, 1)

            self.rect = self.base.get_rect(topleft=self.end_pos)
            self.mask = pygame.mask.from_surface(self.base)
            self.clicked = False
            self.held = False

        def reset(self):
            self.pos.x = self.end_pos[0] - self.base.get_width()*1.75
            self.switch_end_pos(0)
            self.move_timer.reset()

        def switch_end_pos(self, index:int = 0):
            self.end_pos = self.end_positions[index]

        def update(self, screen):
            if abs(self.end_pos[0] - self.pos[0]) > 0:
                self.move_timer.update()
                if self.move_timer.finished:
                    self.pos = self.pos.lerp(self.end_pos, 0.15)

            mousePos = pygame.mouse.get_pos()
            mousePos_masked = mousePos[0] - self.end_pos[0], mousePos[1] - self.end_pos[1]
            mouse = pygame.mouse.get_pressed()


            def mask_collide(pos):
                try: return self.mask.get_at(pos)
                except IndexError: False
                
            if (self.rect.collidepoint(mousePos) and mask_collide(mousePos_masked)):
                if mouse[0]:
                    self.clicked = True
                    [setattr(button, "clicked", False) for button in self.parent.profile_buttons if isinstance(button, Player_Menu.Long_Button) and button != self]
                    [button.switch_end_pos(1) for button in self.parent.profile_buttons if isinstance(button, Player_Menu.Long_Button)]
                screen.blit(self.clicked_img, [self.pos.x, self.pos.y - 2])
            else:
                screen.blit(self.base, self.pos)
                
        ##########################################################################################

    class Profile(Top_Button): #stats and skill tree
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "profile", pos, y_transition_offset)

    class Stats_Select(Long_Button):
        def __init__(self, parent, pos, x_transition_offset=0):
            super().__init__(parent, "stats_select", pos, x_transition_offset)

    class SkillTree_Select(Long_Button):
        def __init__(self, parent, pos, x_transition_offset=0):
            super().__init__(parent, "skilltree_select", pos, x_transition_offset)

        ##########################################################################################

    class Inventory(Top_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "inventory", pos, y_transition_offset)

    class Item_Bottom_Button(pygame.sprite.Sprite):
        def __init__(self, parent, name, pos, y_transition_offset):
            super().__init__()
            self.parent = parent
            self.name = name

            self.base = pygame.image.load(f"assets/gui/item_{name}.png")#.convert_alpha()
            self.base = pygame.transform.scale(self.base, vec(self.base.get_size())*2)
            self.base.set_colorkey((0, 0, 0))
            self.clicked_img = pygame.image.load(f"assets/gui/item_{name}_clicked.png")#.convert_alpha()
            self.clicked_img = pygame.transform.scale(self.clicked_img, vec(self.clicked_img.get_size())*2)
            self.clicked_img.set_colorkey((0, 0, 0))

            self.pos = vec(pos[0], pos[1]+self.base.get_height()*1.5)
            self.end_positions = [pos, [pos[0], pos[1]-26+8]]
            self.end_pos = self.end_positions[0]
            self.move_timer = Timer(y_transition_offset, 1)

            self.rect = self.base.get_rect(topleft=self.end_pos)
            self.mask = pygame.mask.from_surface(self.base)
            self.clicked = False
            self.held = False

        def reset(self):
            self.pos = vec(self.end_positions[0])
            self.switch_end_pos(0)
            self.move_timer.reset()

        def switch_end_pos(self, index:int = 0):
            self.end_pos = self.end_positions[index]

        def update(self, screen):
            if abs(self.end_pos[1] - self.pos[1]) > 0:
                self.move_timer.update()
                if self.move_timer.finished:
                    self.pos = self.pos.lerp(self.end_pos, 0.15)

            mousePos = pygame.mouse.get_pos()
            mousePos_masked = mousePos[0] - self.end_pos[0], mousePos[1] - self.end_pos[1]
            mouse = pygame.mouse.get_pressed()


            def mask_collide(pos):
                try: return self.mask.get_at(pos)
                except IndexError: False
                
            if (self.rect.collidepoint(mousePos) and mask_collide(mousePos_masked)) or self.clicked:
                if mouse[0]:
                    self.clicked = True
                    self.switch_end_pos(1)
                    [setattr(button, "clicked", False) for button in self.parent.item_buttons if isinstance(button, Player_Menu.Item_Bottom_Button) and button != self]
                    [button.switch_end_pos(0) for button in self.parent.item_buttons if isinstance(button, Player_Menu.Item_Bottom_Button) and button != self]
                screen.blit(self.clicked_img, [self.pos.x, self.pos.y - 2])
            else:
                screen.blit(self.base, self.pos)

    class Item_Card(pygame.sprite.Sprite):
        def __init__(self, parent, item, pos, x_transition_offset):
            super().__init__()
            self.parent = parent
            self.item = item
            self.item_mask = pygame.Surface((self.item.image.get_size()), pygame.SRCALPHA)
            pygame.draw.polygon(self.item_mask, (41, 39, 62), pygame.mask.from_surface(self.item.image).outline())

            self.font = Custom_Font.Fluffy
            width = self.font.calc_surf_width(self.item.name.capitalize())
            height = self.font.space_height

            self.name_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            self.font.render(self.name_surf, self.item.name.capitalize(), (210, 210, 210), (0, 0))
            self.name_surf_clicked = pygame.Surface((width, height), pygame.SRCALPHA)
            self.font.render(self.name_surf_clicked, self.item.name.capitalize(), (65, 243, 252), (0, 0))

            self.name_surf_hidden = pygame.Surface((width, height), pygame.SRCALPHA)
            self.font.render(self.name_surf_hidden, self.item.name.capitalize(), (41, 39, 62), (0, 0))
            self.name_surf_clicked_hidden = pygame.Surface((width, height), pygame.SRCALPHA)
            self.font.render(self.name_surf_clicked_hidden, self.item.name.capitalize(), (19, 178, 242), (0, 0))

            
            self.base = pygame.image.load("assets/gui/item_card.png").convert_alpha()
            self.base = pygame.transform.scale(self.base, vec(self.base.get_size())*2.2)
            self.base.set_colorkey((0, 0, 0))
            self.clicked_img = pygame.image.load("assets/gui/item_card_clicked.png").convert_alpha()
            self.clicked_img = pygame.transform.scale(self.clicked_img, vec(self.clicked_img.get_size())*2.2)
            self.clicked_img.set_colorkey((0, 0, 0))

            self.pos = vec(pos[0]-self.base.get_height()*2.5, pos[1])
            self.end_pos = pos
            self.move_timer = Timer(x_transition_offset, 1)

            self.rect = self.base.get_rect(topleft=self.end_pos)
            self.mask = pygame.mask.from_surface(self.base)
            self.clicked = False
            self.held = False

            self.info_card_display = Player_Menu.Item_Info_Card(item)

            self.bolt = Lightning.GUI_Spinner([
                (self.rect.topleft[0] + 24, self.rect.topleft[1] + 2), 
                (self.rect.topright[0] - 11, self.rect.topright[1] + 2), 
                (self.rect.bottomright[0] - 26, self.rect.bottomright[1] - 10),
                (self.rect.bottomleft[0] + 7, self.rect.bottomleft[1] - 10), 
            ], colours=[(65, 243, 252), (19, 178, 242)], line_width=3)

        def reset(self):
            self.pos = vec(self.end_pos[0]-self.base.get_height()*2.5, self.end_pos[1])
            self.move_timer.reset()
            self.clicked = False

        def info_card(self, screen, old):
            if old:
                self.info_card_display.reset()
            self.info_card_display.update(screen)

        def update(self, screen, alpha, y_scroll=0):
            if abs(self.end_pos[0] - self.pos[0]) > 0:
                self.move_timer.update()
                if self.move_timer.finished:
                    self.pos = self.pos.lerp(self.end_pos, 0.15)

            mousePos = pygame.mouse.get_pos()
            mousePos_masked = mousePos[0] - self.end_pos[0], mousePos[1] - self.end_pos[1] - y_scroll
            mouse = pygame.mouse.get_pressed()

            # update collision rect with y offset
            collision_rect = self.rect.copy()
            collision_rect.y += y_scroll
            
            def mask_collide(pos):
                try: return self.mask.get_at(pos)
                except IndexError: False
                
            if ((collision_rect.collidepoint(mousePos) and mask_collide(mousePos_masked)) or self.clicked) and alpha == 255:
                old = False
                if mouse[0]:
                    for key in ["weapons", "armour", "consumables", "key"]:
                        for button in self.parent[key].sprites():
                            button.clicked = False
                    old = True
                    self.clicked = True
                screen.blit(self.clicked_img, [self.pos.x, self.pos.y - 2 + y_scroll])
                
                item_img = self.item.image.copy()
                rect = item_img.get_rect(midtop=(self.pos.x + 36, self.pos.y - 2 + y_scroll + 8))
                screen.blit(self.item_mask, rect.topleft + vec(1,1))
                screen.blit(item_img, rect)

                screen.blit(self.name_surf_clicked_hidden, (self.pos.x+56+1, self.pos.y - 2 + y_scroll + 12+1))
                screen.blit(self.name_surf_clicked, (self.pos.x+56, self.pos.y - 2 + y_scroll + 12))

                if self.clicked:
                    self.bolt.update(screen, y_scroll)
                    self.info_card(screen, old)

            else:
                item_img = self.item.image.copy()
                item_mask = self.item_mask.copy()
                base = self.base.copy()
                name_surf = self.name_surf.copy()
                name_surf_hidden = self.name_surf_hidden.copy()
                if alpha < 255:
                    item_img.set_alpha(alpha)
                    item_mask.set_alpha(alpha)
                    base.set_alpha(alpha)
                    name_surf.set_alpha(alpha)
                    name_surf_hidden.set_alpha(alpha)
                screen.blit(base, self.pos + vec(0, y_scroll))
                
                rect = item_img.get_rect(midtop=(self.pos.x + 36, self.pos.y + y_scroll + 8))
                screen.blit(item_mask, rect.topleft + vec(1,1))
                screen.blit(item_img, rect)

                screen.blit(name_surf_hidden, (self.pos.x+56+1, self.pos.y+ y_scroll + 12+1))
                screen.blit(name_surf, (self.pos.x+56, self.pos.y+ y_scroll + 12))

    class Item_Card_Display(pygame.sprite.Sprite):
        def __init__(self, parent, pos):
            super().__init__()
            self.parent = parent
            self.inventory = self.parent.parent.inventory

            self.pos = pos
            self.y_scroll = 0
            self.true_y_scroll = 0
            self.scroll_speed = 5
            self.item_cards = {key: pygame.sprite.Group() for key in ["weapons", "armour", "consumables", "key"]}
            self.added_items = set()

            self.last_check = "weapons"

        def update_cards(self):
            for i, item in enumerate(self.inventory.data):
                if item not in self.added_items:
                    card = Player_Menu.Item_Card(self.item_cards, item, (self.pos[0], self.pos[1]+(i*50)), (i+1)*2)
                    self.item_cards[item.type].add(card)
                    self.added_items.add(item)

        def scroll(self):
            mousewhl_events = list(filter(lambda e:e.type == pygame.MOUSEWHEEL, self.parent.parent.game.events))
            if len(mousewhl_events) == 0: return

            self.y_scroll += mousewhl_events[0].y * self.scroll_speed
            if self.y_scroll > 0:
                self.y_scroll = 0
            # self.true_y_scroll = lerp

        def update(self, screen, to_check):
            if self.last_check != to_check:
                for card in self.item_cards[self.last_check]:
                    card.reset()
                self.y_scroll = 0
                self.last_check = to_check

            self.update_cards()
            self.scroll()
            for card in self.item_cards[to_check]:
                alpha = 255
                if (card.pos.y + self.y_scroll) < self.pos[1]:
                    dist = max(card.base.get_height()/2 - abs(card.pos.y + self.y_scroll - self.pos[1]), 0)
                    alpha = (dist / card.base.get_height()/2) * 255
                elif (card.pos.y + self.y_scroll) > (self.pos[1] + 225):
                    dist = max(card.base.get_height() / 2 - abs(card.pos.y + self.y_scroll - (self.pos[1] + 225)), 0)
                    alpha = (dist / (card.base.get_height() / 2)) * 255
                card.update(screen, alpha, self.y_scroll)

    class Item_Info_Card(pygame.sprite.Sprite):
        def __init__(self, item):
            super().__init__()
            self.item = item
            self.pos = vec(WIDTH/2 + 30, 90)

            self.image = pygame.image.load(f"assets/inventory_items/{item.name}.png").convert_alpha()
            self.image.set_colorkey((0, 0, 0))
            (42, 42)

            self.line_start = vec(
                self.pos.x + 60, 
                self.pos.y + Custom_Font.FluffyBig.space_height + 10
            )
            self.line_end = vec(
                self.pos.x + 60 + Custom_Font.FluffyBig.calc_surf_width(self.item.name.capitalize())//5,
                self.pos.y + Custom_Font.FluffyBig.space_height + 10
            )
            self.line_end_target = vec(
                self.pos.x + 60 + Custom_Font.FluffyBig.calc_surf_width(self.item.name.capitalize()) * 1.2, 
                self.pos.y + Custom_Font.FluffyBig.space_height + 10
            )

            self.desc = Text_Box(
                ITEM_DESCRIPTIONS[self.item.name.lower()]["text"], 
                (self.pos.x+2, self.pos.y+60), 
                Custom_Font.FluffySmall, 
                speed=1,
                typing_sounds_flag=False
            )

        def reset(self):
            self.line_end = vec(
                self.pos.x + 60 + Custom_Font.FluffyBig.calc_surf_width(self.item.name.capitalize())//5,
                self.pos.y + Custom_Font.FluffyBig.space_height + 10
            )
            self.desc.reset()

        def update(self, screen):
            pygame.draw.rect(screen, (210, 210, 210), [self.pos.x-2, self.pos.y-2, 46, 46], 2)
            screen.blit(self.image, self.image.get_rect(center=(self.pos.x+21, self.pos.y+21)))

            Custom_Font.FluffyBig.render(screen, self.item.name.capitalize(), (210, 210, 210), (self.pos.x + 60, self.pos.y + 10))
            pygame.draw.line(screen, (250, 250, 250), self.line_start, self.line_end, 3)
            self.line_end = self.line_end.lerp(self.line_end_target, 0.3)

            self.desc.update()
            self.desc.render(screen, (200, 200, 200))
            # Custom_Font.FluffySmall.render(screen, ITEM_DESCRIPTIONS[self.item.name.lower()]["text"], (200, 200, 200), (self.pos.x+2, self.pos.y+60))

    class Weapons(Item_Bottom_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "weapons", pos, y_transition_offset)
            self.type = "weapons"

    class Armour(Item_Bottom_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "armour", pos, y_transition_offset)
            self.type = "armour"

    class Consumables(Item_Bottom_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "consumables", pos, y_transition_offset)
            self.type = "consumables"

    class Key_Items(Item_Bottom_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "key", pos, y_transition_offset)
            self.type = "key"

        ##########################################################################################

    class QuestBook(Top_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "questbook", pos, y_transition_offset)

        ##########################################################################################

    class Map(Top_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "map", pos, y_transition_offset)

    class Waypoint_Map:
        def __init__(self):
            self.bg = Starry_Background()

        def update(self, screen):
            self.bg.update(screen)

        ##########################################################################################

    class Settings(Top_Button):
        def __init__(self, parent, pos, y_transition_offset=0):
            super().__init__(parent, "settings", pos, y_transition_offset)

    class Settings_Case(pygame.sprite.Sprite):
        def __init__(self, parent, pos):
            super().__init__()
            self.parent = parent
            self.pos = pos

            self.base = pygame.image.load("assets/gui/settings_case.png").convert_alpha()
            self.base = pygame.transform.scale(self.base, vec(self.base.get_size())*3)
            self.base.set_colorkey((0, 0, 0))

            self.pos = vec(pos[0]+self.base.get_width()*2.5, pos[1])
            self.end_pos = pos

            self.buttons = pygame.sprite.Group()
            self.buttons.add(Player_Menu.Volume_Slider(self.buttons, self.parent.parent.game.music_player, [
                self.end_pos[0] + self.base.get_width() - 80*3 - 24, 
                self.end_pos[1] + self.base.get_height() - 16*3
            ]))

        def update(self, screen):
            if abs(self.end_pos[0] - self.pos[0]) > 0:
                self.pos = self.pos.lerp(self.end_pos, 0.15)

            screen.blit(self.base, self.pos)
            self.buttons.update(screen)

    class Volume_Slider(pygame.sprite.Sprite):
        def __init__(self, parent, mixer, pos):
            super().__init__()
            self.parent = parent
            self.mixer = mixer
            self.pos = pos

            self.base = pygame.Surface((72, 7), pygame.SRCALPHA)
            self.base.fill((20, 16, 32))
            self.base.fill((39, 37, 60), [0, 0, 72, 2])
            self.base = pygame.transform.scale(self.base, vec(self.base.get_size()) * 3)
            pygame.draw.rect(self.base, (1, 0, 0), self.base.get_rect(), 3)

            self.knob = Player_Menu.Volume_Knob(self, self.mixer, 
                                                [self.pos[0] + 3, self.pos[1] - 6], 
                                                [self.pos[0] + self.base.get_width() - 33 - 3, self.pos[1] - 6])

        def update(self, screen):
            screen.blit(self.base, self.pos)

            pygame.draw.rect(screen, [17, 158, 214], [self.pos[0] + 3, self.pos[1] + 3, int(self.knob.pos.x - self.knob.start.x), 3])
            pygame.draw.rect(screen, [65, 243, 252], [self.pos[0] + 3, self.pos[1] + 6, int(self.knob.pos.x - self.knob.start.x), 12])

            vol = str(int(self.mixer.volumes[0] * 100))
            Custom_Font.Fluffy.render(screen, str(vol), (41, 39, 62), [self.pos[0] + self.base.get_width() + 11, self.pos[1] + 5])
            Custom_Font.Fluffy.render(screen, str(vol), (210, 210, 210), [self.pos[0] + self.base.get_width() + 10, self.pos[1] + 4])

            Custom_Font.Fluffy.render(screen, "Music:", (41, 39, 62), [self.pos[0] - Custom_Font.Fluffy.calc_surf_width("Music:") - 4, self.pos[1] + 5])
            Custom_Font.Fluffy.render(screen, "Music:", (210, 210, 210), [self.pos[0] - Custom_Font.Fluffy.calc_surf_width("Music:") - 5, self.pos[1] + 4])

            self.knob.update(screen)

    class Volume_Knob(pygame.sprite.Sprite):
        def __init__(self, parent, mixer, start, end):
            super().__init__()
            self.parent = parent
            self.mixer = mixer

            self.start = vec(start)
            self.end = vec(end)
            self.pos = vec(end)

            self.base = pygame.Surface((14-3, 14-3), pygame.SRCALPHA)
            self.base.fill((57, 58, 74))
            pygame.draw.rect(self.base, (1, 0, 0), self.base.get_rect(), 1)
            pygame.draw.line(self.base, (20, 16, 32), [2, 2], [2, 11-3])
            pygame.draw.line(self.base, (20, 16, 32), [11-3, 2], [11-3, 11-3])
            pygame.draw.line(self.base, (30, 23, 48), [3, 2], [10-3, 2])
            pygame.draw.line(self.base, (30, 23, 48), [3, 11-3], [10-3, 11-3])
            self.base = pygame.transform.scale(self.base, vec(self.base.get_size())*3)

            self.held = False

        def clamp_pos(self):
            if self.pos.x < self.start.x:
                self.pos.x = self.start.x
            if self.pos.x > self.end.x:
                self.pos.x = self.end.x

        def change_volume(self):
            dist = abs(self.start.x - self.pos.x)
            vol = dist / (self.end.x - self.start.x)
            self.mixer.set_vol(vol, "bg")

        def move(self):
            mouse = pygame.mouse.get_pressed()
            mousePos = pygame.mouse.get_pos()

            if mouse[0]:
                if self.held == False:
                    if self.base.get_rect(topleft=self.pos).collidepoint(mousePos):
                        self.held = True
                else:
                    self.pos.x = mousePos[0] - self.base.get_width()/2
                    self.clamp_pos()
                    self.change_volume()
            else:
                self.held = False

        def update(self, screen):
            self.move()

            screen.blit(self.base, self.pos)
            if self.base.get_rect(topleft=self.pos).collidepoint(pygame.mouse.get_pos()) or self.held:
                pygame.draw.rect(screen, [65, 243, 252], [self.pos.x + 6, self.pos.y + 6, 3, 21])
                pygame.draw.rect(screen, [65, 243, 252], [self.pos.x + self.base.get_width() - 9, self.pos.y + 6, 3, 21])
                pygame.draw.rect(screen, [17, 158, 214], [self.pos.x + 6, self.pos.y + 6, 21, 3])
                pygame.draw.rect(screen, [17, 158, 214], [self.pos.x + 6, self.pos.y + self.base.get_height() - 9, 21, 3])