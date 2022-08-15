#!/usr/bin/env python

import csv
import cv2
import argparse
import os
import time
import numpy as np

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
ap.add_argument("-ext", "--extension", required=False, default='png', 
        help="extension name. default is 'png'.")
ap.add_argument("-p", "--path", required=False, default='.', 
        help="path to video frame files default is ./")
ap.add_argument("-t", "--time", required=False, type = float, default=0.033333333, 
        help="Time between frames. Default is 1/30 s")
ap.add_argument("-g", "--gamma", required=True, type=float,
	help="value of gamma")
ap.add_argument("-b", "--black", required=True, type=int,
	help="threshold below which is black")
ap.add_argument("-w", "--white", required=True, type=int,
	help="threshold above which is white")
ap.add_argument("-start", "--start", required=True, type=int,
	help="start frame")
ap.add_argument("-stop", "--stop", required=True, type=int,
	help="stop frame")
args = vars(ap.parse_args())
gamma = args["gamma"]
black = args["black"]
white = args["white"]
path = args["path"]
start = args["start"]
stop = args["stop"]

args = vars(ap.parse_args())

# Arguments
dir_path = path
ext = args['extension']
timedelay = args['time']

images = []
#for f in os.listdir(dir_path):
#    if f.endswith(ext):
#        images.append(f)
#images.sort()

#**********************Read in Analyzed Pulses

pulse = []
pulsex = 30
pulsey = 400

with open('AnalyzedPulses.csv', 'rb') as csvfile:
     pulsefile = csv.reader(csvfile, delimiter=',', quotechar='|')
     for row in pulsefile:
	pulse.append(row)

for count in range(start,stop):
    image = str(pulse[count][1])
    image = image.zfill(6)
    image = image + '.png'
    image_path = os.path.join(dir_path, image)

    frame = cv2.imread(image_path)
    original = frame
    clipped = adjust_clip(original, black=black, white=white)
    gamma = gamma if gamma > 0 else 0.1
    adjusted = adjust_gamma(clipped, gamma=gamma)
    time.sleep(timedelay)

    #write the frame number for viewing
    image = image.strip('.png')
#
#    for i in range(len(pulse)):
#    fstart = pulse[i][1]
#    fnow = int(image)
#	print fnow, fstart
#	if fnow == fstart:
#		print ("Current frame matches",pulse[i][2]," x y ",pulse[i][4], pulse[i][5])
#		fpulses.append(pulse[i])
#    
    frametext = image
#    for p in range(len(fpulses)):
    pulsex = int(pulse[count][2])
    pulsey = int(pulse[count][3])
    area = pulse[count][4]
    pn = pulse[count][8]
    plotx = pulsex
    if plotx > 525:
	plotx = 525

    cv2.circle(adjusted, (pulsex, 400-pulsey), 10, (255,255,255), 1)
    cv2.putText(adjusted,"n="+pn+" a="+area, (plotx,440-pulsey), cv2.FONT_HERSHEY_SIMPLEX, .4, (255,180,10))
    cv2.putText(adjusted,str(pulsex)+" "+str(pulsey), (35,420), cv2.FONT_HERSHEY_SIMPLEX, .4, (255,180,10))
    cv2.putText(adjusted,frametext, (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
    cv2.imshow('video',adjusted)
    if (cv2.waitKey(1) & 0xFF) == ord('q'): # Hit `q` to exit
        print(image)
        break

# Release everything if job is finished
cv2.destroyAllWindows()

