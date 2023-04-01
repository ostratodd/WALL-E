#!/usr/bin/env python3

import numpy as np
import cv2
import argparse

#Script to go through video to find chessboard photos in stereo videos. 

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, type=str,
	help="file name for video")
ap.add_argument("-o", "--outfile", required=True, type=str,
	help="file name for tab delimited data on frames with checkers and their center position")
ap.add_argument ('-c', '--cb_size', nargs=2, type=int, action = 'append', required=True,
        help="need to specify checkerboard size e.g. -c 8 6")
ap.add_argument("--invert", required=False, default=0, type=int,
	help="Invert black and white colors")
ap.add_argument("-l", "--look", required=False, default=1, type=int,
	help="Look at (watch) video while searching for frame pairs")
args = vars(ap.parse_args())
video = args["video"]
cb_size = args["cb_size"]
chessboardSize = tuple(cb_size[0])
invert = args["invert"]
look = args["look"]
outfile = args["outfile"]

frame_size = (640,480)
xmax=0

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


cap = cv2.VideoCapture(video)

#Offsets by xframe, frame frames
loffset = 1
cap.set(1,loffset);

global i
i = 1

with open(outfile, 'w') as f:
     f.write("\t".join(['frame','dist', 'x', 'y', 'xmin','xmax','ymin','ymax']) )
     f.write("\n") 
print("\t".join(['frame','dist', 'x', 'y', 'xmin','xmax','ymin','ymax']) ) 

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == True :
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #Find chessboard corners
        retcorn, corners = cv2.findChessboardCorners(gray, chessboardSize, None)

        if invert == 1:
            adjusted = cv2.bitwise_not(gray)
        else :
            adjusted = gray

        #New code to add corners
        if retcorn == True:

            totcorners = 2 * (chessboardSize[0] * chessboardSize[1])

            corners = cv2.cornerSubPix(adjusted, corners, (11,11), (-1,-1), criteria)
            # Calculate the average distance between each of the corners
            dist_sum = 0
            for i in range(len(corners) - 1):  
                 for j in range(i + 1, len(corners)):
                      dist_sum += np.linalg.norm(corners[i] - corners[j])
            corndist = dist_sum / ((len(corners) - 1) * len(corners) / 2)

            #find extreme corners to later check if they are too close to border
            xarray = corners[:,0,0]	
            yarray = corners[:,0,1]
            ymin = np.min(yarray)
            xmin = np.min(xarray)
            ymax = np.max(yarray)
            xmax = np.max(xarray)

            #Now calculate the center of each chess board to determine movement
            # Calculate the center of all the corners
            center = np.mean(corners, axis=0)
            frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            with open(outfile, 'a') as f:
                 f.write("\t".join([str(frame_num), str(round(corndist, 2)), \
                    str(round(center[0][0],2)), str(round(center[0][1],2)),
                    str(round(xmin,2)), str(round(xmax,2)), str(round(ymin,2)), \
                    str(round(ymax,2))]))
                 f.write("\n") 
            print("\t".join([str(frame_num), str(round(corndist, 2)), \
                    str(round(center[0][0],2)), str(round(center[0][1],2)),
                    str(round(xmin,2)), str(round(xmax,2)), str(round(ymin,2)), \
                    str(round(ymax,2))]))

            if look == 1 :
                # Draw the corners
                cv2.drawChessboardCorners(adjusted, chessboardSize, corners, ret)
#***********
        if look == 1:
            cv2.putText(adjusted,str(frame_num+loffset), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))

            cv2.imshow('frame',adjusted)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
    else:
        break

cap.release()
cv2.destroyAllWindows()
