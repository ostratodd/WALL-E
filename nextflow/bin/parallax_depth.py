import numpy as np
#import cvs
import pandas as pd
import argparse
import matplotlib.pyplot as plt


#focal length in millimeters
F = 3.7
#distance between cameras in millimeters
D = 125

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='./', 
        help="path to video frame files default is ./")
ap.add_argument("-f", "--file", required=True, type=str,
	help="file name for pulse data made by find_contours.py")
args = vars(ap.parse_args())
file = args["file"]
path = args["path"]


def distance(xL, xR, ymode, F, D):
    L = min(xR, xL)				#left cam will always have lower x value
    R = max(xR, xL)
    disparity = R - L				#difference between axis value of the same point on L and R cameras
    z = round(F*D/disparity,3)			#equation to find distance from camera - called z in computer vision
    x = round(L * z / F, 3)
    y = round(ymode * z / F, 3)			#this is height off the lowest view of the cameras
    print("Left: " + str(L) + "\tRight:" + str(R) + "\tDisparity: " + str(disparity) + "\tDist:" + str(z) + "\tYmode: " + str(ymode) + "\tHeight" + str(y) + "\n\n")
    return ([z, x, y])

table = pd.read_csv(path+file, delimiter = '\t')
sorted = table.sort_values(['start', 'modex'])
sorted = sorted.reset_index(drop=True) 		#re-index
print(sorted)

coords = []

#iterate row by row, assuming stereo pairs
for index, row in sorted.iterrows():
    if (index % 2) == 0:  		#assuming all pulses are in stereo pairs, so only analyze 2 at a time
        if sorted.iloc[index]['spulse'] == sorted.iloc[index+1]['spulse'] :	#double check spulse names match
            z = distance(sorted.iloc[index]['modex'], sorted.iloc[index+1]['modex'], sorted.iloc[index]['modey'], F, D)
            coords.append(z)
            print("matching pair:" + sorted.iloc[index]['spulse'] + " coords =" + str(z) )

xco = []
yco = []
zco = []

for i in range(len(coords)) :
    xco.append(coords[i][0])
    yco.append(coords[i][1])
    zco.append(coords[i][2])

print("xco")
print(xco)
print("\nyco")
print(yco)
print("\nzco")
print(zco)




##3d
#plt.figure(figsize=(6,5))
#axes = plt.axes(projection='3d')
#print(type(axes))
#axes.scatter3D(xco, yco, zco, s=10)
#axes.set_xlabel('distance from camera')
#axes.set_ylabel('L-R position from L cam')
#axes.set_zlabel('height')

#2D
plt.scatter(yco,zco)
plt.xlabel('L-R position from L cam')
plt.ylabel('height')


plt.show()

