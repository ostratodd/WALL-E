import matplotlib.pyplot as plt
import csv
from sklearn import metrics
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import argparse

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.', 
        help="path to video frame files default is ./")
ap.add_argument("-f", "--file", required=True, type=str,
	help="file name for pulse data made by find_contours.py")
args = vars(ap.parse_args())
file = args["file"]

table = pd.read_csv(file, delimiter = '\t')

frame = table['frame']
cX = table['cX']
cY = table['cY']
camera = table['camera']


groups = table.groupby('camera')
for name, group in groups:
    plt.plot(table.frame, table.cY, marker='o', linestyle='', ms=1, label=name)
plt.legend()

#plt.scatter(table.frame, table.cY, c=table.camera, s=100, cmap='Greens')
plt.show()

