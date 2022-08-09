#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/* Downloads from Google Drive link, converts to constant frame rate (30 fps) 
    then runs undistort (fisheye) custom for WALLE camera housings           */

workflow {
    params.VIDEO_DIR='video_data'
    params.LOC="Southwater_BZ"
    params.cEXT = '.mkv' 		/* Extension for videos after conversion */

/*    southwater_vids = Channel.of(["161303-1", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"], ["161303-2", "1LzJHVtp41w8dDuvgFG6gpdZlSQHeeVac"], ["185538-1", "1ouXtTiRl70z-hTEcg29FIZlk4pjJUWMQ"], ["185539-2", "1M_Xkw3Z1Vn96DXFrIDNgjVNV5Wkf-Jhz"] )
    southwater_vids = Channel.of(["161303-1", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"])
*/

    southwater_vids = Channel.of(["161303-1", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"], ["161303-2", "1LzJHVtp41w8dDuvgFG6gpdZlSQHeeVac"] )
    download_videos(southwater_vids) | convert_vid

    pairs_ch = Channel.of(["161303-2", "161303-1", 1000, 6000, 15])

    clip_video_pair(pairs_ch) | remove_fisheye
}
process clip_video_pair {
    publishDir "clips"

    conda = 'conda-forge::opencv=3.4.1'

    input:
    tuple val(V1), val(V2), val(start), val(end), val(offset)

    output:
    path '*.mkv'

    script:
    """
    clip2vids.py -v1 "${params.VIDEO_DIR}/${params.LOC}/$V1*${params.cEXT}" -v2 "${params.VIDEO_DIR}/${params.LOC}/$V2*${params.cEXT}" -s $start -e $end -o $offset -w 0

    """
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
    publishDir "$params.VIDEO_DIR/$params.LOC"

    conda = 'conda-forge::ffmpeg=3.4.2'
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
    conda = 'conda-forge::opencv=3.4.1'

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



*/
