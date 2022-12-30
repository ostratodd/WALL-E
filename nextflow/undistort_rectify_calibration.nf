#!/usr/bin/env nextflow

nextflow.enable.dsl=2

mode = "internal"

params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'
params.DATA_DIR='data'

params.watchvideo = 0

workflow MAKE_STEREO_MAPS {
    stereo_ch = Channel.fromPath(params.metadata, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.name, row.VL, row.VR, row.start, row.end, row.offset, row.framesize, row.checkdim, row.squaresize, row.L_move, row.L_mindist, row.L_dist, row.L_bord, row.R_move, row.R_mindist, row.R_dist, row.R_bord,row.P_move, row.P_mindist, row.P_dist) }

    find_singles(stereo_ch)
    find_singles.out | calibrate
    calibrate.out.vidarray | undistort
    undistort.out.vidarray | find_pairs
    find_pairs.out.vidarray | stereo_rectification
    stereo_rectification.out.vidarray | rectify
}

workflow {
    MAKE_STEREO_MAPS()
}

process undistort {
    publishDir "$params.VIDEO_DIR/clips"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist)

    output:
    path '*.mkv'
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist), emit: vidarray

    script:
    """
    denoiseCamera.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}.mkv -p $baseDir/${params.DATA_DIR}/stereo_maps/ -pre ${name}_L_CH_1 -w ${params.watchvideo} -fr ${framesize} -o ${name}${VL}_cl_${start}_${end}
    denoiseCamera.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}.mkv -p $baseDir/${params.DATA_DIR}/stereo_maps/ -pre ${name}_R_CH_1 -w ${params.watchvideo} -fr ${framesize} -o ${name}${VR}_cl_${start}_${end}

    """
}

process find_singles {
    publishDir "$params.VIDEO_DIR/pairs"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist)

    output:
    file '*.png'
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist), emit: vidarray

    script:
    """
    collect_single_checkers.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}.mkv -p ${name}_L -c ${checkdim} -l ${params.watchvideo} -m ${L_move} -e ${L_dist} -b ${L_bord} -n ${L_mindist}
    collect_single_checkers.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}.mkv -p ${name}_R -c ${checkdim} -l ${params.watchvideo} -m ${R_move} -e ${R_dist} -b ${R_bord} -n ${R_mindist}
    """
}



process calibrate {
    publishDir "$params.DATA_DIR/stereo_maps"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    path pairs
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist)

    output:
    path '*.p'
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist), emit: vidarray

    script:
    """
    cameraCalibration.py -c $checkdim -fr $framesize -sq $squaresize -w ${params.watchvideo} -pre ${name}_L_CH_1 -p $baseDir/${params.VIDEO_DIR}/pairs
    cameraCalibration.py -c $checkdim -fr $framesize -sq $squaresize -w ${params.watchvideo} -pre ${name}_R_CH_1 -p $baseDir/${params.VIDEO_DIR}/pairs

    """
}


process stereo_rectification {
    publishDir "$params.DATA_DIR/stereo_maps"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist)

    output:
    path '*.xml'
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist), emit: vidarray

    script:
    """
    stereovision_calibration.py -v1 CH_L -v2 CH_R -pre $name -p $baseDir/${params.VIDEO_DIR}/pairs -c $checkdim -fr $framesize -sq $squaresize
    """

}
process rectify {

    publishDir "$params.VIDEO_DIR/rectified"
    
    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'
    
    input:
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist)
    
    output:
    path '*.mkv'
    
    script:
    """
    rectify_videos.py -v1 $baseDir/${params.VIDEO_DIR}/clips/${name}${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/${name}${VR}_cl_${start}_${end}_undis.mkv -f $baseDir/${params.DATA_DIR}/stereo_maps/${name}_stereoMap.xml -l 1 -pre ${name}

    """
   

}

process find_pairs {
    publishDir "$params.VIDEO_DIR/pairs"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist)

    output:
    path '*.png'
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), val(framesize), val(checkdim), val(squaresize), val(L_move), val(L_mindist), val(L_dist), val(L_bord), val(R_move), val(R_mindist),val(R_dist), val(R_bord),val(P_move), val(P_mindist),val(P_dist), emit: vidarray

    script:
    if( mode == 'internal' )
        """
        collect_stereo_pairs.py -v1 $baseDir/${params.VIDEO_DIR}/clips/${name}${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/${name}${VR}_cl_${start}_${end}_undis.mkv -m ${P_move} -c ${checkdim} -p $name -l ${params.watchvideo} -e ${P_dist} -n ${P_mindist}
        """
    else if( mode == 'external' )
        """
        collect_stereo_pairs.py -v1 $baseDir/${params.VIDEO_DIR}/clips/${name}${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/${name}${VR}_cl_${start}_${end}_undis.mkv -m ${P_move} -c ${checkdim} -p $name -l ${params.watchvideo} -e ${P_dist} -n ${P_mindist}
        """
}

