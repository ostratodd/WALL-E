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
	help="Name to save graphic, leave out to not save")
args = vars(ap.parse_args())
file = args["file"]
outfile = args["outfile"]

table = pd.read_csv(file, delimiter = '\t')

#2d
fig, axs = plt.subplots(ncols=2)
sns.scatterplot(x='frame', y='cX', data=table, hue='camera', edgecolor = 'none', ax=axs[0])
sns.scatterplot(x='frame', y='cY', data=table, hue='camera', edgecolor = 'none', ax=axs[1], legend=False)

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
else :
    outfilename = outfile + '.png'
    plt.savefig(outfilename, bbox_inches='tight')
    plt.show()

