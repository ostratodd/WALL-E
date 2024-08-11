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
        help="prefix for the name of the image files before the required CH")
ap.add_argument("-sq", "--squareSize", required=True, type=float,
        help="Size of an individual square of the checkerboard in mm")
ap.add_argument("-e", "--extension", required=False, default="png", type=str,
        help="extension of files. Default = png")
ap.add_argument("-l", "--look", required=False, default=0, type=int,
        help="Look at (view) images 1=yes 0=no.vDefault = 0")
args = vars(ap.parse_args())
dir_path = args["path"]
if not dir_path.endswith('/'):
    dir_path += '/'
p_path = args["picklepath"]
if not p_path.endswith('/'):
    p_path += '/'
prefix = args["prefix"]
squareSize = args["squareSize"]
ext = args["extension"]
look = args["look"]

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
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
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

    cap_left.release()
    cap_right.release()
    out_left.release()
    out_right.release()

# Specify the input and output video files
input_video_left = 'video_data/clips/cfr_2024bocassmalle4calL_cl_1_5400.mkv'
input_video_right = 'video_data/clips/cfr_2024bocassmalle4calR_cl_1_5400.mkv'
output_video_left = 'rectified_left.avi'
output_video_right = 'rectified_right.avi'

# Rectify and save the videos
rectify_video(input_video_left, input_video_right, output_video_left, output_video_right)

