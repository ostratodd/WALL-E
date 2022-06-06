import numpy as np
import cv2
import argparse
import time

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
ap.add_argument("-e", "--end", required=False, default=0, type=int,
	help="frame to end clipping")
ap.add_argument("-o", "--offset", required=False, default=0, type=int,
	help="number of frames to offset two videos, positive or negative")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
	help="delay time between frames for slo-mo")
args = vars(ap.parse_args())
offset = args["offset"]
delay = args["delay"]
start = args["start"]
end = args["end"]
dir_path = args["path"]
video1 = args["video1"]
video2 = args["video2"]

endframe = end - start

cap = cv2.VideoCapture(video1)
cap2 = cv2.VideoCapture(video2)

#Offsets by xframe, frame frames
loffset = start
cap.set(1,loffset);
roffset=start+offset
cap2.set(1,roffset);

frameSize = (640, 480)

new_filename_l = dir_path + "/" + video1[:-4] + "_clip_" + str(start) + "_" + str(end)+ ".mkv"
new_filename_r = dir_path + "/" + video2[:-4] + "_clip_" + str(start) + "_" + str(end)+ ".mkv"

out_l = cv2.VideoWriter(new_filename_l,cv2.VideoWriter_fourcc('F','F','V','1'), 30, frameSize)
out_r = cv2.VideoWriter(new_filename_r,cv2.VideoWriter_fourcc('F','F','V','1'), 30, frameSize)


frametext=0
while(cap.isOpened()):
    frametext=frametext+1
    ret, frame = cap.read()
    ret, frame2 = cap2.read()

    cv2.imshow('left camera',frame)
    cv2.imshow('right camera',frame2)

    #move window when first opening
    if frametext == 1:
    	cv2.moveWindow('right camera',642, 0)
    	cv2.moveWindow('left camera',0, 0)


    time.sleep(delay)

    #write the frame to outfile
    out_l.write(frame)
    out_r.write(frame2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if frametext == endframe:
        break

cap.release()
cap2.release()
cv2.destroyAllWindows()
