#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.index = "$baseDir/data/index.csv"


/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
    then runs undistort (fisheye) custom for WALLE camera housings           */


workflow {
    params.VIDEO_DIR='video_data'
    params.LOC="Southwater_BZ"


    Channel.fromPath(params.index) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.location, row.videoL, row.linkL, row.videoR, row.linkR ) } \
        | download_videos | flatten | make_cfr
}


process download_videos {

    conda = 'conda-forge::gdown'

    input:
    tuple val(location), val(videoL), val(linkL), val(videoR), val(linkR)

    output:

    path '*.mkv'

    script:

    """
    gdown $linkL -O $videoL
    gdown $linkR -O $videoR

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
