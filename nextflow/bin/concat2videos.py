#!/usr/bin/env python3

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
ap.add_argument("-o", "--output", required=True, type=str,
	help="filename for concatenated output video")

args = vars(ap.parse_args())
dir_path = args["path"]
video1 = args["video1"]
video2 = args["video2"]
outfile = args["output"]


# define input videos
video1 = cv2.VideoCapture(video1)
video2 = cv2.VideoCapture(video2)

# get properties of input videos
fps = int(video1.get(cv2.CAP_PROP_FPS))
width = int(video1.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video1.get(cv2.CAP_PROP_FRAME_HEIGHT))

# define output video writer
out = cv2.VideoWriter(outfile,cv2.VideoWriter_fourcc('H','2','6','4'), fps, (width,height))


# concatenate videos
while video1.isOpened():
    ret1, frame1 = video1.read()
    if ret1:
        out.write(frame1)
    else:
        break

while video2.isOpened():
    ret2, frame2 = video2.read()
    if ret2:
        out.write(frame2)
    else:
        break

# release resources
video1.release()
video2.release()
out.release()
cv2.destroyAllWindows()



