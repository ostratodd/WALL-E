#!/usr/bin/env nextflow

nextflow.enable.dsl=2

workflow {
    params.VIDEO_DIR="video_data"
    params.LOC="Southwater_BZ"
    params.cEXT=".mkv"

/*  channel containing: videoL, videoR, start, end, offset 	*/

    southwater_checker = Channel.of(["161303-2", "161303-1", 1000, 6000, 15]) 
    
    clip_video_pair(southwater_checker)
    clip_video_pair.out.verbiage.view()

}

process clip_video_pair {
    publishDir '$baseDir/clips'

    input:
    tuple val(V1), val(V2), val(start), val(end), val(offset)

    output:
    path '*.mkv', emit: videos
    stdout emit: verbiage

    script:
    """
    echo "Clipped $V1${params.cEXT} and $V2${params.cEXT}"
    clip2vids.py -v1 "${params.VIDEO_DIR}${params.LOC}/$V1${params.cEXT}" -v2 "${params.VIDEO_DIR}${params.LOC}/$V2${params.cEXT}" -s $start -e $end -o $offset -w 0

    """
}


/* UNUSED LINES

    publishDir(
        path: "${params.VIDEO_DIR}/${params.LOC}",
        mode: 'copy',
        saveAs: { fn -> fn.substring(fn.lastIndexOf('/')+1) },
    )



process undistort_fisheye {

}


    path "${params.VIDEO_DIR}${params.LOC}/$V1_clip*" 

    clip_video_pair.out.view()

*/
