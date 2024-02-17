import argparse

# Create an argument parser
parser = argparse.ArgumentParser(description='Filter lines based on the cX column value.')

# Add arguments for input and output files
parser.add_argument('-i', '--input_file', type=str, help='Input file name')
parser.add_argument('-o', '--output_file', type=str, help='Output file name')

# Parse the command-line arguments
args = parser.parse_args()

# Check if both input and output files are provided
if not args.input_file or not args.output_file:
    print("Please provide both input and output file names.")
    parser.print_help()
    exit()

# Open input and output files
with open(args.input_file, 'r') as infile, open(args.output_file, 'w') as outfile:
    # Read and write the header
    header = infile.readline()
    outfile.write(header)

    # Process each line in the input file
    for line in infile:
        # Split the line into columns
        columns = line.strip().split('\t')

        # Extract the value in the cX column
        cX_value = float(columns[2])

        # Check if the value is within the specified range
        if 280 <= cX_value <= 400:
            # Write the line to the output file
            outfile.write(line)

# Print a message indicating the process is complete
print(f"Filtered lines written to {args.output_file}")
