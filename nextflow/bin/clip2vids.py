#!/usr/bin/env python3

import numpy as np
import cv2
import argparse
import time
import ntpath


def path_leaf(path):			#function to extract basename from video filenames
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v1", "--video1", required=True, type=str,
	help="file name for first video")
ap.add_argument("-v2", "--video2", required=True, type=str,
	help="filename for second video")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
	help="frame to start at default = 1")
ap.add_argument("-e", "--end", required=False, default=0, type=int,
	help="frame to end clipping")
ap.add_argument("-o", "--offset", required=False, default=0, type=int,
	help="number of frames to offset two videos, positive or negative")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
	help="delay time between frames for slo-mo")
ap.add_argument("-w", "--watch", required=False, default=1, type=int,
	help="whether or not to watch video while clipping")
args = vars(ap.parse_args())
offset = args["offset"]
delay = args["delay"]
start = args["start"]
end = args["end"]
video1 = args["video1"]
video2 = args["video2"]
watch = args["watch"]

V1 = path_leaf(video1)
V2 = path_leaf(video2)

endframe = end - start

cap = cv2.VideoCapture(video1)
cap2 = cv2.VideoCapture(video2)

#Offsets by xframe, frame frames
loffset = start
cap.set(1,loffset);
roffset=start+offset
cap2.set(1,roffset);

frameSize = (640, 480)


#should check here to make sure video files contains 3 letter extension
new_filename_l = video1[:-4] + "_clip_" + str(start) + "_" + str(end)+ ".mkv"
new_filename_r = video2[:-4] + "_clip_" + str(start) + "_" + str(end)+ ".mkv"

out_l = cv2.VideoWriter(new_filename_l,cv2.VideoWriter_fourcc('H','2','6','4'), 30, frameSize)
out_r = cv2.VideoWriter(new_filename_r,cv2.VideoWriter_fourcc('H','2','6','4'), 30, frameSize)


frametext=0
while(cap.isOpened()):
    frametext=frametext+1
    ret, frame = cap.read()
    ret, frame2 = cap2.read()

    if watch == 1:
        cv2.imshow('left camera',frame)
        cv2.imshow('right camera',frame2)

        #move window when first opening
        if frametext == 1:
            cv2.moveWindow('right camera',642, 0)
            cv2.moveWindow('left camera',0, 0)
    time.sleep(delay)

    #write the frame to outfile
    out_l.write(frame)
    out_r.write(frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if frametext == endframe:
        break

cap.release()
cap2.release()
cv2.destroyAllWindows()
