#!/usr/bin/env python3

import pandas as pd
import argparse
import numpy as np

# Function to determine camera based on cX
def determine_camera(cX):
    return 'left' if cX < 2001 else 'right'

# Function to determine tank based on cX and tank boundaries
def determine_tank(cX, camera, boundaries):
    left_t1, left_t2, left_t3, right_t1, right_t2, right_t3 = boundaries
    if camera == 'left':
        if cX < left_t1:
            return None  # NA for tanks if cX is less than the minimum boundary
        elif left_t1 <= cX < left_t2:
            return 'left_tank1'
        elif left_t2 <= cX < left_t3:
            return 'left_tank2'
        elif left_t3 <= cX <= 2000:  # Left side upper boundary
            return 'left_tank3'
    else:  # camera == 'right'
        if right_t1 <= cX < right_t2:
            return 'right_tank1'
        elif right_t2 <= cX < right_t3:
            return 'right_tank2'
        elif right_t3 <= cX:
            return 'right_tank3'

# Function to calculate cXtank based on the tank and boundaries
def calculate_cXtank(cX, tank, boundaries):
    left_t1, left_t2, left_t3, right_t1, right_t2, right_t3 = boundaries
    if tank == 'left_tank1':
        return cX - left_t1
    elif tank == 'left_tank2':
        return cX - left_t2
    elif tank == 'left_tank3':
        return cX - left_t3
    elif tank == 'right_tank1':
        return cX - right_t1
    elif tank == 'right_tank2':
        return cX - right_t2
    elif tank == 'right_tank3':
        return cX - right_t3
    else:
        return np.nan  # NA if tank is not determined or cX is out of range

# Parse arguments
ap = argparse.ArgumentParser(description="Analyze CSV file and add camera, tank, and cXtank columns.")
ap.add_argument("-f", "--file", required=True, type=str, help="Path to the CSV file")
ap.add_argument("-t", "--tank_boundaries", nargs=6, required=True, type=int, help="6 boundaries for left and right tanks in the order: left_tank1, left_tank2, left_tank3, right_tank1, right_tank2, right_tank3")

args = ap.parse_args()

# Read the CSV file
df = pd.read_csv(args.file, delimiter='\t')

# Add the 'camera' column
df['camera'] = df['cX'].apply(determine_camera)

# Add the 'tank' column based on the boundaries provided
df['tank'] = df.apply(lambda row: determine_tank(row['cX'], row['camera'], args.tank_boundaries), axis=1)

# Add the 'cXtank' column by subtracting the appropriate tank boundary from cX
df['cXtank'] = df.apply(lambda row: calculate_cXtank(row['cX'], row['tank'], args.tank_boundaries), axis=1)

# Output the modified DataFrame to a new CSV file
output_file = 'analyzed_' + args.file
df.to_csv(output_file, sep='\t', index=False)

print(f"Analysis complete. Results saved to {output_file}")

