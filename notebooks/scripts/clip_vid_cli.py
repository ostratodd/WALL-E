#!/usr/bin/env python3
import argparse
import cv2
import os
import sys
import time
from typing import Optional, Tuple

def parse_hms_to_seconds(s: str) -> int:
    """
    Accepts 'SS', 'MM:SS', or 'HH:MM:SS' and returns total seconds (int).
    """
    parts = s.strip().split(":")
    try:
        if len(parts) == 1:
            return int(float(parts[0]))
        elif len(parts) == 2:
            m, sec = parts
            return int(m) * 60 + int(float(sec))
        elif len(parts) == 3:
            h, m, sec = parts
            return int(h) * 3600 + int(m) * 60 + int(float(sec))
        else:
            raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid time format '{s}'. Use SS, MM:SS, or HH:MM:SS."
        )

def human_time(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

def clip_video(
    video_path: str,
    start_seconds: int,
    end_seconds: Optional[int],
    delay: float = 0.0,
    watch: bool = True,
    output: Optional[str] = None,
    codec: str = "H264",
    ext: str = ".mkv",
) -> str:
    """
    Clips a video by (start_seconds, end_seconds) using the *file's* FPS.

    - If end_seconds is None, clip goes to the end of the file.
    - 'delay' sleeps per displayed frame (only affects on-screen playback speed).
    - 'watch' controls on-screen preview.
    - 'codec' is a fourcc string (e.g., H264, mp4v, XVID).
    - 'ext' is the output extension (e.g., .mkv, .mp4).
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"File not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open: {video_path}")

    try:
        frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps    = cap.get(cv2.CAP_PROP_FPS)

        if video_fps is None or video_fps <= 0:
            # Fallback to 30 if container is weird
            video_fps = 30.0

        # Translate seconds to frame indices using the *actual* FPS
        start_frame = int(round(start_seconds * video_fps))
        if end_seconds is None:
            end_frame = total_frames
        else:
            end_frame = int(round(end_seconds * video_fps))

        if start_frame < 0:
            start_frame = 0
        if end_frame > total_frames:
            end_frame = total_frames

        if start_frame >= end_frame:
            raise ValueError(
                f"Invalid time range: start {human_time(start_seconds)} "
                f"({start_frame}f) >= end {human_time(end_seconds or start_seconds)} "
                f"({end_frame}f), total frames={total_frames}"
            )

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        frame_size = (frame_width, frame_height)

        base = os.path.splitext(os.path.basename(video_path))[0]
        if output is None:
            output = f"{base}_clipped_{start_frame}_{end_frame}{ext}"

        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(output, fourcc, video_fps, frame_size)
        if not out.isOpened():
            raise RuntimeError(
                f"Failed to open output writer. Check codec '{codec}' and extension '{ext}'."
            )

        frame_count = 0
        window_name = "Video Clip"
        if watch:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 800, 600)
            cv2.moveWindow(window_name, 100, 100)

        while True:
            # Stop when we’ve written the intended range
            if start_frame + frame_count >= end_frame:
                break

            ret, frame = cap.read()
            if not ret:
                break

            if watch:
                cv2.imshow(window_name, frame)
                # Exit early with 'q'
                if (cv2.waitKey(1) & 0xFF) == ord('q'):
                    print("\n[INFO] User exited by pressing 'q'.")
                    break

            if delay > 0:
                time.sleep(delay)

            out.write(frame)
            frame_count += 1

        return output

    except KeyboardInterrupt:
        print("\n[INFO] User interrupted with Ctrl+C.")
        return output if 'output' in locals() and output else ""
    finally:
        # Always release safely
        try:
            cap.release()
        except Exception:
            pass
        try:
            if 'out' in locals():
                out.release()
        except Exception:
            pass
        try:
            cv2.destroyAllWindows()
            cv2.waitKey(1)  # Helps macOS close windows
        except Exception:
            pass

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Clip a segment from a video using start/end times.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("video", help="Path to the input video file.")
    p.add_argument(
        "--start",
        type=parse_hms_to_seconds,
        default="0",
        help="Start time (SS, MM:SS, or HH:MM:SS).",
    )
    p.add_argument(
        "--end",
        type=parse_hms_to_seconds,
        default=None,
        help="End time (SS, MM:SS, or HH:MM:SS). If omitted, clips to end of file.",
    )
    p.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Sleep per displayed frame (seconds). Affects preview speed only.",
    )
    p.add_argument(
        "--no-watch",
        action="store_true",
        help="Disable on-screen preview while processing.",
    )
    p.add_argument(
        "-o", "--output",
        default=None,
        help="Output filename (e.g., myclip.mp4). If omitted, autogenerated.",
    )
    p.add_argument(
        "--codec",
        default="H264",
        help="FourCC codec (e.g., H264, mp4v, XVID).",
    )
    p.add_argument(
        "--ext",
        default=".mkv",
        help="Output extension if autogenerated (e.g., .mp4, .mkv).",
    )
    return p

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        out_file = clip_video(
            video_path=args.video,
            start_seconds=args.start if isinstance(args.start, int) else parse_hms_to_seconds(args.start),
            end_seconds=args.end if (args.end is None or isinstance(args.end, int)) else parse_hms_to_seconds(args.end),
            delay=max(0.0, args.delay),
            watch=not args.no_watch,
            output=args.output,
            codec=args.codec,
            ext=args.ext,
        )
        if out_file:
            print(f"[INFO] Clipped video saved as: {out_file}")
        else:
            print("[WARN] No output file produced.")
        return 0
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

