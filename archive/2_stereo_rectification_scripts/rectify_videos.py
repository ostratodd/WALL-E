#Much of original script copied from Nico Nielsen Github
import numpy as np
import cv2
import argparse

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.',
        help="path to video frame files default is ./")
ap.add_argument("-v1", "--video1", required=True, type=str,
        help="file name for first video")
ap.add_argument("-v2", "--video2", required=True, type=str,
        help="filename for second video")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
        help="frame to start at default = 1")
ap.add_argument("-w", "--watch", required=False, default=1, type=int,
        help="whether (1) or not (0) to watch video while writing. Default = 1")
ap.add_argument("-l", "--lines", required=False, default=0, type=int,
        help="whether (1) or not (0) to add horizontal lines to check SR. Default = 0")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
        help="delay time between frames for slo-mo")
args = vars(ap.parse_args())
delay = args["delay"]
start = args["start"]
dir_path = args["path"]
watch = args["watch"]
lines = args["lines"]
video1 = args["video1"]
video2 = args["video2"]


# Camera parameters to undistort and rectify images
cv_file = cv2.FileStorage()
cv_file.open('stereoMap.xml', cv2.FileStorage_READ)

stereoMapL_x = cv_file.getNode('stereoMapL_x').mat()
stereoMapL_y = cv_file.getNode('stereoMapL_y').mat()
stereoMapR_x = cv_file.getNode('stereoMapR_x').mat()
stereoMapR_y = cv_file.getNode('stereoMapR_y').mat()


# Open both videos

cap_left = cv2.VideoCapture(video1)
cap_right = cv2.VideoCapture(video2)

#open a file to write to
frameSize = (640,480)
out_l = cv2.VideoWriter('rectifiedL_' + '.avi',cv2.VideoWriter_fourcc('F','F','V','1'), 30, frameSize)
out_r = cv2.VideoWriter('rectifiedR_' + '.avi',cv2.VideoWriter_fourcc('F','F','V','1'), 30, frameSize)

while(cap_right.isOpened() and cap_left.isOpened()):

    succes_right, frame_right = cap_right.read()
    succes_left, frame_left = cap_left.read()


    cv2.imshow("orig frame right", frame_right) 
    cv2.moveWindow("orig frame right",642, 600)
    cv2.imshow("orig frame left", frame_left)
    cv2.moveWindow("orig frame left",1, 600)


    # Undistort and rectify images
    frame_right = cv2.remap(frame_right, stereoMapR_x, stereoMapR_y, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
    frame_left = cv2.remap(frame_left, stereoMapL_x, stereoMapL_y, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
                     
    #If watch variable is true
    # Show the frames
    if watch == 1:
      if lines == 1:
        for line in range(0, int(frame_left.shape[0] / 50)):
            frame_left[line * 50, :] = 255
            frame_right[line * 50, :] = 255
      cv2.imshow("frame right", frame_right) 
      cv2.moveWindow("frame right",642, 150)
      cv2.imshow("frame left", frame_left)
      cv2.moveWindow("frame left",1, 150)

    #write the frame to outfile
    out_l.write(frame_left)
    out_r.write(frame_right)

    # Hit "q" to close the window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release and destroy all windows before termination
cap_right.release()
cap_left.release()

cv2.destroyAllWindows()
