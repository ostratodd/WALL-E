import numpy as np
import cv2 as cv
import glob
import argparse

################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.', 
        help="path to video frame files default is ./")
ap.add_argument("-v", "--video", required=True, type=str,
	help="prefix of file name for left stills")
ap.add_argument("-c", "--cb_size", required=False, default="(8,6)", type=str,
        help="size of checkerboard x,y Default = (8,6)")
ap.add_argument("-e", "--extension", required=False, default="png", type=str,
	help="extension of files. Default = png")
args = vars(ap.parse_args())
dir_path = args["path"]
video = args["video"]
cb_size = args["cb_size"]
ext = args["extension"]

#chessboardSize = cb_size #Need to debug to pass this in through command line
chessboardSize = (9,6)
frameSize = (640,480)
size_of_chessboard_squares_mm = 25

#Object points from https://chowdera.com/2022/04/202204061029576597.html
subpix_criteria = (cv.TERM_CRITERIA_EPS+cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)
#calibration_flags = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv.fisheye.CALIB_CHECK_COND+cv.fisheye.CALIB_FIX_SKEW
calibration_flags = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv.fisheye.CALIB_FIX_SKEW
objp = np.zeros((1, chessboardSize[0]*chessboardSize[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:chessboardSize[0], 0:chessboardSize[1]].T.reshape(-1, 2)
_img_shape = None
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.


##Obj points from stereo rectify script
## termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)
## prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
#objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
#objp[:,:2] = np.mgrid[0:chessboardSize[0],0:chessboardSize[1]].T.reshape(-1,2)
#objp = objp * size_of_chessboard_squares_mm
## Arrays to store object points and image points from all the images.
#objpoints = [] # 3d point in real world space
#imgpoints = [] # 2d points in image plane.


images = sorted(glob.glob(dir_path + '/' + video + '*.' + ext))

for fname in images:

    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)

    # If found, add object points, image points (after refining them)
    if ret == True:

        objpoints.append(objp)

        corners = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)

        # Draw and display the corners
        cv.drawChessboardCorners(img, chessboardSize, corners, ret)
        cv.imshow('img', img)
        cv.waitKey(10)
    else:
        cv.imshow('img', img)
        cv.waitKey(1)

cv.destroyAllWindows()


#Now use corner points for fisheye calibration
N_OK = len(objpoints) 
K = np.zeros((3, 3)) 
D = np.zeros((4, 1)) 
rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)] 
tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)] 
rms, _, _, _, _ = \
    cv.fisheye.calibrate(
        objpoints,
        imgpoints,
        gray.shape[::-1],
        K,
        D,
        rvecs,
        tvecs,
        calibration_flags,
        (cv.TERM_CRITERIA_EPS+cv.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    )
print("Found " + str(N_OK) + " valid images for calibration")
#print("DIM=" + str(_img_shape[::-1]))
print("K=np.array(" + str(K.tolist()) + ")")
print("D=np.array(" + str(D.tolist()) + ")")




#images = glob.glob('checkers_manual/CHECKER_L*.png')
#for fname in images:
#    img = cv2.imread(fname)
#    print ("Reading file " + fname)
#    if _img_shape == None:
#        _img_shape = img.shape[:2]
#else:
#    assert _img_shape == img.shape[:2], "All images must share the same size."
#    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
## Find the chess board corners
#    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)
#    #ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
#
## If found, add object points, image points (after refining them)
#    if ret == True:
#        print("***Found corners")
#        objpoints.append(objp)
#        cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),subpix_criteria)
#        imgpoints.append(corners)
