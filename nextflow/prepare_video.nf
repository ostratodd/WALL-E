#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/* Downloads from Google Drive link, converts to constant frame rate (30 fps) 
    then runs undistort (fisheye) custom for WALLE camera housings           */

workflow {
    params.VIDEO_DIR='video_data'
    params.LOC="Southwater_BZ"

/*    southwater_vids = Channel.of(["161303-1", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"], ["161303-2", "1LzJHVtp41w8dDuvgFG6gpdZlSQHeeVac"], ["185538-1", "1ouXtTiRl70z-hTEcg29FIZlk4pjJUWMQ"], ["185539-2", "1M_Xkw3Z1Vn96DXFrIDNgjVNV5Wkf-Jhz"] )
    southwater_vids = Channel.of(["161303-1", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"])
*/

    southwater_vids = Channel.of(["161303-2_L", "1LzJHVtp41w8dDuvgFG6gpdZlSQHeeVac", "161303-1_R", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"] )
    download_videos(southwater_vids) | convert_vid

    /* now clip the video and take care of offset */
    southwater_checker = Channel.of(["161303-2_L", "161303-1_R", 1000, 1200, 15])
    clip_video_pair(southwater_checker) | view

    
}

process download_videos {
    publishDir "$params.VIDEO_DIR/$params.LOC"
    conda = 'conda-forge::gdown'
    params.EXT = '.ASF'

    input:
    tuple val(V1), val(LINK1), val(V2), val(LINK2)

    output:
    path '*_L.ASF', emit: LV
    path '*_R.ASF', emit: RV

    script:
    """
    gdown $LINK1 -O $V1${params.EXT}
    gdown $LINK2 -O $V2${params.EXT}
    """
}

process convert_vid {
    publishDir "$params.VIDEO_DIR/$params.LOC"

    conda = 'conda-forge::ffmpeg=3.4.2'
    params.fps = 30
    params.cEXT = '.mkv' 		/* Extension for videos after conversion */

    input:
    path LV
    path RV

    output:
    path '*.mkv'
    
    script:
    """
    ffmpeg -i $LV -f matroska -vcodec libx264 -an -framerate ${params.fps} $LV${params.cEXT}
    ffmpeg -i $RV -f matroska -vcodec libx264 -an -framerate ${params.fps} $RV${params.cEXT}
    """
}
process remove_fisheye {
    publishDir "$params.VIDEO_DIR/$params.LOC"

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
process clip_video_pair {
    conda = 'conda-forge::opencv=4.5.5 conda-forge::numpy=1.22.4'

    input:
    tuple val(V1), val(V2), val(start), val(end), val(offset)

    output:
    stdout

    script:
    """
    echo "Clipped $V1${params.cEXT} and $V2${params.cEXT} and wrote to data directory"
    clip2vids.py -v1 $baseDir/${params.VIDEO_DIR}/${params.LOC}/$V1${params.EXT}${params.cEXT} -v2 $baseDir/${params.VIDEO_DIR}/${params.LOC}/$V2${params.EXT}${params.cEXT} -s $start -e $end -o $offset -w 0

    """
}

/*UNUSED

 publishDir "$params.VIDEO_DIR/$params.LOC"
 pairs_ch = Channel.of(["161303-2", "161303-1", 1000, 6000, 15])


    clip_video_pair(pairs_ch) | view
*/
