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
args = vars(ap.parse_args())
file = args["file"]

table = pd.read_csv(file, delimiter = '\t')

fig, axs = plt.subplots(ncols=2)
sns.scatterplot(x='frame', y='cX', data=table, hue='camera', edgecolor = 'none', ax=axs[0])
sns.scatterplot(x='frame', y='cY', data=table, hue='camera', edgecolor = 'none', ax=axs[1])

plt.show()

