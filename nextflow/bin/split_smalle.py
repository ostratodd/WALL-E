import cv2

# Open the input video
input_video_path = '/Users/oakley/Desktop/out_00.mp4'  # Replace with your video file path
cap = cv2.VideoCapture(input_video_path)

# Get the width and height of the video frames
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Calculate the width of the left and right halves
half_width = frame_width // 2

# Define the codec and create VideoWriter objects
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec if needed
left_output_path = 'left_half_video.mp4'
right_output_path = 'right_half_video.mp4'
left_out = cv2.VideoWriter(left_output_path, fourcc, 30.0, (half_width, frame_height))
right_out = cv2.VideoWriter(right_output_path, fourcc, 30.0, (half_width, frame_height))

# Process each frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Split the frame into left and right halves
    left_half = frame[:, :half_width]
    right_half = frame[:, half_width:]
    
    # Write the halves to their respective video files
    left_out.write(left_half)
    right_out.write(right_half)

# Release everything
cap.release()
left_out.release()
right_out.release()
cv2.destroyAllWindows()

