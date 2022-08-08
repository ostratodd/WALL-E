#!/usr/bin/env bash

#echo "Writing a file" > $1.mkv

ffmpeg -i $1 -f matroska -vcodec libx264 -an -framerate 30 -crf 0 $2.mkv
#ffmpeg -i $1.ASF -f matroska -vcodec libx264 -an -framerate 30 -crf 0 $2R.mkv

