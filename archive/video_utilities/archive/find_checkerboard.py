import numpy as np
import cv2 as cv
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('--left_file', type=str, required=True, help='left matrix file')
args = vars(ap.parse_args())
left = args["left_file"]


# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

#for fname in images:

print("Reading file: " + left + "\n")

img = cv.imread(left)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.imshow('img', img)
cv.waitKey(1500)

# Find the chess board corners
ret, corners = cv.findChessboardCorners(gray, (9,7), None)
print("ret = " + str(ret))

# If found, add object points, image points (after refining them)
if ret == True:
        print("FOUND points")
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (9,7), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)

cv.destroyAllWindows()
