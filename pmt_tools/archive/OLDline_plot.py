# line_plot.py
"""
A live auto-updating plot of random numbers pulled from a web API
"""

import time
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv

#def animate(i, xs:list, ys:list):
#    # grab the data from thingspeak.com
#    # Add x and y to lists
#    xs.append(dt.datetime.now().strftime('%H:%M:%S'))
#    ys.append(flt)
#    # Limit x and y lists to 10 items
#    xs = xs[-10:]
#    ys = ys[-10:]
#    # Draw x and y lists
#    ax.clear()
#    ax.plot(xs, ys)
#    # Format plot
#    ax.set_ylim([0,255])
#    plt.xticks(rotation=45, ha='right')
#    plt.subplots_adjust(bottom=0.20)
#    ax.set_title('Photon counts')
#    ax.set_xlabel('Time')
#    ax.set_ylabel('Photons')

def animate(i):
    with open('pmt_test.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
#            data.append(int(row.strip()))
             print(row[1])
        ax.clear()
        ax.plot(row[1][-5:]) # plot the last 5 data points

##Read data for plotting
#with open('pmt_test.csv', newline='') as csvfile:
#    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
#    for row in spamreader:
#        print(', '.join(row))

# Create figure for plotting
fig, ax = plt.subplots()
xs = []
ys = []

## Set up plot to call animate() function every 1000 milliseconds
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
