#!/usr/bin/env python3

#This python script prints the baseline (distance between cameras) as calculated from the calibration process

import pickle
import argparse
import numpy as np

def parse_arguments():
    parser = argparse.ArgumentParser(description="Print baseline distance from stereo calibration data.")
    parser.add_argument("-c", "--calibration", required=True, help="Path to the pickle file with calibration data.")
    return parser.parse_args()

def print_baseline(calibration_file):
    # Load calibration data from the pickle file
    with open(calibration_file, 'rb') as f:
        calibration_data = pickle.load(f)

    # Extract the translation vector T from the calibration data
    T = calibration_data.get('T')

    if T is not None:
        # Calculate the baseline (magnitude of the translation vector)
        baseline_mm = np.linalg.norm(T)
        print(f"Baseline (distance between cameras): {baseline_mm:.2f} mm")
    else:
        print("Translation vector 'T' not found in the calibration data.")

def main():
    args = parse_arguments()
    print_baseline(args.calibration)

if __name__ == "__main__":
    main()
