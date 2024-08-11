#!/usr/bin/env python3

import numpy as np
import cv2
import argparse
import math
import os, errno
import glob
import sys

#Script to go through video to find chessboard photos in stereo videos. A movement threshold compares current to previous
#location of board because if the board is moving quickly, unsynced l/r video causes much noise in calibration, mainly in WALLE

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v1", "--video1", required=True, type=str,
	help="file name for first video")
ap.add_argument("-v2", "--video2", required=True, type=str,
	help="filename for second video")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
	help="frame to start at default = 1")
ap.add_argument ('-c', '--cb_size', nargs=2, type=int, action = 'append', required=True,
        help="need to specify checkerboard size e.g. -c 8 6")
ap.add_argument("-d", "--offset", required=False, default=0, type=int,
	help="number of frames to offset two videos, positive or negative")
ap.add_argument("-l", "--look", required=False, default=1, type=int,
	help="Look at (watch) video while searching for frame pairs")
ap.add_argument("-o", "--outfile", required=True, type=str,
        help="File name to output a csv file with frame numbers and checkerboard data")

args = vars(ap.parse_args())
offset = args["offset"]
start = args["start"]
video1 = args["video1"]
video2 = args["video2"]
cb_size = args["cb_size"]
chessboardSize = tuple(cb_size[0])
look = args["look"]
outfile = args["outfile"]

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

cap = cv2.VideoCapture(video1)
cap2 = cv2.VideoCapture(video2)

# Get the width and height of the video frames
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Get the total number of frames in each video
total_frames1 = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
total_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))
total_frames = min(total_frames1, total_frames2)

print(f"Total Frames in this Video: {total_frames} ")


#Offsets by xframe, frame frames
loffset = start
cap.set(1,loffset);
roffset=start+offset
cap2.set(1,roffset);

global i
i = 1
boards=0	#count chessboards
frametext=0

with open(outfile, 'w') as f:
     f.write("\t".join(['frame','dist', 'x', 'y', 'xmin','xmax','ymin','ymax']) )
     f.write("\n")
print("\t".join(['frame','dist', 'x', 'y', 'xmin','xmax','ymin','ymax']) )

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

#New code to add corners
        if retL and retR == True:
            totcorners = 2 * (chessboardSize[0] * chessboardSize[1])
            cornersL = cv2.cornerSubPix(gray, cornersL, (11,11), (-1,-1), criteria)
            cornersR = cv2.cornerSubPix(gray2, cornersR, (11,11), (-1,-1), criteria)

            dist_sumR = 0
            for i in range(len(cornersR) - 1):
                 for j in range(i + 1, len(cornersR)):
                      dist_sumR += np.linalg.norm(cornersR[i] - cornersR[j])
            dist_sumL = 0
            for i in range(len(cornersL) - 1):
                 for j in range(i + 1, len(cornersL)):
                      dist_sumL += np.linalg.norm(cornersL[i] - cornersL[j])

            # Calculate the average distance between each of the corners as an estimate of distance from camera
            corndistR = dist_sumR / ((len(cornersR) - 1) * len(cornersR) / 2)
            corndistL = dist_sumL / ((len(cornersL) - 1) * len(cornersL) / 2)
            corndist = (corndistR + corndistL) /2

            # Calculate the center of all the corners
            centerR = np.mean(cornersR, axis=0)
            centerL = np.mean(cornersL, axis=0)
            centerX = (centerR[0][0] + centerL[0][0])/2	#average center X for L and R views of boards
            centerY = (centerR[0][1] + centerL[0][1])/2

            if boards > 0 :
              #find extreme corners to later check if they are too close to border
              xarrayL = cornersL[:,0,0]
              yarrayL = cornersL[:,0,1]
              xarrayR = cornersR[:,0,0]
              yarrayR = cornersR[:,0,1]
              ymin = min(np.min(yarrayL,axis=0),np.min(yarrayR,axis=0))
              xmin = min(np.min(xarrayL,axis=0),np.min(xarrayR,axis=0))
              ymax = max(np.max(yarrayL,axis=0),np.max(yarrayR,axis=0))
              xmax = max(np.min(xarrayL,axis=0),np.max(xarrayR,axis=0))


              frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
              with open(outfile, 'a') as f:
                 f.write("\t".join([str(frame_num), str(round(corndist, 2)), \
                    str(round(centerX,2)), str(round(centerY,2)),
                    str(round(xmin,2)), str(round(xmax,2)), str(round(ymin,2)), \
                    str(round(ymax,2))]))
                 f.write("\n")   
              print("\t".join([str(frame_num), str(round(corndist, 2)), \
                    str(round(centerX,2)), str(round(centerY,2)),
                    str(round(xmin,2)), str(round(xmax,2)), str(round(ymin,2)), \
                    str(round(ymax,2))]))
              if look == 1 :
                # Draw the corners
                cv2.drawChessboardCorners(gray, chessboardSize, cornersL, ret)
                cv2.drawChessboardCorners(gray2, chessboardSize, cornersR, ret2)
            boards = boards + 1


#***********
        if look == 1:
            cv2.putText(gray,str(frametext+loffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
            cv2.putText(gray2,str(frametext+roffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))

            cv2.imshow('frame',gray)
            cv2.imshow('frame2',gray2)

            #move window when first opening
            if frametext == 1:
                cv2.moveWindow('frame2',642, 0)
                cv2.moveWindow('frame',0, 0)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
        if frametext % 50 == 0:
            progress = (frametext / total_frames) * 100
            print(f"Processed {frametext} frames out of {total_frames} ({progress:.2f}%)")

    else:
        break

cap.release()
cap2.release()
cv2.destroyAllWindows()
