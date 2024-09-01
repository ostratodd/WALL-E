#!/usr/bin/env python3

import numpy as np
import cv2
import argparse
import time
import os

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.',
                help="path to video frame files; default is ./")
ap.add_argument("-g", "--gamma", required=False, default=0.8, type=float,
                help="value of gamma - a correction for human visualization")
ap.add_argument("-b", "--black", required=False, default=110, type=int,
                help="threshold below which is black. Value ranges from 0-255.")
ap.add_argument("-mb", "--multipleb", required=False, nargs=3, type=int,
                help="three black threshold values for multiple adjustments. Values range from 0-255.")
ap.add_argument("-w", "--white", required=False, default=255, type=int,
                help="threshold above which is white. Values range from 0-255")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
                help="frame to start at; default = 1")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
                help="delay time between frames for slo-mo")
ap.add_argument("-v", "--view", required=False, default=1, type=int,
                help="choose whether to view video (1) or not (0)")
args = vars(ap.parse_args())

delay = args["delay"]
gamma = args["gamma"]
black = args["black"]
white = args["white"]
multipleb = args["multipleb"]
start = args["start"]
view = args["view"]
dir_path = args["path"]

# Check if dir_path exists
if not os.path.exists(dir_path):
    print("The specified directory path does not exist.")
    exit()

# Function to adjust clip
def adjust_clip(image, black=0, white=255):
    zeros = np.array([i * 0 for i in np.arange(0, black)]).astype("uint8")
    whites = np.array([(i * 0) + 255 for i in np.arange(0, 256 - white)]).astype("uint8")
    table = np.array([i + black for i in np.arange(0, white - black)]).astype("uint8")
    table = np.concatenate((zeros, table, whites))
    return cv2.LUT(image, table)

# Function to adjust gamma
def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

# Process each video file in the directory
for filename in os.listdir(dir_path):
    if filename.endswith((".mp4", ".avi", ".mov", ".mkv")):  # Add other video formats if needed
        video_path = os.path.join(dir_path, filename)

        # Create a separate output file for each video
        video_name = os.path.splitext(filename)[0]
        out_path = os.path.join(dir_path, f"{video_name}_brightness_26Aug_2B.csv")
        f = open(out_path, "w+")

        cap = cv2.VideoCapture(video_path)
        cap.set(1, start)

        frametext = 0
        while cap.isOpened():
            frametext += 1
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Handle multiple black thresholds
            if multipleb:
                bright_values = []
                for b in multipleb:
                    clipped = adjust_clip(gray, black=b, white=white)
                    adjusted = adjust_gamma(clipped, gamma=gamma)
                    bright = format(adjusted.mean(), '.3f')
                    bright_values.append(bright)
                f.write(f"{frametext + start}," + ",".join(bright_values) + f",{gray.mean():.3f}\n")
            else:
                clipped = adjust_clip(gray, black=black, white=white)
                adjusted = adjust_gamma(clipped, gamma=gamma)
                bright = format(adjusted.mean(), '.3f')
                f.write(f"{frametext + start},{bright},{gray.mean():.3f}\n")

            if view == 1:
                # Display the first adjusted brightness value if multiple values are calculated
                cv2.putText(adjusted, str(frametext + start), (35, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 180, 10))
                cv2.putText(adjusted, bright_values[0] if multipleb else bright, (175, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 180, 10))
                cv2.putText(adjusted, str(gray.mean()), (375, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 180, 10))
                cv2.imshow('frame', adjusted)

            time.sleep(delay)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        f.close()

cv2.destroyAllWindows()

