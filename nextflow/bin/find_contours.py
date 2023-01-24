#!/usr/bin/env python3

import cv2
import argparse
import os
import time
import numpy as np
#from matplotlib import pyplot as plt

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
ap.add_argument("-d", "--delay", required=False, default=0.03333333, type=float,
        help="delay time between frames for slo-mo")
ap.add_argument("-m", "--minArea", required=False, default=1.5, type=float,
        help="minimumArea to be considered a pulse")
ap.add_argument("-f", "--file", required=True, type=str,
        help="Name of outfile to write pulse data")
ap.add_argument("-l", "--look", required=False, default=1, type=int,
        help="whether or not to look at (watch) the video during analysis")

args = vars(ap.parse_args())
offset = args["offset"]
delay = args["delay"]
gamma = args["gamma"]
black = args["black"]
white = args["white"]
start = args["start"]
video1 = args["video1"]
video2 = args["video2"]
minArea = args["minArea"]
file = args["file"]
watch = args["look"]


writefile = open('contours_' + file + '.tab', 'w')

#Print Header
print("camera\tframe\tx\ty\tarea\tminI\tmaxI\tmeanI" )
#writefile.write("camera\tframe\tx\ty\tarea\tminI\tmaxI\tmeanI\n" )
writefile.write("camera\tframe\tcX\tcY\n" )

#create array to later plot x,y
rxlist = [ ]
rylist = [ ]

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

        time.sleep(delay)

        #analyze contours for left video
        imgray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,black,white,0)
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        contourcount = 0
        cX = 0
        cY = 0
        for c in contours:
            if cv2.contourArea(c) > minArea:
                 contourcount = contourcount + 1
                 M = cv2.moments(c)
                 cX = int(M["m10"] / M["m00"])
                 cY = int(M["m01"] / M["m00"])
                 center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                 mask = np.zeros(imgray.shape,np.uint8)
                 cv2.drawContours(mask,[c],0,255,-1)
                 mean_val = cv2.mean(frame,mask = mask)
                 min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(imgray,mask = mask)
                 print("left\t" + str(frametext) + "\t" + str(cX) + "\t" + str(500-cY) + "\t" + str(cv2.contourArea(c) ) + "\t" + 
	             str(min_val) + "\t" + str(max_val) + "\t" + str(mean_val[0]) )
    #             writefile.write("left\t" + str(frametext) + "\t" + str(cX) + "\t" + str(500-cY) + "\t" + str(cv2.contourArea(c) ) + "\t" + 
    #	         str(min_val) + "\t" + str(max_val) + "\t" + str(mean_val[0]) + "\n" )
                 writefile.write("left\t" + str(frametext) + "\t" + str(cX) + "\t" + str(500-cY) + "\n")
                 cv2.drawContours(adjusted,contours,-1,(255,180,10),-1)
            else:
                 cv2.drawContours(adjusted,contours,-1,(0,0,0),-1)


        #analyze contours for right video
        imgray2 = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
        ret2,thresh2 = cv2.threshold(imgray2,black,white,0)
        contours2, hierarchy = cv2.findContours(thresh2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        contourcount2 = 0
        cX2 = 0
        cY2 = 0
        for d in contours2:
            if cv2.contourArea(d) > minArea:
                 contourcount2 = contourcount2 + 1
                 M2 = cv2.moments(d)
                 cX2 = int(M2["m10"] / M2["m00"])
                 cY2 = int(M2["m01"] / M2["m00"])
                 center = (int(M2["m10"] / M2["m00"]), int(M2["m01"] / M2["m00"]))
                 mask = np.zeros(imgray2.shape,np.uint8)
                 cv2.drawContours(mask,[d],0,255,-1)
                 mean_val2 = cv2.mean(frame2,mask = mask)
                 min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(imgray2,mask = mask)
                 print("right\t" + str(frametext) + "\t" + str(cX2) + "\t" + str(500-cY2) + "\t" + str(cv2.contourArea(d) ) + "\t" + 
	             str(min_val2) + "\t" + str(max_val2) + "\t" + str(mean_val2[0]) )
     #             writefile.write("right\t" + str(frametext) + "\t" + str(cX2) + "\t" + str(500-cY2) + "\t" + str(cv2.contourArea(d) ) + "\t" + 
    #	         str(min_val2) + "\t" + str(max_val2) + "\t" + str(mean_val2[0]) + "\n" )
                 writefile.write("right\t" + str(frametext) + "\t" + str(cX2) + "\t" + str(500-cY2) + "\n")

                 cv2.drawContours(adjusted2,contours2,-1,(100,180,10),-1)
            else:
                 cv2.drawContours(adjusted2,contours2,-1,(0,0,0),-1)
        if watch == 1:
            #write the frame number for viewing
            cv2.putText(adjusted, str(frametext)+",X:"+str(cX), (30,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
            cv2.putText(adjusted2, str(frametext)+",X:"+str(cX2), (30,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
    #        cv2.putText(adjusted2, str(frametext), (30,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
#            cv2.imshow('video',adjusted)
            cv2.imshow('video2',adjusted2)

            #move window when first opening
            if frametext == 1:
                cv2.moveWindow('video2',642, 0)
                cv2.moveWindow('video',0, 0)

            if (cv2.waitKey(1) & 0xFF) == ord('q'): # Hit `q` to exit
                print(image)
                break
    else:
        break
# Release everything if job is finished
cv2.destroyAllWindows()

#plot.scatter(rxlist,rylist)
#plot.show()
