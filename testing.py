import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.offsetbox import OffsetImage
import numpy as np

# Load your PNG images
image_files = [f'assets/worlds/Sky/bg-{i}.png' for i in range(5)]

# Create a 3D scatter plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Coordinates for the images
x = np.arange(len(image_files))
y = np.zeros(len(image_files))
z = np.zeros(len(image_files))

# Plot the images
for i, image_file in enumerate(image_files):
    img = plt.imread(image_file)
    ab = OffsetImage(img, zoom=0.5)
    ab.image.axes = ax
    ax.add_artist(ab)
    ab.set_offset((x[i], y[i]))
    ab.set_zorder(i)

# Set plot limits and labels
ax.set_xlim(0, len(image_files))
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Rotate the plot
ax.view_init(elev=80, azim=40)

# Hide axes
ax.set_axis_off()

plt.show()
