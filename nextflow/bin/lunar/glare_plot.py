#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scatter plot of Frame vs cX colored by glare or cluster.')
    parser.add_argument('input_file', type=str, help='Path to the input tab-delimited file.')
    parser.add_argument('--cluster', action='store_true', help='Use this flag to color by cluster instead of glare.')
    args = parser.parse_args()

    # Load the input file
    df = pd.read_csv(args.input_file, sep='\t')

    plt.figure(figsize=(10, 6))

    if args.cluster:
        # Color only the cluster '-1' differently
        cluster_negative_one = df[df['cluster'] == -1]
        cluster_other = df[df['cluster'] != -1]

        # Plot cluster '-1' in a specific color (e.g., red)
        plt.scatter(
            cluster_negative_one['frame'],
            cluster_negative_one['cX'],
            color='red',
            alpha=0.6,
            label="Cluster -1"
        )

        # Plot all other clusters in another color (e.g., blue)
        plt.scatter(
            cluster_other['frame'],
            cluster_other['cX'],
            color='blue',
            alpha=0.6,
            label="Other Clusters"
        )

        plt.legend(loc='upper right', title="Clusters", fontsize='small', markerscale=1.2)

    else:
        # Color by glare
        df['glare_color'] = df['glare'].apply(lambda x: 'red' if x == 'yes' else 'blue')

        # Plot the data based on glare
        for glare_value in df['glare'].unique():
            glare_data = df[df['glare'] == glare_value]
            plt.scatter(
                glare_data['frame'],
                glare_data['cX'],
                color='red' if glare_value == 'yes' else 'blue',
                alpha=0.6,
                label=f"Glare: {glare_value}"
            )
        plt.legend(loc='upper right', title="Glare", fontsize='small', markerscale=1.2)

    plt.xlabel('Frame')
    plt.ylabel('cX')
    plt.title('Scatter Plot of Frame vs cX')
    plt.show()

if __name__ == '__main__':
    main()

