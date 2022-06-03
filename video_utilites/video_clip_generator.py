import cv2
import argparse
from video_frame_loader import VideoFrameLoader
from file_checker import check_if_file_exists
import sys

#Script written by Capstone Class, including Vincent Wang, Wesley Peery


def generate_clip(left_video_filename, right_video_filename, start_frame, end_frame):
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    vfl = VideoFrameLoader(left_video_filename, right_video_filename)

    new_filename_l = left_video_filename[:-4] + "_clip_" + str(start_frame) + "_" + str(end_frame)+ ".mkv"
    new_filename_r = right_video_filename[:-4] + "_clip_" + str(start_frame) + "_" + str(end_frame)+ ".mkv"

    cp_left_video = cv2.VideoWriter(new_filename_l, fourcc, 30, (640, 478))
    cp_right_video = cv2.VideoWriter(new_filename_r, fourcc, 30, (640, 478))


    left_succ, left_img = vfl.get_left_frame(start_frame)
    right_succ, right_img = vfl.get_right_frame(start_frame)

    frame = start_frame

    while left_succ and right_succ and frame <= end_frame:
        cp_left_video.write(left_img)
        # right_img = cv2.flip(right_img, -1)
        cp_right_video.write(right_img)

        
        left_succ, left_img = vfl.get_next_left_frame()
        right_succ, right_img = vfl.get_next_right_frame()
        frame += 1
        cv2.imshow('clipping window',left_succ)


    print("Done! Your videos have been placed in the paths \"" +
          new_filename_l + "\" and \"" + new_filename_r + "\"")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("left_video", help="filename of the left video feed")
    parser.add_argument("right_video", help="filename of the right video feed")

    parser.add_argument("-s", "--start_frame", type=int,
                       help="start frame of the videos")
    parser.add_argument("-e", "--end_frame", type=int,
                       help="end frame of the videos")

    args = parser.parse_args()

    left_video_filename = args.left_video
    right_video_filename = args.right_video
    start_frame = args.start_frame
    end_frame = args.end_frame

    if end_frame < start_frame:
        sys.exit("Error: Get out of here with your impossible tasks! End frame is less than the start frame.")

    check_if_file_exists(left_video_filename)
    check_if_file_exists(right_video_filename)

    generate_clip(left_video_filename, right_video_filename, start_frame, end_frame)


if __name__ == '__main__':
    main()

