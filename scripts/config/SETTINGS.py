import pygame

    ##############################################################################################

DEBUG = True
WINDOW_TITLE = "Super Schizo Man"
LOADED_SPRITE_NUMBER = 0
MAX_LOADED_SPRITES = 346

    ##############################################################################################

SIZE = (WIDTH, HEIGHT) = 640, 400
SCREEN_CENTER = (WIDTH/2, HEIGHT/2)

FPS = 60
CAMERA_FOLLOW_SPEED = 12

    ##############################################################################################

#   PHYSICS
FRIC = 0.9
GRAV = 20

ENVIRONMENT_SETTINGS: dict[str, bool | int] = {
    "rain" : False,
    "snow" : False,
    "cherry_blossom" : False,
    "wind" : -2
}

    ##############################################################################################
    
TILE_SIZE = 24
Z_LAYERS: dict[str , int] = {
    "background offgrid" : 4,
    "background particle" : 5,
    "player_dash" : 5.5,
    "player" : 6,
    "partner" : 6.5,
    "items" : 7,
    "midground offgrid" : 8,
    "tiles" : 9,
    "attacks": 10, 
    "foreground offgrid" : 11,
    "foreground particle" : 12,
    "in-game gui" : 14
}

"""
    A dictionary containing the z values for the order of sprite blitting.

    "background offgrid" : 4,
    "background particle" : 5,
    "player_dash" : 5.5,
    "player" : 6,
    "partner" : 6.5,
    "items" : 7,
    "midground offgrid" : 8,
    "tiles" : 9,
    "attacks": 10, 
    "foreground offgrid" : 11,
    "foreground particle" : 12,
    "in-game gui" : 14
"""
    ##############################################################################################

CONTROLS: dict[str, pygame.key.ScancodeWrapper] = {
    "up"        : pygame.K_w,
    "down"      : pygame.K_s,
    "left"      : pygame.K_a,
    "right"     : pygame.K_d,
    "jump"      : pygame.K_SPACE,

    "heavy"     : pygame.K_k, #might not use these + replace with mouse
    "light"     : pygame.K_j,
    "dash"      : pygame.K_l,
    "switch_l"  : pygame.K_u,
    "switch_r"  : pygame.K_i,
    #other buttons could be used h, u, r, c, f, n, m

    "menu_open" : pygame.K_ESCAPE,
    "inv_open"  : pygame.K_TAB,

    "pickup_item" : pygame.K_e,
}

"""
    A dictionary containing the key mappings for player controls.

    - "dash": space
    - "jump": w
"""

# reminder: enable "up key toggle" for jump option in settings later