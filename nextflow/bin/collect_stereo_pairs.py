#!/usr/bin/env python3

import numpy as np
import cv2
import argparse
import time
import math
#Script to go through video to find chessboard photos in stereo videos. A movement threshold compares current to previous
#location of board because if the board is moving quickly, unsynced l/r video causes much noise in calibration

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prefix", required=True, 
        help="You must specify a prefix name to write captured checkerboard images ")
ap.add_argument("-v1", "--video1", required=True, type=str,
	help="file name for first video")
ap.add_argument("-v2", "--video2", required=True, type=str,
	help="filename for second video")
ap.add_argument("-g", "--gamma", required=False, default=1,type=float,
	help="value of gamma")
ap.add_argument("-b", "--black", required=False, default=0, type=int,
	help="threshold below which is black")
ap.add_argument("-w", "--white", required=False, default=255, type=int,
	help="threshold above which is white")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
	help="frame to start at default = 1")
ap.add_argument ('-c', '--cb_size', nargs=2, type=int, action = 'append', required=True,
        help="need to specify checkerboard size e.g. -c 8 6")
ap.add_argument("-o", "--offset", required=False, default=0, type=int,
	help="number of frames to offset two videos, positive or negative")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
	help="delay time between frames for slo-mo")
ap.add_argument("-m", "--moveThresh", required=False, default=3, type=float,
	help="Movement threshold - average number of pixels moved for corners of chess board")
ap.add_argument("-e", "--edgeThresh", required=False, default=24, type=float,
	help="Movement threshold - average number of pixels moved for corners of chess board")
ap.add_argument("--invert", required=False, default=0, type=int,
	help="Movement threshold - average number of pixels moved for corners of chess board")
ap.add_argument("-l", "--look", required=False, default=1, type=int,
	help="Look at (watch) video while searching for frame pairs")
args = vars(ap.parse_args())
moveThresh = args["moveThresh"]
edgeThresh = args["edgeThresh"]
offset = args["offset"]
delay = args["delay"]
gamma = args["gamma"]
black = args["black"]
white = args["white"]
start = args["start"]
prefix = args["prefix"]
video1 = args["video1"]
video2 = args["video2"]
cb_size = args["cb_size"]
chessboardSize = tuple(cb_size[0])
invert = args["invert"]
look = args["look"]

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def adjust_clip(image, black=0, white=255):
	# build a lookup table mapping the pixel values [0, 255] to
	# set values below black to 0 and above white to 255
	zeros = np.array([i * 0
		for i in np.arange(0,black)]).astype("uint8")
	whites = np.array([(i * 0) + 255
		for i in np.arange(0,256-white)]).astype("uint8")
	table = np.array([i + black
		for i in np.arange(0,white-black)]).astype("uint8")
	table = np.concatenate((zeros,table,whites))
	return cv2.LUT(image, table)

def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)

cap = cv2.VideoCapture(video1)
cap2 = cv2.VideoCapture(video2)

#Offsets by xframe, frame frames
loffset = start
cap.set(1,loffset);
roffset=start+offset
cap2.set(1,roffset);

global i
i = 1

#********************* Define board

## Arrays to store object points and image points from all the images.
difcornL = [] #will be difference of corners from last reading
old_cornersL = [] #Keep corners from previous time chessboard was found
difcornR = [] #will be difference of corners from last reading
old_cornersR = [] #Keep corners from previous time chessboard was found


#**********************
boards=0	#count chessboards
frametext=0

while(cap.isOpened()):
    frametext=frametext+1
    ret, frame = cap.read()
    ret2, frame2 = cap2.read()

    if ret == True and ret2 == True:


        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

#Find chessboard corners
        retL, cornersL = cv2.findChessboardCorners(gray, chessboardSize, None)
        retR, cornersR = cv2.findChessboardCorners(gray2, chessboardSize, None)

        clipped = adjust_clip(gray, black=black, white=white)
        gamma = gamma if gamma > 0 else 0.1
        adjusted = adjust_gamma(clipped, gamma=gamma)

        clipped2 = adjust_clip(gray2, black=black, white=white)
        adjusted2 = adjust_gamma(clipped2, gamma=gamma)

        if invert == 1:
            adjusted = cv2.bitwise_not(adjusted)
            adjusted2 = cv2.bitwise_not(adjusted2)

#New code to add corners
        if retL and retR == True:

            # Draw and display the corners
            #cv2.drawChessboardCorners(adjusted, chessboardSize, cornersL, retL)
            #cv2.drawChessboardCorners(adjusted2, chessboardSize, cornersR, retR)

            totcorners = 2 * (chessboardSize[0] * chessboardSize[1])

            cornersL = cv2.cornerSubPix(adjusted, cornersL, (11,11), (-1,-1), criteria)
            flatcornL = cornersL.reshape([1, totcorners]) #Need to calculate array size based on checkerboard size

            cornersR = cv2.cornerSubPix(adjusted, cornersR, (11,11), (-1,-1), criteria)
            flatcornR = cornersR.reshape([1, totcorners]) #Need to calculate array size based on checkerboard size

            X1 = float(cornersL[0][0][0])	#convert first 2 corners to x,y coordinates to find distance
            Y1 = float(cornersL[0][0][1])
            X2 = float(cornersL[1][0][0])
            Y2 = float(cornersL[1][0][1])
            corndist = math.sqrt((X1-X2)**2 + (Y1-Y2)**2)

            if boards > 0 :
              difcornL = np.subtract(flatcornL, old_cornersL)
              difcornL = np.abs(difcornL)
              movementL = np.average(difcornL)

              difcornR = np.subtract(flatcornR, old_cornersR)
              difcornR = np.abs(difcornR)
              movementR = np.average(difcornR)

              #check distance between corners to exclude boards far away in view, which seem inaccurate

              if movementL and movementR < moveThresh: #means board in camera view did not move much from previous capture
                if corndist > edgeThresh :
                    #Add frame to printed video -- could add a toggle option here
                    #cv2.putText(adjusted,str(frametext+loffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
                    #cv2.putText(adjusted2,str(frametext+roffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))

                    cv2.imwrite(prefix + "_CH_L_" + str(frametext) + ".png", adjusted)
                    cv2.imwrite(prefix + "_CH_R_" + str(frametext) + ".png", adjusted2)
                    print("*** Meets edge proximity threshold " + str(corndist) + " Meets movement threshold. LEFT:" + str(movementL) + " RIGHT:" + str(movementR) + " writing images")
                else:
                    print("Chessboard corners too close (board too distant) " + str(corndist) +  " SKIP")
              else :
                print("Exceeds movement threshold moveThresh = " + str(moveThresh) + " LEFT:" + str(movementL) + " RIGHT:" + str(movementR) + " SKIP")

            boards = boards + 1
            old_cornersL = flatcornL
            old_cornersR = flatcornR

#***********
        if look == 1:
            cv2.putText(adjusted,str(frametext+loffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
            cv2.putText(adjusted2,str(frametext+roffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))

            cv2.imshow('frame',adjusted)
            cv2.imshow('frame2',adjusted2)

            #move window when first opening
            if frametext == 1:
                cv2.moveWindow('frame2',642, 0)
                cv2.moveWindow('frame',0, 0)

            time.sleep(delay)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
    else:
        break

cap.release()
cap2.release()
cv2.destroyAllWindows()
