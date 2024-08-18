import cv2
import numpy as np
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Test quality of stereo rectified videos.")
    parser.add_argument("-v1", "--video1", required=True, help="Path to the left video.")
    parser.add_argument("-v2", "--video2", required=True, help="Path to the right video.")
    parser.add_argument("-p", "--pattern", required=True, type=str, help="Checkerboard pattern size as NxM (e.g., 9x6).")
    parser.add_argument("-s", "--squareSize", required=True, type=float, help="Size of one square in the checkerboard (in mm).")
    return parser.parse_args()

def find_checkerboard_corners(frame, pattern_size):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)
    if ret:
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), 
                                   criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01))
    return ret, corners

def analyze_stereo_videos(video1_path, video2_path, pattern_size, square_size):
    cap_left = cv2.VideoCapture(video1_path)
    cap_right = cv2.VideoCapture(video2_path)

    objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
    objp *= square_size

    objpoints = []  # 3D points in real world space
    imgpoints_left = []  # 2D points in left image plane
    imgpoints_right = []  # 2D points in right image plane

    frame_idx = 0
    while cap_left.isOpened() and cap_right.isOpened():
        ret_left, frame_left = cap_left.read()
        ret_right, frame_right = cap_right.read()

        if not ret_left or not ret_right:
            break

        frame_idx += 1

        ret_left, corners_left = find_checkerboard_corners(frame_left, pattern_size)
        ret_right, corners_right = find_checkerboard_corners(frame_right, pattern_size)

        if ret_left and ret_right:
            objpoints.append(objp)
            imgpoints_left.append(corners_left)
            imgpoints_right.append(corners_right)

            # Check alignment of corresponding points
            alignment_error = np.mean(np.abs(corners_left[:, :, 1] - corners_right[:, :, 1]))
            print(f"Frame {frame_idx}: Alignment Error = {alignment_error:.3f} pixels")

    cap_left.release()
    cap_right.release()

    if len(objpoints) == 0:
        print("No valid frames found with detected checkerboards.")
        return

    # Stereo Calibration (usually done before rectification)
    retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(
        objpoints, imgpoints_left, imgpoints_right, None, None, None, None, 
        flags=cv2.CALIB_FIX_INTRINSIC
    )

    # Rectify stereo images and calculate projection matrices
    R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, 
                                                frame_left.shape[:2], R, T, flags=cv2.CALIB_ZERO_DISPARITY)

    # Compute 3D points from stereo matching
    reprojection_errors = []
    distance_errors = []
    for i in range(len(objpoints)):
        # Project points to 3D space
        points_left = cv2.undistortPoints(imgpoints_left[i], cameraMatrix1, distCoeffs1, R=R1, P=P1)
        points_right = cv2.undistortPoints(imgpoints_right[i], cameraMatrix2, distCoeffs2, R=R2, P=P2)

        disparity = points_left[:, :, 0] - points_right[:, :, 0]
        points_3D = cv2.reprojectImageTo3D(disparity.reshape(-1, 1), Q)

        # Compute distances between adjacent points in the checkerboard pattern
        for j in range(0, len(points_3D) - 1, pattern_size[0]):
            real_distance = square_size / 1000.0  # Convert mm to meters
            measured_distance = np.linalg.norm(points_3D[j] - points_3D[j + 1])
            distance_errors.append(abs(measured_distance - real_distance))

    # Calculate and print the mean reprojection and distance errors
    mean_distance_error = np.mean(distance_errors)
    print(f"Mean Distance Error: {mean_distance_error:.6f} meters")

def main():
    args = parse_arguments()
    pattern_size = tuple(map(int, args.pattern.split('x')))
    square_size = args.squareSize

    analyze_stereo_videos(args.video1, args.video2, pattern_size, square_size)

if __name__ == "__main__":
    main()

