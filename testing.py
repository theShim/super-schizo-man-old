import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Data points
times = ['7:50', '15:21']
y_values = [39.4, 38.5]

# Convert times to datetime objects
x_values = []
for time in times:
    hours, minutes = map(int, time.split(':'))
    x_values.append(datetime(year=2024, month=1, day=1, hour=hours, minute=minutes))

# Plot the points
plt.scatter(x_values, y_values, label='Data Points')

# Calculate line of best fit
x_values_numeric = [(x - x_values[0]).total_seconds() / 3600 for x in x_values]  # Convert to numeric values (hours)
m, b = np.polyfit(x_values_numeric, y_values, 1)

# Find the x-value when y = 0
x_at_y0 = -b / m
if x_at_y0 >= 0:
    x_at_y0_time = x_values[0] + timedelta(hours=x_at_y0)
    plt.plot([x_values[0], x_at_y0_time], [y_values[0], 0], color='red', label='Line of Best Fit')
    plt.scatter(x_at_y0_time, 0, color='green', label='Interpolated Point (y = 0)')

# Plot the line of best fit up to the point where y = 37
x_at_37_numeric = (37 - b) / m
x_at_37_time = x_values[0] + timedelta(hours=x_at_37_numeric)
x_values_for_fit = np.linspace(x_values_numeric[0], x_at_37_numeric, 100)
y_values_for_fit = m * x_values_for_fit + b
plt.plot([x_values[0], x_at_37_time], [y_values[0], 37], color='red', linestyle='dashed')

# Plot the point where the line passes through y = 37
plt.scatter(x_at_37_time, 37, color='green')

# Add labels and legend
plt.xlabel('Time (24-hour format)')
plt.ylabel('Arbitrary Units')
plt.title('Graph with Line of Best Fit')
plt.legend()

# Show plot
plt.grid(True)
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))  # Set format for x-axis
plt.show()

# Print the interpolated times
if x_at_y0 >= 0:
    print("The time where y = 0 is approximately:", x_at_y0_time.strftime('%d'))
print("The time where y = 37 is approximately:", x_at_37_time.strftime('%d'))
