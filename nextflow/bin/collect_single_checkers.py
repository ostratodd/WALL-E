#!/usr/bin/env python3

import numpy as np
import cv2
import argparse
import time
import math
import os, errno
import glob
import sys

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

#********Delete previous files 
# Get a list of all the file paths that ends with .txt from in specified directory
oldfiles = prefix + "_single_*.png"
fileList = glob.glob(oldfiles)
# Iterate over the list of filepaths & remove each file.
for filePath in fileList:
    try:
        os.remove(filePath)
        print("Removing old files")
    except:
        print("Error while deleting file : ", filePath)

def find_closest(input_list, input_value):
  arr = np.asarray(input_list)
  i = (np.abs(arr - input_value)).argmin()
  return arr[i]


# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


cap = cv2.VideoCapture(video)

#Offsets by xframe, frame frames
loffset = 1
cap.set(1,loffset);

global i
i = 1

#********************* Define board
difcorn = [] #will be difference of corners from last reading to gauge movemeht
old_corners = [] #Keep corners from previous time chessboard was found

## Arrays to store object points and image points from all the images.
keepersX = [0,0] #keep clips when x or y is far enough from closest previous keeper
keepersY = [0,0] #keep clips when x or y is far enough from closest previous keeper


#**********************
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
            flatcorn = corners.reshape([1, totcorners]) #Need to calculate array size based on checkerboard size


            #find extreme corners to later check if they are too close to border
            xarray = corners[:,0,0]	
            yarray = corners[:,0,1]
            ymin = np.min(yarray)
            xmin = np.min(xarray)
            ymax = np.max(yarray)
            xmax = np.max(xarray)

            #convert first 2 corners to x,y coordinates to find distance from previously stored
            X1 = float(corners[0][0][0])	
            Y1 = float(corners[0][0][1])
            X2 = float(corners[1][0][0])
            Y2 = float(corners[1][0][1])
            #distance between corners is sq size, so smaller squares far away
            corndist = math.sqrt((X1-X2)**2 + (Y1-Y2)**2) 

            if boards > 0 :
              difcorn = np.subtract(flatcorn, old_corners) 
              difcorn = np.abs(difcorn)
              movement = np.average(difcorn)
              #print("Movement: " + str(movement))
              if movement < moveThresh:
                #check distance between corners to exclude boards far away in view, which seem inaccurate. Higher edgeThresh means only closer boards kept
                if corndist > edgeThresh :
                    #check if any checkerboard corner is too close to border, which messes up calibration when edge is out of view
                    if xmin > border and xmax < (640-border) and ymin > border and ymax < (480-border) :
                        closest = find_closest(keepersX, X1)	#keepers is the X and Y value of one corner to keep only if far enough from previous keeper
                        closestY = find_closest(keepersY, Y1)
                        if np.abs(X1 - closest) > mindist or np.abs(Y1 - closestY) > mindist:
                            keepersX.append(X1)
                            keepersY.append(Y1)
                            print("***" + str(frametext) + ": Meets edge proximity threshold and distance. " + str(corndist) + " Not too close (" + str(round(mindist)) + ") at " + str(round(np.abs(X1-closest),3)) + str(round(np.abs(Y1-closestY),3)) + " writing images")
                            cv2.imwrite(prefix + "_single_" + str(frametext) + ".png", adjusted)
                        else:
                            print(str(frametext) + ": mindist (-n) of " + str(mindist) + " not exceeded. Too close to existing board. X,Y: " + str(round(np.abs(X1-closest),3)) + "," + str(round(np.abs(Y1-closestY),3)) )
                    else :
                        print(str(frametext) + ": Too close to border, ignoring. Border parameter set to " + str(border) )
                else:
                    print(str(frametext) + ": edgeThresh of " + str(edgeThresh) + " exceeded. ie Chessboard corners too close together (board too distant from camera) " + str(round(corndist,3)) +  " SKIP")
            else:
                print("Too much movement moveThresh (-m) of " + str(moveThresh) + " exceeded")
            boards = boards + 1
            old_corners = flatcorn

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
