#!/usr/bin/env python3

import cv2
import glob
import numpy as np
import os
import pickle
import argparse
import sys

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.',
        help="path to video frame files default is ./")
ap.add_argument("-pre", "--prefix", required=False, default='',
        help="prefix for the name of the image files before the required CH")
ap.add_argument ('-c', '--cb_size', nargs=2, type=int, action = 'append', required=True,
        help="need to specify checkerboard size e.g. -c 8 6")
ap.add_argument("-sq", "--squareSize", required=True, type=float,
        help="Size of an individual square of the checkerboard in mm")
ap.add_argument("-e", "--extension", required=False, default="png", type=str,
        help="extension of files. Default = png")
ap.add_argument("-l", "--look", required=False, default=0, type=int,
        help="Look at (view) images 1=yes 0=no.vDefault = 0")
args = vars(ap.parse_args())
dir_path = args["path"]
if not dir_path.endswith('/'):
    dir_path += '/'
prefix = args["prefix"]
squareSize = args["squareSize"]
cb_size = args["cb_size"]
chessboard_size = tuple(cb_size[0])
ext = args["extension"]
look = args["look"]

# Calibration settings
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

# Scale the object points by the size of the checkerboard squares (in mm)
objp *= squareSize  # Now objp is in millimeters or the units of squareSize

def calibrate_camera(image_paths):
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane

    for image_path in image_paths:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

    if not objpoints or not imgpoints:
        raise ValueError("No chessboard corners found in images.")

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    return mtx, dist

# File paths for the individual camera images
left_path = dir_path + prefix + "_L_single_" + "*." + ext
right_path = dir_path + prefix + "_R_single_" + "*." + ext

left_image_paths = glob.glob(left_path)
right_image_paths = glob.glob(right_path)

# Calibrate each camera
mtx_left, dist_left = calibrate_camera(left_image_paths)
mtx_right, dist_right = calibrate_camera(right_image_paths)

# Extract focal lengths
focal_length_left_x = mtx_left[0, 0]
focal_length_left_y = mtx_left[1, 1]
focal_length_right_x = mtx_right[0, 0]
focal_length_right_y = mtx_right[1, 1]

print("Left camera matrix:\n", mtx_left)
print("Left camera distortion coefficients:\n", dist_left)
print("Left camera focal length (x):", focal_length_left_x, "pixels")
print("Left camera focal length (y):", focal_length_left_y, "pixels")

print("Right camera matrix:\n", mtx_right)
print("Right camera distortion coefficients:\n", dist_right)
print("Right camera focal length (x):", focal_length_right_x, "pixels")
print("Right camera focal length (y):", focal_length_right_y, "pixels")

# Helper function to extract the index from filename
def extract_index(filename):
    basename = os.path.basename(filename)
    index = basename.split('_')[-1].split('.')[0]
    return index


# Read stereo images

# File paths for the individual camera images
left_path = dir_path + prefix + "_pair_L_" + "*." + ext
right_path = dir_path + prefix + "_pair_R_" + "*." + ext

stereo_left_image_paths = glob.glob(left_path)
stereo_right_image_paths = glob.glob(right_path)

# Create a dictionary to match left and right images
left_images_dict = {extract_index(p): p for p in stereo_left_image_paths}
right_images_dict = {extract_index(p): p for p in stereo_right_image_paths}

# Prepare object points
objpoints = []  # 3d point in real world space
imgpoints_left = []  # 2d points in image plane of left camera
imgpoints_right = []  # 2d points in image plane of right camera

# Find matching pairs
common_indices = set(left_images_dict.keys()).intersection(set(right_images_dict.keys()))

for index in common_indices:
    img_left_path = left_images_dict[index]
    img_right_path = right_images_dict[index]

    img_left = cv2.imread(img_left_path)
    img_right = cv2.imread(img_right_path)
    gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret_left, corners_left = cv2.findChessboardCorners(gray_left, chessboard_size, None)
    ret_right, corners_right = cv2.findChessboardCorners(gray_right, chessboard_size, None)

    # If found, add object points, image points (after refining them)
    if ret_left and ret_right:
        print(f"Chessboard corners found for pair: {img_left_path} and {img_right_path}")
        objpoints.append(objp)

        corners2_left = cv2.cornerSubPix(gray_left, corners_left, (11, 11), (-1, -1), criteria)
        imgpoints_left.append(corners2_left)

        corners2_right = cv2.cornerSubPix(gray_right, corners_right, (11, 11), (-1, -1), criteria)
        imgpoints_right.append(corners2_right)
    else:
        print(f"Chessboard corners not found for pair: {img_left_path} and {img_right_path}")

print(f"Number of valid stereo pairs: {len(objpoints)}")

if len(objpoints) > 0:
    # Stereo calibration
    ret, mtx_left, dist_left, mtx_right, dist_right, R, T, E, F = cv2.stereoCalibrate(
        objpoints, imgpoints_left, imgpoints_right,
        mtx_left, dist_left, mtx_right, dist_right,
        gray_left.shape[::-1], criteria
    )

    print("Rotation matrix between the two cameras:\n", R)
    print("Translation vector between the two cameras:\n", T)
    print("Essential matrix:\n", E)
    print("Fundamental matrix:\n", F)

    # Stereo rectification
    R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(
        mtx_left, dist_left, mtx_right, dist_right,
        gray_left.shape[::-1], R, T, alpha=0
    )

    # Initialize rectification maps
    left_map1, left_map2 = cv2.initUndistortRectifyMap(
        mtx_left, dist_left, R1, P1, gray_left.shape[::-1], cv2.CV_16SC2
    )
    right_map1, right_map2 = cv2.initUndistortRectifyMap(
        mtx_right, dist_right, R2, P2, gray_right.shape[::-1], cv2.CV_16SC2
    )

    # Save calibration data
    calibration_data = {
        'mtx_left': mtx_left,
        'dist_left': dist_left,
        'mtx_right': mtx_right,
        'dist_right': dist_right,
        'R': R,
        'T': T,
        'R1': R1,
        'R2': R2,
        'P1': P1,
        'P2': P2,
        'Q': Q,
        'left_map1': left_map1,
        'left_map2': left_map2,
        'right_map1': right_map1,
        'right_map2': right_map2
    }

    #write file name out using prefix with pickle
    outfile = prefix + "_stereomap.pkl"
    with open(outfile, 'wb') as f:
        pickle.dump(calibration_data, f)

else:
    print("No valid stereo pairs found. Please ensure the chessboard is visible in both camera views for the stereo pairs.")

