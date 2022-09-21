#!/usr/bin/env python3

import numpy as np
from rigid_transform_3D import rigid_transform_3D
import matplotlib.pyplot as plt
import pandas as pd
import argparse


# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f1", "--file1", required=True, type=str,
	help="file name for coordinates")
ap.add_argument("-f2", "--file2", required=False, default='', type=str,
	help="file name for coordinates to align")

args = vars(ap.parse_args())
file1 = args["file1"]
file2 = args["file2"]



# Test with random data
# Random rotation and translation
R = np.random.rand(3,3)
t = np.random.rand(3,1)

#file1 = '~/Documents/GitHub/WALL-E/nextflow/data/contours/all_known_labtest.tab'
#file2 = '~/Documents/GitHub/WALL-E/nextflow/data/contours/all_labtest.tab'

table = pd.read_csv(file1, delimiter = '\t')
table2 = pd.read_csv(file2, delimiter = '\t')

df_table = pd.DataFrame(table)
df_table2 = pd.DataFrame(table2)


xco1 = df_table['d2cam'].tolist()
yco1 = df_table['lrd'].tolist()
zco1 = df_table['height'].tolist()

xco2 = df_table2['d2cam'].tolist()
yco2 = df_table2['lrd'].tolist()
zco2 = df_table2['height'].tolist()


A = np.array([xco1,yco1,zco1])
B = np.array([xco2,yco2,zco2])


# Recover R and t
ret_R, ret_t = rigid_transform_3D(B, A)



print("Rotated")
rotated = (ret_R@B) + ret_t
print(rotated)

xcoR=rotated[0]
ycoR=rotated[1]
zcoR=rotated[2]

plt.figure(figsize=(6,5))
axes = plt.axes(projection='3d')
print(type(axes))
##Just print A and B
#axes.scatter3D(xco2, yco2, zco2, s=10, c = 'limegreen')
#axes.scatter3D(xco1, yco1, zco1, s=8, c = 'b')

##Just print B and rotated B
#axes.scatter3D(xco2, yco2, zco2, s=10, c = 'limegreen')
#axes.scatter3D(xcoR, ycoR, zcoR, s=8, c = 'b')

#Just print A and rotated B
axes.scatter3D(xco1, yco1, zco1, s=10, c = 'limegreen')
axes.scatter3D(xcoR, ycoR, zcoR, s=8, c = 'b')

#if label == 1:
#    for i in range(len(xco)):
#        axes.text(xco[i],yco[i],zco[i], '%s' % (str(names[i])), size=10, zorder=1, color='k')

plt.show()
