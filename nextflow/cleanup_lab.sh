#Clean up noise that was in lab that would not normally be in situ, so not worth trying to automate

#First, filter noise at x values outside of observed pulses
python bin/manual_contour_filter.py -i data/contours/contours_lab101.tab -o data/contours/contours_NEWlab101.tab
python bin/manual_contour_filter.py -i data/contours/contours_lab102.tab -o data/contours/contours_NEWlab102.tab


#Now re-segment pulses
./bin/segment_pulses.py -f data/contours/contours_NEWlab101.tab -n NEWlab101 -HPP 0.5 -HPD 10 -XMAX 5 -YMAX 5 -SRMAX 10 -PDMIN 3 -PSD 10 -PFD 70 -XD 300
./bin/segment_pulses.py -f data/contours/contours_NEWlab102.tab -n NEWlab102 -HPP 0.5 -HPD 10 -XMAX 5 -YMAX 5 -SRMAX 10 -PDMIN 3 -PSD 10 -PFD 10 -XD 300

#copy newly segmented and stereo pairs to contours directory
cp segmented_NEWlab101.tab data/contours/
cp stereo_NEWlab101.tab data/contours

#cp segmented_NEWlab102.tab data/contours/
#cp stereo_NEWlab102.tab data/contours

#Now calculate absolute values for coordinates
./bin/parallax_depth.py -f data/contours/stereo_NEWlab101.tab -o NEWlab101 -d 125 -F 3.7 -ALPHA 65 -frame_width 640 -frame_height 480 -rate 30
cp coordinates_NEWlab101.tab data/contours 

#./bin/parallax_depth.py -f data/contours/stereo_NEWlab102.tab -o NEWlab102 -d 125 -F 3.7 -ALPHA 65 -frame_width 640 -frame_height 480 -rate 30
#cp coordinates_NEWlab102.tab data/contours 

