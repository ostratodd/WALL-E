import cv2

# Open the video file
video_path = 'video_data/cfr_2024bocassmalle4calL.mp4'  # Replace with your video file path
cap = cv2.VideoCapture(video_path)

# Check if the video opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
else:
    # Read the first frame to get the dimensions
    ret, frame = cap.read()
    if ret:
        height, width = frame.shape[:2]
        print(f"Frame width: {width}")
        print(f"Frame height: {height}")
    else:
        print("Error: Could not read the frame.")

# Release the video capture object
cap.release()

