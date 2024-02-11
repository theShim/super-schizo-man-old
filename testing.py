import matplotlib.pyplot as plt
import numpy as np

# Define the list of pairs
data_pairs = [(1, 1), (2, 9), (2, 0), (2, 0)]

# Extract x-values and y-values from the list of pairs
x_values, y_values = zip(*data_pairs)

# Create a scatter plot
plt.scatter(x_values, y_values, label='Data Points')

# Fit a linear trend line (polynomial of degree 1) to the data
trend_coefficients = np.polyfit(x_values, y_values, 1)
trend_line = np.poly1d(trend_coefficients)

# Generate x values for the trend line
trend_x = np.linspace(min(x_values), max(x_values), 100)
# Calculate corresponding y values for the trend line
trend_y = trend_line(trend_x)

# Plot the trend line
plt.plot(trend_x, trend_y, color='red', linestyle='--', label='Trend Line')
# Calculate and print correlation coefficient
correlation_coefficient = np.corrcoef(x_values, y_values)[0, 1]
print(f"Correlation Coefficient: {correlation_coefficient}")

# Add labels and legend
plt.xlabel('X Values')
plt.ylabel('Y Values')
plt.legend()

# Show plot
plt.show()
