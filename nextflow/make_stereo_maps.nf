#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'
params.DATA_DIR='data'

/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
    then runs undistort (fisheye) custom for WALLE camera housings           */


workflow MAKE_STEREO_MAPS {
    stereo_ch = Channel.fromPath(params.metadata, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.videoR, row.start, row.end, row.movement, row.checksize, row.name, row.distance) }

    find_pairs(stereo_ch) | stereo_rectification


}

workflow {
    MAKE_STEREO_MAPS()
}

process stereo_rectification {
    publishDir "$params.DATA_DIR/stereo_maps"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    path pairs
    val(checksize)
    val(name)


    output:
    path '*.xml'

    script:
    """
    stereovision_calibration.py -v1 CH_L -v2 CH_R -pre $name -p $baseDir/${params.VIDEO_DIR}/pairs -c $checksize
    """

}

process find_pairs {
    publishDir "$params.VIDEO_DIR/pairs"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    tuple val(VL), val(VR), val(start), val(end), val(movement), val(checksize), val(name), val(distance)

    output:
    path '*.png'
    val(checksize)
    val(name)

    script:
    """
    collect_stereo_pairs.py -v1 $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}_undis.mkv -m ${movement} -c ${checksize} -p $name -l 0 -e $distance
    """
}

