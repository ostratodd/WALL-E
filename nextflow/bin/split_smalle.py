#!/usr/bin/env python3

import numpy as np
import cv2
import argparse
import time

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.',
        help="path to video file not including filename. Default is ./")
ap.add_argument("-v", "--video", required=True, type=str,
        help="file name for first video")
ap.add_argument("-V1", "--leftvideo", required=True, type=str,
        help="file name for left video output")
ap.add_argument("-V2", "--rightvideo", required=True, type=str,
        help="file name for first video")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
        help="frame to start at default = 1")
ap.add_argument("-e", "--end", required=False, default=0, type=int,
        help="last frame for clip")
args = vars(ap.parse_args())
start = args["start"]
endframe = args["end"]
dir_path = args["path"]
video = args["video"]
leftvideo = args["leftvideo"]
rightvideo = args["rightvideo"]


# Open the input video
input_video_path = video  # Replace with your video file path
cap = cv2.VideoCapture(input_video_path)

# Get the width and height of the video frames
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Calculate the width of the left and right halves
half_width = frame_width // 2

new_filename_l = leftvideo + "_cl_" + str(start) + "_" + str(endframe) + ".mkv"
new_filename_r = rightvideo + "_cl_" + str(start) + "_" + str(endframe) + ".mkv"

print("New file name:" + new_filename_l)

out_l = cv2.VideoWriter(new_filename_l,cv2.VideoWriter_fourcc('H','2','6','4'), 30, (half_width, frame_height))
out_r = cv2.VideoWriter(new_filename_r,cv2.VideoWriter_fourcc('H','2','6','4'), 30, (half_width, frame_height))

frametext=0
# Process each frame
while cap.isOpened():
    frametext=frametext+1
    ret, frame = cap.read()
    if not ret:
        break
    
    # Split the frame into left and right halves
    left_half = frame[:, :half_width]
    right_half = frame[:, half_width:]
    
    # Write the halves to their respective video files
    out_l.write(left_half)
    out_r.write(right_half)

    if endframe > 0:
        if frametext == endframe:
            break


# Release everything
cap.release()
out_l.release()
out_r.release()
cv2.destroyAllWindows()
