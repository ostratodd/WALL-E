import os

import cv2

from gui.pipeline1.utilities.constants import LEFT_FRAMES_COUNT_PREFIX, RIGHT_FRAMES_COUNT_PREFIX
from image_converter import cv2_bgr_image_to_tkinter, cv2_bgr_image_to_tkinter_with_resize


class VideoFrameLoader:
    def __init__(self, left_feed_filename, right_feed_filename):
        self.vc_left = cv2.VideoCapture(left_feed_filename)
        self.vc_right = cv2.VideoCapture(right_feed_filename)
        self.left_feed_filename = left_feed_filename
        self.right_feed_filename = right_feed_filename
        self.left_feed_basename = os.path.basename(left_feed_filename)
        self.right_feed_basename = os.path.basename(right_feed_filename)
        self.last_frame_num_left = None
        self.last_frame_num_right = None

    def get_left_frame(self, frame_num):
        self.vc_left.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        return self.vc_left.read()

    def get_left_current_frame_num(self):
        return self.vc_left.get(cv2.CAP_PROP_POS_FRAMES)

    def set_left_current_frame_num(self, frame_num):
        self.vc_left.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

    def get_left_frame_tkinter(self, frame_num):
        self.vc_left.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, img = self.vc_left.read()
        if success:
            return True, cv2_bgr_image_to_tkinter(img)
        else:
            return False, None

    def get_left_frame_tkinter_with_resize(self, frame_num, width, height):
        self.vc_left.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, img = self.vc_left.read()
        if success:
            return True, cv2_bgr_image_to_tkinter_with_resize(img, width, height)
        else:
            return False, None

    def get_next_left_frame(self):
        return self.vc_left.read()

    def get_next_left_frame_tkinter(self):
        success, img = self.vc_left.read()
        if success:
            return True, cv2_bgr_image_to_tkinter(img)
        else:
            return False, None

    def get_next_left_frame_tkinter_with_resize(self, width, height):
        success, img = self.vc_left.read()
        if success:
            return True, cv2_bgr_image_to_tkinter_with_resize(img, width, height)
        else:
            return False, None

    def get_right_frame(self, frame_num):
        self.vc_right.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        return self.vc_right.read()

    def get_right_current_frame_num(self):
        return self.vc_right.get(cv2.CAP_PROP_POS_FRAMES)

    def set_right_current_frame_num(self, frame_num):
        self.vc_right.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

    def get_right_frame_tkinter(self, frame_num):
        self.vc_right.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, img = self.vc_right.read()
        if success:
            return True, cv2_bgr_image_to_tkinter(img)
        else:
            return False, None

    def get_right_frame_tkinter_with_resize(self, frame_num, width, height):
        self.vc_right.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, img = self.vc_right.read()
        if success:
            return True, cv2_bgr_image_to_tkinter_with_resize(img, width, height)
        else:
            return False, None

    def get_next_right_frame(self):
        return self.vc_right.read()

    def get_next_right_frame_tkinter(self):
        success, img = self.vc_right.read()
        if success:
            return True, cv2_bgr_image_to_tkinter(img)
        else:
            return False, None

    def get_next_right_frame_tkinter_with_resize(self, width, height):
        success, img = self.vc_right.read()
        if success:
            return True, cv2_bgr_image_to_tkinter_with_resize(img, width, height)
        else:
            return False, None

    def count_frames_in_videos(self, controller):
        if self.last_frame_num_left is None:
            self.last_frame_num_left = count_frames_in_vc_object(self.vc_left, controller, LEFT_FRAMES_COUNT_PREFIX)

        if self.last_frame_num_right is None:
            self.last_frame_num_right = count_frames_in_vc_object(self.vc_right, controller, RIGHT_FRAMES_COUNT_PREFIX)

        return self.last_frame_num_left, self.last_frame_num_right


def count_frames_in_vc_object(vc_obj, controller, message_prefix):
    vc_obj.set(cv2.CAP_PROP_POS_FRAMES, 0)

    count = 0
    controller.update_frame(message_prefix + str(count))
    while True:
        success, _ = vc_obj.read()

        if not success:
            break

        count += 1

        # Update the controller every 100 frames
        if count == 0 or count % 1000 == 0:
            controller.update_frame(message_prefix + str(count))

    # In case there's something glitchy with the last frame
    count -= 1
    controller.update_frame(message_prefix + str(count))
    return count
