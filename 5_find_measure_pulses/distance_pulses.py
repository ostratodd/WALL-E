import matplotlib.pyplot as plt
import csv
import pandas as pd
import numpy as np
import argparse

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.', 
        help="path to video frame files default is ./")
ap.add_argument("-f", "--file", required=True, type=str,
	help="file name for pulse data made by find_contours.py")
args = vars(ap.parse_args())
file = args["file"]

XMAX = 15
YMAX = 15

SRMAX = 5

oldX = 0
oldY = 0
oldF = 0
framearray = []
rowcount = 1
rpulse = []
lpulse = []

table = pd.read_csv(file, delimiter = '\t')

sorted = table.sort_values(['camera', 'frame', 'cX', 'cY'])

curpulse = []
pulses = []

for index, row in sorted.iterrows():
    #first form pulses if contiguous frames are close in both x and y


    if index > 1:
        difX = abs(int(row['cX']) - oldX) 
        difY = abs(int(row['cY']) - oldY) 
        difF = abs(int(row['frame']) - oldF)
        if(difX < XMAX and difY < YMAX and difF < 2) :
            if curpulse:
                curpulse.append(table.iloc[index])
            else :
                curpulse.append(oldRow)
                curpulse.append(table.iloc[index])
        else :
            if curpulse:
                pulses.append(curpulse)
                curpulse = []	#reset to start new pulse
                print("\n\n")
 
#           print("Found a pulse. Frame:" + str(row['frame']) + " X:" + str(row['cX']) + " Y:" + str(row['cY']))

    oldRow = table.iloc[index]
    oldF = row['frame']
    oldX = row['cX']
    oldY = row['cY']

print(pulses[0])
print("Total pulses: " + str(len(pulses)))





#********
#This unused code puts together into an array multiple contours found on the same frame
#    for row in table:
#        #Is there more than one contour from the same frame number?
#        #Need to analyze those together
#        if rowcount > 1:
#            if row[1] == oldRow[1]:
#                if framearray :
#                    framearray.append(row)
#                else :
#                    framearray.append(oldRow)
#                    framearray.append(row)
#            else :
#                if framearray:
#                    print(framearray)
#                framearray = []
#            #Is current contour close enough to form a pulse?
#
#
#            #Save current row into oldRow value
#        oldRow = row
#        rowcount = rowcount + 1
