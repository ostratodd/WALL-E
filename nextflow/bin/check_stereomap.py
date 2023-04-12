import cv2
import numpy as np
import argparse

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p1", "--picture1", required=True, type=str,
        help="file name for video")
ap.add_argument("-p2", "--picture2", required=True, type=str,
        help="file name for video")
ap.add_argument("-s", "--stereofile", required=True, type=str,
        help="stereomap xml file")
ap.add_argument("-b", "--baseline", required=True, type=float,
        help="Measured distance between cameras")
args = vars(ap.parse_args())
left = args["picture1"]
right = args["picture2"]
stereofile = args["stereofile"]
baseline = args["baseline"]



# Load the stereomap XML file
stereomap = cv2.stereoCalibrate("copy_final_files/2019southwater_stereoMap.xml")

# Load the stereo images
img_left = cv2.imread(left, cv2.IMREAD_GRAYSCALE)
img_right = cv2.imread(right, cv2.IMREAD_GRAYSCALE)

# Rectify the stereo images
rectified_left, rectified_right = cv2.stereoRectify(stereomap[0], stereomap[1], img_left, img_right)

# Compute the disparity map
disparity = cv2.StereoSGBM_create().compute(rectified_left, rectified_right)

# Compute the depth map
Q = stereomap[3]
points_3d = cv2.reprojectImageTo3D(disparity, Q)
depth_map = points_3d[:,:,2]

# Compute the mean and standard deviation of the depth map
mean_depth = np.mean(depth_map)
std_depth = np.std(depth_map)

# Check the quality of the stereo rectification parameters
if abs(mean_depth - baseline) < tolerance and std_depth < max_std_deviation:
    print("Mean depth: " + str(mean_depth) + " Baseline: " + str(baseline))
    print("Good quality stereo rectification parameters")
else:
    print("Mean depth: " + str(mean_depth) + " Baseline: " + str(baseline))
    print("Poor quality stereo rectification parameters")

