#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
   and clips files according to metadata input */

/* File parameters */
params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'

/* Video parameters */
params.fps = 30
params.watch = 0

workflow DOWNLOAD_RAW {

    Channel.fromPath(params.metadata) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.linkL, row.videoR, row.linkR, row.start, row.end, row.offset, row.name) } \
        | download_videos 
        download_videos.out.downloads | flatten | make_cfr 
        download_videos.out.vidarray | clip_video_pair
}

workflow {
    DOWNLOAD_RAW()
}


process clip_video_pair {
    publishDir "$params.VIDEO_DIR/clips"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(V1), val(V2), val(start), val(end), val(offset), val(name)

    output:
    path '*.mkv'

    script:

    """
    clip2vids.py -v1 $baseDir/${params.VIDEO_DIR}/cfr_$name$V1${params.cEXT} -v2 $baseDir/${params.VIDEO_DIR}/cfr_$name$V2${params.cEXT} -s $start -e $end -o $offset -w ${params.watch}
    """
}

process download_videos {

    conda = 'conda-forge::gdown'

    input:
    tuple val(videoL), val(linkL), val(videoR), val(linkR), val(start), val(end), val(offset), val(name)

    output:
    path '*.mkv', emit: downloads
    tuple val(videoL), val(videoR), val(start), val(end), val(offset), val(name), emit: vidarray

    script:

    """
    gdown $linkL -O $name$videoL${params.cEXT}
    gdown $linkR -O $name$videoR${params.cEXT}

    """
}
process make_cfr {
    publishDir "$params.VIDEO_DIR"

    conda = 'conda-forge::ffmpeg=4.3.1'

    input:
    path vid

    output:
    path '*.mkv'
    
    script:
    """
    ffmpeg -i $vid -f matroska -vcodec libx264 -an -framerate ${params.fps} cfr_$vid

    """
}

