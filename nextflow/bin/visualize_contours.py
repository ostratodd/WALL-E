#!/usr/bin/env python3

import matplotlib.pyplot as plt
import csv
import pandas as pd
import argparse
import seaborn as sns

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.', 
        help="path to video frame files default is ./")
ap.add_argument("-f", "--file", required=True, type=str,
	help="file name for pulse data made by find_contours.py")
ap.add_argument("-o", "--outfile", required=False, default='', type=str,
	help="file name for pulse data made by find_contours.py")
ap.add_argument('--segments', action='store_true')
ap.add_argument('--contours', dest='segments', action='store_false')
ap.set_defaults(segments=False)

args = vars(ap.parse_args())
file = args["file"]
outfile = args["outfile"]
segments = args["segments"]

table = pd.read_csv(file, delimiter = '\t')

if segments :
    colorby = 'pulse'
else:
    colorby = 'camera'

#2d
fig, axs = plt.subplots(ncols=2)
sns.scatterplot(x='frame', y='cX', data=table, hue=colorby, edgecolor = 'none', ax=axs[0])
sns.scatterplot(x='frame', y='cY', data=table, hue=colorby, edgecolor = 'none', ax=axs[1], legend=False)

##3d
#plt.figure(figsize=(6,5))
#axes = plt.axes(projection='3d')
#print(type(axes))
#axes.scatter3D(table['frame'], table['cX'], table['cY'], s=10)
#axes.set_xlabel('frame')
#axes.set_ylabel('x position')
#axes.set_zlabel('y position')

if outfile == '' :
    plt.show()
else:
    fileout = outfile + '.pdf'
    plt.savefig(fileout)

