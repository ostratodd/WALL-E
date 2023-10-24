#!/bin/bash

# Set the number of processors you want to use for parallel execution.
# You can adjust this value based on the number of available processors.
NUM_PROCESSORS=$(sysctl -n hw.ncpu)

# Directory containing the files to analyze.
DIRECTORY="/Volumes/oakley_lab/aquarium/2023Pan/July22_2023"

# Function to wait for background processes to finish.
function wait_for_background_jobs {
    local current_jobs=$(jobs -p)
    while (( $(echo "$current_jobs" | wc -w) >= NUM_PROCESSORS )); do
        sleep 1
        current_jobs=$(jobs -p)
    done
}

# Loop through files from output_0.mp4 to output_25.mp4.
for i in {1..23}; do
    # Create the input file name (e.g., output_0.mp4, output_1.mp4, etc.).
    input_file="output_${i}.mp4"

    # Create the output CSV file name (e.g., output0.csv, output1.csv, etc.).
    output_csv="output${i}.csv"

    # Command to analyze the file using brightnessOverTime.py.
    cmd="./brightnessOverTime.py -p $DIRECTORY -f $input_file -o $output_csv -v 0 &"

    # Execute the command in the background and wait if there are already too many jobs running.
    eval "$cmd"
    wait_for_background_jobs
done

# Wait for any remaining background jobs to finish.
wait

