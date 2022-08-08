#!/usr/bin/env nextflow

nextflow.enable.dsl=2

process download_videos {

    conda = 'conda-forge::gdown conda-forge::ffmpeg conda-forge::x264'

    input:
    tuple val(V1), val(LINK)

    output:
    path '*.mkv'

    script:
    """
    gdown $LINK -O $V1${params.EXT}
    test.sh $V1${params.EXT} $V1

    """
}

process convert_vid {

    publishDir "$params.VIDEO_DIR/$params.LOC"

    conda = 'conda-forge::ffmpeg conda-forge::x264'

    params.cEXT = '.mkv'
    params.fps = 30

    input:
    path V1

    output:
    path '*.mkv'
    
    script:
    """

    ffmpeg -i $V1 -f matroska -vcodec libx264 -an -framerate 30 TEST.mkv

    """
}

workflow {


    params.VIDEO_DIR='video_data'
    params.LOC='southwater_pan'
    params.EXT=".ASF"

    southwater_vids = Channel.of(["161303-1", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"])
    download_videos(southwater_vids)

/*    convert_vid(download_videos.out) */
}


/* UNUSED
    file '*.mkv', emit: mkvid
    southwater_vids = Channel.of(["161303-1", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"], ["161303-2", "1LzJHVtp41w8dDuvgFG6gpdZlSQHeeVac"], ["185538-1", "1ouXtTiRl70z-hTEcg29FIZlk4pjJUWMQ"], ["185539-2", "1M_Xkw3Z1Vn96DXFrIDNgjVNV5Wkf-Jhz"] )
    sleep 5m
    southwater_asf = Channel.fromPath('$params.VIDEO_DIR/$params.LOC/*.ASF')
    data = channel.fromPath('/Users/oakley/Documents/GitHub/WALL-E/nextflow/junk.txt')




*/
