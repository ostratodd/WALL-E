# live_plot_sensor.py

import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
import numpy as np
import cv2
import argparse
import time

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='./', 
        help="path to video frame files default is ./")
ap.add_argument("-v", "--video", required=True, type=str,
	help="file name for first video")
ap.add_argument("-i", "--infile", required=True, type=str,
	help="file name for csv formatted pmt data with 2 columns")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
	help="frame to start video at default = 1")
ap.add_argument("-ps", "--pmt_start", required=False, default=1, type=int,
	help="pmt point of first video frame default = 1")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
	help="delay time between frames for slo-mo")
args = vars(ap.parse_args())
delay = args["delay"]
start = args["start"]
pmt_start = args["pmt_start"]	#pmt point of the first video frame
dir_path = args["path"]
video = args["video"]
infile = args["infile"]

video_fps = 30
pmt_fps = 40

conversion = (1/pmt_fps) / (1/video_fps)  	#how many pmt frames per video frame?

cap = cv2.VideoCapture(video)

#Read data from file into array called pmt
pmt = []
ntime = []
with open(infile, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
         ntime.append(int(row[0]))
         pmt.append(int(row[1]))
ymax = max(pmt)
length = len(pmt)

# create empty list to store data
# create figure and axes objects
data_lst = []
time_lst = []
fig, ax = plt.subplots()

cap.set(1,start);	#starting point of video

frametext=0

# animation function
def animate(i, data_lst, pmt, time_lst, ntime):
    global frametext
    global start
    global pmt_start


    #show current video frame
    frametext=frametext+1
    ret, frame = cap.read()
    #variable called 'adjusted' because copied from other script that adjusts video 
    adjusted = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.putText(adjusted,str(frametext+start), (35,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,180,10))
    cv2.imshow('frame',adjusted)

#To move video frame if desired
#    #move window when first opening
#    if frametext == 1:
#    	cv2.moveWindow('frame',642, 400)


    #build data originally from file
    cnt = pmt_start + int((frametext * conversion)) 	#formula to find pmt point for current data frame
    time_lst.append(ntime[cnt])
    data_lst.append(pmt[cnt])

    # Limit the data list to x values
    data_lst = data_lst[-500:]
    time_lst = time_lst[-500:]
    # clear the last frame and draw the next frame
    ax.clear()
    ax.plot(time_lst, data_lst)

    # Format plot
    ax.set_ylim([75000, 200000])
    ax.set_xlim([cnt-250,cnt+250])
    ax.set_title("PMT Reading Plot")
    ax.set_ylabel("PMT Reading")
    #set aspect ratio
    ratio = 0.3
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)
    #set position of window at bottom




    time.sleep(delay)



# run the animation and show the figure
ani = animation.FuncAnimation(
     fig, animate, frames=length, fargs=(data_lst, pmt, time_lst, ntime), interval=1, repeat=False)

plt.show()

cap.release()
cv2.destroyAllWindows()
