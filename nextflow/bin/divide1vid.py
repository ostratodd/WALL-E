#!/usr/bin/env python3

import numpy as np
import cv2
import argparse
import time
import ntpath

def path_leaf(path):                    #function to extract basename from video filenames
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.', 
        help="path to video frame files default is ./")
ap.add_argument("-v1", "--video", required=True, type=str,
	help="file name for first video")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
	help="frame to start at default = 1")
ap.add_argument("-o", "--offset", required=False, default=0, type=int,
	help="number of frames to offset two videos, positive or negative")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
	help="delay time between frames for slo-mo")
args = vars(ap.parse_args())
offset = args["offset"]
start = args["start"]
dir_path = args["path"]
video = args["video"]

video_path = dir_path + video
cap = cv2.VideoCapture(video_path)

#get base name for video
vid = path_leaf(video)


# Check if video opened successfully
if not cap.isOpened(): 
    print("Error opening video")

# Get the Default resolutions and fps
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
print("FPS = " + str(fps) + " Frame sizes: w:" + str(frame_width) + " h:" + str(frame_height) )

lpath = dir_path + "left" + vid[:-4] + '.mkv'
rpath = dir_path + "right" + vid[:-4] + '.mkv'

# Define the codec and create VideoWriter objects.
out1 = cv2.VideoWriter(lpath  ,cv2.VideoWriter_fourcc('H','2','6','4'), fps, (frame_width//2, frame_height))
out2 = cv2.VideoWriter(rpath ,cv2.VideoWriter_fourcc('H','2','6','4'), fps, (frame_width//2, frame_height))

print("writing " + lpath)
print("writing " + rpath)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Dividing the frame into two halves
    left_half = frame[:, :frame_width//2]
    right_half = frame[:, frame_width//2:]

    # Writing the two halves into two separate video files
    out1.write(left_half)
    out2.write(right_half)

# Release everything when the job is finished
cap.release()
out1.release()
out2.release()
cv2.destroyAllWindows()

