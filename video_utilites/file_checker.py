import os
import sys


def check_if_file_exists(filename):
    if not os.path.isfile(filename):
        sys.exit("File doesn't exist: " + filename)
