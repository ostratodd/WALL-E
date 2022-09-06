#!/usr/bin/env python3

import cv2
import argparse
import os
import time
import numpy as np
import pandas as pd

frameSize = (640,480)

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

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v1", "--video1", required=True, type=str,
        help="file name for first video")
ap.add_argument("-v2", "--video2", required=True, type=str,
        help="filename for second video")
ap.add_argument("-g", "--gamma", required=False, default=0.8,type=float,
        help="value of gamma")
ap.add_argument("-b", "--black", required=False, default=110, type=int,
        help="threshold below which is black")
ap.add_argument("-w", "--white", required=False, default=255, type=int,
        help="threshold above which is white")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
        help="frame to start at default = 1")
ap.add_argument("-o", "--offset", required=False, default=0, type=int,
        help="number of frames to offset two videos, positive or negative")
ap.add_argument("-d", "--delay", required=False, default=2, type=float,
        help="delay time between frames for slo-mo")
ap.add_argument("-m", "--minArea", required=False, default=2, type=float,
        help="Minimum area of blob to be recognized as blob")
ap.add_argument("-f", "--file", required=True, type=str,
        help="Name of tab delimited file of stereo pulses")

args = vars(ap.parse_args())
offset = args["offset"]
delay = args["delay"]
gamma = args["gamma"]
black = args["black"]
white = args["white"]
start = args["start"]
video1 = args["video1"]
video2 = args["video2"]
file = args["file"]
minArea = args["minArea"]


watch =1

#Need to read stereo file here
#*****************************
table = pd.read_csv(file, delimiter = '\t')
sorted = table.sort_values(['pulse', 'camera'])
sorted = sorted.reset_index(drop=True)          #re-index
print(sorted)

cap = cv2.VideoCapture(video1)
cap2 = cv2.VideoCapture(video2)

frametext=0
while(cap.isOpened() and cap2.isOpened() ):
    capret1, frame = cap.read()
    capret2, frame2 = cap2.read()
    if capret1 == True and capret2 == True :

        frametext=frametext+1

        original = frame
        original2 = frame2

        clipped = adjust_clip(original, black=black, white=white)
        clipped2 = adjust_clip(original2, black=black, white=white)

        gamma = gamma if gamma > 0 else 0.1

        adjusted = adjust_gamma(clipped, gamma=gamma)
        adjusted2 = adjust_gamma(clipped2, gamma=gamma)

        #Loop through pulse data to see if any are on current frame
        for index, row in sorted.iterrows():
            if int(row['frame']) == frametext :
                print("Pulse " + str(row['pulse']) + " is detected on frame " + row['camera'] + " " + str(frametext) + "X,Y: " + str(row['cX']) + "," + str(640-row['cY']) )
                color = (0,0,255)
                color = (0,255,0)
                color = (255,0,0)
                txtoffset = 25
                font = cv2.FONT_HERSHEY_PLAIN
                if row['camera'] == 'left' :
                    cv2.circle(adjusted,(row['cX'], 500-row['cY']), 4, color, 2)
                    cv2.putText(adjusted, row['pulse'], (row['cX'] + txtoffset, 500-row['cY']), font, 1, color)
                elif row['camera'] == 'right' :
                    cv2.circle(adjusted2,(row['cX'], 500-row['cY']), 4, color, 2 )
                    cv2.putText(adjusted2, row['pulse'], (row['cX'] + txtoffset, 500-row['cY']), font, 1, color)


        if watch == 1:
            #write the frame number for viewing
            cv2.putText(adjusted, str(frametext), (30,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
            cv2.putText(adjusted2, str(frametext), (30,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))

            cv2.imshow('video',adjusted)
            cv2.imshow('video2',adjusted2)


            time.sleep(delay)


            #move window when first opening
            if frametext == 1:
                cv2.moveWindow('video2',642, 0)
                cv2.moveWindow('video',0, 0)

            if (cv2.waitKey(1) & 0xFF) == ord('q'): # Hit `q` to exit
                break
    else:
        break
# Release everything if job is finished
cv2.destroyAllWindows()

