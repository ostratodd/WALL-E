#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'
params.DATA_DIR='data'

params.watch = 1
params.lines = 1

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
    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    publishDir "$params.VIDEO_DIR/rectified"

    input:
    tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap)

    output:
    path('*.mkv')

    script:
    """
    rectify_videos.py -v1 $baseDir/${params.VIDEO_DIR}/clips/${name}_L_CH_1_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/${name}_R_CH_1_undis.mkv -f $baseDir/data/stereo_maps/${stereomap}_stereoMap.xml -l ${params.lines} -w ${params.watch} -pre ${name}
    """
}
