#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'

/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
    then runs undistort (fisheye) custom for WALLE camera housings           */


workflow DOWNLOAD_RAW {

    Channel.fromPath(params.metadata) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.location, row.videoL, row.linkL, row.videoR, row.linkR, row.name) } \
        | download_videos | flatten | make_cfr 
}

workflow {
    DOWNLOAD_RAW()
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

process download_videos {

    conda = 'conda-forge::gdown'

    input:
    tuple val(location), val(videoL), val(linkL), val(videoR), val(linkR), val(name)

    output:
    path '*.mkv'

    script:

    """
    gdown $linkL -O $name$videoL${params.cEXT}
    gdown $linkR -O $name$videoR${params.cEXT}

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

