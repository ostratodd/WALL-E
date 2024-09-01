import pandas as pd
import matplotlib.pyplot as plt
import argparse

# Set up the argument parser
ap = argparse.ArgumentParser(description="Plot frame vs cX from CSV file")
ap.add_argument("-f", "--file", required=True, type=str, help="Path to the CSV file")
args = vars(ap.parse_args())

# Load the CSV file into a DataFrame
data = pd.read_csv(args['file'], delimiter='\t')

# Convert columns to numpy arrays before plotting
frame = data['frame'].to_numpy()
cX = data['cX'].to_numpy()

# Plot the data as individual points
plt.scatter(frame, cX, marker='o', s=5)
plt.xlabel('Frame')
plt.ylabel('cX')
plt.title('Frame vs. cX')
plt.grid(True)
plt.show()

