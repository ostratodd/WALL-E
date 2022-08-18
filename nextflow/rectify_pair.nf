#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'

/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
    then runs undistort (fisheye) custom for WALLE camera housings           */


workflow RECTIFY {

    pairs_ch = Channel.fromPath(params.metadata, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videoL, row.videoR, row.start, row.end, row.name, row.stereomap) }

    rectify(pairs_ch)
}
workflow {
    RECTIFY()
}
process rectify {
    conda = 'conda-forge::opencv=3.4.1 conda-forge::numpy=1.9.3'

    publishDir "$params.VIDEO_DIR/rectified"

    input:
    tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap)

    output:
    path('*.mkv')

    script:
    """
    rectify_videos.py -v1 $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}_undis.mkv -f $baseDir/${params.VIDEO_DIR}/stereo_maps/${stereomap}_stereoMap.xml -l 0 -w 0 -pre ${name}
    """
}
