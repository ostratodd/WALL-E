#!/usr/bin/env python3

import argparse

def frame_to_time(frame_number, fps=30):
    # Calculate total seconds
    total_seconds = frame_number / fps
    
    # Convert to minutes and seconds
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    
    return minutes, seconds, total_seconds

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Convert frame number to time in minutes:seconds and total seconds.")
    parser.add_argument("frame_number", type=int, help="The frame number to convert")
    args = parser.parse_args()

    # Convert frame number to time
    minutes, seconds, total_seconds = frame_to_time(args.frame_number)

    # Print results
    print(f"Time: {minutes}:{seconds:.2f} (minutes:seconds)")
    print(f"Total seconds: {total_seconds:.2f} seconds")

if __name__ == "__main__":
    main()

