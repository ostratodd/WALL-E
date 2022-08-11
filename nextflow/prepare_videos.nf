#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.index = "$baseDir/data/index.csv"


/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
    then runs undistort (fisheye) custom for WALLE camera housings           */

params.cEXT = '.mkv'

workflow {
    params.VIDEO_DIR='video_data'

    Channel.fromPath(params.index) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.location, row.videoL, row.linkL, row.videoR, row.linkR ) } \
        | download_videos | flatten | make_cfr | collect | finish_download

    pairs_ch = Channel.fromPath(params.index, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.videoR, row.start, row.end, row.offset) }

/*    finish_download(make_cfr.out) */
    clip_video_pair(finish_download.out.state, pairs_ch)

}

process clip_video_pair {
    conda = 'conda-forge::opencv=4.5.5 conda-forge::numpy=1.22.4'

    input:
    val ready
    tuple val(V1), val(V2), val(start), val(end), val(offset)

    output:
    path '*.mkv'

    script:

    """
    clip2vids.py -v1 $baseDir/${params.VIDEO_DIR}/cfr_$V1 -v2 $baseDir/${params.VIDEO_DIR}/cfr_$V2 -s $start -e $end -o $offset -w 1

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


/*


*/
