#!/usr/bin/env python3

import numpy as np
import cv2
import argparse
import time
import math
import os, errno
import glob
import sys
import multiprocessing

#Script to go through video to find chessboard photos in stereo videos. 

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prefix", required=True, 
        help="You must specify a prefix name to write captured checkerboard images ")
ap.add_argument("-v", "--video", required=True, type=str,
	help="file name for video")
ap.add_argument ('-c', '--cb_size', nargs=2, type=int, action = 'append', required=True,
        help="need to specify checkerboard size e.g. -c 8 6")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
	help="delay time between frames for slo-mo")
ap.add_argument("-m", "--moveThresh", required=False, default=1, type=float,
	help="estimates movement speed from previous to keep if below threshold")
ap.add_argument("-n", "--nimdist", required=False, default=10, type=float,
	help="miNdist threshold - number of pixels corner must (min distance) from previous to keep")
ap.add_argument("-e", "--edgeThresh", required=False, default=24, type=float,
	help="edge threshold is estimate for distance from camera of checkerboard (exclude far away ones)")
ap.add_argument("--invert", required=False, default=0, type=int,
	help="Invert black and white colors")
ap.add_argument("-l", "--look", required=False, default=1, type=int,
	help="Look at (watch) video while searching for frame pairs")
ap.add_argument("-b", "--border", required=False, default=40, type=int,
	help="Imposes a distance from the border of the frame to not select checkerboards that go out of view")
args = vars(ap.parse_args())
moveThresh = args["moveThresh"]
mindist = args["nimdist"]
edgeThresh = args["edgeThresh"]
delay = args["delay"]
prefix = args["prefix"]
video = args["video"]
border = args["border"]
cb_size = args["cb_size"]
chessboardSize = tuple(cb_size[0])
invert = args["invert"]
look = args["look"]

frame_size = (640,480)
xmax=0

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


cap = cv2.VideoCapture(video)

#Offsets by xframe, frame frames
loffset = 1
cap.set(1,loffset);

global i
i = 1
boards=0	#count chessboards
frametext=0

while(cap.isOpened()):
    frametext=frametext+1
    ret, frame = cap.read()

    if ret == True :


        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#Find chessboard corners
        retcorn, corners = cv2.findChessboardCorners(gray, chessboardSize, None)

        if invert == 1:
            adjusted = cv2.bitwise_not(gray)
        else :
            adjusted = gray

#New code to add corners
        if retcorn == True:

            totcorners = 2 * (chessboardSize[0] * chessboardSize[1])

            corners = cv2.cornerSubPix(adjusted, corners, (11,11), (-1,-1), criteria)

            # Calculate the average distance between each of the corners
            dist_sum = 0
            for i in range(len(corners) - 1):  
                 for j in range(i + 1, len(corners)):
                      dist_sum += np.linalg.norm(corners[i] - corners[j])
            corndist = dist_sum / ((len(corners) - 1) * len(corners) / 2)

            #find extreme corners to later check if they are too close to border
            xarray = corners[:,0,0]	
            yarray = corners[:,0,1]
            ymin = np.min(yarray)
            xmin = np.min(xarray)
            ymax = np.max(yarray)
            xmax = np.max(xarray)

            #Now calculate the center of each chess board to determine movement
            # Calculate the center of all the corners
            center = np.mean(corners, axis=0)
 
            if boards > 0 :
                 print(str(frametext) + "\t" + str(round(corndist,2)) + "\t" + str(round(center[0][0],2)) + "\t" + str(round(center[0][1],2)), str(xmin), str(ymin),str(xmax),str(ymax) )
            boards = boards + 1

            if look == 1 :
                # Draw the corners
                cv2.drawChessboardCorners(adjusted, chessboardSize, corners, ret)
#***********
        if look == 1:
            cv2.putText(adjusted,str(frametext+loffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))

            cv2.imshow('frame',adjusted)

            time.sleep(delay)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
    else:
        break

cap.release()
cv2.destroyAllWindows()
