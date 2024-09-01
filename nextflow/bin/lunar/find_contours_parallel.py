#!/usr/bin/env python3

import cv2
import argparse
import numpy as np
import concurrent.futures
import gc

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

def process_frame(frametext, frame, frame_height, black, white, gamma, minArea):
    clipped = adjust_clip(frame, black=black, white=white)
    adjusted = adjust_gamma(clipped, gamma=gamma)

    imgray = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, black, white, 0)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for c in contours:
        if cv2.contourArea(c) > minArea:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cY_flipped = frame_height - cY  # Flip the y-axis

                mask = np.zeros(imgray.shape, np.uint8)
                cv2.drawContours(mask, [c], 0, 255, -1)
                min_val, max_val, _, _ = cv2.minMaxLoc(imgray, mask=mask)
                mean_val = cv2.mean(frame, mask=mask)
                results.append((frametext, cX, cY_flipped, cv2.contourArea(c), min_val, max_val, mean_val[0]))

    return results

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, type=str, help="filename for the video")
ap.add_argument("-g", "--gamma", required=False, default=0.8, type=float, help="value of gamma")
ap.add_argument("-b", "--black", required=False, default=110, type=int, help="threshold below which is black")
ap.add_argument("-w", "--white", required=False, default=255, type=int, help="threshold above which is white")
ap.add_argument("-s", "--start", required=False, default=1, type=int, help="frame to start at, default = 1")
ap.add_argument("-m", "--minArea", required=False, default=1.5, type=float, help="minimum area to be considered a pulse")
ap.add_argument("-f", "--file", required=True, type=str, help="name of outfile to write pulse data")
ap.add_argument("-t", "--threads", required=False, default=2, type=int, help="number of threads to use when computing")

args = ap.parse_args()

cv2.setNumThreads(args.threads)

writefile = open('contours_' + args.file + '.tab', 'w')
writefile.write("frame\tcX\tcY\tarea\tminI\tmaxI\tmeanI\n")

cap = cv2.VideoCapture(args.video)

# Get the height of the video frame
ret, frame = cap.read()
if not ret:
    print("Failed to read video")
    cap.release()
    exit()

frame_height = frame.shape[0]  # The height of the frame

frametext = 0

# Process frames in smaller batches to limit memory usage
with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frametext += 1
        future = executor.submit(process_frame, frametext, frame, frame_height, args.black, args.white, args.gamma, args.minArea)
        
        # Handle the result as soon as it's ready
        try:
            results = future.result()
            for result in results:
                writefile.write("\t".join(map(str, result)) + "\n")
        except Exception as exc:
            print(f"Generated an exception: {exc}")

        # Explicitly free memory if necessary
        del frame
        gc.collect()

cap.release()
writefile.close()

