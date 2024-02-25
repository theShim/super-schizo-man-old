

#class handler for entity animations
class SpriteAnimator:
    def __init__(self, sprites, loop=True, animation_speed=4):
        self.sprites = sprites
        self.animation_speed = animation_speed
        self.frame_index = 0
        self.finished = False
        self.loop = loop
            
    def copy(self):
        return SpriteAnimator(self.sprites, self.loop, self.animation_speed)

        ######################################################################################

    #restart the animation
    def reset_frame(self):
        self.frame_index = 0

    #updating the animation
    def next(self, dt=0):
        self.frame_index += self.animation_speed * dt

    #accessing the current sprite
    def get_sprite(self):
        try:
            return self.sprites[int(self.frame_index)]
        except IndexError:
            if self.loop:
                self.reset_frame()
                return self.sprites[self.frame_index]
            else:
                self.finished = True