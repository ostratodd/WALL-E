#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.metadata = "$baseDir/data/metadata.csv"


/*****The following parameters are set at defaults, but do not work for all videos. To change these, it is s easiest to use an input file ******/
	
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'
params.DATA_DIR='data'

/*Camera parameters*/
params.ALPHA = 65
params.FOCAL = 3.7      /* focal length of camera */
params.frame_width = 640
params.frame_height = 480
params.FPS = 30
params.framesize = "640 480"
params.baseline = 125

/*Video parameters (if watching) */
params.watchvideo = 0
params.lines = 0
params.delay = 0


workflow {
    pairs_ch = Channel.fromPath(params.metadata, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.VL, row.VR, row.start, row.end, row.name, row.stereomap, row.baseline, row.contourBlack, row.contourMinpulse, row.segXMAX, row.segYMAX, row.segHPD, row.segPDMIN, row.segHPP, row.pairPSD, row.pairPFD, row.pairSRMAX, row.pairXD, row.vizMindis) }

    undistort(pairs_ch)
    rectify(undistort.out.uvidarray)
    find_contours(rectify.out.rvidarray)
    segment_contours(find_contours.out)
    parallax_depth(segment_contours.out.stereo)
}

process undistort {
    publishDir "$params.VIDEO_DIR/clips"
        
    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap),val(baseline),val(contourBlack),val(contourMinpulse),val(segXMAX),val(segYMAX),val(segHPD),val(segPDMIN),val(segHPP),val(pairPSD),val(pairPFD),val(pairSRMAX),val(pairXD),val(vizMindis)

    output:
    path '*.mkv'
    tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap),val(baseline),val(contourBlack),val(contourMinpulse),val(segXMAX),val(segYMAX),val(segHPD),val(segPDMIN),val(segHPP),val(pairPSD),val(pairPFD),val(pairSRMAX),val(pairXD),val(vizMindis), emit: uvidarray
 
    script:
    """   
    denoiseCamera.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}.mkv -p $baseDir/${params.DATA_DIR}/stereo_maps/ -pre ${stereomap}_L_single -w ${params.watchvideo} -fr ${params.framesize} -o ${name}${VL}_cl_${start}_${end}
    denoiseCamera.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}.mkv -p $baseDir/${params.DATA_DIR}/stereo_maps/ -pre ${stereomap}_R_single -w ${params.watchvideo} -fr ${params.framesize} -o ${name}${VR}_cl_${start}_${end}

    """
}
process rectify {
    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    publishDir "$params.VIDEO_DIR/rectified"

    input:
    tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap),val(baseline),val(contourBlack),val(contourMinpulse),val(segXMAX),val(segYMAX),val(segHPD),val(segPDMIN),val(segHPP),val(pairPSD),val(pairPFD),val(pairSRMAX),val(pairXD),val(vizMindis)

    output:
    path('*.mkv')
    tuple file('*L.mkv'), file('*R.mkv'), val(name), val(baseline),val(contourBlack),val(contourMinpulse),val(segXMAX),val(segYMAX),val(segHPD),val(segPDMIN),val(segHPP),val(pairPSD),val(pairPFD),val(pairSRMAX),val(pairXD),val(vizMindis), emit: rvidarray
 


    script:
    """
    rectify_videos.py -v1 $baseDir/${params.VIDEO_DIR}/clips/${name}${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/${name}${VR}_cl_${start}_${end}_undis.mkv -f $baseDir/${params.DATA_DIR}/stereo_maps/${stereomap}_stereoMap.xml -l ${params.lines} -w ${params.watchvideo} -pre ${name}
    """
}

process find_contours {

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'
    publishDir "$params.DATA_DIR/contours"

    input:
    tuple val(VL), val(VR), val(name), val(baseline),val(contourBlack),val(contourMinpulse),val(segXMAX),val(segYMAX),val(segHPD),val(segPDMIN),val(segHPP),val(pairPSD),val(pairPFD),val(pairSRMAX),val(pairXD),val(vizMindis)
    
    output:
    tuple file('*.tab'), val(name), val(baseline),val(segXMAX),val(segYMAX),val(segHPD),val(segPDMIN),val(segHPP),val(pairPSD),val(pairPFD),val(pairSRMAX),val(pairXD),val(vizMindis)

    script:
    """
    find_contours.py -v1 $VL -v2 $VR -b ${contourBlack} -m ${contourMinpulse} -f ${name} -l ${params.watchvideo} -d ${params.delay}

    """
}
process segment_contours {
    conda = 'conda-forge::matplotlib=3.3.3 conda-forge::pandas=1.2.0  conda-forge::seaborn=0.12.2  conda-forge::numpy=1.24.2 conda-forge::scipy=1.10.1'

    publishDir "$params.DATA_DIR/contours"

    input:
    tuple file(f), val(name), val(baseline),val(segXMAX),val(segYMAX),val(segHPD),val(segPDMIN),val(segHPP),val(pairPSD),val(pairPFD),val(pairSRMAX),val(pairXD),val(vizMindis)
    
    output:
    tuple file('segmented_*.tab'), val(name)
    tuple file('stereo_*.tab'), val(name), val(baseline), emit: stereo

    script:
    """
    segment_pulses.py -f $f -n $name -HPP ${segHPP} -HPD ${segHPD} -XMAX ${segXMAX} -YMAX ${segYMAX} -SRMAX ${pairSRMAX} -PDMIN ${segPDMIN} -PSD ${pairPSD} -PFD ${pairPFD} -XD ${pairXD}
    """
}
process parallax_depth {
    conda = 'conda-forge::matplotlib=3.3.3 conda-forge::pandas=1.2.0  conda-forge::seaborn=0.12.2  conda-forge::numpy=1.19.4'
    publishDir "$params.DATA_DIR/contours"

    input:
    tuple file(f), val(name), val(baseline)

    output:
    tuple file('coordinates_*.tab')

    script:
    """
    parallax_depth.py -f $f -o $name -d ${baseline} -F ${params.FOCAL} -ALPHA ${params.ALPHA} -frame_width ${params.frame_width} -frame_height ${params.frame_height} -rate ${params.FPS} 

    """
}
