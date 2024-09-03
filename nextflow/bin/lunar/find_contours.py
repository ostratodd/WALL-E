#!/usr/bin/env python3

import cv2
import argparse
import time
import numpy as np

def adjust_clip(image, black=0, white=255):
    table = np.concatenate((
        np.zeros(black, dtype="uint8"),
        np.arange(black, white, dtype="uint8"),
        np.full(256-white, 255, dtype="uint8")
    ))
    return cv2.LUT(image, table)

def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** invGamma * 255 for i in np.arange(0, 256)], dtype="uint8")
    return cv2.LUT(image, table)

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, type=str, help="filename for the video")
ap.add_argument("-g", "--gamma", required=False, default=0.8, type=float, help="value of gamma")
ap.add_argument("-b", "--black", required=False, default=110, type=int, help="threshold below which is black")
ap.add_argument("-w", "--white", required=False, default=255, type=int, help="threshold above which is white")
ap.add_argument("-s", "--start", required=False, default=1, type=int, help="frame to start at, default = 1")
ap.add_argument("-d", "--delay", required=False, default=0.03333333, type=float, help="delay time between frames for slo-mo")
ap.add_argument("-m", "--minArea", required=False, default=1.5, type=float, help="minimum area to be considered a pulse")
ap.add_argument("-f", "--file", required=True, type=str, help="name of outfile to write pulse data")
ap.add_argument("-l", "--look", required=False, default=1, type=int, help="whether or not to watch the video during analysis")

args = vars(ap.parse_args())

writefile = open('contours_' + args["file"] + '.tab', 'w')
writefile.write("frame\tcX\tcY\tarea\tminI\tmaxI\tmeanI\n")

cap = cv2.VideoCapture(args["video"])
frametext = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frametext += 1

    clipped = adjust_clip(frame, black=args["black"], white=args["white"])
    adjusted = adjust_gamma(clipped, gamma=args["gamma"])

    imgray = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, args["black"], args["white"], 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cX, cY = None, None
    for c in contours:
        if cv2.contourArea(c) > args["minArea"]:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                mask = np.zeros(imgray.shape, np.uint8)
                cv2.drawContours(mask, [c], 0, 255, -1)
                min_val, max_val, _, _ = cv2.minMaxLoc(imgray, mask=mask)
                mean_val = cv2.mean(frame, mask=mask)
                writefile.write(f"{frametext}\t{cX}\t{500-cY}\t{cv2.contourArea(c)}\t{min_val}\t{max_val}\t{mean_val[0]}\n")
                cv2.drawContours(adjusted, [c], -1, (255, 180, 10), -1)

    if args["look"] == 1:
        if cX is not None and cY is not None:
            cv2.putText(adjusted, f"{frametext},X:{cX}", (30, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 180, 10))
        cv2.imshow('video', adjusted)

        if frametext == 1:
            cv2.moveWindow('video', 0, 0)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    time.sleep(args["delay"])

cv2.destroyAllWindows()
writefile.close()

