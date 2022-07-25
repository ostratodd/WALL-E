import matplotlib.pyplot as plt
import csv
import pandas as pd
import numpy as np
import argparse

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, default='.', 
        help="path to video frame files default is ./")
ap.add_argument("-f", "--file", required=True, type=str,
	help="file name for pulse data made by find_contours.py")
args = vars(ap.parse_args())
file = args["file"]

MAXX = 15
MAXY = 5


oldRow = []
framearray = []
rowcount = 1

with open(file) as file_obj:
    heading = next(file_obj)
    reader_obj = csv.reader(file_obj, delimiter= '\t')

    for row in reader_obj:
        #Is there more than one contour from the same frame number?
        #Need to analyze those together
        if rowcount > 1:
            if row[1] == oldRow[1]:
                if framearray :
                    framearray.append(row)
                else :
                    framearray.append(oldRow)
                    framearray.append(row)
            else :
                if framearray:
                    print(framearray)
                framearray = []
            #Is current contour close enough to form a pulse?


            #Save current row into oldRow value
        oldRow = row
        rowcount = rowcount + 1
