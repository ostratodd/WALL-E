import argparse
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

def process_data(file_path, min_cluster_size, output_path):
    # Load the tab-delimited file into a pandas DataFrame
    data = pd.read_csv(file_path, sep='\t')
    
    # Normalize cX, cY, frame, and area using StandardScaler
    scaler = StandardScaler()
    data[['cX', 'cY', 'frame', 'area']] = scaler.fit_transform(data[['cX', 'cY', 'frame', 'area']])
    
    # Apply DBSCAN clustering algorithm
    clustering = DBSCAN(eps=0.3, min_samples=50).fit(data[['cX', 'cY', 'frame', 'area']])
    data['cluster'] = clustering.labels_
    
    # Count the number of elements in each cluster
    cluster_counts = data['cluster'].value_counts()
    
    # Create a new column 'glare' based on the cluster size threshold
    data['glare'] = data['cluster'].apply(lambda x: 'no' if x == -1 else ('yes' if cluster_counts.get(x, 0) >= min_cluster_size else 'no'))
    
    # Save the updated DataFrame to a new file
    data.to_csv(output_path, sep='\t', index=False)
    print(f"Processed data saved to {output_path}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Cluster contours and detect glare.')
    parser.add_argument('file_path', type=str, help='Path to the input tab-delimited file')
    parser.add_argument('min_cluster_size', type=int, help='Minimum number of elements to consider a cluster as glare')
    parser.add_argument('output_path', type=str, help='Path to the output file')

    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Call the processing function
    process_data(args.file_path, args.min_cluster_size, args.output_path)

if __name__ == '__main__':
    main()

