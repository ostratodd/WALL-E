#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'

/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
    then runs undistort (fisheye) custom for WALLE camera housings           */


workflow {

    pairs_ch = Channel.fromPath(params.metadata, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.videoR, row.start, row.end, row.name, row.stereomap) }

    rectify(pairs_ch)
    find_contours(rectify.out.vidarray)
    segment_contours(find_contours.out)
    visualize(find_contours.out)
    visualize_segments(segment_contours.out[0])
}

process segment_contours {
    conda = 'conda-forge::matplotlib conda-forge::pandas conda-forge::seaborn conda-forge::numpy'

    publishDir "$params.VIDEO_DIR/contours"

    input:
    tuple file(f), val(name)
    
    output:
    tuple file('segmented_*.tab'), val(name)
    tuple file('stereo_*.tab'), val(name)

    script:
    """
    segment_pulses.py -f $f -n $name

    """
}


process visualize {
    publishDir "$params.VIDEO_DIR/plots"
    conda = 'conda-forge::matplotlib conda-forge::pandas conda-forge::seaborn conda-forge::numpy'

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
    publishDir "$params.VIDEO_DIR/plots"
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
    tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap)

    output:
    path('*.mkv')
    tuple file('*L.mkv'), file('*R.mkv'), val(name), emit: vidarray

    script:
    """
    rectify_videos.py -v1 $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}_undis.mkv -f $baseDir/${params.VIDEO_DIR}/stereo_maps/${stereomap}_stereoMap.xml -l 0 -w 0 -pre ${name}
    """
}

process find_contours {
    params.black = 120
    params.minpulse = 3

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'
    publishDir "$params.VIDEO_DIR/contours"

    input:
    tuple val(VL), val(VR), val(name)
    
    output:
    tuple file('*.tab'), val(name)

    script:
    """
    find_contours.py -v1 $VL -v2 $VR -b ${params.black} -m ${params.minpulse} -f ${name} -l 0

    """
}

/*

    conda = 'conda-forge::opencv=4.5.5 conda-forge::numpy=1.22.4'

*/
