#!/usr/bin/env nextflow

nextflow.enable.dsl=2


workflow {

    params.VIDEO_DIR="/Users/oakley/Documents/GitHub/WALL-E/video_data/"
    params.LOC="southwater_pan"
    params.EXT=".ASF"

    southwater_vids = Channel.of(["161303-1", "1_vhH9mNFtHswIcBcIwN0XQ_7L6Q6eCq6"], ["161303-2", "1LzJHVtp41w8dDuvgFG6gpdZlSQHeeVac"], ["185538-1", "1ouXtTiRl70z-hTEcg29FIZlk4pjJUWMQ"], ["185539-2", "1M_Xkw3Z1Vn96DXFrIDNgjVNV5Wkf-Jhz"] )

    download_videos(southwater_vids)

}
process download_videos {

    publishDir(
        path: "${params.VIDEO_DIR}/${params.LOC}",
        mode: 'copy',
        saveAs: { fn -> fn.substring(fn.lastIndexOf('/')+1) },
    )


    conda = 'conda-forge::gdown'

    params.cEXT = '.mkv'
    params.fps = 30

    input:
    tuple val(V1), val(LINK)

    output:
    path '*.mkv'

    script:
    """

    gdown $LINK -O $V1${params.EXT}
    ffmpeg -i $V1${params.EXT} -f matroska -vcodec libx264 -an -framerate 30 -crf 0 $V1${params.cEXT}

    """
}
