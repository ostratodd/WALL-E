#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/* Downloads from Google Drive link, converts to constant frame rate (30 fps) 
    then runs undistort (fisheye) custom for WALLE camera housings           */

workflow {
    params.VIDEO_DIR='video_data'
    params.LOC="Southwater_BZ"

    southwater_vids = Channel.of(["161303-1", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"], ["161303-2", "1LzJHVtp41w8dDuvgFG6gpdZlSQHeeVac"], ["185538-1", "1ouXtTiRl70z-hTEcg29FIZlk4pjJUWMQ"], ["185539-2", "1M_Xkw3Z1Vn96DXFrIDNgjVNV5Wkf-Jhz"] )
    download_videos(southwater_vids) | convert_vid | remove_fisheye
}

process download_videos {
    conda = 'conda-forge::gdown'
    params.EXT = '.ASF'

    input:
    tuple val(V1), val(LINK)

    output:
    path '*.ASF'

    script:
    """
    gdown $LINK -O $V1${params.EXT}
    """
}
process convert_vid {
    conda = 'conda-forge::ffmpeg=4.4.1'
    params.cEXT = '.mkv'
    params.fps = 30

    input:
    path V1

    output:
    path '*.mkv'
    
    script:
    """
    ffmpeg -i $V1 -f matroska -vcodec libx264 -an -framerate ${params.fps} $V1${params.cEXT}
    """
}
process remove_fisheye {
    conda = 'conda-forge::opencv'

    publishDir "$params.VIDEO_DIR/$params.LOC"

    input:
    path V1

    output:
    path '*.mkv'

    script:
    """
    remove_fisheye.py -v $V1
    """
}


/*UNUSED

    southwater_vids = Channel.of(["161303-1", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"])


*/
