#!/usr/bin/env python3

import cv2
import pickle
import argparse
import sys

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.',
        help="path to video frame files default is ./")
ap.add_argument("-pp", "--picklepath", required=False, default='.',
        help="path to pickle calibration files default is ./")
ap.add_argument("-pre", "--prefix", required=False, default='',
        help="prefix for the name of stereofile made by pickle")
ap.add_argument("-w", "--watch", required=False, default=1, type=int,
        help="whether (1) or not (0) to watch video while writing. Default = 1")
ap.add_argument("-l", "--lines", required=False, default=0, type=int,
        help="whether (1) or not (0) to add horizontal lines to check SR. Default = 0")
ap.add_argument("-v1", "--video1", required=True, type=str,
        help="file name for first video")
ap.add_argument("-v2", "--video2", required=True, type=str,
        help="filename for second video")
args = vars(ap.parse_args())
dir_path = args["path"]
if not dir_path.endswith('/'):
    dir_path += '/'
p_path = args["picklepath"]
if not p_path.endswith('/'):
    p_path += '/'
prefix = args["prefix"]
watch = args["watch"]
lines = args["lines"]
video1 = args["video1"]
video2 = args["video2"]

picklefile = p_path + prefix + "_stereomap.pkl"

# Load calibration data
with open(picklefile, 'rb') as f:
    calibration_data = pickle.load(f)

mtx_left = calibration_data['mtx_left']
dist_left = calibration_data['dist_left']
mtx_right = calibration_data['mtx_right']
dist_right = calibration_data['dist_right']
R1 = calibration_data['R1']
R2 = calibration_data['R2']
P1 = calibration_data['P1']
P2 = calibration_data['P2']
Q = calibration_data['Q']
left_map1 = calibration_data['left_map1']
left_map2 = calibration_data['left_map2']
right_map1 = calibration_data['right_map1']
right_map2 = calibration_data['right_map2']

# Rectify original videos
def rectify_video(input_video_left, input_video_right, output_video_left, output_video_right):
    cap_left = cv2.VideoCapture(input_video_left)
    cap_right = cv2.VideoCapture(input_video_right)


    # Get video properties
    frame_width = int(cap_left.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap_left.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap_left.get(cv2.CAP_PROP_FPS)

    # Define the codec and create VideoWriter objects

    fourcc = cv2.VideoWriter_fourcc('h','2','6','4')
    out_left = cv2.VideoWriter(output_video_left, fourcc, fps, (frame_width, frame_height))
    out_right = cv2.VideoWriter(output_video_right, fourcc, fps, (frame_width, frame_height))

    while cap_left.isOpened() and cap_right.isOpened():
        ret_left, frame_left = cap_left.read()
        ret_right, frame_right = cap_right.read()

        if not ret_left or not ret_right:
            break

        # Rectify frames
        rectified_left = cv2.remap(frame_left, left_map1, left_map2, cv2.INTER_LINEAR)
        rectified_right = cv2.remap(frame_right, right_map1, right_map2, cv2.INTER_LINEAR)

        # Write the frames to the output video files
        out_left.write(rectified_left)
        out_right.write(rectified_right)

        #If watch variable is true
        # Show the frames
        if watch == 1:
          if lines == 1:
            for line in range(0, int(rectified_left.shape[0] / 50)):
                rectified_left[line * 50, :] = 255
                rectified_right[line * 50, :] = 255
          cv2.imshow("frame right", rectified_right)
          cv2.moveWindow("frame right",900, 150)
          cv2.imshow("frame left", rectified_left)
          cv2.moveWindow("frame left",1, 150)

       # Hit "q" to close the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap_left.release()
    cap_right.release()
    out_left.release()
    out_right.release()

# Specify the input and output video files
input_video_left = video1
input_video_right = video2

#open a file to write to 
output_video_left = prefix + '_rectifiedL' + '.mkv'
output_video_right = prefix + '_rectifiedR' + '.mkv'

# Rectify and save the videos
rectify_video(input_video_left, input_video_right, output_video_left, output_video_right)

