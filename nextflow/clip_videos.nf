#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.index = "$baseDir/data/index.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'

/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
    then runs undistort (fisheye) custom for WALLE camera housings           */


workflow CLIP {

    pairs_ch = Channel.fromPath(params.index, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.videoR, row.start, row.end, row.offset, row.name) }

    clip_video_pair(pairs_ch) | flatten | remove_fisheye

}
workflow MAKE_STEREO_MAPS {
    stereo_ch = Channel.fromPath(params.index, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.videoR, row.start, row.end, row.stereoMap, row.movement, row.checksize, row.stereoMap, row.distance) }

    find_pairs(finish_defish.out.state, stereo_ch) | stereo_rectification


}

workflow {
    CLIP()
}

process remove_fisheye {
    publishDir "$params.VIDEO_DIR/clips"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    path V1

    output:
    path '*.mkv'

    script:
    """
    remove_fisheye.py -v $V1
    """
}

process stereo_rectification {
    publishDir "$params.VIDEO_DIR/stereo_maps"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    path pairs
    val(checksize)
    val(stereomap)


    output:
    path '*.xml'

    script:
    """
    stereovision_calibration.py -v1 CH_L -v2 CH_R -pre $stereomap -p $baseDir/${params.VIDEO_DIR}/pairs -c $checksize
    """

}

process find_pairs {
    publishDir "$params.VIDEO_DIR/pairs"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    val ready
    tuple val(VL), val(VR), val(start), val(end), val(stereomap), val(movement), val(checksize), val(stereoMap), val(distance)

    output:
    path '*.png'
    val(checksize)
    val(stereomap)

    script:
    """
    collect_stereo_pairs.py -v1 $baseDir/${params.VIDEO_DIR}/cfr_${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/cfr_${VR}_cl_${start}_${end}_undis.mkv -m ${movement} -c ${checksize} -p $stereoMap -l 0 -e $distance
    """
}

process clip_video_pair {
    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    tuple val(V1), val(V2), val(start), val(end), val(offset), val(name)

    output:
    path '*.mkv'

    script:

    """
    clip2vids.py -v1 $baseDir/${params.VIDEO_DIR}/cfr_$name$V1${params.cEXT} -v2 $baseDir/${params.VIDEO_DIR}/cfr_$name$V2${params.cEXT} -s $start -e $end -o $offset -w 0
    """
}

