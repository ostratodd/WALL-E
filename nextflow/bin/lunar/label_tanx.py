#!/usr/bin/env python3

import pandas as pd
import argparse
import numpy as np

# Function to determine camera based on cX
def determine_camera(cX):
    return 'left' if cX < 2001 else 'right'

# Function to determine tank based on cX and tank boundaries
def determine_tank(cX, boundaries):
    t1, t2, t3, t4, t5, t6, t7, t8 = boundaries
    
    if cX < t1:
        return 'noise'  # cX is less than the first tank boundary, considered noise
    elif t1 <= cX < t2:
        return 'left_tank1'
    elif t2 <= cX < t3:
        return 'left_tank2'
    elif t3 <= cX < t4:
        return 'left_tank3'
    elif t4 <= cX < t5:
        return 'noise'  # Noise area between left and right tanks
    elif t5 <= cX < t6:
        return 'right_tank1'
    elif t6 <= cX < t7:
        return 'right_tank2'
    elif t7 <= cX <= t8:
        return 'right_tank3'
    else:
        return 'noise'  # Any other values are considered noise

# Function to calculate cXtank based on the tank and boundaries
def calculate_cXtank(cX, tank, boundaries):
    t1, t2, t3, t4, t5, t6, t7, t8 = boundaries
    if tank == 'left_tank1':
        return cX - t1
    elif tank == 'left_tank2':
        return cX - t2
    elif tank == 'left_tank3':
        return cX - t3
    elif tank == 'right_tank1':
        return cX - t5
    elif tank == 'right_tank2':
        return cX - t6
    elif tank == 'right_tank3':
        return cX - t7
    else:
        return np.nan  # NA if tank is not determined or cX is out of range

# Parse arguments
ap = argparse.ArgumentParser(description="Analyze CSV file and add camera, tank, and cXtank columns.")
ap.add_argument("-f", "--file", required=True, type=str, help="Path to the CSV file")
ap.add_argument("-t", "--tank_boundaries", nargs=8, required=True, type=int, help="8 boundaries for left and right tanks in the order: t1, t2, t3, t4, t5, t6, t7, t8")

args = ap.parse_args()

# Read the CSV file
df = pd.read_csv(args.file, delimiter='\t')

# Add the 'camera' column
df['camera'] = df['cX'].apply(determine_camera)

# Add the 'tank' column based on the boundaries provided
df['tank'] = df.apply(lambda row: determine_tank(row['cX'], args.tank_boundaries), axis=1)

# Add the 'cXtank' column by subtracting the appropriate tank boundary from cX
df['cXtank'] = df.apply(lambda row: calculate_cXtank(row['cX'], row['tank'], args.tank_boundaries), axis=1)

# Output the modified DataFrame to a new CSV file
output_file = 'analyzed_' + args.file
df.to_csv(output_file, sep='\t', index=False)

print(f"Analysis complete. Results saved to {output_file}")

