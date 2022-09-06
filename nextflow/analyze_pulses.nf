#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.infile = "$baseDir/data/infile.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'
params.DATA_DIR='data'


/* Parameters for finding contours */
params.black = 120
params.minpulse = 2
params.watchvideo = 1
params.delay = 0
params.HPP = 2

/* Parameters for visualizing contours */
params.mindis = 20



/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
    then runs undistort (fisheye) custom for WALLE camera housings           */


workflow {

    pairs_ch = Channel.fromPath(params.infile, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.videoR, row.start, row.end, row.name, row.stereomap, row.baseline) }

    rectify(pairs_ch)
    find_contours(rectify.out.vidarray)
    segment_contours(find_contours.out)
    parallax_depth(segment_contours.out.stereo)
    visualize(find_contours.out)
    visualize_segments(segment_contours.out[0])
    visualize_coordinates(parallax_depth.out[0])
}

process visualize_coordinates {

    publishDir "$params.DATA_DIR/plots"
    conda = 'conda-forge::matplotlib conda-forge::pandas conda-forge::seaborn conda-forge::numpy'

    input :
    tuple file(f), val(name)

    output :
    file('*.pdf')


    script:
    """
    visualize_coordinates.py -f $f -o ${name}_coordinateplot -d ${params.mindis}
    """
}
process parallax_depth {
    conda = 'conda-forge::matplotlib conda-forge::pandas conda-forge::seaborn conda-forge::numpy'
    publishDir "$params.DATA_DIR/contours"

    input:
    tuple file(f), val(name), val(baseline)

    output:
    tuple file('coordinates_*.tab'), val(name)

    script:
    """
    parallax_depth.py -f $f -o $name -d $baseline -F ${params.FOCAL} -ALPHA ${params.ALPHA} -frame_width ${params.frame_width} -frame_height ${params.frame_height} -rate ${params.FPS} 

    """
}
process segment_contours {
    conda = 'conda-forge::matplotlib conda-forge::pandas conda-forge::seaborn conda-forge::numpy'

    publishDir "$params.DATA_DIR/contours"

    input:
    tuple file(f), val(name), val(baseline)
    
    output:
    tuple file('segmented_*.tab'), val(name)
    tuple file('stereo_*.tab'), val(name), val(baseline), emit: stereo

    script:
    """
    segment_pulses.py -f $f -n $name -HPP ${params.HPP} -HPD ${params.HPD} -XMAX ${params.XMAX} -YMAX ${params.YMAX} -SRMAX ${params.SRMAX} -PDMIN ${params.PDMIN} -PSD ${params.PSD} -PFD ${params.PFD} -XD ${params.XD}
    """
}


process visualize {
    publishDir "$params.DATA_DIR/plots"
    conda = 'conda-forge::matplotlib conda-forge::pandas conda-forge::seaborn conda-forge::numpy'

    input :
    tuple file(f), val(name), val(baseline)

    output :
    file('*.pdf')

    script :
    """
    visualize_contours.py -f $f -o ${name}_contourplot
    """

}
process visualize_segments {
    publishDir "$params.DATA_DIR/plots"
    conda = 'conda-forge::matplotlib conda-forge::pandas conda-forge::seaborn conda-forge::numpy'

    input :
    tuple file(f), val(name)

    output :
    file('*.pdf')

    script :
    """
    visualize_contours.py -f $f -o ${name}_segmented
    """

}

process rectify {
    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    publishDir "$params.VIDEO_DIR/rectified"

    input:
    tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap), val(baseline)

    output:
    path('*.mkv')
    tuple file('*L.mkv'), file('*R.mkv'), val(name), val(baseline), emit: vidarray

    script:
    """
    rectify_videos.py -v1 $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}_undis.mkv -f $baseDir/${params.DATA_DIR}/stereo_maps/${stereomap}_stereoMap.xml -l 0 -w 0 -pre ${name}
    """
}

process find_contours {

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'
    publishDir "$params.DATA_DIR/contours"

    input:
    tuple val(VL), val(VR), val(name), val(baseline)
    
    output:
    tuple file('*.tab'), val(name), val(baseline)

    script:
    """
    find_contours.py -v1 $VL -v2 $VR -b ${params.black} -m ${params.minpulse} -f ${name} -l ${params.watchvideo} -d ${params.delay}

    """
}

/*

    conda = 'conda-forge::opencv=4.5.5 conda-forge::numpy=1.22.4'

*/
