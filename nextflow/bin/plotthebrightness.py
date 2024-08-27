import matplotlib.pyplot as plt
import pandas as pd

# Load the CSV file into a pandas DataFrame
file_path = './vidtest/cfr_2024bocassmalle4calR_cl_1_5400_brightness_26Aug_2B.csv'  # Replace with your actual file path
df = pd.read_csv(file_path, header=None)

# Assign column names for easier reference
df.columns = ['Frame', 'b=150', 'b=175', 'b=200', 'Raw']

# Convert columns to appropriate data types
df['Frame'] = df['Frame'].astype(int)
df['b=150'] = df['b=150'].astype(float)
df['b=175'] = df['b=175'].astype(float)
df['b=200'] = df['b=200'].astype(float)
df['Raw'] = df['Raw'].astype(float)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(df['Frame'].values, df['b=150'].values, label='b=150', color='blue')
plt.plot(df['Frame'].values, df['b=175'].values, label='b=175', color='green')
plt.plot(df['Frame'].values, df['b=200'].values, label='b=200', color='red')
plt.plot(df['Frame'].values, df['Raw'].values, label='Raw', color='orange')

# Adding labels and title
plt.xlabel('Frame')
plt.ylabel('Brightness')
plt.title('Brightness and Raw Brightness Over Frames')
plt.legend()

# Display the plot
plt.show()

