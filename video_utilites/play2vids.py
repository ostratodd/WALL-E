import numpy as np
import cv2
import argparse
import time

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.', 
        help="path to video frame files default is ./")
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
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
	help="delay time between frames for slo-mo")
args = vars(ap.parse_args())
offset = args["offset"]
delay = args["delay"]
gamma = args["gamma"]
black = args["black"]
white = args["white"]
start = args["start"]
dir_path = args["path"]
video1 = args["video1"]
video2 = args["video2"]



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


frametext=0
while(cap.isOpened()):
    frametext=frametext+1
    ret, frame = cap.read()
    ret, frame2 = cap2.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)


    clipped = adjust_clip(gray, black=black, white=white)
    gamma = gamma if gamma > 0 else 0.1
    adjusted = adjust_gamma(clipped, gamma=gamma)


    clipped2 = adjust_clip(gray2, black=black, white=white)
    adjusted2 = adjust_gamma(clipped2, gamma=gamma)

    cv2.putText(adjusted,str(frametext+loffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
    cv2.putText(adjusted2,str(frametext+roffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))

    cv2.imshow('frame',adjusted)
    cv2.imshow('frame2',adjusted2)

    #move window when first opening
    if frametext == 1:
    	cv2.moveWindow('frame2',642, 0)
    	cv2.moveWindow('frame',0, 0)


    time.sleep(delay)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cap2.release()
cv2.destroyAllWindows()
