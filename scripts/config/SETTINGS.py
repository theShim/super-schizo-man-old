import pygame

    ##############################################################################################

DEBUG = not True
WINDOW_TITLE = "Super Schizo Man"
LOADED_SPRITE_NUMBER = 0
MAX_LOADED_SPRITES = 181

    ##############################################################################################

SIZE = (WIDTH, HEIGHT) = 1280//2, 800//2
SCREEN_CENTER = (WIDTH/2, HEIGHT/2)

FPS = 46
CAMERA_FOLLOW_SPEED = 12

    ##############################################################################################

#   PHYSICS
FRIC = 0.9
GRAV = 0.4

ENVIRONMENT_SETTINGS = {
    "rain" : True,
    "wind" : -2
}

    ##############################################################################################
    
TILE_SIZE = 24
Z_LAYERS = {
    "background offgrid" : 4,
    "background particle" : 5,
    "player" : 6,
    "partner" : 6.5,
    "items" : 7,
    "midground offgrid" : 8,
    "tiles" : 9,
    "attacks": 10, 
    "foreground offgrid" : 11,
    "foreground particle" : 12
}
    ##############################################################################################

CONTROLS = {
    "up"        : pygame.K_w,
    "down"      : pygame.K_s,
    "left"      : pygame.K_a,
    "right"     : pygame.K_d,
    "jump"      : pygame.K_SPACE,

    "heavy"     : pygame.K_h,
    "light"     : pygame.K_j,
    "dash"      : pygame.K_l,
    "switch_l"  : pygame.K_i,
    "switch_r"  : pygame.K_o,

    "menu_open" : pygame.K_ESCAPE,
    "inv_open"  : pygame.K_e,
}
# reminder: enable "up key toggle" for jump option in settings later