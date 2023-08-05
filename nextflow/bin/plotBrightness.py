import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates

# Function to convert frame numbers to datetime
def frame_to_time(frame_number, start_time, frame_rate):
    return start_time + timedelta(seconds=frame_number/frame_rate)

# Load the data
data = pd.read_csv('July20brightness', header=None)

# Frame rate
frame_rate = 15

# Start time
start_time = datetime.strptime('19:00:00', '%H:%M:%S')

# Frame to time conversion
data[0] = data[0].apply(lambda x: frame_to_time(x, start_time, frame_rate))

rolltime = 900 	#number of seconds over which to calculate moving aferage
moveave = int(rolltime * frame_rate)

# Calculate the moving average of y over rolltime frames
data[1] = data[1].rolling(window=moveave).mean()

# Define x and y
x = data[0]  # The first column is indexed as 0 in Python
y = data[1]  # The third column is indexed as 2

# Create scatter plot
plt.scatter(x, y, s=1)

# Set x and y axis labels
plt.xlabel('time')
plt.ylabel('average brightness per ' + str(rolltime/60) + ' min'  )

# Define the date format
date_format = mdates.DateFormatter('%H:%M:%S')

# Apply the date format
plt.gca().xaxis.set_major_formatter(date_format)

# Display the plot
plt.show()

