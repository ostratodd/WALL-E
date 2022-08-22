#!/usr/bin/env python3

import matplotlib.pyplot as plt
import csv
import pandas as pd
import argparse
import seaborn as sns
import numpy as np

#function to make axes all on same scale
def set_axes_equal(ax):
    '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    '''

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5*max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.', 
        help="path to video frame files default is ./")
ap.add_argument("-f", "--file", required=True, type=str,
	help="file name for pulse data made by find_contours.py")
ap.add_argument("-o", "--outfile", required=False, default='', type=str,
	help="file name for pulse data made by find_contours.py")
ap.add_argument("-d", "--mindis", required=False, default='0', type=int,
	help="Minimum disparity value (max distance from camera) to plot")
args = vars(ap.parse_args())
file = args["file"]
outfile = args["outfile"]
mindis = args["mindis"]

table = pd.read_csv(file, delimiter = '\t')

df_table = pd.DataFrame(table)


df_table = df_table[df_table.disparity > mindis]

print(df_table)

xco = df_table['d2cam'].tolist()
yco = df_table['lrd'].tolist()
zco = df_table['height'].tolist()
markercolor = df_table['start'].tolist()

#3d
plt.figure(figsize=(6,5))
axes = plt.axes(projection='3d')
print(type(axes))
axes.scatter3D(xco, yco, zco, s=10, c = 'blue')


set_axes_equal(axes)
axes.set_xlabel('distance from camera')
axes.set_ylabel('L-R position from L cam')
axes.set_zlabel('height')





if outfile == '' :
    plt.show()
else:
    fileout = outfile + '.pdf'
    plt.savefig(fileout)

