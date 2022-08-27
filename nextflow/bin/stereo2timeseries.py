#!/usr/bin/env python3

import matplotlib.pyplot as plt
import csv
import pandas as pd
import argparse
import seaborn as sns
import numpy as np
from operator import attrgetter


# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", required=True, type=str,
	help="file name for pulse data made by find_contours.py")
ap.add_argument("-o", "--outfile", required=False, default='', type=str,
	help="file name for pulse data made by find_contours.py")
args = vars(ap.parse_args())
file = args["file"]
outfile = args["outfile"]

table = pd.read_csv(file, delimiter = '\t')

df_table = pd.DataFrame(table)


s = (pd.concat([pd.Series(r.pname,pd.interval_range(r.start, r.end)) 
               for r in df_table.itertuples()])
        .index
        .value_counts()
        .sort_index())

#print(s.to_string())

time_series = s.rename_axis('frame').reset_index(name='pulses')

filtered = time_series.pulses.rolling(window=15).mean()


#print(time_series['frame'].map(attrgetter('left')))



plt.plot(time_series['frame'].map(attrgetter('left')), filtered)
plt.show()
