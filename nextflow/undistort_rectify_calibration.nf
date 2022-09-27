#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'
params.DATA_DIR='data'

params.watch = 0

workflow MAKE_STEREO_MAPS {
    stereo_ch = Channel.fromPath(params.metadata, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.videoR, row.start, row.end, row.movement, row.checksize, row.squaresize, row.name, row.distance, row.framesize, row.mindist, row.singledist) }

    find_singles(stereo_ch)
    find_singles.out | calibrate
    calibrate.out.vidarray | undistort
    undistort.out.vidarray | find_pairs
    find_pairs.out.vidarray | stereo_rectification
    
}

workflow {
    MAKE_STEREO_MAPS()
}

process undistort {
    publishDir "$params.VIDEO_DIR/clips"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3 conda-forge::pickle5'

    input:
    tuple val(VL), val(VR), val(start), val(end), val(movement), val(checksize), val(squaresize), val(name), val(distance), val(framesize), val(mindist), val(singledist)

    output:
    path '*.mkv'
    tuple val(VL), val(VR), val(start), val(end), val(movement), val(checksize), val(squaresize), val(name), val(distance), val(framesize), val(mindist), val(singledist), emit: vidarray

    script:
    """
    denoiseCamera.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}.mkv -p $baseDir/${params.DATA_DIR}/stereo_maps/ -pre ${name}_L_CH_1 -w ${params.watch} -fr ${framesize}
    denoiseCamera.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}.mkv -p $baseDir/${params.DATA_DIR}/stereo_maps/ -pre ${name}_R_CH_1 -w ${params.watch} -fr ${framesize}

    """
}

process find_singles {
    publishDir "$params.VIDEO_DIR/pairs"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3 conda-forge::pickle5'

    input:
    tuple val(VL), val(VR), val(start), val(end), val(movement), val(checksize), val(squaresize), val(name), val(distance), val(framesize), val(mindist), val(singledist)

    output:
    file '*.png'
    tuple val(VL), val(VR), val(start), val(end), val(movement), val(checksize), val(squaresize), val(name), val(distance), val(framesize), val(mindist), val(singledist), emit: vidarray

    script:
    """
    collect_single_checkers.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}.mkv -p ${name}_L -c ${checksize} -l ${params.watch} -m ${mindist}
    collect_single_checkers.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}.mkv -p ${name}_R -c ${checksize} -l ${params.watch} -m ${mindist}
    """
}



process calibrate {
    publishDir "$params.DATA_DIR/stereo_maps"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    path pairs
    tuple val(VL), val(VR), val(start), val(end), val(movement), val(checksize), val(squaresize), val(name), val(distance), val(framesize), val(mindist), val(singledist)

    output:
    path '*.p'
    tuple val(VL), val(VR), val(start), val(end), val(movement), val(checksize), val(squaresize), val(name), val(distance), val(framesize), val(mindist), val(singledist), emit: vidarray

    script:
    """
    cameraCalibration.py -c $checksize -fr $framesize -sq $squaresize -w ${params.watch} -pre ${name}_L_CH_1 -p $baseDir/${params.VIDEO_DIR}/pairs
    cameraCalibration.py -c $checksize -fr $framesize -sq $squaresize -w ${params.watch} -pre ${name}_R_CH_1 -p $baseDir/${params.VIDEO_DIR}/pairs

    """
}


process stereo_rectification {
    publishDir "$params.DATA_DIR/stereo_maps"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    tuple val(VL), val(VR), val(start), val(end), val(movement), val(checksize), val(squaresize), val(name), val(distance), val(framesize), val(mindist), val(singledist)

/*    path pairs
    val(checksize)
    val(name)
    val(squaresize)
    val(framesize) */

    output:
    path '*.xml'

    script:
    """
    stereovision_calibration.py -v1 CH_L -v2 CH_R -pre $name -p $baseDir/${params.VIDEO_DIR}/pairs -c $checksize -fr $framesize -sq $squaresize
    """

}

process find_pairs {
    publishDir "$params.VIDEO_DIR/pairs"

    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    input:
    tuple val(VL), val(VR), val(start), val(end), val(movement), val(checksize), val(squaresize), val(name), val(distance), val(framesize), val(mindist), val(singledist)

    output:
    path '*.png'
    tuple val(VL), val(VR), val(start), val(end), val(movement), val(checksize), val(squaresize), val(name), val(distance), val(framesize), val(mindist), val(singledist), emit: vidarray

    script:
    """
    collect_stereo_pairs.py -v1 $baseDir/${params.VIDEO_DIR}/clips/${name}_L_CH_1_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/${name}_R_CH_1_undis.mkv -m ${movement} -c ${checksize} -p $name -l ${params.watch} -e $distance
    """
}

