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
ap.add_argument("-g", "--gamma", required=False, default=1.0,type=float,
	help="value of gamma")
ap.add_argument("-b", "--black", required=False, default=0, type=int,
	help="threshold below which is black")
ap.add_argument("-w", "--white", required=False, default=255, type=int,
	help="threshold above which is white")
ap.add_argument("-s", "--start", required=False, default=1, type=int,
	help="frame to start video at default = 1")
ap.add_argument("-ps", "--pmt_start", required=False, default=1, type=int,
	help="data point time to start video at default = 1")
ap.add_argument("-o", "--offset", required=False, default=0, type=int,
	help="number of frames to offset video to match pmt trace, positive or negative")
ap.add_argument("-d", "--delay", required=False, default=0, type=float,
	help="delay time between frames for slo-mo")
args = vars(ap.parse_args())
offset = args["offset"]
delay = args["delay"]
gamma = args["gamma"]
black = args["black"]
white = args["white"]
start = args["start"]
pmt_start = args["pmt_start"]
dir_path = args["path"]
video = args["video"]
infile = args["infile"]


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
mngr = plt.get_current_fig_manager()
# to put it into the upper left corner for example:
mngr.window.setGeometry(50,100,640, 545)


start=pmt_start

# animation function
def animate(i, data_lst, pmt, time_lst, ntime):
    #build data originally from file
    cnt = start + i
    time_lst.append(ntime[cnt])
    data_lst.append(pmt[cnt])

    # Limit the data list to x values
    data_lst = data_lst[-500:]
    time_lst = time_lst[-500:]
    # clear the last frame and draw the next frame
    ax.clear()
    ax.plot(time_lst, data_lst)

    # Format plot
    ax.set_ylim([10000, 500000])
    ax.set_xlim([cnt-250,cnt+250])
    ax.set_title("PMT Reading Live Plot")
    ax.set_ylabel("PMT Reading")
    #set aspect ratio
    ratio = 0.3
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)
    #set position of window at bottom

# run the animation and show the figure
ani = animation.FuncAnimation(
    fig, animate, frames=length, fargs=(data_lst, pmt, time_lst,ntime), interval=1, repeat=False)

plt.show()

