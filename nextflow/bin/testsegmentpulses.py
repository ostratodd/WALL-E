#!/usr/bin/env python3

import csv
import pandas as pd
import argparse
import numpy as np

import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import fcluster



from scipy.optimize import linear_sum_assignment

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='./', 
        help="path to video frame files MUST include trailing /. Default is ./")
ap.add_argument("-f", "--file", required=True, type=str,
	help="file name for pulse data made by find_contours.py")
ap.add_argument("-n", "--name", required=True, type=str,
	help="file name for two output files")
ap.add_argument("-HPP", "--HPP", required=False, default=2.0, type=float,
	help="hot pixel proportion = percentage of frames that contain a contour at the same X-axis value to be considered noise")
ap.add_argument("-HPD", "--HPD", required=False, default=2, type=int,
	help="hot pixel distance - include HPD pixels away from hot pixel in filtering")
ap.add_argument("-XMAX", "--XMAX", required=False, default=10, type=int,
	help="Must be withing XMAX pixels from frame to frame to be same pulse")
ap.add_argument("-YMAX", "--YMAX", required=False, default=10, type=int,
	help="Must be withing YMAX pixels from frame to frame to be same pulse")
ap.add_argument("-PDMIN", required=False, default=3, type=int,
	help="Minimum num of consectuive frames to be a pulse")
ap.add_argument("-SRMAX", required=False, default=5, type=int,
	help="Must be withing SRMAX pixels in Yaxis to be same stereo pulse (stereo rectification should take care of this)")
ap.add_argument("-PSD", required=False, default=5, type=int,
	help="Pulse-start difference (max allowed diff in frame start to be considered stereo pair)")
ap.add_argument("-PFD", required=False, default=5, type=int,
	help="Pulse-finish difference (max allowed diff in frame end to be considered stereo pair)")
ap.add_argument("-XD", required=False, default=300, type=int,
	help="Max disparity allowed to be a possible stereo pulse")
args = vars(ap.parse_args())
file = args["file"]
name = args["name"]
HPP = args["HPP"]
HPD = args["HPD"]
XMAX = args["XMAX"]
YMAX = args["YMAX"]
SRMAX = args["SRMAX"]
PDMIN = args["PDMIN"]
PSD = args["PSD"]
PFD = args["PFD"]
XD = args["XD"]

FS = 3 	#FrameSkip how many frames can be skipped and still be a pulse

	#Parameters for weighting differences between frame start, frame end, and y for distance matrix to match pulses
SFW = 1
EFW = 1
YDW = 1

#This script reads in file with contours from find_contours.py
#It clusters contours bsed on x,y,and frame into pulses based on Euclidean distance < min_d1
#If that results in clusters that include the same frame >1 (not allowed) it re-clusters and uses distance < min_d2

table = pd.read_csv(file, delimiter = '\t')

#Divide into L and R camera data frames
df_left = table[table['camera']=='left']
df_left = df_left.drop(labels='camera', axis='columns')
df_right = table[table['camera']=='right']
df_right = df_right.drop(labels='camera', axis='columns')
df_left = df_left.reset_index(drop=True)
df_right = df_right.reset_index(drop=True)
 
ZL = linkage(df_left, method='complete', metric='euclidean')
ZR = linkage(df_right, method='complete', metric='euclidean')

#can see euclidean distance dendrogram
#plt.figure(figsize=(30, 10))
#dendrogram(Z)
#plt.show()

max_d1 = 50
max_d2 = 10

clustersL = fcluster(ZL, max_d1, criterion='distance')
clustersR = fcluster(ZR, max_d1, criterion='distance')

df_left['pulse'] = clustersL
df_right['pulse'] = clustersR

df_left = df_left.sort_values(['pulse','frame'])
df_right = df_right.sort_values(['pulse','frame'])


#Find rows with duplicate pulse and frame - each frame should only appear once in a pulse
duplicateR = df_right[df_right.duplicated(['frame', 'pulse'])]
pwdR = (duplicateR['pulse'].unique())

duplicateL = df_left[df_left.duplicated(['frame', 'pulse'])]
pwdL = (duplicateL['pulse'].unique())

count = 0
for dpulses in pwdR:
     df_rightduped = df_right[df_right['pulse'] == dpulses].copy()
     ZRD = linkage(df_rightduped[["cX", "cY"]], method='complete', metric='euclidean')
     df_rightduped['pulseD'] = fcluster(ZRD, max_d2, criterion='distance') 
     df_rightduped = df_rightduped.sort_values(['pulseD','frame'])
     if count == 0:
         df_right_split = df_rightduped
     else:
         df_right_split = pd.concat([df_right_split, df_rightduped])
     count = count+1
#combine old pulse name with _newpulse name then delete extra (new) pulse column
df_right_split["pulse"] = df_right_split["pulse"].astype(str).str.cat(df_right_split["pulseD"].astype(str), sep = "_")
df_right_split = df_right_split.drop(['pulseD'],axis='columns')
#now drop old pulses with duplicated frames before adding them back as separate pulses
drops = df_right[ (df_right['pulse']==dpulses) ].index
df_right.drop(drops, inplace=True)
df_right_final = pd.concat([df_right, df_right_split])

#print("ALL right pulses")
#print(df_right_final.to_string())

count = 0
for dpulses in pwdL:
     df_leftduped = df_left[df_left['pulse'] == dpulses].copy()
     ZLD = linkage(df_leftduped[["cX", "cY"]], method='complete', metric='euclidean')
     df_leftduped['pulseD'] = fcluster(ZLD, max_d2, criterion='distance')
     df_leftduped = df_leftduped.sort_values(['pulseD','frame'])
     if count == 0:
         df_left_split = df_leftduped
     else:
         df_left_split = pd.concat([df_left_split, df_leftduped])
     count = count+1
#combine old pulse name with _newpulse name then delete extra (new) pulse column
df_left_split["pulse"] = df_left_split["pulse"].astype(str).str.cat(df_left_split["pulseD"].astype(str), sep = "_")
df_left_split = df_left_split.drop(['pulseD'],axis='columns')
#now drop old pulses with duplicated frames before adding them back as separate pulses
drops = df_left[ (df_left['pulse']==dpulses) ].index
df_left.drop(drops, inplace=True)
df_left_final = pd.concat([df_left, df_left_split])
df_left_final['camera'] = 'left'
df_left_final['pulse']= "L"+df_left_final['pulse'].astype('string')
df_right_final['pulse']= "R"+df_right_final['pulse'].astype('string')
df_right_final['camera'] = 'right'
finalpulses = pd.concat([df_right_final, df_left_final])
finalpulses = finalpulses.reset_index(drop=True)
print(finalpulses.to_string())

#******************


finalpulses = finalpulses.sort_values(['pulse', 'frame', 'camera', 'cX', 'cY'])

xmode = finalpulses.mode()['cX'][0]					#find most common X-axis value
uframes = len(pd.unique(finalpulses['frame']))				#count total number of unique frames
noisepulses = 0

#Should probably separate out L and R cameras and do them separately
noisepulses = noisepulses + finalpulses['cX'].value_counts()[xmode]	#count total number of times most common X value is found

#Want to also account for pixels adjacent to hot pixels, but this has a bug with southwater2 data
##I think there is a mistake here because it will count x-1 twice
#for i in range(1, HPD + 1):
#    if (xmode + i) in finalpulses['cX']:
#        print("\n\n\nXMODE PLUS I IS IN FINAL PULSES i=" + str(i) + " xmodei]=" + str(xmode+i) + "\n\n\n\n")
#        noisepulses = noisepulses + finalpulses['cX'].value_counts()[xmode + i] 	#Find number of frames within +/- HPD of most common value
#    if (xmode - i) in finalpulses['cX']:
#        noisepulses = noisepulses + finalpulses['cX'].value_counts()[xmode - i]


#Replace pulse name with 'noise' for most common x-axis value, if it is above the HPP threshold defining it as Hot Pixel noise
#print("noisepulses = " + str(noisepulses) + "uframes " + str(uframes))
if(noisepulses/uframes > HPP) :
    finalpulses.loc[finalpulses.cX == xmode, 'pulse'] = "noise"
    for i in range(1, HPD + 1) :
        finalpulses.loc[finalpulses.cX == xmode + i, 'pulse'] = "noise"
        finalpulses.loc[finalpulses.cX == xmode - i, 'pulse'] = "noise"
        finalpulses.loc[finalpulses.cX == xmode, 'pulse'] = "noise"
        finalpulses.loc[finalpulses.cX == xmode + 1, 'pulse'] = "noise"
        finalpulses.loc[finalpulses.cX == xmode - 1, 'pulse'] = "noise"

print("AFTER NOISE")
print(finalpulses.to_string())
#Next define as noise pulses that are too short to be a pulse
unique_pulses = finalpulses['pulse'].unique()
for rezy in unique_pulses:
    df_single_pulse = finalpulses[finalpulses['pulse']==rezy]
    if df_single_pulse['cX'].count() < PDMIN :
        print(rezy + " is too short to be a pulse based on PDMIN = " + str(PDMIN))
        finalpulses.loc[finalpulses.pulse == rezy, 'pulse'] = "too_short"

noise = finalpulses.loc[finalpulses['pulse'] == 'noise']
too_short = finalpulses.loc[finalpulses['pulse'] == 'too_short']
denoised = finalpulses.loc[finalpulses['pulse'] != 'noise']
denoised = denoised.loc[finalpulses['pulse'] != 'too_short']

#Finally, will find most probable stereo pairs based on correspondence of frame start/stop, correspondence of Y-axis point, and possibly X-axis disparity
#Working with only denoised data at this point
#create a new df with information about entire pulses instead of frame-by frame
pulse_names = denoised['pulse'].unique()
pulserows = []
for rezy in pulse_names :
    df_frames = denoised[denoised['pulse']==rezy]
    pulserows.append([df_frames['camera'].mode()[0], rezy, df_frames['frame'].min(), df_frames['frame'].max(), df_frames['cX'].min(), df_frames['cX'].max(), df_frames['cX'].mode()[0], df_frames['cY'].min(), df_frames['cY'].max(), df_frames['cY'].mode()[0]])
df_pulse_sums = pd.DataFrame(pulserows, columns=['camera','pulse','start', 'finish', 'minx', 'maxx', 'modex', 'miny', 'maxy', 'modey'])

#Add empty column for spulse (stereo pulse)
df_pulse_sums['spulse'] = 'none'

#Divide into L and R camera data frames
df_left = df_pulse_sums[df_pulse_sums['camera']=='left']
df_right = df_pulse_sums[df_pulse_sums['camera']=='right']
df_left = df_left.reset_index(drop=True)
df_right = df_right.reset_index(drop=True)

print("ALL RIGHT PULSES")
print(df_right)
print("ALL LEFT PULSES")
print(df_left)

#Next find pulses with any other in opposite camera close enough in start, finish, y and low enough in x disparity to qualify as left/right stereo pairs
#This narrows down in turn right pulses similar enough in Yaxis value, then start then finish time of pulse
#Later pass candidates into hungarian algorithm to assign best pairs from those remaining as possible
for index, lrow in df_left.iterrows():
    lpulse = [lrow['start'], lrow['finish'], lrow['modey'], lrow['modex'], lrow['pulse'] ] 
    for i, rrow in df_right.iterrows() :
        rpulse = [rrow['start'], rrow['finish'], rrow['modey'], rrow['modex'], rrow['pulse']]
        startdif = abs(rpulse[0]-lpulse[0])	#Difference in start pulse frame
        findif = abs(rpulse[1]-lpulse[1])	#Difference in finish pulse frame
        ydif = abs(rpulse[2]-lpulse[2])		#Difference in y-axis position
        xdif = abs(rpulse[3]-lpulse[3])		#Difference in x-axis position, same as disparity, but some disparities unreasonable
        if(abs(startdif < PSD and findif < PFD and ydif < SRMAX and xdif < XD)) :
            right_match_i = i
            df_left.at[index, 'spulse'] = ("candidate")
            df_right.at[right_match_i, 'spulse'] = ("candidate")

left_pairless = df_left.loc[df_left['spulse'] == 'none']
right_pairless = df_right.loc[df_right['spulse'] == 'none']

print("LEFT PAIRLESS")
print(left_pairless)

print("RIGHT PAIRLESS")
print(right_pairless)

df_left = df_left.loc[df_left['spulse'] == 'candidate']
df_right = df_right.loc[df_right['spulse'] == 'candidate']
df_left = df_left.reset_index(drop=True)
df_right = df_right.reset_index(drop=True)

spairN = 1

pulmatrix = np.zeros((len(df_left.index),len(df_right.index)))

#Create dict of dicts to use hungarian algorithm to match pulses
for index, lrow in df_left.iterrows():
    lpulse = [lrow['start'], lrow['finish'], lrow['modey'], lrow['modex'], lrow['pulse'] ] 
    for i, rrow in df_right.iterrows() :
        rpulse = [rrow['start'], rrow['finish'], rrow['modey'], rrow['modex'], rrow['pulse']]
        startdif = abs(rpulse[0]-lpulse[0])	#Difference in start pulse frame
        findif = abs(rpulse[1]-lpulse[1])	#Difference in finish pulse frame
        ydif = abs(rpulse[2]-lpulse[2])		#Difference in y-axis position
        xdif = rpulse[3]-lpulse[3]		#Difference in x-axis position (disparity)
        cost = int((ydif * YDW) + (startdif * SFW) + (findif * EFW))
        #print("Cost between " + str(lpulse[4]) + " and " + str(rpulse[4]) + " = " + str(cost))
        pulmatrix[index][i] = cost
print(pulmatrix)
#This command executes the Hungarian algorithm to match the most similar left and right pulses based on the distance matrix
row_ind, col_ind = linear_sum_assignment(pulmatrix)

# can only match as many pairs as minimum rows in left or right tables
#Therefore, choose the camera with the fewest pulses to loop through and change
#The name of spulse in corresponding L and R 
#print(col_ind)

if len(df_left) <= len(df_right) :
    for i, lrow in df_left.iterrows() :
        #print("left pulse " + str(lrow['pulse']) + " ... Best right col index" + str(col_ind[i]))
        #print("\t" + df_right.loc[[col_ind[i]]]['pulse'].item() )
        df_left.at[i, 'spulse'] = ("sp" + str(i))
        df_right.at[col_ind[i], 'spulse'] = ("sp" + str(i))
else :
    for i, rrow in df_right.iterrows() :
        #print("right pulse " + str(rrow['pulse']) + " ... Best left col index" + str(col_ind[i]))
        #print("\t" + df_left.loc[[col_ind[i]]]['pulse'].item() )
        df_right.at[i, 'spulse'] = ("sp" + str(i))
        df_left.at[col_ind[i], 'spulse'] = ("sp" + str(i))

#print(row_ind)
#print (pulmatrix[row_ind, col_ind].sum())




df_stereo_pairs = pd.concat([df_left, df_right], axis=0)

#remove pulses without a stereo pair
df_stereo_pairs = df_stereo_pairs.loc[df_stereo_pairs['spulse'] != 'none']
df_stereo_pairs = df_stereo_pairs.loc[df_stereo_pairs['spulse'] != 'candidate']


#Print to screen
#print("SEGMENTED PULSES")
#print(finalpulses.to_string())
print("\nSTEREO PAIRS")
df_stereo_pairs = df_stereo_pairs.sort_values(['spulse'])

print(df_stereo_pairs.to_string())
# saving as a CSV file
finalpulses.to_csv('segmented_' + name + '.tab', sep ='\t')
df_stereo_pairs.to_csv('stereo_' + name + '.tab', sep ='\t')
