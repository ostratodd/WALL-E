#!/usr/bin/env python3

import csv
import pandas as pd
import argparse
import numpy as np

from scipy.optimize import linear_sum_assignment


# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='./', 
        help="path to video frame files MUST include trailing /. Default is ./")
ap.add_argument("-f", "--file", required=True, type=str,
	help="file name for pulse data made by find_contours.py")
ap.add_argument("-n", "--name", required=True, type=str,
	help="file name for two output files")
ap.add_argument("-HPP", "--HPP", required=False, default=0.15, type=float,
	help="hot pixel proportion = percentage of frames that contain a contour at the same X-axis value to be considered noise")
args = vars(ap.parse_args())
file = args["file"]
name = args["name"]
HPP = args["HPP"]

#Parameters for segmenting into pulses
XMAX = 10	#max distance in X to be still considered the same pulse
YMAX = 10

SRMAX = 5	#max difference for correspondence of Y axis, assuming stereo rectification aligns Y
HPD = 2		#hot pixel distance (number of pixels +/- ) from defined hot pixels

PDMIN = 3 	#minimum number of frames for pulse duration

#Stereo parameters
PSD = 5 	#Pulse-start difference (minimum to diff in frame start to be considered stereo pair)
PFD = 5
YD = 10

table = pd.read_csv(file, delimiter = '\t')
sorted = table.sort_values(['camera', 'frame', 'cX', 'cY'])
sorted = sorted.reset_index(drop=True)	#need to re-index df to use index later in order of sorted rows

curpulse = pd.DataFrame(columns=table.columns)	#create a new dataframe for each new pulse as it is built
pulses = pd.DataFrame(columns=table.columns)	#create a new dataframe for all the pulses
pulses["pulse"] = "" #add column for pulse identifier 
pulseN = 1 #Number of pulse
difF = 0
OldDifF = -1

for index, row in sorted.iterrows():
    #first form pulses if contiguous frames are close in both x and y
    if index > 0:
        difX = abs(int(row['cX']) - sorted.iloc[index-1]['cX']) 
        difY = abs(int(row['cY']) - sorted.iloc[index-1]['cY']) 
        difF = abs(int(row['frame']) - sorted.iloc[index-1]['frame'])
        #print below to help debug
        #print("\tindex:" + str(index) + " frame:" + str(row['frame']) + " difF:" + str(difF) + " difX:" + str(difX) + " difY:" + str(difY) + " olddiff:" + str(oldDifF))

        #if difF is zero, multiple contours are on same frame, so automatically keep to sort later
        if (difF == 1 and oldDifF ==0) or (difX < XMAX and difY < YMAX and difF < 3) or (difF == 0): 
            if len(curpulse.index) > 0 :
                curpulse = pd.concat([curpulse, pd.DataFrame(sorted.iloc[index]).transpose()], axis=0) #append data row to current pulse
                #curpulse = curpulse.append(sorted.iloc[index]) #append data row to current pulse
                #print(curpulse)
            else :
                curpulse = pd.concat([curpulse, pd.DataFrame(sorted.iloc[index-1]).transpose()], axis=0) #append data row to current pulse
                curpulse = pd.concat([curpulse, pd.DataFrame(sorted.iloc[index]).transpose()], axis=0)
                #curpulse = curpulse.append(sorted.iloc[index-1])
                #curpulse = curpulse.append(sorted.iloc[index])
        else :
            if len(curpulse.index) > 0:
                #add column data to curpulse with an identifier for this pulse
                pname = ["p" + str(pulseN)] * len(curpulse.index)
                curpulse['pulse'] = pname
                pulses = pd.concat([pulses, curpulse], ignore_index=True)
                #pulses = pulses.append(curpulse, ignore_index=True) #add current pulse into df with all pulses
                curpulse.drop(curpulse.index[:], inplace=True)	#reset to start new pulse
                pulseN = pulseN + 1
    oldRow = sorted.iloc[index]
    oldDifF = difF	#if previous frame had multiple countours must keep current if it is zero

#finalize remaining pulse at the end of the loop
if len(curpulse.index) > 0:
    pname = ["p" + str(pulseN)] * len(curpulse.index)
    curpulse['pulse'] = pname
    pulses = pd.concat([pulses, curpulse], ignore_index=True)
    #pulses = pulses.append(curpulse, ignore_index=True) #add current pulse into df with all pulses
    curpulse.drop(curpulse.index[:], inplace=True)	#reset to start new pulse
    pulseN = pulseN + 1

pulses = pulses.sort_values(['pulse', 'camera', 'cX', 'cY', 'frame'])
pulses = pulses.reset_index(drop=True)	#need to re-index df to use index later in order of sorted rows

#*****************
#Next need to divide muliple pulses that span the same frames and are therefore in same pulse
pulseN = 1 						#start pulse numbering over again to rename
finalpulses = pd.DataFrame(columns=table.columns)	#create a new dataframe for the final pulses

for index, row in pulses.iterrows():
    if index > 0:
        difX = abs(int(row['cX']) - pulses.iloc[index-1]['cX']) 
        difY = abs(int(row['cY']) - pulses.iloc[index-1]['cY']) 
        #print below to help debug
        #print("\tindex:" + str(index) + " frame:" + str(row['frame']) + " difF:" + str(difF) + " difX:" + str(difX) + " difY:" + str(difY) + " olddiff:" + str(oldDifF))
        if (difX < XMAX and difY < YMAX): 
            if len(curpulse.index) > 0 :
                curpulse = pd.concat([curpulse, pd.DataFrame(pulses.iloc[index]).transpose()], axis=0) #append data row to current pulse
                #curpulse = curpulse.append(pulses.iloc[index]) #append data row to current pulse
            else :
                curpulse = pd.concat([curpulse, pd.DataFrame(pulses.iloc[index-1]).transpose()], axis=0) #append data row to current pulse
                curpulse = pd.concat([curpulse, pd.DataFrame(pulses.iloc[index]).transpose()], axis=0) #append data row to current pulse
#                curpulse = curpulse.append(pulses.iloc[index-1])
#                curpulse = curpulse.append(pulses.iloc[index])
        else :
            if len(curpulse.index) > 0:
                #add column data to curpulse with an identifier for this pulse
                pname = ["p" + str(pulseN)] * len(curpulse.index)
                curpulse['pulse'] = pname
                finalpulses = pd.concat([finalpulses, curpulse], ignore_index=True)
#                finalpulses = finalpulses.append(curpulse, ignore_index=True) #add current pulse into df with all pulses
                curpulse.drop(curpulse.index[:], inplace=True)	#reset to start new pulse
                pulseN = pulseN + 1
    oldRow = pulses.iloc[index]

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

#Finally, find most probable stereo pairs based on correspondence of frame start/stop, correspondence of Y-axis point, and possibly X-axis disparity
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

print(df_left)
print(df_right)

#Next find pulses close enough in start, finish, and y to qualify as left/right stereo pairs
#This narrows down in turn right pulses similar enough in Yaxis value, then start then finish time of pulse
#The best of remaining Candidates is currently chosen based on closest Y-axis value

spairN = 1

pulmatrix = np.zeros((len(df_left.index),len(df_right.index)))

print("Matrix of size: " + str(len(df_left.index)) + "x" + str(len(df_right.index)) )
#Create dict of dicts to use hungarian algorithm to match pulses
for index, lrow in df_left.iterrows():
    lpulse = [lrow['start'], lrow['finish'], lrow['modey'], lrow['modex'], lrow['pulse'] ] 
    for i, rrow in df_right.iterrows() :
        rpulse = [rrow['start'], rrow['finish'], rrow['modey'], rrow['modex'], rrow['pulse']]
        startdif = abs(rpulse[0]-lpulse[0])	#Difference in start pulse frame
        findif = abs(rpulse[1]-lpulse[1])	#Difference in finish pulse frame
        ydif = abs(rpulse[2]-lpulse[2])		#Difference in y-axis position
        xdif = rpulse[3]-lpulse[3]		#Difference in x-axis position (disparity)
        cost = int(ydif + startdif + findif)
        #print("Cost for [][]=c " + str(index) + "/" + str(i) + " = " + str(cost) )
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
        print("left pulse " + str(lrow['pulse']) + " ... Best right col index" + str(col_ind[i]))
        print("\t" + df_right.loc[[col_ind[i]]]['pulse'].item() )
        df_left.at[i, 'spulse'] = ("sp" + str(i))
        df_right.at[col_ind[i], 'spulse'] = ("sp" + str(i))
else :
    for i, rrow in df_right.iterrows() :
        print("right pulse " + str(rrow['pulse']) + " ... Best left col index" + str(col_ind[i]))
        print("\t" + df_left.loc[[col_ind[i]]]['pulse'].item() )
        df_right.at[i, 'spulse'] = ("sp" + str(i))
        df_left.at[col_ind[i], 'spulse'] = ("sp" + str(i))

#print(row_ind)
#print (pulmatrix[row_ind, col_ind].sum())






#        if(abs(startdif < PSD and findif < PFD and ydif < YD)) :
#            multimatch.append(i)
#            print("Left pulse:" + str(df_left.at[index, 'pulse']) + " matches Right index: " + str(df_right.at[i, 'pulse']) + " ydif,startdif,findif,xdif = " + str(ydif) + " " + str(startdif) + " " + str(findif) + " " + str(xdif)) 
#            right_match_i = i
#    if(len(multimatch) > 1) :
#        print ("Left pulse:" + str(df_left.at[index, 'pulse']) + " matches more than one right pulse\n")
#        df_left.at[index, 'spulse'] = ("multimatch")
#    else:
#        print ("Left pulse " + str(df_left.at[index, 'pulse']) + " has unique match to " + str(df_right.at[right_match_i, 'pulse'])  + " ydif,startdif,findif,xdif = " + str(ydif) + " " + str(startdif) + " " + str(findif) + " " + str(xdif) + "\n" )
#        df_left.at[index, 'spulse'] = ("sp" + str(spairN))
#        df_right.at[right_match_i, 'spulse'] = ("sp" + str(spairN))
#        spairN = spairN + 1

df_stereo_pairs = pd.concat([df_left, df_right], axis=0)
#remove pulses without a stereo pair
df_stereo_pairs = df_stereo_pairs.loc[df_stereo_pairs['spulse'] != 'none']


#Print to screen
print("SEGMENTED PULSES")
print(finalpulses.to_string())
print("\nSTEREO PAIRS")
df_stereo_pairs = df_stereo_pairs.sort_values(['spulse'])

print(df_stereo_pairs.to_string())
# saving as a CSV file
finalpulses.to_csv('segmented_' + name + '.tab', sep ='\t')
df_stereo_pairs.to_csv('stereo_' + name + '.tab', sep ='\t')
