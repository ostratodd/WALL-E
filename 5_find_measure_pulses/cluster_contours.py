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

table = pd.read_csv(file, delimiter = '\t', header = [0,1])


db = DBSCAN(eps=3.5, min_samples = 5).fit(table)

core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

set(db.labels_)
from collections import Counter
print(Counter(db.labels_))


print("Estimated number of clusters: %d" % n_clusters_)
print("Estimated number of noise points: %d" % n_noise_)


unique_labels = set(labels)
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]


for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = labels == k
    plt.plot(
        table['cX'][class_member_mask & core_samples_mask],
        table['cY'][class_member_mask & core_samples_mask],
        "o",
        markerfacecolor=tuple(col),
        markeredgecolor="k",
        markersize=14,
    )

    plt.plot(
        table['cX'][class_member_mask & ~core_samples_mask],
        table['cY'][class_member_mask & ~core_samples_mask],
        "o",
        markerfacecolor=tuple(col),
        markeredgecolor="k",
        markersize=6,
    )
plt.title("Estimated number of clusters: %d" % n_clusters_)
plt.show()


print(table['cX'][class_member_mask])
print(table['cY'][class_member_mask])
