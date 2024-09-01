#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import argparse

# Parse arguments
ap = argparse.ArgumentParser(description="Plot results from CSV file with merged technical replicates and smoothed data.")
ap.add_argument("-f", "--file", required=True, type=str, help="Path to the CSV file")
ap.add_argument("-s", "--seconds", required=True, type=int, help="Duration in seconds to average over")
args = ap.parse_args()

# Convert seconds to frames (30 frames per second)
window_size = args.seconds * 30
print(f"Rolling window size in frames: {window_size}")

# Read the CSV file
df = pd.read_csv(args.file, delimiter='\t')

# Merge technical replicates for each tank and rename the categories
df['tank'] = df['tank'].replace({
    'right_tank1': 'tank1',
    'left_tank1': 'tank1',
    'right_tank2': 'tank2',
    'left_tank2': 'tank2',
    'right_tank3': 'tank3',
    'left_tank3': 'tank3'
})

# Convert 'frame' to numeric
df['frame'] = pd.to_numeric(df['frame'], errors='coerce')

# Ensure 'frame' is sorted
df = df.sort_values(by=['frame'])

# Group by frame and tank to count pulses per frame
df_counts = df.groupby(['frame', 'tank']).size().reset_index(name='pulse_count')

# Apply a rolling mean to get the average number of pulses over the specified window size in frames
df_counts['rolling_avg'] = df_counts.groupby('tank')['pulse_count'].transform(
    lambda x: x.rolling(window=window_size, min_periods=1).mean()
)

# Convert to numpy arrays for plotting
frames = df_counts['frame'].to_numpy()
rolling_avg_counts = df_counts['rolling_avg'].to_numpy()
tanks = df_counts['tank'].to_numpy()

# Determine the maximum frame value
max_frame = df_counts['frame'].max()
print(f"Max frame value in the dataset: {max_frame}")

# Plotting using matplotlib
plt.figure(figsize=(10, 6))

# Define more distinct color palette
palette = {'tank1': '#e41a1c',  # red
           'tank2': '#377eb8',  # blue
           'tank3': '#4daf4a'}  # green

# Plot each tank separately
for tank in set(tanks):
    # Filter data for each tank
    filtered_data = df_counts[df_counts['tank'] == tank]
    # Convert columns to numpy arrays to avoid multi-dimensional indexing issues
    tank_frames = filtered_data['frame'].to_numpy()
    tank_rolling_avg = filtered_data['rolling_avg'].to_numpy()
    
    # Plot the data for the tank
    plt.plot(tank_frames, tank_rolling_avg, label=tank, color=palette[tank])

# Customize the plot
plt.title(f"Rolling Average of Pulses Over Time (Window Size = {args.seconds} Seconds)")
plt.xlabel("Frame")
plt.ylabel("Average Number of Pulses")
plt.xlim([0, max_frame])  # Set x-axis limits to the maximum frame value
plt.legend(title="Tank")
plt.grid(True)

# Show the plot
plt.show()

