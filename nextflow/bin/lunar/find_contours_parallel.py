#!/usr/bin/env python3

import cv2
import argparse
import numpy as np
import concurrent.futures
import gc
import glob

def adjust_clip(image, black=0):
    # Adjusts pixel values: sets all pixel values below `black` to 0
    table = np.concatenate((
        np.zeros(black, dtype="uint8"),  # Set all pixel values below 'black' to 0
        np.arange(black, 256, dtype="uint8")  # Keep pixel values above 'black' unchanged
    ))
    return cv2.LUT(image, table)

def process_frame(frametext, frame, frame_height, black, minArea, maxArea, video_file):
    clipped = adjust_clip(frame, black=black)  # Apply threshold using clipping

    imgray = cv2.cvtColor(clipped, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    
    # Apply thresholding: Pixels below `black` will become 0
    _, thresh = cv2.threshold(imgray, black, 255, cv2.THRESH_TOZERO)
    
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    for c in contours:
        area = cv2.contourArea(c)
        if minArea <= area <= maxArea:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cY_flipped = frame_height - cY  # Flip the y-axis

                mask = np.zeros(imgray.shape, np.uint8)
                cv2.drawContours(mask, [c], 0, 255, -1)
                min_val, max_val, _, _ = cv2.minMaxLoc(imgray, mask=mask)
                mean_val = cv2.mean(frame, mask=mask)
                
                # Debugging output to check contour area and frame number
                #print(f"Frame {frametext}: Contour with area {area} passed filter from video {video_file}")

                results.append((frametext, cX, cY_flipped, area, min_val, max_val, mean_val[0], video_file))

    return results

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--videos", required=True, type=str, help="pattern for the video filenames (e.g., '/Users/oakley/Downloads/out_*.mp4')")
ap.add_argument("-b", "--black", required=False, default=110, type=int, help="threshold below which is black")
ap.add_argument("-m", "--minArea", required=False, default=1.5, type=float, help="minimum area to be considered a pulse")
ap.add_argument("-x", "--maxArea", required=False, default=1000.0, type=float, help="maximum area to be considered a pulse")
ap.add_argument("-f", "--file", required=True, type=str, help="name of outfile to write pulse data")
ap.add_argument("-t", "--threads", required=False, default=2, type=int, help="number of threads to use when computing")
ap.add_argument("-bt", "--brightnessThreshold", required=False, default=200, type=float, help="average brightness threshold to skip frames when lights are on")

args = ap.parse_args()

cv2.setNumThreads(args.threads)

writefile = open('contours_' + args.file + '.tab', 'w')
writefile.write("frame\tcX\tcY\tarea\tminI\tmaxI\tmeanI\tvideo\n")  # Added 'video' column

# Use glob to find all video files matching the pattern
video_files = sorted(glob.glob(args.videos))

if not video_files:
    print(f"No videos found matching pattern: {args.videos}")
    exit()

# Initialize cumulative frame count
cumulative_frame = 0

# Process each video file
for video_file in video_files:
    cap = cv2.VideoCapture(video_file)
    print(f"Processing video file: {video_file}")
    if not cap.isOpened():
        print(f"Failed to open video file: {video_file}")
        continue

    # Get the height of the video frame
    ret, frame = cap.read()
    if not ret:
        print(f"Failed to read from video file: {video_file}")
        cap.release()
        continue

    frame_height = frame.shape[0]  # The height of the frame
    local_frame_number = 0  # Frame count for the current video

    # Use a thread pool executor to process frames in parallel
    max_tasks = args.threads * 2  # Limit the number of concurrent tasks
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_frame = {}  # Dictionary to keep track of submitted futures
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Calculate the average brightness of the frame
            average_brightness = cv2.mean(frame)[0]

            # Check if the brightness exceeds the threshold
            if average_brightness > args.brightnessThreshold:
                #print(f"Skipping frame {local_frame_number + 1} in {video_file} due to high brightness ({average_brightness:.2f})")
                local_frame_number += 1
                cumulative_frame += 1
                continue  # Skip this frame and move to the next

            local_frame_number += 1
            cumulative_frame += 1

            # Limit the number of concurrent tasks to avoid running out of memory
            if len(future_to_frame) >= max_tasks:
                # Wait for any future to complete before submitting a new one
                done, _ = concurrent.futures.wait(future_to_frame, return_when=concurrent.futures.FIRST_COMPLETED)
                for future in done:
                    frame_id = future_to_frame[future]
                    try:
                        results = future.result()
                        for result in results:
                            writefile.write("\t".join(map(str, result)) + "\n")
                    except Exception as exc:
                        print(f"Frame {frame_id} generated an exception: {exc}")
                    del future_to_frame[future]  # Remove completed futures from the dictionary

            # Submit the frame processing task to the executor
            future = executor.submit(process_frame, cumulative_frame, frame, frame_height, args.black, args.minArea, args.maxArea, video_file)
            future_to_frame[future] = cumulative_frame  # Track the future with frame info

            # Explicitly free memory if necessary
            del frame
            gc.collect()

        # Process any remaining futures
        for future in concurrent.futures.as_completed(future_to_frame):
            frame_id = future_to_frame[future]
            try:
                results = future.result()
                for result in results:
                    writefile.write("\t".join(map(str, result)) + "\n")
            except Exception as exc:
                print(f"Frame {frame_id} generated an exception: {exc}")

    cap.release()

writefile.close()

