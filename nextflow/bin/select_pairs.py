#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cv2
import argparse
import glob
import os
import sys

#Script to select video frames from a video containing checkerboards. Uses a previously created
#tab delimited file with all instances called id_all_checkerframes.py
#by THO

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filein", required=True,
        help="csv file with 5 columns of frame, dist, centerx, centery. From id_all_checkerframes.py")
ap.add_argument("-p", "--prefix", required=True,
        help="You must specify a prefix name to write captured checkerboard images ")
ap.add_argument("-v1", "--video1", required=True, type=str,
        help="file name for video")
ap.add_argument("-v2", "--video2", required=True, type=str,
        help="file name for video")
ap.add_argument("-n", "--number", required=False, default=50, type=float,
        help="number of frames to keep by writing individual files")
ap.add_argument("-e", "--edgeThresh", required=False, default=90, type=float,
        help="edge threshold is estimate for distance from camera of checkerboard (exclude far away ones)")
ap.add_argument("-l", "--look", required=False, default=0, type=int,
        help="Look at (watch) graphs of data while selecting")
ap.add_argument("-b", "--border", required=False, default=40, type=int,
        help="Imposes a distance from the border of the frame to not select checkerboards that go out of view")
ap.add_argument("-r", "--ratio", required=False, default=1, type=float,
        help="A factor to weight the distance from camera relative to the x-y camera values. Usually will be <1 to diversify x-y positions more")
ap.add_argument("-m", "--movement", required=False, default=100, type=float,
        help="A threshold value for movement (pixel distance) above which moving boards will be removed ")

args = vars(ap.parse_args())
edgeThresh = args["edgeThresh"]
prefix = args["prefix"]
video1 = args["video1"]
video2 = args["video2"]
number = args["number"]
border = args["border"]
look = args["look"]
filein = args["filein"]
mult = args["ratio"]
movement = args["movement"]


# compute the minimum absolute difference between the value of 'x' and the previous and next rows in 'x'

import numpy as np

#calculate 3d movement of center of board. This takes the minimum movement of each row compared to previous and next
#row. Taking the min should account for cases where board is first detected and would appear to have moved a lot up to that point
def compute_movement(row):
    prev = np.nan if row.name == 0 or (row.name-1) not in df.index else np.sqrt((row['x'] - df.loc[row.name-1, 'x'])**2 + (row['y'] - df.loc[row.name-1, 'y'])**2 + (row['dist'] - df.loc[row.name-1, 'dist'])**2)
    next = np.nan if row.name == len(df)-1 or (row.name+1) not in df.index else np.sqrt((row['x'] - df.loc[row.name+1, 'x'])**2 + (row['y'] - df.loc[row.name+1, 'y'])**2 + (row['dist'] - df.loc[row.name+1, 'dist'])**2)
    return abs(min(prev, next))

def plot_3d(df):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(df['dist'], df['x'], df['y'], s=10)
    ax.set_xlabel('Dist from cam')
    ax.set_ylabel('X camera axis')
    ax.set_zlabel('Y camera axis')
    plt.show()


# Load the tab-delimited text file into a pandas DataFrame
df = pd.read_csv(filein, sep='\t')

if look == 1:
     # create histogram
     plt.hist(df['dist'], bins=10)
     plt.title('Histogram of all values of distance from camera metric (dist between squares)')
     plt.xlabel('Value')
     plt.ylabel('Frequency')
     plt.show()

#add a new column and calculate a movement metric in that column, to use for identifying
#frames that occur when board is not moving as rapidly

df['movement'] = df.apply(compute_movement, axis=1)


if look == 1:
     # create histogram
     bins = np.arange(1, 5, 0.1)
     plt.hist(df['movement'], bins=bins)
     plt.title('Histogram of all values of movement from previously detected board')
     plt.xlabel('Value')
     plt.ylabel('Frequency')
     plt.show()


df_close = df[df['dist'] > edgeThresh]
df_close =df_close[df_close['movement'] < movement]

if look ==1:
     plot_3d(df_close)

df = df_close

#multiply distance from camera by mult to weight that parameter relative to x-y for selection of points
df['dist'] = df['dist'] * mult

#********Delete previous files
# Get a list of all the file paths that ends with .txt from in specified directory
oldfiles = prefix + "_pair_*.png"
fileList = glob.glob(oldfiles) 
# Iterate over the list of filepaths & remove each file.
for filePath in fileList:
    try:
        os.remove(filePath)
        print("Removing old files")
    except:
        print("Error while deleting file : ", filePath)


# Calculate the pairwise distances between all points
points = df.iloc[:,2:4].values
dists = np.linalg.norm(points[:,np.newaxis,:] - points[np.newaxis,:,:], axis=2)

# Calculate the average distance between each pair of points
corndist = np.sum(np.triu(dists, k=1)) / (len(df) * (len(df) - 1) / 2)

# Set random seed for reproducibility
np.random.seed(1234)

num_samples = number
sampled_indices = []
remaining_indices = set(range(len(df)))

while len(sampled_indices) < num_samples:
    # Pick a random index from the remaining indices
    if len(remaining_indices) == 0:
        break
    idx = np.random.choice(list(remaining_indices))
    sampled_indices.append(idx)
    remaining_indices.remove(idx)
    # Calculate the distances between the selected point and all remaining points
    dists_to_remaining = dists[idx, list(remaining_indices)]
    # Find the point with the maximum average distance to all other points
    if len(dists_to_remaining) > 0:
        max_dist_idx = np.argmax(np.mean(dists_to_remaining, axis=0))
        # Remove the point with the maximum average distance from the remaining indices
        if len(remaining_indices) > max_dist_idx:
            remaining_indices.remove(list(remaining_indices)[max_dist_idx])
        else:
            break
    else:
        break

# Select the sampled rows from the original DataFrame
df_sampled = df.iloc[sampled_indices,:]

print(df_sampled)
if look == 1:
    plot_3d(df_sampled)


# Read the video file
cap1 = cv2.VideoCapture(video1)
cap2 = cv2.VideoCapture(video2)

df = df_sampled

# Iterate over the frame numbers and extract the corresponding frames for left camera
for frame_num in df['frame']:
    # Set the frame position to the current frame number
    cap1.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

    # Read the next frame from the video
    ret1, frame1 = cap1.read()

    # Process the frame here, for example, save it to a file
    cv2.imwrite(f'{prefix}_pair_L_{frame_num}.png', frame1)

# Iterate over the frame numbers and extract the corresponding frames for right camera
for frame_num in df['frame']:
    # Set the frame position to the current frame number
    cap2.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

    # Read the next frame from the video
    ret2, frame2 = cap2.read()

    # Process the frame here, for example, save it to a file
    cv2.imwrite(f'{prefix}_pair_R_{frame_num}.png', frame2)


# Release the video capture object
cap1.release()
cap2.release()

