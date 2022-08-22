from matplotlib import pyplot as plt
import numpy as np
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
args = vars(ap.parse_args())
file = args["file"]
outfile = args["outfile"]

table = pd.read_csv(file, delimiter = '\t')

pulsedur = (table['finish'] - table['start']).tolist()
 
#print(pulsedur)
 
## Creating histogram
#fig, ax = plt.subplots(figsize =(10, 7))
#ax.hist(pulsedur, bins = 10)

#3d
plt.figure(figsize=(6,5))
axes = plt.axes(projection='3d')
print(type(axes))
axes.scatter3D(table['start'], table['modex'], table['modey'], s=10)
axes.set_xlabel('frame')
axes.set_ylabel('x position')
axes.set_zlabel('y position')


 
# Show plot
plt.show()
