#!/usr/bin/env python3

import numpy as np
import cv2
import argparse
import time
import math
import os, errno
import glob
import sys

width = 640
height = 480

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
ap.add_argument("-t", "--threshold", required=False, default=0, type=int,
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
ap.add_argument("-n", "--nimdist", required=False, default=10, type=float,
	help="Minimum distance from previously saved board")
ap.add_argument("--invert", required=False, default=0, type=int,
	help="Invert black and white")
ap.add_argument("-l", "--look", required=False, default=1, type=int,
	help="Look at (watch) video while searching for frame pairs")
ap.add_argument("-b", "--border", required=False, default=40, type=int,
        help="Imposes a distance from the border of the frame to not select checkerboards that go out of view")

args = vars(ap.parse_args())
moveThresh = args["moveThresh"]
edgeThresh = args["edgeThresh"]
offset = args["offset"]
delay = args["delay"]
gamma = args["gamma"]
black = args["threshold"]
white = args["white"]
start = args["start"]
prefix = args["prefix"]
video1 = args["video1"]
video2 = args["video2"]
cb_size = args["cb_size"]
chessboardSize = tuple(cb_size[0])
invert = args["invert"]
look = args["look"]
mindist = args["nimdist"]
border = args["border"]

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Define a function to find the closest point to a given point in a list of points
def find_closest_point(point, point_list):
    closest_point = None
    min_distance = float('inf')
    for p in point_list:
        distance = np.linalg.norm(np.array(point) - np.array(p))
        if distance < min_distance:
            min_distance = distance
            closest_point = p
    return closest_point


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

#********Delete previous files
# Get a list of all the file paths that ends with .txt from in specified directory
oldfiles = prefix + "_pair_?_*.png"
fileList = glob.glob(oldfiles) 
# Iterate over the list of filepaths & remove each file.
for filePath in fileList:
    try:
        os.remove(filePath)
        print("Removing old files ")
    except:
        print("Error while deleting file : ", filePath)



#Offsets by xframe, frame frames
loffset = start
cap.set(1,loffset);
roffset=start+offset
cap2.set(1,roffset);

global i
i = 1

## Arrays to store object points and image points from all the images. This allows only keeping distinct new boards
keeperCentersR = [0,0]	
keeperCentersL = [0,0]
keeperDists = [0]

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
            #flatcornL = cornersL.reshape([1, totcorners]) #Need to calculate array size based on checkerboard size

            cornersR = cv2.cornerSubPix(adjusted, cornersR, (11,11), (-1,-1), criteria)
            #flatcornR = cornersR.reshape([1, totcorners]) #Need to calculate array size based on checkerboard size
            #Trying new way to calculate checker distances
            dist_sum = 0
            for i in range(len(cornersR) - 1):
                 for j in range(i + 1, len(cornersR)):
                      dist_sum += np.linalg.norm(cornersR[i] - cornersR[j])

            # Calculate the average distance between each of the corners
            corndist = dist_sum / ((len(cornersR) - 1) * len(cornersR) / 2)
#            print("New e: " + str(corndist))

            #Now calculate the center of each chess board to determine movement
            # Calculate the center of all the corners
            centerR = np.mean(cornersR, axis=0)
            centerL = np.mean(cornersL, axis=0)

            if boards > 0 :
              #find extreme corners to later check if they are too close to border
              xarrayL = cornersL[:,0,0]
              yarrayL = cornersL[:,0,1]
              yminL = np.min(yarrayL)
              xminL = np.min(xarrayL)
              ymaxL = np.max(yarrayL)
              xmaxL = np.max(xarrayL)

              xarrayR = cornersR[:,0,0]
              yarrayR = cornersR[:,0,1]
              yminR = np.min(yarrayR)
              xminR = np.min(xarrayR)
              ymaxR = np.max(yarrayR)
              xmaxR = np.max(xarrayR)

              X1 = float(cornersL[0][0][0])	#convert first 2 corners to x,y coordinates to find proximity to saved boards -- could improve by using center
              Y1 = float(cornersL[0][0][1])
              X2 = float(cornersL[1][0][0])
              Y2 = float(cornersL[1][0][1])

              #compare the new center of the board to the old center of the board to estimate movement
#              newL = np.abs(np.subtract(centerL, old_centerL))
#              newR = np.abs(np.subtract(centerR, old_centerR))

              movementL = np.linalg.norm(centerL - old_centerL)
              movementR = np.linalg.norm(centerR - old_centerR)

              #divide movement by rough estimate of distance of board from cam to allow more movement for closer boards 100* is arbitrary scale
              movementL = 100 * (movementL/corndist)
              movementR = 100 * (movementR/corndist)

              if movementL < moveThresh and movementR < moveThresh: #means board in camera view did not move much from previous capture
                        closeCenterR = find_closest_point(centerR,keeperCentersR)
                        closeCenterL = find_closest_point(centerL,keeperCentersL)
                        closestR = np.linalg.norm(centerR - closeCenterR)
                        closestL = np.linalg.norm(centerL - closeCenterL)
 
                        if closestL > mindist and closestR > mindist:
                            if corndist > edgeThresh :	#corndist is the average size of checkersquares, if large enough, means close enough to keep
                                if xminL > border and xmaxL < (640-border) and yminL > border and ymaxL < (480-border) and xminR > border and xmaxR < (640-border) and yminR > border and ymaxR < (480-border):
                                    #Add frame number to printed video -- could add a toggle option here
                                    #cv2.putText(adjusted,str(frametext+loffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
                                    #cv2.putText(adjusted2,str(frametext+roffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
                                    cv2.imwrite(prefix + "_pair_L_" + str(frametext) + ".png", adjusted)
                                    cv2.imwrite(prefix + "_pair_R_" + str(frametext) + ".png", adjusted2)
                                    print(str(frametext) + "***\t -e:" + str(round(corndist,2)) + "\t-n [" + str(mindist) + "]\t-m \tL:" + str(round(movementL,2)) + " R:" + str(round(movementR,2)) + "\t-b++ ["+str(border)+"]"  )
                                    keeperCentersR.append(centerR)
                                    keeperCentersL.append(centerL)
                                else :
                                    print(str(frametext) + "\t -e++:" + str(round(corndist,2)) + "\t-n [" + str(mindist) + "]\t-m \tL:" + str(round(movementL,2)) + " R:" + str(round(movementR,2)) + "\t-b++ ["+str(border)+"]"  )
                                    if yminR < border or yminL < border:
                                        print("\t\t yminR=" + str(yminR) + " yminL=" + str(yminL))
                                    elif xminR < border or xminL < border:
                                        print("\t*xminR=" + str(xminR) + " xminL=" + str(xminL))
                                    elif (640-xmaxR) < border or (640-xmaxL) < border:
                                        print("\t*xmaxR=" + str(640-xmaxR) + " xmaxL=" + str(640-xmaxL))
                                    elif (480-ymaxR) < border or (480-ymaxL) < border:
                                        print("\t*ymaxR=" + str(480-ymaxR) + " ymaxL=" + str(480-ymaxL))
                            else:
                                 print(str(frametext) + "\t -e++:" + str(round(corndist,2)) + "\t-n [" + str(mindist) + "]\t-m \tL:" + str(round(movementL,2)) + " R:" + str(round(movementR,2)) + "\t-b ["+str(border)+"]"  )
                        else:
                            print(str(frametext) + "\t -e:" + str(round(corndist,2)) + "\t-n++ [" + str(mindist) + "]\t-m \tL:" + str(round(movementL,2)) + " R:" + str(round(movementR,2)) + "\t-b ["+str(border)+"]"  )
              else :
                print(str(frametext) + "\t -e:" + str(round(corndist,2)) + "\t-n [" + str(mindist) + "]\t-m++ \tL:" + str(round(movementL,2)) + " R:" + str(round(movementR,2)) + "\t-b ["+str(border)+"]"  )

            boards = boards + 1
            #save center of board to compare next frame for movement
            old_centerL = centerL
            old_centerR = centerR

#***********
        if look == 1:
            cv2.putText(adjusted,str(frametext+loffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
            cv2.putText(adjusted2,str(frametext+roffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
#            cv2.putText(adjusted2,str(xminR), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))

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
