#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import argparse

def normalize_data(data):
    # Normalize cX, cY, frame, and area using StandardScaler
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(data[['cX', 'cY', 'frame', 'area']])
    return normalized_data

def cluster_data(data, eps, min_samples):
    # Perform DBSCAN clustering
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    cluster_labels = dbscan.fit_predict(data)
    return cluster_labels

def process_file(input_file, output_file, min_cluster_size, eps=0.5, min_samples=5):
    # Load the data
    df = pd.read_csv(input_file, sep='\t')

    # Normalize the data for clustering
    normalized_data = normalize_data(df)

    # Cluster the data
    cluster_labels = cluster_data(normalized_data, eps=eps, min_samples=min_samples)

    # Add cluster labels to the original dataframe
    df['cluster'] = cluster_labels

    # Determine the size of each cluster
    cluster_counts = df['cluster'].value_counts()

    # Add the 'glare' column based on the cluster size
    df['glare'] = df['cluster'].apply(
        lambda x: 'yes' if (x != -1 and cluster_counts[x] >= min_cluster_size) else 'no'
    )

    # Remove the 'cluster' column for the output
    df.drop(columns=['cluster'], inplace=True)

    # Write the new file
    df.to_csv(output_file, sep='\t', index=False)

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Cluster contour data and label glare.')
    parser.add_argument('input_file', type=str, help='Path to the input tab-delimited file.')
    parser.add_argument('output_file', type=str, help='Path to the output file.')
    parser.add_argument('--min_cluster_size', type=int, default=10000, help='Minimum number of elements in a cluster to be considered glare.')
    parser.add_argument('--eps', type=float, default=0.3, help='Epsilon parameter for DBSCAN.')
    parser.add_argument('--min_samples', type=int, default=50, help='Minimum number of samples for a cluster in DBSCAN.')
    args = parser.parse_args()

    # Process the file
    process_file(args.input_file, args.output_file, args.min_cluster_size, eps=args.eps, min_samples=args.min_samples)

