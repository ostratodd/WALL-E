import cv2
import time
import os

def clip_video(video_path, start_minute=0, start_second=0, end_minute=0, end_second=0, fps=30, delay=0, watch=True):
    """
    Clips a video based on time input and saves the output.

    Parameters:
    - video_path (str): Path to the input video.
    - start_minute (int): Minute where the clip should start.
    - start_second (int): Second where the clip should start.
    - end_minute (int): Minute where the clip should end.
    - end_second (int): Second where the clip should end.
    - fps (int): Frames per second of the video (default: 30).
    - delay (float): Time (in seconds) between frames. Default is 0 for fastest playback.
    - watch (bool): Whether to display the video while processing (default: True).

    Returns:
    - str: The filename of the clipped video.
    """

    try:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"File not found: {video_path}")

        filename = os.path.basename(video_path)
        name, ext = os.path.splitext(filename)

        cap = cv2.VideoCapture(video_path)

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = int(cap.get(cv2.CAP_PROP_FPS))

        start = (start_minute * 60 + start_second) * fps
        end = (end_minute * 60 + end_second) * fps

        if start >= total_frames or end > total_frames or start >= end:
            raise ValueError(f"Invalid time range: start={start}, end={end}, total frames={total_frames}")

        cap.set(cv2.CAP_PROP_POS_FRAMES, start)

        frameSize = (frame_width, frame_height)

        output_filename = f"{name}_clipped_{start}_{end}.mkv"
        out = cv2.VideoWriter(output_filename, cv2.VideoWriter_fourcc(*'H264'), video_fps, frameSize)

        frame_count = 0
        window_name = "Video Clip"

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if start + frame_count >= end:
                break

            if watch:
                cv2.imshow(window_name, frame)



            if watch:
                cv2.imshow(window_name, frame)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

                # ✅ Move and resize window
                cv2.resizeWindow(window_name, 800, 600)  # Resize
                cv2.moveWindow(window_name, 100, 100)    # Move it to the top-left corner

                # ✅ Handle proper exit on 'q'
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n[INFO] User exited by pressing 'q'.")
                    break

            if delay > 0:
                time.sleep(delay)

            out.write(frame)
            frame_count += 1

    except KeyboardInterrupt:
        print("\n[INFO] User interrupted the process with Ctrl+C.")

    finally:
        print("[INFO] Releasing video resources...")
        cap.release()
        out.release()

        # ✅ Ensure windows are properly destroyed
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # Helps force window closure on macOS

        print(f"[INFO] Clipped video saved as: {output_filename}")

    return output_filename
