#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.index = "$baseDir/data/index.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'

/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
    then runs undistort (fisheye) custom for WALLE camera housings           */


workflow PREPARE_CLIPS {

    Channel.fromPath(params.index) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.location, row.videoL, row.linkL, row.videoR, row.linkR, row.start, row.end, row.offset ) } \
        | download_videos | flatten | make_cfr | finish_download

    pairs_ch = Channel.fromPath(params.index, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.videoR, row.start, row.end, row.offset) }

    clip_video_pair(finish_download.out.state, pairs_ch) \
    | flatten \
    | remove_fisheye | finish_defish
}
workflow MAKE_STEREO_MAPS {
    stereo_ch = Channel.fromPath(params.index, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.videoR, row.start, row.end, row.stereoMap, row.movement, row.checksize, row.stereoMap, row.distance) }

    find_pairs(finish_defish.out.state, stereo_ch) | stereo_rectification


}

workflow {
    PREPARE_CLIPS()
}

process download_videos {

    conda = 'conda-forge::gdown'

    input:
    tuple val(location), val(videoL), val(linkL), val(videoR), val(linkR)

    output:
    path '*.mkv'

    script:

    """
    gdown $linkL -O $videoL${params.cEXT}
    gdown $linkR -O $videoR${params.cEXT}

    """
}



process remove_fisheye {
    publishDir "$params.VIDEO_DIR"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    path V1

    output:
    path '*.mkv'

    script:
    """
    remove_fisheye.py -v $V1
    """
}

process stereo_rectification {
    publishDir "$params.VIDEO_DIR/stereo_maps"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    path pairs
    val(checksize)
    val(stereomap)


    output:
    path '*.xml'

    script:
    """
    stereovision_calibration.py -v1 CH_L -v2 CH_R -pre $stereomap -p $baseDir/${params.VIDEO_DIR}/pairs -c $checksize
    """

}

process find_pairs {
    publishDir "$params.VIDEO_DIR/pairs"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    val ready
    tuple val(VL), val(VR), val(start), val(end), val(stereomap), val(movement), val(checksize), val(stereoMap), val(distance)

    output:
    path '*.png'
    val(checksize)
    val(stereomap)

    script:
    """
    collect_stereo_pairs.py -v1 $baseDir/${params.VIDEO_DIR}/cfr_${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/cfr_${VR}_cl_${start}_${end}_undis.mkv -m ${movement} -c ${checksize} -p $stereoMap -l 0 -e $distance
    """
}

process clip_video_pair {
    publishDir "$params.VIDEO_DIR"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    val ready
    tuple val(V1), val(V2), val(start), val(end), val(offset)

    output:
    path '*.mkv', emit: paired_vid

    script:

    """
    clip2vids.py -v1 $baseDir/${params.VIDEO_DIR}/cfr_$V1${params.cEXT} -v2 $baseDir/${params.VIDEO_DIR}/cfr_$V2${params.cEXT} -s $start -e $end -o $offset -w 0
    """
}

process finish_download {

    input:
    path vids

    output:
    val true, emit: state

    script:

    """
    echo "Finished download"
    """
}

process finish_defish {

    input:
    path vids

    output:
    val true, emit: state

    script:

    """
    echo "Finished undistorting"
    """
}

process make_cfr {
    publishDir "$params.VIDEO_DIR"

    conda = 'conda-forge::ffmpeg=3.4.2'
    params.fps = 30

    input:
    path vid

    output:
    path '*.mkv'
    
    script:
    """
    ffmpeg -i $vid -f matroska -vcodec libx264 -an -framerate ${params.fps} cfr_$vid

    """
}

/*

    echo "collect_stereo_pairs.py -v1 cfr_"+$V1+"_cl_$start_$end_undis.mkv -v2 cfr_$V2_cl_$start_$end_undis.mkv  -m $movement -c $checksize "

 -v2 cfr_$V2_cl_$start_$end_undis.mkv  -m $movement -c $checksize "




#----------------------workflow works with one video




*/
