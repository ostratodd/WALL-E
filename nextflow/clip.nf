#!/usr/bin/env nextflow

nextflow.enable.dsl=2


workflow {
    params.SCRIPTS_DIR = "/Users/oakley/Documents/GitHub/WALL-E/"
    params.VIDEO_DIR="/Users/oakley/Documents/GitHub/WALL-E/video_data/"
    params.LOC="southwater_pan"
    params.cEXT=".mkv"

    params.start=1000
    params.end=6000
    params.offset=-15

    southwater_checker = Channel.of(["/Users/oakley/Documents/GitHub/WALL-E/video_data/southwater_pan/161303-1.mkv", "/Users/oakley/Documents/GitHub/WALL-E/video_data/southwater_pan/161303-2.mkv"])
    
    clip_video_pair(southwater_checker)

}
process clip_video_pair {

    conda = 'conda-forge::opencv'

    input:
    tuple path(V1), path(V2)

    output:
    stdout

    script:
    """

    python ${params.SCRIPTS_DIR}video_utilities/play2vids.py -v1 $V1 -v2 $V2 -s ${params.start}

    """
}
