#!/usr/bin/env nextflow

nextflow.enable.dsl=2

workflow {
    params.VIDEO_DIR="video_data"
    params.LOC="Southwater_BZ"
    params.EXT=".ASF"
    params.cEXT=".mkv"

/*  channel containing: videoL, videoR, start, end, offset 	*/

    southwater_checker = Channel.of(["161303-2_L", "161303-1_R", 1000, 1200, 15]) 
    
    clip_video_pair(southwater_checker) | view

}

process clip_video_pair {
    input:
    tuple val(V1), val(V2), val(start), val(end), val(offset)

    output:
    stdout

    script:
    """
    echo "Clipped $V1${params.cEXT} and $V2${params.cEXT} and wrote to data directory"
    clip2vids.py -v1 $baseDir/${params.VIDEO_DIR}/${params.LOC}/$V1${params.EXT}${params.cEXT} -v2 $baseDir/${params.VIDEO_DIR}/${params.LOC}/$V2${params.EXT}${params.cEXT} -s $start -e $end -o $offset -w 1

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
