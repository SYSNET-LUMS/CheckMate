import matplotlib.pyplot as plt
import pandas as pd

# Read data from CSV file
# Replace 'traces/RF_2.csv' with the actual filename
df = pd.read_csv('traces/RF_2.csv')

# Assuming the data column you want to plot is called 'Value'
# Replace 'Value' with the actual column name in your CSV
# If you're not sure about the column name, print df.head() to inspect the dataframe
data = df  # Replace 'Value' with your actual column name

# Create subplots
fig, axs = plt.subplots(2, 1, figsize=(10, 10))

# Plot all data points in the first subplot
axs[0].plot(data, 'o-', label='All data points')
axs[0].set_title('All Data Points')
axs[0].set_xlabel('Index')
axs[0].set_ylabel('Value')
axs[0].legend()

# Plot every 6th data point in the second subplot
every_6th_data = data[::6]
indices = list(range(0, len(data), 6))  # Create corresponding x indices for every 6th point

axs[1].plot(indices, every_6th_data, 'o-', label='Every 6th data point')
axs[1].set_title('Every 6th Data Point')
axs[1].set_xlabel('Index')
axs[1].set_ylabel('Value')
axs[1].legend()

# Adjust layout
plt.tight_layout()
plt.show()
