# animated_line_plot.py

from random import randint
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import matplotlib.animation as animation


# create empty lists for the x and y data
xs = []
ys = []

# function that draws each frame of the animation
def animate(i, xs:list, ys:list):

    xs = xs[-10:]
    ys = ys[-10:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    ax.set_ylim([0,368533])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.20)
    ax.set_title('Plot of random numbers from https://qrng.anu.edu.au')
    ax.set_xlabel('Date Time (hour:minute:second)')
    ax.set_ylabel('Random Number')

#    ax.clear()
#    ax.plot(x,y)
#    ax.set_xlim([0,200])
#    ax.set_ylim([0,10])

# create the figure and axes objects
fig, ax = plt.subplots()


with open('pmt_test.csv', newline='') as csvfile:
        infile = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in infile:
            ys.append(int(row[1]))
            ani = animation.FuncAnimation(fig, animate, fargs=(xs,ys), interval=1000)
            plt.show()







#ani = FuncAnimation(fig, animate, frames=500, interval=50)
