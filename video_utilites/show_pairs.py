# import the cv2 library
import cv2
import argparse

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument('--left_file', type=str, required=True, help='left matrix file')
ap.add_argument('--right_file', type=str, required=True, help='right matrix file')
ap.add_argument('--image_format', type=str, required=True, help='image format, png/jpg')

args = vars(ap.parse_args())
left = args["left_file"]
right = args["right_file"]
format = args["image_format"]


# The function cv2.imread() is used to read an image.
img_grayscale = cv2.imread(left,0)

# The function cv2.imshow() is used to display an image in a window.
cv2.imshow('graycsale image',img_grayscale)

# waitKey() waits for a key press to close the window and 0 specifies indefinite loop
cv2.waitKey(0)

# cv2.destroyAllWindows() simply destroys all the windows we created.
cv2.destroyAllWindows()

# The function cv2.imwrite() is used to write an image.
cv2.imwrite('grayscale.jpg',img_grayscale)




