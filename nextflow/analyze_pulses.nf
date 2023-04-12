#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'
params.DATA_DIR='data'

/*****The following parameters are set at defaults, but do not work for all videos. To change these, it is s easiest to use an input file ******/
	
/*Camera parameters*/
params.framesize = "640 480"
params.baseline		/*distance between cameras */


/* Parameters for finding contours */
params.black = 120
params.minpulse = 2
params.watchvideo = 0
params.lines = 0
params.delay = 0
params.HPP = 2  /* hot pixel noise filtering parameter >2 does not filter. 0.15 filter more aggressively */

/* Parameters for visualizing contours */
params.mindis = 20	

/* Parameters for segmenting pulses across frames into single pulses */
params.XMAX = 10
params.YMAX = 10
params.PDMIN = 30
params.HPD = 2

/* Parameters for pairing pulses across left and right cameras into stereo pulses */
params.PSD = 500
params.PFD = 500
params.SRMAX = 10
params.XD = 250


workflow {

    pairs_ch = Channel.fromPath(params.metadata, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.VL, row.VR, row.start, row.end, row.name, row.stereomap) }

    undistort(pairs_ch)
    rectify(undistort.out.uvidarray)
    find_contours(rectify.out.rvidarray)
    segment_contours(find_contours.out)
    parallax_depth(segment_contours.out.stereo)
    visualize(find_contours.out)
    visualize_segments(segment_contours.out[0])
    visualize_coordinates(parallax_depth.out[0])
}

process undistort {
    publishDir "$params.VIDEO_DIR/clips"
        
    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap)
    
    output:
    path '*.mkv'
    tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap), emit: uvidarray
 
    script:
    """   
    denoiseCamera.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}.mkv -p $baseDir/${params.DATA_DIR}/stereo_maps/ -pre ${stereomap}_L_single -w ${params.watchvideo} -fr ${params.framesize} -o ${name}${VL}_cl_${start}_${end}
    denoiseCamera.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}.mkv -p $baseDir/${params.DATA_DIR}/stereo_maps/ -pre ${stereomap}_R_single -w ${params.watchvideo} -fr ${params.framesize} -o ${name}${VR}_cl_${start}_${end}

    """
}
process rectify {
    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    publishDir "$params.VIDEO_DIR/rectified"

    input:
    tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap)

    output:
    path('*.mkv')
    tuple file('*L.mkv'), file('*R.mkv'), val(name), emit: rvidarray

    script:
    """
    rectify_videos.py -v1 $baseDir/${params.VIDEO_DIR}/clips/${name}${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/${name}${VR}_cl_${start}_${end}_undis.mkv -f $baseDir/${params.DATA_DIR}/stereo_maps/${stereomap}_stereoMap.xml -l ${params.lines} -w ${params.watchvideo} -pre ${name}
    """
}


process visualize_coordinates {

    publishDir "$params.DATA_DIR/plots"
    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4 conda-forge::scipy=1.6.0 conda-forge::pandas=1.2.0 conda-forge::seaborn=0.12.2'

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
    conda = 'conda-forge::matplotlib=3.3.3 conda-forge::pandas=1.2.0  conda-forge::seaborn=0.12.2  conda-forge::numpy=1.19.4'
    publishDir "$params.DATA_DIR/contours"

    input:
    tuple file(f), val(name)

    output:
    tuple file('coordinates_*.tab'), val(name)

    script:
    """
    parallax_depth.py -f $f -o $name -d ${params.baseline} -F ${params.FOCAL} -ALPHA ${params.ALPHA} -frame_width ${params.frame_width} -frame_height ${params.frame_height} -rate ${params.FPS} 

    """
}
process segment_contours {
    conda = 'conda-forge::matplotlib=3.3.3 conda-forge::pandas=1.2.0  conda-forge::seaborn=0.12.2  conda-forge::numpy=1.24.2 conda-forge::scipy=1.10.1'

    publishDir "$params.DATA_DIR/contours"

    input:
    tuple file(f), val(name)
    
    output:
    tuple file('segmented_*.tab'), val(name)
    tuple file('stereo_*.tab'), val(name), emit: stereo

    script:
    """
    segment_pulses.py -f $f -n $name -HPP ${params.HPP} -HPD ${params.HPD} -XMAX ${params.XMAX} -YMAX ${params.YMAX} -SRMAX ${params.SRMAX} -PDMIN ${params.PDMIN} -PSD ${params.PSD} -PFD ${params.PFD} -XD ${params.XD}
    """
}


process visualize {
    publishDir "$params.DATA_DIR/plots"
    conda = 'conda-forge::matplotlib=3.3.3 conda-forge::pandas=1.2.0  conda-forge::seaborn=0.12.2  conda-forge::numpy'

    input :
    tuple file(f), val(name)

    output :
    file('*.pdf')

    script :
    """
    visualize_contours.py -f $f -o ${name}_contourplot
    """

}
process visualize_segments {
    publishDir "$params.DATA_DIR/plots"
    conda = 'conda-forge::matplotlib=3.3.3 conda-forge::pandas=1.2.0  conda-forge::seaborn=0.12.2  conda-forge::numpy'

    input :
    tuple file(f), val(name)

    output :
    file('*.pdf')

    script :
    """
    visualize_contours.py -f $f -o ${name}_segmented
    """

}

process find_contours {

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'
    publishDir "$params.DATA_DIR/contours"

    input:
    tuple val(VL), val(VR), val(name)
    
    output:
    tuple file('*.tab'), val(name)

    script:
    """
    find_contours.py -v1 $VL -v2 $VR -b ${params.black} -m ${params.minpulse} -f ${name} -l ${params.watchvideo} -d ${params.delay}

    """
}

/*

    conda = 'conda-forge::opencv=4.5.5 conda-forge::numpy=1.22.4'

*/
