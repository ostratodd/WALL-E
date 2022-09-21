#!/usr/bin/env python3

import numpy as np
import cv2 as cv
import glob

#program from derived from Nico Nielsen at https://raw.githubusercontent.com/niconielsen32/ComputerVision/master/cameraCalibration.py


################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################

chessboardSize = (9,6)
frameSize = (640,480)
size_of_chessboard_squares_mm = 21


# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)


# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:chessboardSize[0],0:chessboardSize[1]].T.reshape(-1,2)

objp = objp * size_of_chessboard_squares_mm


# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.


images = glob.glob('*R*.png')

for image in images:

    img = cv.imread(image)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)

    # If found, add object points, image points (after refining them)
    if ret == True:

        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)

        # Draw and display the corners
        cv.drawChessboardCorners(img, chessboardSize, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(10)


cv.destroyAllWindows()




############## CALIBRATION #######################################################

ret, cameraMatrix, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, frameSize, None, None)

print("Camera calibrated: ", ret)
print("Camera Matrix\n", cameraMatrix)
print("Distortion\n", dist)

############## UNDISTORTION #####################################################


def undistort(img, cameraMatrix, dist) :
    h,  w = img.shape[:2]
    newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))

    # Undistort
    dst = cv.undistort(img, cameraMatrix, dist, None, newCameraMatrix)

    # crop the image
    x, y, w, h = roi

    dst = dst[y:y+h, x:x+w]


    ## Undistort with Remapping
    #This is a different algorithm for remapping -- not sure of the resulting differences though
    #mapx, mapy = cv.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
    #dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)

    ## crop the image
    #x, y, w, h = roi
    #dst = dst[y:y+h, x:x+w]
    return(dst)


video = "../../video_data/cfr_2022labtest155703-1_L.mkv"
watch = 1


#*******************
# Open video
cap = cv.VideoCapture(video)
        
#open a file to write to
frameSize = (640,480)
    
        
#should check here to make sure video files contains 3 letter extension
outfile = video[:-4] + "_LINundis.mkv"

out = cv.VideoWriter(outfile,cv.VideoWriter_fourcc('H','2','6','4'), 30, frameSize)

print("Undistorting fish eye video and writing to " + outfile)
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

        #write the frame to outfile
        out.write(uframe)

       # Hit "q" to close the window
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
# Release and destroy all windows before termination
cap.release()
cv.destroyAllWindows()

