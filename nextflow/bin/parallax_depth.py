#!/usr/bin/env python3

import numpy as np
#import cvs
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import numpy as np


# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--distance", required=True, 
        help="Distance in mm between paired cameras (baseline)")
ap.add_argument("-f", "--file", required=True, type=str,
	help="file name for pulse data made by find_contours.py")
ap.add_argument("-o", "--outfile", required=True, type=str,
	help="file name for output data")
ap.add_argument("-FOCAL", required=False, default=3.7, type=float,
	help="Focal length of camera")
ap.add_argument("-ALPHA", required=False, default=65, type=float,
	help="Degrees of field of view of camera")
ap.add_argument("-frame_width", required=False, default=640, type=int,
	help="Pixel width of video view")
ap.add_argument("-frame_height", required=False, default=480, type=int,
	help="Pixel height of video view")
ap.add_argument("-rate", required=False, default=30, type=int,
	help="Frame rate of video")
args = vars(ap.parse_args())
file = args["file"]
outfile = args["outfile"]
distance = args["distance"]
F = args["FOCAL"]
ALPHA = args["ALPHA"]
frame_height = args["frame_height"]
frame_width = args["frame_width"]
FPS = args["rate"]

D = float(distance)	#also called baseline (distance bewteen cameras in mm)
writefile = open('coordinates_' + outfile + '.tab', 'w')




def distance(xL, xR, ymode, F, D):
    #R = xR - (frame_width/2)	#calculates distance from optical center				
    #L = xL - (frame_width/2)
    #ymode = ymode - (frame_height/2)
    R = xR
    L = xL

    disparity = abs(R - L)			#difference between axis value of the same point on L and R cameras

    f_pixel = (frame_width * 0.5) / np.tan(ALPHA * 0.5 * np.pi/180)	#formula for focal length in pixels using alpha which is field of fiew angle
    F = f_pixel

    z = round(F*D/disparity,3)			#equation to find distance from camera - called z in computer vision
    x = round(L * z / F, 3)
    y = round(ymode * z / F, 3)			#this is height off the lowest view of the cameras
#    print("Left: " + str(L) + "\tRight:" + str(R) + "\tDisparity: " + str(disparity) + "\tDist:" + str(z) + "\tYmode: " + str(ymode) + "\tHeight: " + str(y))
    return ([z, x, y])

table = pd.read_csv(file, delimiter = '\t')
sorted = table.sort_values(['spulse', 'camera'])
sorted = sorted.reset_index(drop=True) 		#re-index
print(sorted)

coords = []
tab = "\t"

#Header
header = ("pname\tlname\trname\tstart\tend\tduration\tdisparity\td2cam\tlrd\theight\tmaxI\tmeanI\tmeanArea")
print(header)
writefile.write(header + '\n')

#iterate row by row, assuming stereo pairs
for index, row in sorted.iterrows():
    if (index % 2) == 0:  		#assuming all pulses are in stereo pairs, so only analyze 2 at a time
        if sorted.iloc[index]['spulse'] == sorted.iloc[index+1]['spulse'] :	#double check spulse names match
            startp = min(sorted.iloc[index]['start'], sorted.iloc[index+1]['start'])
            endp = max(sorted.iloc[index]['finish'], sorted.iloc[index+1]['finish'])
            disparity = abs(sorted.iloc[index]['modex'] - sorted.iloc[index+1]['modex'])
            z = distance(sorted.iloc[index]['modex'], sorted.iloc[index+1]['modex'], sorted.iloc[index]['modey'], F, D)
            coords.append(z)
            maxI = max(sorted.iloc[index]['maxI'], sorted.iloc[index + 1]['maxI'] ) 
            meanI =    np.mean([sorted.iloc[index]['meanI'], sorted.iloc[index + 1]['meanI']])
            meanArea = np.mean([sorted.iloc[index]['meanArea'], sorted.iloc[index + 1]['meanArea']] ) 
            out = tab.join([sorted.iloc[index]['spulse'],sorted.iloc[index]['pulse'],sorted.iloc[index+1]['pulse'],str(startp),str(endp),str(round((endp-startp)/FPS,2)),str(disparity),str(z[0]),str(z[1]),str(z[2]), str(maxI), str(meanI),str(meanArea)])
            print(out)
            writefile.write(out + '\n')
        else:
            print("ERROR: pulse names " + sorted.iloc[index]['spulse'] + " " + sorted.iloc[index+1]['spulse'] + " do not match in input file. Make sure input (stereo) file is formatted correctly")
