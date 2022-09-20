#!/usr/bin/env python3

import numpy as np
import cv2
import argparse

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, type=str,
        help="file name for video to undistort")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
        help="frame to start at default = 1")
ap.add_argument("-w", "--watch", required=False, default=0, type=int,
        help="whether (1) or not (0) to watch video while writing. Default = 1")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
        help="delay time between frames for slo-mo")
args = vars(ap.parse_args())
delay = args["delay"]
start = args["start"]
watch = args["watch"]
video = args["video"]

#**********************
# You should replace these 3 lines with the output in calibration step
DIM = (640, 480) 
K = np.array([[526.756924435422, 0.0, 330.221556181272], [0.0, 478.43311043812145, 249.44524334088075], [0.0, 0.0, 1.0]])
D = np.array([[-0.07527166402108293], [0.006777363197177597], [-0.32231954249568173], [0.43735394851622683]])
#***********************

def undistort(img_orig, balance=0.0, dim2=None, dim3=None):
    dim1 = img_orig.shape[:2][::-1]  #dim1 is the dimension of input image to un-distort
    assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
    if not dim2:
        dim2 = dim1
    if not dim3:
        dim3 = dim1
    scaled_K = K * dim1[0] / DIM[0]  # The values of K is to scale with image dimension.
    scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0
    # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye(3), balance=balance)
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img_orig, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return(undistorted_img)


# Open video
cap = cv2.VideoCapture(video)

#open a file to write to
frameSize = (640,480)


#should check here to make sure video files contains 3 letter extension
outfile = video[:-4] + "_undis.mkv"

out = cv2.VideoWriter(outfile,cv2.VideoWriter_fourcc('H','2','6','4'), 30, frameSize)

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

        uframe = undistort(frame)
                    
        #If watch variable is true
        # Show the frames
        if watch == 1:
          cv2.imshow("frame", uframe) 

        #write the frame to outfile
        out.write(uframe)

        # Hit "q" to close the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
# Release and destroy all windows before termination
cap.release()
cv2.destroyAllWindows()
