#!/bin/bash
#*******
#This section contains variables for the pipeline 
#1. Name and location of video with checkers
DIRECTORY='southwater_pan'
V1=
V2=

#2. First clip the video where the checkerboards are. Will need to manually determine offset. Clipping reduces size of video for faster analyses 

OFFSET=11
CHECKER_S=1200
CHECKER_E=1300

#3 Next pull the checkerboard frames into a folder for calibration
MOVE_THRESH=1
CB_SIZE='8 6'

#4 find stereo vision parameters. No new variables here.

#5 rectify checkerboard video to check quality of stereo rectification
