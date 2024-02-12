import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

# Number of points
num_points = 5000

# Generate x values from 0 to 2*pi
x_values = np.linspace(0, 2*np.pi, num_points)

# Calculate sine values for each x
sin_values = np.sin(x_values)

# Create a DataFrame
df = pd.DataFrame({'x': x_values, 'sin(x)': sin_values})

# Save DataFrame to Excel
df.to_excel('data_points.xlsx', index=False)

plt.plot(x_values, sin_values)
plt.title('Sine Function')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True)
plt.show()
