#!/usr/bin/env python

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
ap.add_argument("-ext", "--extension", required=False, default='png', help="extension name. default is 'png'.")
ap.add_argument("-t", "--time", required=False, type = float, default=0.033333333, help="Time between frames. Default is 1/30 s")
ap.add_argument("-g", "--gamma", required=True, type=float,
	help="value of gamma")
ap.add_argument("-b", "--black", required=True, type=int,
	help="threshold below which is black")
ap.add_argument("-w", "--white", required=True, type=int,
	help="threshold above which is white")
args = vars(ap.parse_args())
gamma = args["gamma"]
black = args["black"]
white = args["white"]

args = vars(ap.parse_args())

# Arguments
dir_path = '.'
ext = args['extension']
timedelay = args['time']

images = []
for f in os.listdir(dir_path):
    if f.endswith(ext):
        images.append(f)
images.sort()


#Print Header
print("Frame"+","+"X"+","+"Y")

for image in images:
    image_path = os.path.join(dir_path, image)
    frame = cv2.imread(image_path)
    original = frame
    clipped = adjust_clip(original, black=black, white=white)
    gamma = gamma if gamma > 0 else 0.1
    adjusted = adjust_gamma(clipped, gamma=gamma)
    time.sleep(timedelay)


    imgray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,black,white,0)
    _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contourcount = 0


    #Now count the contours
    thecX = 0
    thecY = 0
    themeanval = 0
    for c in contours:
	if cv2.contourArea(c) > 0:
             contourcount = contourcount + 1
             M = cv2.moments(c)
             cX = int(M["m10"] / M["m00"])
             cY = int(M["m01"] / M["m00"])
             center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
             mask = np.zeros(imgray.shape,np.uint8)
             cv2.drawContours(mask,[c],0,255,-1)
             mean_val = cv2.mean(frame,mask = mask)
	     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(imgray,mask = mask)

             #This is adding each centroid to a list
             cv2.rectangle(adjusted, (cX-10,cY-10), (cX+10,cY+10), (155, 0, 0), 2)

	     #strip the suffix off the file name to leave just frame number
             image = image.strip('.png')

	     print(image+","+str(cX)+","+str(400-cY))

#	     #Keep just the pulse around 600 for now
#             if cX > 40 and cX < 60:
#                  thecX = cX
#                  thecY = cY
#		  themeanval = mean_val[0]
#                  cv2.rectangle(adjusted, (45,265), (65,285), (155, 0, 0), 2)
#                  print("x50"+ "\t" + str(image) + "\t" + str(themeanval))
#
#             if cX > 80 and cX < 100:
#                  thecX = cX
#                  thecY = cY
#		  themeanval = mean_val[0]
#		  cv2.rectangle(adjusted, (90,240), (110,260), (155, 0, 0), 2)
#                  print("x80"+ "\t" + str(image) + "\t" + str(themeanval))
#


    #write the frame number for viewing
    frametext = image
    cv2.putText(adjusted,frametext, (30,450), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)

    frametext3 = str(contourcount)+" x="+ str(thecX) + " y=" + str(thecY) + " mI=" + str(themeanval)
    cv2.putText(adjusted,frametext3, (30,400), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255))
#    cv2.putText(adjusted,'0', (50,278), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)
#    cv2.putText(adjusted,'x', (90,250), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)


    cv2.imshow('video',adjusted)
    if (cv2.waitKey(1) & 0xFF) == ord('q'): # Hit `q` to exit
        print(image)
        break

# Release everything if job is finished
cv2.destroyAllWindows()

