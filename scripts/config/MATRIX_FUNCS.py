import numpy as np
import math

    ##############################################################################################

class MatrixFunctions:

    PROJECTION_MATRIX = [[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 0]]
    
    def multiply_matrix(a, b):
        return np.dot(a, b)
    
    def rotate_x(angle):
        return np.array([
            [1, 0, 0],
            [0, math.cos(angle), math.sin(angle)],
            [0, -math.sin(angle), math.cos(angle)],
        ])

    def rotate_y(angle):
        return np.array([
            [math.cos(angle), 0, -math.sin(angle)],
            [0, 1, 0],
            [math.sin(angle), 0, math.cos(angle)],
        ])

    def rotate_z(angle):
        return np.array([
            [math.cos(angle), math.sin(angle), 0],
            [-math.sin(angle), math.cos(angle), 0],
            [0, 0, 1],
        ])