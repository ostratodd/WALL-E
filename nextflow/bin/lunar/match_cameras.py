#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import numpy as np

# Parse arguments
ap = argparse.ArgumentParser(description="Plot correlations between left and right tanks.")
ap.add_argument("-f", "--file", required=True, type=str, help="Path to the CSV file")
ap.add_argument("-o", "--outfile", required=True, type=str, help="Name of the output file")
ap.add_argument("-dx", "--distance_x", required=False, type=float, default=200, help="Maximum allowed difference for cX (default: 200)")
ap.add_argument("-dy", "--distance_y", required=False, type=float, default=200, help="Maximum allowed difference for cY (default: 200)")
args = ap.parse_args()

# Read the CSV file
df = pd.read_csv(args.file, delimiter='\t')

# Filter out rows where 'tank' is 'noise'
df = df[df['tank'] != 'noise']

# Add a new column for the match status
df['match_status'] = ""

# Function to find the closest pairs between two lists considering both cX and cY values
def find_closest_pairs(left, right, left_indices, right_indices):
    pairs = []
    used_right_indices = set()
    for left_val, left_idx in zip(left, left_indices):
        closest_idx = None
        closest_dist = float('inf')
        for idx, (right_val, right_idx) in enumerate(zip(right, right_indices)):
            if idx in used_right_indices:
                continue
            # Calculate Euclidean distance between the left and right points
            dist = np.sqrt((left_val[0] - right_val[0])**2 + (left_val[1] - right_val[1])**2)
            if dist < closest_dist:
                closest_dist = dist
                closest_idx = idx
        if closest_idx is not None:
            pairs.append((left_val, right[closest_idx], left_idx, right_indices[closest_idx]))
            used_right_indices.add(closest_idx)
    return pairs

# Prepare lists to store matched, included, and excluded pairs for plotting and printing
included_pairs_tank1 = []
excluded_pairs_tank1_x = []
excluded_pairs_tank1_y = []
excluded_pairs_tank1_both = []
included_pairs_tank2 = []
excluded_pairs_tank2_x = []
excluded_pairs_tank2_y = []
excluded_pairs_tank2_both = []
included_pairs_tank3 = []
excluded_pairs_tank3_x = []
excluded_pairs_tank3_y = []
excluded_pairs_tank3_both = []

# Group by frame and process each group
for frame, group in df.groupby('frame'):

    # Separate data for each left and right tank within this frame
    left_tank1 = group[group['tank'] == 'left_tank1'][['cXtank', 'cY']].values
    right_tank1 = group[group['tank'] == 'right_tank1'][['cXtank', 'cY']].values
    left_indices_tank1 = group[group['tank'] == 'left_tank1'].index
    right_indices_tank1 = group[group['tank'] == 'right_tank1'].index
    
    left_tank2 = group[group['tank'] == 'left_tank2'][['cXtank', 'cY']].values
    right_tank2 = group[group['tank'] == 'right_tank2'][['cXtank', 'cY']].values
    left_indices_tank2 = group[group['tank'] == 'left_tank2'].index
    right_indices_tank2 = group[group['tank'] == 'right_tank2'].index

    left_tank3 = group[group['tank'] == 'left_tank3'][['cXtank', 'cY']].values
    right_tank3 = group[group['tank'] == 'right_tank3'][['cXtank', 'cY']].values
    left_indices_tank3 = group[group['tank'] == 'left_tank3'].index
    right_indices_tank3 = group[group['tank'] == 'right_tank3'].index
    
    # Find closest pairs for each tank pair
    pairs_tank1 = find_closest_pairs(left_tank1, right_tank1, left_indices_tank1, right_indices_tank1)
    pairs_tank2 = find_closest_pairs(left_tank2, right_tank2, left_indices_tank2, right_indices_tank2)
    pairs_tank3 = find_closest_pairs(left_tank3, right_tank3, left_indices_tank3, right_indices_tank3)

    # Separate included and excluded pairs based on the distance thresholds for cX and cY
    for (left_val, right_val, left_idx, right_idx) in pairs_tank1:
        left_val_x, left_val_y = left_val
        right_val_x, right_val_y = right_val
        x_diff_too_high = abs(left_val_x - right_val_x) > args.distance_x
        y_diff_too_high = abs(left_val_y - right_val_y) > args.distance_y
        if x_diff_too_high and y_diff_too_high:
            excluded_pairs_tank1_both.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'bothdif'
            df.at[right_idx, 'match_status'] = 'bothdif'
        elif x_diff_too_high:
            excluded_pairs_tank1_x.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'xdif'
            df.at[right_idx, 'match_status'] = 'xdif'
        elif y_diff_too_high:
            excluded_pairs_tank1_y.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'ydif'
            df.at[right_idx, 'match_status'] = 'ydif'
        else:
            included_pairs_tank1.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'match'
            df.at[right_idx, 'match_status'] = 'match'

    # Repeat the same process for tanks 2 and 3
    for (left_val, right_val, left_idx, right_idx) in pairs_tank2:
        left_val_x, left_val_y = left_val
        right_val_x, right_val_y = right_val
        x_diff_too_high = abs(left_val_x - right_val_x) > args.distance_x
        y_diff_too_high = abs(left_val_y - right_val_y) > args.distance_y
        if x_diff_too_high and y_diff_too_high:
            excluded_pairs_tank2_both.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'bothdif'
            df.at[right_idx, 'match_status'] = 'bothdif'
        elif x_diff_too_high:
            excluded_pairs_tank2_x.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'xdif'
            df.at[right_idx, 'match_status'] = 'xdif'
        elif y_diff_too_high:
            excluded_pairs_tank2_y.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'ydif'
            df.at[right_idx, 'match_status'] = 'ydif'
        else:
            included_pairs_tank2.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'match'
            df.at[right_idx, 'match_status'] = 'match'

    for (left_val, right_val, left_idx, right_idx) in pairs_tank3:
        left_val_x, left_val_y = left_val
        right_val_x, right_val_y = right_val
        x_diff_too_high = abs(left_val_x - right_val_x) > args.distance_x
        y_diff_too_high = abs(left_val_y - right_val_y) > args.distance_y
        if x_diff_too_high and y_diff_too_high:
            excluded_pairs_tank3_both.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'bothdif'
            df.at[right_idx, 'match_status'] = 'bothdif'
        elif x_diff_too_high:
            excluded_pairs_tank3_x.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'xdif'
            df.at[right_idx, 'match_status'] = 'xdif'
        elif y_diff_too_high:
            excluded_pairs_tank3_y.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'ydif'
            df.at[right_idx, 'match_status'] = 'ydif'
        else:
            included_pairs_tank3.append((left_val, right_val))
            df.at[left_idx, 'match_status'] = 'match'
            df.at[right_idx, 'match_status'] = 'match'

# Write the updated DataFrame to a new tab-delimited file
df.to_csv(args.outfile, sep='\t', index=False)

print(f"Updated data has been written to {args.outfile}")

# Plotting
plt.figure(figsize=(15, 10))

# Plot for left_tank1 vs. right_tank1
plt.subplot(3, 1, 1)
if included_pairs_tank1:
    left_vals1, right_vals1 = zip(*included_pairs_tank1)
    left_vals1_x, left_vals1_y = zip(*left_vals1)
    right_vals1_x, right_vals1_y = zip(*right_vals1)
    plt.scatter(left_vals1_x, right_vals1_x, color='#1f77b4', s=20, alpha=0.7, label='Included')
if excluded_pairs_tank1_x:
    left_vals1_excl, right_vals1_excl = zip(*excluded_pairs_tank1_x)
    left_vals1_excl_x, left_vals1_excl_y = zip(*left_vals1_excl)
    right_vals1_excl_x, right_vals1_excl_y = zip(*right_vals1_excl)
    plt.scatter(left_vals1_excl_x, right_vals1_excl_x, color='red', s=20, alpha=0.7, label='Excluded (x)')
if excluded_pairs_tank1_y:
    left_vals1_excl, right_vals1_excl = zip(*excluded_pairs_tank1_y)
    left_vals1_excl_x, left_vals1_excl_y = zip(*left_vals1_excl)
    right_vals1_excl_x, right_vals1_excl_y = zip(*right_vals1_excl)
    plt.scatter(left_vals1_excl_x, right_vals1_excl_x, color='yellow', s=20, alpha=0.7, label='Excluded (y)')
if excluded_pairs_tank1_both:
    left_vals1_excl, right_vals1_excl = zip(*excluded_pairs_tank1_both)
    left_vals1_excl_x, left_vals1_excl_y = zip(*left_vals1_excl)
    right_vals1_excl_x, right_vals1_excl_y = zip(*right_vals1_excl)
    plt.scatter(left_vals1_excl_x, right_vals1_excl_x, color='orange', s=20, alpha=0.7, label='Excluded (both)')
plt.xlim(0, 600)
plt.ylim(0, 600)
plt.title("Correlation between Left Tank 1 and Right Tank 1")
plt.xlabel("Left Tank 1 cX")
plt.ylabel("Right Tank 1 cX")
plt.grid(True)
plt.legend()

# Plot for left_tank2 vs. right_tank2
plt.subplot(3, 1, 2)
if included_pairs_tank2:
    left_vals2, right_vals2 = zip(*included_pairs_tank2)
    left_vals2_x, left_vals2_y = zip(*left_vals2)
    right_vals2_x, right_vals2_y = zip(*right_vals2)
    plt.scatter(left_vals2_x, right_vals2_x, color='#0077bb', s=20, alpha=0.7, label='Included')
if excluded_pairs_tank2_x:
    left_vals2_excl, right_vals2_excl = zip(*excluded_pairs_tank2_x)
    left_vals2_excl_x, left_vals2_excl_y = zip(*left_vals2_excl)
    right_vals2_excl_x, right_vals2_excl_y = zip(*right_vals2_excl)
    plt.scatter(left_vals2_excl_x, right_vals2_excl_x, color='red', s=20, alpha=0.7, label='Excluded (x)')
if excluded_pairs_tank2_y:
    left_vals2_excl, right_vals2_excl = zip(*excluded_pairs_tank2_y)
    left_vals2_excl_x, left_vals2_excl_y = zip(*left_vals2_excl)
    right_vals2_excl_x, right_vals2_excl_y = zip(*right_vals2_excl)
    plt.scatter(left_vals2_excl_x, right_vals2_excl_x, color='yellow', s=20, alpha=0.7, label='Excluded (y)')
if excluded_pairs_tank2_both:
    left_vals2_excl, right_vals2_excl = zip(*excluded_pairs_tank2_both)
    left_vals2_excl_x, left_vals2_excl_y = zip(*left_vals2_excl)
    right_vals2_excl_x, right_vals2_excl_y = zip(*right_vals2_excl)
    plt.scatter(left_vals2_excl_x, right_vals2_excl_x, color='orange', s=20, alpha=0.7, label='Excluded (both)')
plt.xlim(0, 600)
plt.ylim(0, 600)
plt.title("Correlation between Left Tank 2 and Right Tank 2")
plt.xlabel("Left Tank 2 cX")
plt.ylabel("Right Tank 2 cX")
plt.grid(True)
plt.legend()

# Plot for left_tank3 vs. right_tank3
plt.subplot(3, 1, 3)
if included_pairs_tank3:
    left_vals3, right_vals3 = zip(*included_pairs_tank3)
    left_vals3_x, left_vals3_y = zip(*left_vals3)
    right_vals3_x, right_vals3_y = zip(*right_vals3)
    plt.scatter(left_vals3_x, right_vals3_x, color='#004488', s=20, alpha=0.7, label='Included')
if excluded_pairs_tank3_x:
    left_vals3_excl, right_vals3_excl = zip(*excluded_pairs_tank3_x)
    left_vals3_excl_x, left_vals3_excl_y = zip(*left_vals3_excl)
    right_vals3_excl_x, right_vals3_excl_y = zip(*right_vals3_excl)
    plt.scatter(left_vals3_excl_x, right_vals3_excl_x, color='red', s=20, alpha=0.7, label='Excluded (x)')
if excluded_pairs_tank3_y:
    left_vals3_excl, right_vals3_excl = zip(*excluded_pairs_tank3_y)
    left_vals3_excl_x, left_vals3_excl_y = zip(*left_vals3_excl)
    right_vals3_excl_x, right_vals3_excl_y = zip(*right_vals3_excl)
    plt.scatter(left_vals3_excl_x, right_vals3_excl_x, color='yellow', s=20, alpha=0.7, label='Excluded (y)')
if excluded_pairs_tank3_both:
    left_vals3_excl, right_vals3_excl = zip(*excluded_pairs_tank3_both)
    left_vals3_excl_x, left_vals3_excl_y = zip(*left_vals3_excl)
    right_vals3_excl_x, right_vals3_excl_y = zip(*right_vals3_excl)
    plt.scatter(left_vals3_excl_x, right_vals3_excl_x, color='orange', s=20, alpha=0.7, label='Excluded (both)')
plt.xlim(0, 600)
plt.ylim(0, 600)
plt.title("Correlation between Left Tank 3 and Right Tank 3")
plt.xlabel("Left Tank 3 cX")
plt.ylabel("Right Tank 3 cX")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

