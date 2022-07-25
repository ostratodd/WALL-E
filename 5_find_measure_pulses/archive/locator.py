import numpy as np
import cv2
import sys

# Ostracod Model

class Ostracod:
    def __init__(self, location, area, brightness):
        self.location = location            # x, y coordinates
        self.area = area                    # area of the contour
        self.brightness = brightness        # 0-255
        self.matches = []                   # indexes of another ostracod in a corresponding stereo frame, match value


def calculate_location(image, mask):
    """Calculate centroid of contour

    :param image: Image of entire Frame (numpy array)
    :param mask: Mask of location of pulse (numpy array)
    :return: Centroid - (x,y) - of contour
    """
    _, _, _, max_loc = cv2.minMaxLoc(image, mask=mask)
    return max_loc

def calculate_area(contour):
    """Calculates area of a single contour

    :param contour: Contour - Numpy array of (x,y) coordinates of boundary points of the object
    :return: Area of contour
    """
    return cv2.contourArea(contour)

def calculate_brightness(image, mask):
    """Brightness of pulse area

    :param image: Image of entire Frame (numpy array)
    :param mask: Mask of location of pulse (numpy array)
    :return: Brightness
    """
    brightness = cv2.mean(image, mask=mask)
    return brightness[0]

def find_contours(threshold):
    """Finds contours in thresholded image

    :param threshold: Image that has been thresholded (numpy array)
    :return: List of contours, which are numpy arrays of (x,y) coordinates of boundary points of the object
    """
    _, contours, _ = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def filter_image(image, threshold):
    """Filters given image

    :param image: Image to be thresholded (numpy array) 
    :param threshold: Threshold brightness value
    :return: Thresholded image (numpy array)
    """
    retval, thresh = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return thresh

def get_ostracods(image):
    """Gets list of Ostracod objects found in a given image

    :param image: Image to search for Ostracods
    :return: List of Ostracod objects
    """
    if image is None:
        sys.exit("unable to load image")
    if len(image[0][0]) == 3:
        imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        imgray = image
    threshold = filter_image(imgray, 90)
    contours = find_contours(threshold)
    ostracod_list = []
    for c in contours:
        mask = np.zeros(imgray.shape, np.uint8)
        cv2.drawContours(mask, [c], 0, 255, -1)
        brightness = calculate_brightness(imgray, mask)
        area = calculate_area(c)
        location = calculate_location(imgray, mask)
        if area >= 5:
            print("HIT ostracod!!")
            loc_list = [location[0], location[1], 0]
            ostracod = Ostracod(loc_list, area, brightness)
            ostracod_list.append(ostracod)
    return ostracod_list


def main():
    image = cv2.imread('image_example.png')
    get_ostracods(image)


if __name__ == '__main__':
    main()

