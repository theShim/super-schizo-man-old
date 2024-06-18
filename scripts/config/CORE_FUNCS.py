import pygame
import math
import random
import json
from PIL import Image, ImageFilter
import cv2
import typing
import numpy as np

    ##############################################################################################

#   RENAMING COMMON FUNCTIONS
vec = pygame.math.Vector2
vec3 = pygame.math.Vector3

    ##############################################################################################

#   GENERAL STUFF
def gen_rand_colour() -> tuple[float]:
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

def euclidean_distance(point1: list[float], point2: list[float]) -> float:
    return (((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2) ** 0.5)

def rotate(origin: list, point: list, angle: float) -> list[float]:
    ox, oy = origin
    px, py = point
    angle = math.radians(angle)

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]

def lerp(a: float, b: float, lerp_factor: float) -> float:
    return (lerp_factor * a) + ((1 - lerp_factor) * b)

def gaussian_blur(surf, radius=6):
    pil_image = Image.frombytes("RGBA", surf.get_size(), pygame.image.tostring(surf, "RGBA"))
    pil_blurred = pil_image.filter(ImageFilter.GaussianBlur(radius=radius))

    blurred_surface = pygame.image.fromstring(pil_blurred.tobytes(), pil_blurred.size, "RGBA")
    return blurred_surface

def normalize(val, amt, target):
    if val > target + amt:
        val -= amt
    elif val < target - amt:
        val += amt
    else:
        val = target
    return val

def warp(surf: pygame.Surface,
         warp_pts,
         smooth=True,
         out: pygame.Surface = None) -> typing.Tuple[pygame.Surface, pygame.Rect]:
    """Stretches a pygame surface to fill a quad using cv2's perspective warp.

        Args:
            surf: The surface to transform.
            warp_pts: A list of four xy coordinates representing the polygon to fill.
                Points should be specified in clockwise order starting from the top left.
            smooth: Whether to use linear interpolation for the image transformation.
                If false, nearest neighbor will be used.
            out: An optional surface to use for the final output. If None or not
                the correct size, a new surface will be made instead.

        Returns:
            [0]: A Surface containing the warped image.
            [1]: A Rect describing where to blit the output surface to make its coordinates
                match the input coordinates.
    """
    if len(warp_pts) != 4:
        raise ValueError("warp_pts must contain four points")

    w, h = surf.get_size()
    is_alpha = surf.get_flags() & pygame.SRCALPHA

    # XXX throughout this method we need to swap x and y coordinates
    # when we pass stuff between pygame and cv2. I'm not sure why .-.
    src_corners = np.float32([(0, 0), (0, w), (h, w), (h, 0)])
    quad = [tuple(reversed(p)) for p in warp_pts]

    # find the bounding box of warp points
    # (this gives the size and position of the final output surface).
    min_x, max_x = float('inf'), -float('inf')
    min_y, max_y = float('inf'), -float('inf')
    for p in quad:
        min_x, max_x = min(min_x, p[0]), max(max_x, p[0])
        min_y, max_y = min(min_y, p[1]), max(max_y, p[1])
    warp_bounding_box = pygame.Rect(int(min_x), int(min_y),
                                    int(max_x - min_x),
                                    int(max_y - min_y))

    shifted_quad = [(p[0] - min_x, p[1] - min_y) for p in quad]
    dst_corners = np.float32(shifted_quad)

    mat = cv2.getPerspectiveTransform(src_corners, dst_corners)

    orig_rgb = pygame.surfarray.pixels3d(surf)

    flags = cv2.INTER_LINEAR if smooth else cv2.INTER_NEAREST
    dsize = (int(warp_bounding_box.width), int(warp_bounding_box.height))
    out_rgb = cv2.warpPerspective(orig_rgb, mat, dsize, flags=flags)

    if out is None or out.get_size() != out_rgb.shape[0:2]:
        out = pygame.Surface(out_rgb.shape[0:2], pygame.SRCALPHA if is_alpha else 0)

    pygame.surfarray.blit_array(out, out_rgb)

    if is_alpha:
        orig_alpha = pygame.surfarray.pixels_alpha(surf)
        out_alpha = cv2.warpPerspective(orig_alpha, mat, dsize, flags=flags)
        alpha_px = pygame.surfarray.pixels_alpha(out)
        alpha_px[:] = out_alpha
    else:
        out.set_colorkey(surf.get_colorkey())

    # XXX swap x and y once again...
    return out, pygame.Rect(warp_bounding_box.y, warp_bounding_box.x,
                            warp_bounding_box.h, warp_bounding_box.w)

#bezier stuff
def ptOnCurve(b, t):
    q = b.copy()
    for k in range(1, len(b)):
        for i in range(len(b) - k):
            q[i] = (1-t) * q[i][0] + t * q[i+1][0], (1-t) * q[i][1] + t * q[i+1][1]
    return round(q[0][0]), round(q[0][1])

def bezierfy(points, samples): #no idea how this works just does, i think it's just recursive lerping though
    pts = [ptOnCurve(points, i/samples) for i in range(samples+1)]
    return pts

    ##############################################################################################

#   FILE STUFF
def read_file(path):
    file = open(path)
    data = file.readlines()
    file.close()
    return data

def write_file(path, data):
    file = open(path)
    file.write(data + '\n')
    file.close()


def read_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def write_json(path, dict):
    with open(path, 'w') as json_file:
        json.dump(dict, json_file)

    ##############################################################################################
    
class QuitWindow(BaseException):
    def __init__(self):
        super().__init__()

    ##############################################################################################
        
class Timer:
    def __init__(self, duration: float, speed: float):
        self.t = 0
        self.end = duration
        self.speed = speed
        self.finished = False

        self.run = True

    #turn on/off
    def switch(self, flag:bool=None):
        if flag != None: 
            self.run = flag
        else: 
            self.run = not self.run

    def reset(self):
        self.t = 0
        self.finished = False

    def change_speed(self, speed: float|int):
        self.speed = speed

    def update(self):
        if self.run:
            if self.t < self.end:
                self.t += self.speed
            else:
                self.finished = True

    ##############################################################################################

#counting total number of lines written in the directory
import os                
def countLinesIn(directory):
    total_lines = 0
    uncommented_total = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    uncommented_total += len(list(filter(lambda l:l[0] != "#", filter(lambda l: len(l), map(lambda l: l.strip(), lines)))))
    print(f"Total Lines: {total_lines} | Uncommented: {uncommented_total}")