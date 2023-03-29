#!/usr/bin/env python3
import cv2
import argparse

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, type=str,
        help="file name for video to undistort")
ap.add_argument("-w", "--watch", required=False, default=0, type=int,
        help="whether (1) or not (0) to watch video while writing. Default = 0")
ap.add_argument("-o", "--outfile", required=True, type=str,
        help="outfile for video name not including extension")
ap.add_argument("-a", "--alpha", required=False, type=float, default=0.05,
        help="alpha smoothing value is percent weight of current frame, e.g. 0.05")
#ap.add_argument ('-fr', '--frameSize', nargs=2, type=int, action = 'append', required=True,
#        help="need to specify frame size of video e.g. -c 640 480")

args = vars(ap.parse_args())
watch = args["watch"]
video = args["video"]
alpha = args["alpha"]
outfile = args["outfile"]
#frameSize = args["frameSize"]
#frameSize = tuple(frameSize[0])


# Open the video file
cap = cv2.VideoCapture(video)

# Get the frames per second (fps) of the video
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(outfile, fourcc, fps, (int(cap.get(3)),int(cap.get(4))))


#out = cv2.VideoWriter(outfile,cv2.VideoWriter_fourcc('H','2','6','4'), fps, (int(cap.get(3)),int(cap.get(4))))

# Initialize variables for the moving average
num_frames = 0
moving_average = None

while(cap.isOpened()):
    # Read a frame from the video
    ret, frame = cap.read()

    if ret == True:
        # Increment the number of frames
        num_frames += 1

        # Add the frame to the moving average
        if moving_average is None:
            moving_average = frame.astype("float")
        else:
            cv2.accumulateWeighted(frame, moving_average, alpha)

        # Convert the moving average to uint8
        output = cv2.convertScaleAbs(moving_average)

        # Write the output frame to the video file
        out.write(output)


        #If watch variable is true
        # Show the frames
        if watch == 1:
          cv2.imshow("frame", output)
          # Hit "q" to close the window
          if cv2.waitKey(1) & 0xFF == ord('q'):
              break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()
