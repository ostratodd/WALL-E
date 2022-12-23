#!/usr/bin/env python3

import numpy as np
import cv2 as cv
import glob
import pickle
import argparse

#program derived from Nico Nielsen at https://raw.githubusercontent.com/niconielsen32/ComputerVision/master/cameraCalibration.py


################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='./',
        help="path to parameter file. default is ./")
ap.add_argument("-v", "--video", required=True, type=str,
        help="file name for video to undistort")
ap.add_argument("-w", "--watch", required=False, default=0, type=int,
        help="whether (1) or not (0) to watch video while writing. Default = 1")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
        help="delay time between frames for slo-mo")
ap.add_argument("-pre", "--prefix", required=True, type=str,
        help="prefix name for parameters file ending in .p")
ap.add_argument("-o", "--outfile", required=True, type=str,
        help="outfile for video name not including extension")
ap.add_argument ('-fr', '--frameSize', nargs=2, type=int, action = 'append', required=True,
        help="need to specify frame size of video e.g. -c 640 480")

args = vars(ap.parse_args())
delay = args["delay"]
watch = args["watch"]
video = args["video"]
prefix = args["prefix"]
outfile = args["outfile"]
dir_path = args["path"]
frameSize = args["frameSize"]
frameSize = tuple(frameSize[0])


########## READ PICKLE PARAM FILE########################
infile = dir_path + prefix + ".p"
print("Opening infile ", infile)
calib_result_pickle = pickle.load( open(infile, "rb" ) )

cameraMatrix = calib_result_pickle["cameraMatrix"]
dist = calib_result_pickle["dist"]
rvecs = calib_result_pickle["rvecs"]
tvecs = calib_result_pickle["tvecs"]


############## UNDISTORTION #####################################################
def undistort(img, cameraMatrix, dist) :
    h,  w = img.shape[:2]
    newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))

    # Undistort
    dst = cv.undistort(img, cameraMatrix, dist, None, newCameraMatrix)

    ## crop the image to remove black sections of the image
    #x, y, w, h = roi
    #dst = dst[y:y+h, x:x+w]


    ## Undistort with Remapping
    #This is a different algorithm for remapping -- not sure of the resulting differences though
    #mapx, mapy = cv.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
    #dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)

    ## crop the image
    #x, y, w, h = roi
    #dst = dst[y:y+h, x:x+w]
    return(dst)


#*******************
# Open video to undistort and save
cap = cv.VideoCapture(video)
        
#should check here to make sure video files contains 3 letter extension
vidoutfile = outfile + "_undis.mkv"

out = cv.VideoWriter(vidoutfile,cv.VideoWriter_fourcc('H','2','6','4'), 30, frameSize)

print("Undistorting fish eye video and writing to " + vidoutfile)
_img_shape = None

while(cap.isOpened()):
    succes, frame = cap.read()

    if succes == True:
        if _img_shape == None:
            _img_shape = frame.shape[:2]
        else:
            assert _img_shape == frame.shape[:2], "All images must share the same size."

        # Undistort and rectify images

        uframe = undistort(frame, cameraMatrix, dist)

        #If watch variable is true
        # Show the frames
        if watch == 1:
          cv.imshow("frame", uframe)
          # Hit "q" to close the window
          if cv.waitKey(1) & 0xFF == ord('q'):
              break

        #write the frame to outfile
        out.write(uframe)

    else:
        break
# Release and destroy all windows before termination
cap.release()
cv.destroyAllWindows()

