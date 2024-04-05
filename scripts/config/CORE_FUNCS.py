import pygame
import math
import random
import json
import io 
from PIL import Image, ImageFilter

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
                print(file)
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    total_lines += len(lines)

                    uncommented_total += len(list(filter(lambda l:l[0] != "#", filter(lambda l: len(l), map(lambda l: l.strip(), lines)))))
    print(f"Total Lines: {total_lines} | Uncommented: {uncommented_total}")