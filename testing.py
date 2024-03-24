import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Define the circle equation
def circle_equation(x):
    return np.sqrt(4 - x**2)

# Rotation function
def rotate_circle_around_x_axis(angle):
    # Define the rotation matrix around x-axis
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(angle), -np.sin(angle)],
                   [0, np.sin(angle), np.cos(angle)]])
    
    # Generate points on the circle
    x = np.linspace(-2, 2, 20)
    y = circle_equation(x)
    
    # Rotate each point
    rotated_points = np.dot(Rx, np.vstack([x, y, np.zeros_like(x)]))
    
    return rotated_points[0], rotated_points[1], rotated_points[2]

# Function to update plot for each frame of the animation
def update_plot(frame):
    ax.clear()

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-2, 2)
    
    # Original circle
    x_original = np.linspace(-2, 2, 100)
    y_original = circle_equation(x_original)
    ax.plot(x_original, y_original, np.zeros_like(x_original), label='Original Circle', color='b')
    
    # Rotated circle
    angle = (frame / frames) * (2 * np.pi)
    x_rotated, y_rotated, z_rotated = rotate_circle_around_x_axis(angle)
    ax.plot(x_rotated, y_rotated, z_rotated, label='Rotated Circle', color='r')

    angle = ((frame + (frames/2)) / frames) * (2 * np.pi)
    x_rotated, y_rotated, z_rotated = rotate_circle_around_x_axis(angle)
    ax.plot(x_rotated, y_rotated, z_rotated, label='Rotated Circle', color='r')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'Rotation around X-axis by {angle:.2f} radians')
    ax.legend()

# Create a figure and axes
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Number of frames for the animation
frames = 360//4

# Animate the rotation
ani = FuncAnimation(fig, update_plot, frames=frames, interval=50)

plt.show()


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def icosphere(radius, subdivisions=1):
    # Define icosahedron vertices
    phi = (1 + np.sqrt(5)) / 2
    vertices = np.array([
        [-1, phi, 0],
        [1, phi, 0],
        [-1, -phi, 0],
        [1, -phi, 0],
        [0, -1, phi],
        [0, 1, phi],
        [0, -1, -phi],
        [0, 1, -phi],
        [phi, 0, -1],
        [phi, 0, 1],
        [-phi, 0, -1],
        [-phi, 0, 1]
    ])

    # Normalize vertices
    vertices /= np.linalg.norm(vertices, axis=1)[:, np.newaxis]

    # Define icosahedron faces
    faces = np.array([
        [0, 11, 5],
        [0, 5, 1],
        [0, 1, 7],
        [0, 7, 10],
        [0, 10, 11],
        [1, 5, 9],
        [5, 11, 4],
        [11, 10, 2],
        [10, 7, 6],
        [7, 1, 8],
        [3, 9, 4],
        [3, 4, 2],
        [3, 2, 6],
        [3, 6, 8],
        [3, 8, 9],
        [4, 9, 5],
        [2, 4, 11],
        [6, 2, 10],
        [8, 6, 7],
        [9, 8, 1]
    ])

    # Subdivide faces
    for _ in range(subdivisions):
        new_faces = []
        for face in faces:
            v0, v1, v2 = vertices[face]
            v01 = (v0 + v1) / 2
            v12 = (v1 + v2) / 2
            v20 = (v2 + v0) / 2

            v01 /= np.linalg.norm(v01)
            v12 /= np.linalg.norm(v12)
            v20 /= np.linalg.norm(v20)

            v_idx = len(vertices)
            vertices = np.vstack([vertices, v01, v12, v20])

            new_faces.append([face[0], v_idx - 2, v_idx])
            new_faces.append([face[1], v_idx - 1, v_idx])
            new_faces.append([face[2], v_idx, v_idx - 2])

        faces = np.array(new_faces)

    # Scale vertices
    vertices *= radius

    return vertices, faces

# Generate icosphere vertices and faces
vertices, faces = icosphere(radius=1, subdivisions=1)

# Plotting
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot vertices
ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], color='b')

# Plot faces
for face in faces:
    v0, v1, v2 = vertices[face]
    ax.plot([v0[0], v1[0], v2[0], v0[0]], 
            [v0[1], v1[1], v2[1], v0[1]], 
            [v0[2], v1[2], v2[2], v0[2]], 'k-')

# Set equal aspect ratio
ax.set_box_aspect([1,1,1])

plt.title('Icosphere')
plt.show()
