import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm

def stereo_calibrate_from_video(video_path, checkerboard_size, square_size, output_file="stereo_calibration.npz", recalibrate=True):
    """
    Performs stereo calibration using a clipped video, or skips to visualization if recalibrate=False.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"File not found: {video_path}")

    # ✅ If recalibrate=False, skip directly to visualization.
    if not recalibrate and os.path.exists(output_file):
        print("[INFO] Skipping calibration and loading existing calibration file...")
        visualize_first_checkerboard_pair(video_path, output_file, checkerboard_size)
        return output_file

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError("Error opening video file.")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"[INFO] Total frames in video: {total_frames}")

    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    half_width = frame_width // 2

    objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:checkerboard_size[1], 0:checkerboard_size[0]].T.reshape(-1, 2)
    objp *= square_size

    objpoints, imgpoints_left, imgpoints_right = [], [], []

    frame_skip = 5
    detected_frames = 0
    detected_frame_indices = []

    with tqdm(total=total_frames, desc="Processing Video", unit="frame") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            pbar.update(1)

            if frame_count % frame_skip != 0:
                continue

            left_img_full = frame[:, :half_width]
            right_img_full = frame[:, half_width:]

            gray_left = cv2.cvtColor(left_img_full, cv2.COLOR_BGR2GRAY)
            gray_right = cv2.cvtColor(right_img_full, cv2.COLOR_BGR2GRAY)

            ret_left, _ = cv2.findChessboardCorners(gray_left, checkerboard_size, None)
            ret_right, _ = cv2.findChessboardCorners(gray_right, checkerboard_size, None)

            if ret_left and ret_right:
                detected_frames += 1
                objpoints.append(objp)
                detected_frame_indices.append(frame_count)

    cap.release()
    cv2.destroyAllWindows()

    if detected_frames == 0:
        print("[ERROR] No valid checkerboard frames detected! Exiting calibration.")
        return None

    print(f"[INFO] Processed {total_frames} frames. Detected checkerboard in {detected_frames} frames.")

    cap = cv2.VideoCapture(video_path)
    imgpoints_left, imgpoints_right = [], []
    valid_objpoints = []
    gray_left_full, gray_right_full = None, None

    with tqdm(total=len(detected_frame_indices), desc="Retrieving full-res checkerboards", unit="frame") as pbar:
        for frame_idx in detected_frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, full_frame = cap.read()
            if not ret:
                continue

            left_img_full = full_frame[:, :half_width]
            right_img_full = full_frame[:, half_width:]
            gray_left_full = cv2.cvtColor(left_img_full, cv2.COLOR_BGR2GRAY)
            gray_right_full = cv2.cvtColor(right_img_full, cv2.COLOR_BGR2GRAY)

            ret_left, corners_left = cv2.findChessboardCorners(gray_left_full, checkerboard_size, None)
            ret_right, corners_right = cv2.findChessboardCorners(gray_right_full, checkerboard_size, None)

            if ret_left and ret_right:
                valid_objpoints.append(objp)
                imgpoints_left.append(corners_left)
                imgpoints_right.append(corners_right)

            pbar.update(1)

    cap.release()

    if len(valid_objpoints) == 0:
        print("[ERROR] No valid full-resolution checkerboard frames found!")
        return None

    print(f"[INFO] Using {len(valid_objpoints)} valid checkerboard frames for calibration.")

    print("[INFO] Calibrating individual cameras...")
    retL, mtxL, distL, rvecsL, tvecsL = cv2.calibrateCamera(
        valid_objpoints, imgpoints_left, gray_left_full.shape[::-1], None, None,
        flags=cv2.CALIB_ZERO_TANGENT_DIST  # ✅ Forces zero tangential distortion
    )
    retR, mtxR, distR, rvecsR, tvecsR = cv2.calibrateCamera(
        valid_objpoints, imgpoints_right, gray_right_full.shape[::-1], None, None,
        flags=cv2.CALIB_ZERO_TANGENT_DIST
    )

    print(f"[INFO] Left Camera Matrix:\n{mtxL}")
    print(f"[INFO] Right Camera Matrix:\n{mtxR}")

    print("[INFO] Performing stereo calibration...")
    ret, mtxL, distL, mtxR, distR, R, T, E, F = cv2.stereoCalibrate(
        valid_objpoints, imgpoints_left, imgpoints_right,
        mtxL, distL, mtxR, distR,
        gray_left_full.shape[::-1],
        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5),
        flags=cv2.CALIB_FIX_INTRINSIC | cv2.CALIB_ZERO_TANGENT_DIST
    )

    print("[INFO] Stereo calibration complete.")

    np.savez(output_file, ret=ret, mtxL=mtxL, distL=distL, mtxR=mtxR, distR=distR, R=R, T=T, E=E, F=F)
    print(f"[INFO] Stereo calibration saved to {output_file}")

    print("[INFO] Running stereo rectification visualization...")
    visualize_first_checkerboard_pair(video_path, output_file, checkerboard_size)

    return output_file




def visualize_first_checkerboard_pair(video_path, stereo_calib_file, checkerboard_size, frame_skip=5):
    print("[INFO] Extracting first checkerboard frame for visualization...")
    
    # Load stereo calibration results
    data = np.load(stereo_calib_file)
    mtxL, distL, mtxR, distR, R, T = data['mtxL'], data['distL'], data['mtxR'], data['distR'], data['R'], data['T']
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Error opening video file: {video_path}")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    half_width = frame_width // 2

    first_left_img = None
    first_right_img = None

    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    with tqdm(total=total_frames, desc="Searching for first checkerboard frame", unit="frame") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            pbar.update(1)
            if frame_count % frame_skip != 0:
                continue

            left_img = frame[:, :half_width]
            right_img = frame[:, half_width:]

            gray_left = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
            gray_right = cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY)

            ret_left, _ = cv2.findChessboardCorners(gray_left, checkerboard_size, None)
            ret_right, _ = cv2.findChessboardCorners(gray_right, checkerboard_size, None)

            if ret_left and ret_right:
                first_left_img = left_img.copy()
                first_right_img = right_img.copy()
                break
    
    cap.release()

    if first_left_img is None or first_right_img is None:
        print("[ERROR] No valid checkerboard frames found for visualization.")
        return
    
    print("[INFO] First detected checkerboard frame found. Performing rectification...")
    image_size = (first_left_img.shape[1], first_left_img.shape[0])
    
    # Stereo Rectification
    R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(mtxL, distL, mtxR, distR, image_size, R, T)
    print(f"[DEBUG] P1:\n{P1}")
    print(f"[DEBUG] P2:\n{P2}")
    print(f"[DEBUG] Q:\n{Q}")
    
    # Undistortion Maps
    mapL1, mapL2 = cv2.initUndistortRectifyMap(mtxL, distL, R1, P1, image_size, cv2.CV_32FC1)
    mapR1, mapR2 = cv2.initUndistortRectifyMap(mtxR, distR, R2, P2, image_size, cv2.CV_32FC1)
    print(f"[DEBUG] mapL1 min/max: {np.min(mapL1)}, {np.max(mapL1)}")
    print(f"[DEBUG] mapL2 min/max: {np.min(mapL2)}, {np.max(mapL2)}")
    print(f"[DEBUG] mapR1 min/max: {np.min(mapR1)}, {np.max(mapR1)}")
    print(f"[DEBUG] mapR2 min/max: {np.min(mapR2)}, {np.max(mapR2)}")
    
    # **Manual Undistortion Before Full Rectification**
    undistorted_left = cv2.undistort(first_left_img, mtxL, distL, None, mtxL)
    undistorted_right = cv2.undistort(first_right_img, mtxR, distR, None, mtxR)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(cv2.cvtColor(undistorted_left, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Undistorted Left Camera Image")
    axes[0].axis("off")

    axes[1].imshow(cv2.cvtColor(undistorted_right, cv2.COLOR_BGR2RGB))
    axes[1].set_title("Undistorted Right Camera Image")
    axes[1].axis("off")
    plt.show()
    
    print("[INFO] Applying full rectification...")
    rectified_left = cv2.remap(first_left_img, mapL1, mapL2, cv2.INTER_LINEAR)
    rectified_right = cv2.remap(first_right_img, mapR1, mapR2, cv2.INTER_LINEAR)
    
    def draw_epilines(img, num_lines=20, color=(0, 255, 0), thickness=1):
        h, w = img.shape[:2]
        for i in range(1, num_lines + 1):
            y = i * (h // num_lines)
            cv2.line(img, (0, y), (w, y), color, thickness)
        return img

    rectified_left = draw_epilines(rectified_left)
    rectified_right = draw_epilines(rectified_right)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(cv2.cvtColor(rectified_left, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Rectified First Checkerboard - Left")
    axes[0].axis("off")

    axes[1].imshow(cv2.cvtColor(rectified_right, cv2.COLOR_BGR2RGB))
    axes[1].set_title("Rectified First Checkerboard - Right")
    axes[1].axis("off")
    
    plt.show()
    print("[INFO] Visualization complete.")
