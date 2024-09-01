#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse

# Parse arguments
ap = argparse.ArgumentParser(description="Plot results from CSV file.")
ap.add_argument("-f", "--file", required=True, type=str, help="Path to the CSV file")
args = ap.parse_args()

# Read the CSV file
df = pd.read_csv(args.file, delimiter='\t')

# Filter out rows where 'tank' is 'noise'
df = df[df['tank'] != 'noise']

# Define custom color palette for left and right tanks
custom_palette = {
    'left_tank1': '#1f77b4',  # light blue
    'left_tank2': '#0077bb',  # medium blue
    'left_tank3': '#004488',  # dark blue
    'right_tank1': '#ff7f0e',  # light orange
    'right_tank2': '#d62728',  # medium orange
    'right_tank3': '#8c564b'   # dark orange
}

# Set the style for seaborn
sns.set(style="whitegrid")

# Create the plot
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x="frame", y="cXtank", hue="tank", palette=custom_palette, s=100)

# Customize the plot
plt.title("Frame vs cX Colored by Tank")
plt.xlabel("Frame")
plt.ylabel("cX")
plt.legend(title="Tank")
plt.grid(True)

# Show the plot
plt.show()

