import matplotlib.pyplot as plt
import csv
import pandas as pd
import numpy as np
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


#Parameters for segmenting into pulses
XMAX = 5	#max distance in X to be still considered the same pulse
YMAX = 5

SRMAX = 5	#max difference for correspondence of Y axis, assuming stereo rectification aligns Y
HPP = 0.15 	#hot pixel proportion = percentage of frames that contain a contour at the same X-axis value to be considered noise
HPD = 2		#hot pixel distance (number of pixels +/- ) from defined hot pixels

PDMIN = 3 	#minimum number of frames for pulse duration


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
                curpulse = curpulse.append(sorted.iloc[index]) #append data row to current pulse
            else :
                curpulse = curpulse.append(sorted.iloc[index-1])
                curpulse = curpulse.append(sorted.iloc[index])
        else :
            if len(curpulse.index) > 0:
                #add column data to curpulse with an identifier for this pulse
                pname = ["p" + str(pulseN)] * len(curpulse.index)
                curpulse['pulse'] = pname
                pulses = pulses.append(curpulse, ignore_index=True) #add current pulse into df with all pulses
                curpulse.drop(curpulse.index[:], inplace=True)	#reset to start new pulse
                pulseN = pulseN + 1
    oldRow = sorted.iloc[index]
    oldDifF = difF	#if previous frame had multiple countours must keep current if it is zero

#finalize remaining pulse at the end of the loop
if len(curpulse.index) > 0:
    pname = ["p" + str(pulseN)] * len(curpulse.index)
    curpulse['pulse'] = pname
    pulses = pulses.append(curpulse, ignore_index=True) #add current pulse into df with all pulses
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
                curpulse = curpulse.append(pulses.iloc[index]) #append data row to current pulse
            else :
                curpulse = curpulse.append(pulses.iloc[index-1])
                curpulse = curpulse.append(pulses.iloc[index])
        else :
            if len(curpulse.index) > 0:
                #add column data to curpulse with an identifier for this pulse
                pname = ["p" + str(pulseN)] * len(curpulse.index)
                curpulse['pulse'] = pname
                finalpulses = finalpulses.append(curpulse, ignore_index=True) #add current pulse into df with all pulses
                curpulse.drop(curpulse.index[:], inplace=True)	#reset to start new pulse
                pulseN = pulseN + 1
    oldRow = pulses.iloc[index]

finalpulses = finalpulses.sort_values(['pulse', 'frame', 'camera', 'cX', 'cY'])
#finalpulses = finalpulses.reset_index(drop=True)	#need to re-index df to use index later in order of sorted rows

xmode = finalpulses.mode()['cX'][0]					#find most common X-axis value
uframes = len(pd.unique(finalpulses['frame']))		#count total number of unique frames
noisepulses = 0

#Should probably separate out L and R cameras and do them separately
noisepulses = noisepulses + finalpulses['cX'].value_counts()[xmode]	#count total number of times most common X value is found

#I think there is a mistake here because it will count x-1 twice
for i in range(1, HPD + 1):
    if xmode + i in finalpulses['cX']:
        noisepulses = noisepulses + finalpulses['cX'].value_counts()[xmode + i] 	#Find number of frames within +/- HPD of most common value
    if xmode - i in finalpulses['cX']:
        noisepulses = noisepulses + finalpulses['cX'].value_counts()[xmode - i]


#Replace pulse name with 'noise' for most common x-axis value, if it is above the HPP threshold defining it as Hot Pixel noise
if(noisepulses/uframes > HPP) :
    finalpulses.loc[finalpulses.cX == xmode, 'pulse'] = "noise"
    for i in range(1, HPD + 1) :
        finalpulses.loc[finalpulses.cX == xmode + i, 'pulse'] = "noise"
        finalpulses.loc[finalpulses.cX == xmode - i, 'pulse'] = "noise"
        finalpulses.loc[finalpulses.cX == xmode, 'pulse'] = "noise"
        finalpulses.loc[finalpulses.cX == xmode + 1, 'pulse'] = "noise"
        finalpulses.loc[finalpulses.cX == xmode - 1, 'pulse'] = "noise"

#Visualize before noise



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
#df_pulse_sums = pd.DataFrame(columns=['camera','pulse','start', 'finish', 'minx', 'maxx', 'miny', 'maxy'])
df_pulse_sums = pd.DataFrame(columns=['camera','pulse'], index = ['0', '1'])
pulse_frames = denoised['pulse'].unique()
dfrows = 0
for rezy in pulse_frames:
    df_frames = denoised[denoised['pulse']==rezy]
    print("rezy: " + rezy)
    #df_pulse_sums[i] = [df_frames['camera'].mode(), rezy,  df_frames['frame'].min(), df_frames['frame'].max(), df_frames['cX'].min(), df_frames['cX'].max(), df_frames['cY'].min(), df_frames['cY'].max() ]
    df_pulse_sums[dfrows] = ['left', 'p8']
    dfrows = dfrows + 1
print(df_pulse_sums)
        #print(rezy + " is too short to be a pulse based on PDMIN = " + str(PDMIN))
        #finalpulses.loc[finalpulses.pulse == rezy, 'pulse'] = "too_short"

#Divide into L and R camera data frames
df_left = denoised[denoised['camera']=='left']
df_right = denoised[denoised['camera']=='right']
df_left = pulses.reset_index(drop=True)	
df_right = pulses.reset_index(drop=True)	

#print(df_left.to_string())
#print(df_right.to_string())




#Visualize after removing noise
#print(finalpulses.to_string())

fig, axs = plt.subplots(ncols=2)
sns.scatterplot(x='frame', y='cX', data=denoised, hue='pulse', edgecolor = 'none', ax=axs[0], legend = False)
axs[0].set_ylim(1, 640)
sns.scatterplot(x='frame', y='cY', data=denoised, hue='pulse', edgecolor = 'none', ax=axs[1], legend = False)
axs[1].set_ylim(1, 480)

##sns.scatterplot(x='frame', y='cX', data=noise, edgecolor = 'black', ax=axs[0], legend = False)

plt.show()



