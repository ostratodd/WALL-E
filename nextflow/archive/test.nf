#!/usr/bin/env nextflow

nextflow.enable.dsl=2

params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'
params.DATA_DIR='data'
params.AN_DIR="$baseDir/analyses/southwater2019/"

workflow {

    pairs_ch = Channel.fromPath(params.metadata, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.VL, row.VR, row.start, row.end, row.name, row.stereomap, row.paramfile) }


     pfile = params.AN_DIR + 'params_southwater2019_pan1.config'
     myfile = file(pfile)
     print myfile.text


    getParameters(pairs_ch)
}

process getParameters {

     input:
     tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap), val(paramfile)

     output:
     tuple val(VL), val(VR), val(start), val(end), val(name), val(stereomap), emit: uvidarray

     """
     echo "HELLO"
     """
}

