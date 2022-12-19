#!/usr/bin/env python3

import numpy as np
import cv2 as cv
import glob
import pickle
import argparse

#program derived from Nico Nielsen at https://raw.githubusercontent.com/niconielsen32/ComputerVision/master/cameraCalibration.py


################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.',
        help="path to video frame files default is ./")
ap.add_argument("-w", "--watch", required=False, default=0, type=int,
        help="whether (1) or not (0) to watch video while writing. Default = 1")
ap.add_argument("-d", "--delay", required=False, default=10, type=int,
        help="delay time between frames for slo-mo")
ap.add_argument("-pre", "--prefix", required=True, type=str,
        help="prefix name for rectified videos L and R")
ap.add_argument("-e", "--extension", required=False, default = ".png", type=str,
        help="file extension for checkerboard images default = .png ")
ap.add_argument ('-c', '--cb_size', nargs=2, type=int, action = 'append', required=True,
        help="need to specify checkerboard size e.g. -c 8 6")
ap.add_argument ('-fr', '--frameSize', nargs=2, type=int, action = 'append', required=True,
        help="need to specify frame size of video e.g. -c 640 480")
ap.add_argument("-sq", "--squareSize", required=True, type=int,
        help="Size of an individual square of the checkerboard in mm")
args = vars(ap.parse_args())
delay = args["delay"]
watch = args["watch"]
prefix = args["prefix"]
extension = args["extension"]
cb_size = args["cb_size"]
chessboardSize = tuple(cb_size[0])
frameSize = args["frameSize"]
frameSize = tuple(frameSize[0])
ext = args["extension"]
squareSize = args["squareSize"]
dir_path = args["path"]

size_of_chessboard_squares_mm = squareSize

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)


# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:chessboardSize[0],0:chessboardSize[1]].T.reshape(-1,2)

objp = objp * size_of_chessboard_squares_mm


# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.


images = glob.glob(prefix + "*" + extension)

#images = glob.glob("*.png")
for image in images:

    img = cv.imread(image)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)

    # If found, add object points, image points (after refining them)
    if ret == True:

        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)

        if watch == 1 :
            # Draw and display the corners
            cv.drawChessboardCorners(img, chessboardSize, corners2, ret)
            cv.imshow('img', img)
            cv.waitKey(delay)
cv.destroyAllWindows()




############## CALIBRATION #######################################################

ret, cameraMatrix, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, frameSize, None, None)

#print("Camera calibrated: ", ret)
print("Camera Matrix\n", cameraMatrix)
#print("Distortion\n", dist)

###SAVE parameters to files###
calib_result_pickle = {}
calib_result_pickle["cameraMatrix"] = cameraMatrix
calib_result_pickle["dist"] = dist
calib_result_pickle["rvecs"] = rvecs
calib_result_pickle["tvecs"] = tvecs

#Writes the matrices to a .p file using pickle, which can be loaded later
paramfile = prefix + ".p"
pickle.dump(calib_result_pickle, open(paramfile, "wb" ))
